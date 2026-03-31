import numpy as np
import torch
import torchaudio
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple

from torch import nn
from torch.nn import BCEWithLogitsLoss, CrossEntropyLoss, MSELoss
from transformers import AutoConfig, Wav2Vec2FeatureExtractor
from transformers.file_utils import ModelOutput
from transformers.models.wav2vec2.modeling_wav2vec2 import (
    Wav2Vec2Model,
    Wav2Vec2PreTrainedModel,
)

from app.core.config import settings


@dataclass
class SpeechClassifierOutput(ModelOutput):
    loss: Optional[torch.FloatTensor] = None
    logits: torch.FloatTensor = None
    hidden_states: Optional[Tuple[torch.FloatTensor]] = None
    attentions: Optional[Tuple[torch.FloatTensor]] = None


class Wav2Vec2ClassificationHead(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.dense = nn.Linear(config.hidden_size, config.hidden_size)
        self.dropout = nn.Dropout(config.final_dropout)
        self.out_proj = nn.Linear(config.hidden_size, config.num_labels)

    def forward(self, features, **kwargs):
        x = features
        x = self.dropout(x)
        x = self.dense(x)
        x = torch.tanh(x)
        x = self.dropout(x)
        x = self.out_proj(x)
        return x


class Wav2Vec2ForSpeechClassification(Wav2Vec2PreTrainedModel):
    def __init__(self, config):
        super().__init__(config)
        self.num_labels = config.num_labels
        self.pooling_mode = getattr(config, "pooling_mode", "mean")
        self.config = config

        self.wav2vec2 = Wav2Vec2Model(config)
        self.classifier = Wav2Vec2ClassificationHead(config)

        self.init_weights()

    def merged_strategy(self, hidden_states, mode="mean"):
        if mode == "mean":
            return torch.mean(hidden_states, dim=1)
        if mode == "sum":
            return torch.sum(hidden_states, dim=1)
        if mode == "max":
            return torch.max(hidden_states, dim=1)[0]
        raise ValueError("Unsupported pooling mode")

    def forward(
        self,
        input_values,
        attention_mask=None,
        output_attentions=None,
        output_hidden_states=None,
        return_dict=None,
        labels=None,
    ):
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        outputs = self.wav2vec2(
            input_values,
            attention_mask=attention_mask,
            output_attentions=output_attentions,
            output_hidden_states=output_hidden_states,
            return_dict=return_dict,
        )
        hidden_states = outputs[0]
        hidden_states = self.merged_strategy(hidden_states, mode=self.pooling_mode)
        logits = self.classifier(hidden_states)

        loss = None
        if labels is not None:
            if self.config.problem_type is None:
                if self.num_labels == 1:
                    self.config.problem_type = "regression"
                elif self.num_labels > 1 and (labels.dtype == torch.long or labels.dtype == torch.int):
                    self.config.problem_type = "single_label_classification"
                else:
                    self.config.problem_type = "multi_label_classification"

            if self.config.problem_type == "regression":
                loss_fct = MSELoss()
                loss = loss_fct(logits.view(-1, self.num_labels), labels)
            elif self.config.problem_type == "single_label_classification":
                loss_fct = CrossEntropyLoss()
                loss = loss_fct(logits.view(-1, self.num_labels), labels.view(-1))
            else:
                loss_fct = BCEWithLogitsLoss()
                loss = loss_fct(logits, labels)

        if not return_dict:
            output = (logits,) + outputs[2:]
            return ((loss,) + output) if loss is not None else output

        return SpeechClassifierOutput(
            loss=loss,
            logits=logits,
            hidden_states=outputs.hidden_states,
            attentions=outputs.attentions,
        )


class GenreService:
    _instance = None
    _model = None
    _config = None
    _feature_extractor = None
    _device = None
    _sampling_rate = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GenreService, cls).__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if self._model is not None:
            return

        model_path = Path(settings.GENRE_MODEL_PATH)
        if not model_path.exists():
            raise FileNotFoundError(f"Genre model path not found: {model_path}")

        self._device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self._config = AutoConfig.from_pretrained(str(model_path), local_files_only=True)
        self._feature_extractor = Wav2Vec2FeatureExtractor.from_pretrained(
            str(model_path),
            local_files_only=True,
        )
        self._sampling_rate = self._feature_extractor.sampling_rate
        self._model = Wav2Vec2ForSpeechClassification.from_pretrained(
            str(model_path),
            local_files_only=True,
        ).to(self._device)
        self._model.eval()

    @property
    def model(self):
        return self._model

    @property
    def config(self):
        return self._config

    @property
    def feature_extractor(self):
        return self._feature_extractor

    @property
    def sampling_rate(self):
        return self._sampling_rate

    @property
    def device(self):
        return self._device

    def speech_file_to_array_fn(self, path: str) -> np.ndarray:
        speech_array, source_rate = torchaudio.load(path)
        if speech_array.shape[0] > 1:
            speech_array = torch.mean(speech_array, dim=0, keepdim=True)
        resampler = torchaudio.transforms.Resample(source_rate, self.sampling_rate)
        speech = resampler(speech_array).squeeze().numpy()
        return speech

    def predict_top3(self, path: str, chunk_seconds: int = 5) -> list[dict]:
        audio = self.speech_file_to_array_fn(path)
        chunk_size = int(chunk_seconds * self.sampling_rate)

        all_scores = []

        for i in range(0, len(audio), chunk_size):
            chunk = audio[i:i + chunk_size]
            if len(chunk) < self.sampling_rate:
                continue

            inputs = self.feature_extractor(
                chunk,
                sampling_rate=self.sampling_rate,
                return_tensors="pt",
                padding=True,
            )
            inputs = {k: v.to(self.device) for k, v in inputs.items()}

            with torch.no_grad():
                logits = self.model(**inputs).logits
                scores = torch.softmax(logits, dim=-1)[0].cpu().numpy()
                all_scores.append(scores)

        if not all_scores:
            raise ValueError("Could not extract genre scores from audio")

        mean_scores = np.mean(all_scores, axis=0)
        top_ids = np.argsort(mean_scores)[::-1][:3]

        return [
            {
                "label": self.config.id2label[int(i)],
                "score": float(mean_scores[int(i)]),
            }
            for i in top_ids
        ]