import re
from pathlib import Path

import torch
import torchaudio
from transformers import WhisperProcessor, WhisperForConditionalGeneration

from app.core.config import settings


class TranscriptionError(Exception):
    pass


class TranscriptionService:
    _instance = None
    _processor: WhisperProcessor | None = None
    _model: WhisperForConditionalGeneration | None = None
    _device: str | None = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TranscriptionService, cls).__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if self._processor is not None and self._model is not None:
            return

        self._device = "cuda" if torch.cuda.is_available() else "cpu"

        self._processor = WhisperProcessor.from_pretrained(
            settings.WHISPER_MODEL_PATH,
            local_files_only=True,
        )
        self._model = WhisperForConditionalGeneration.from_pretrained(
            settings.WHISPER_MODEL_PATH,
            local_files_only=True,
        )

        self._model.config.forced_decoder_ids = None
        self._model.generation_config.forced_decoder_ids = None

        self._model.to(self._device)
        self._model.eval()

    @property
    def device(self) -> str:
        return self._device

    @property
    def processor(self) -> WhisperProcessor:
        return self._processor

    @property
    def model(self) -> WhisperForConditionalGeneration:
        return self._model

    @staticmethod
    def load_audio(audio_path: str) -> tuple[torch.Tensor, int]:
        path = Path(audio_path)
        if not path.exists():
            raise TranscriptionError(f"Audio file not found: {audio_path}")

        waveform, sample_rate = torchaudio.load(str(path))

        if waveform.shape[0] > 1:
            waveform = torch.mean(waveform, dim=0, keepdim=True)

        if sample_rate != 16000:
            resampler = torchaudio.transforms.Resample(
                orig_freq=sample_rate,
                new_freq=16000,
            )
            waveform = resampler(waveform)
            sample_rate = 16000

        return waveform, sample_rate

    @staticmethod
    def detect_language_hint(track_title: str | None = None, artist: str | None = None) -> str | None:
        text = f"{artist or ''} {track_title or ''}".lower()

        if re.search(r"[а-яё]", text):
            return "ru"

        return None

    def split_and_transcribe(
        self,
        waveform: torch.Tensor,
        sample_rate: int,
        language: str | None = None,
        chunk_length_s: int | None = None,
        overlap_s: int | None = None,
    ) -> str:
        chunk_length_s = chunk_length_s or settings.WHISPER_CHUNK_LENGTH_SEC
        overlap_s = overlap_s or settings.WHISPER_OVERLAP_SEC

        chunk_size = int(chunk_length_s * sample_rate)
        overlap = int(overlap_s * sample_rate)

        if chunk_size <= overlap:
            raise TranscriptionError("chunk_length_s must be greater than overlap_s")

        chunks = []
        i = 0
        while i < waveform.shape[1]:
            chunk = waveform[:, i:i + chunk_size]
            if chunk.shape[1] > 0:
                chunks.append(chunk)
            i += chunk_size - overlap

        transcriptions: list[str] = []

        with torch.no_grad():
            for chunk in chunks:
                processed = self.processor(
                    chunk.squeeze().numpy(),
                    sampling_rate=sample_rate,
                    return_tensors="pt",
                )

                input_features = processed.input_features.to(self.device)

                attention_mask = None
                if hasattr(processed, "attention_mask") and processed.attention_mask is not None:
                    attention_mask = processed.attention_mask.to(self.device)

                generate_kwargs = {
                    "input_features": input_features,
                    "task": "transcribe",
                    "num_beams": 5,
                }

                if attention_mask is not None:
                    generate_kwargs["attention_mask"] = attention_mask

                if language:
                    generate_kwargs["language"] = language

                predicted_ids = self.model.generate(**generate_kwargs)

                text = self.processor.batch_decode(
                    predicted_ids,
                    skip_special_tokens=True,
                )[0].strip()

                if text:
                    transcriptions.append(text)

        return " ".join(transcriptions).strip()

    def transcribe_track(
        self,
        audio_path: str,
        track_title: str | None = None,
        artist: str | None = None,
    ) -> str:
        waveform, sample_rate = self.load_audio(audio_path)
        language = self.detect_language_hint(track_title=track_title, artist=artist)

        text = self.split_and_transcribe(
            waveform=waveform,
            sample_rate=sample_rate,
            language=language,
        )

        if not text:
            raise TranscriptionError("Transcription is empty")

        return text