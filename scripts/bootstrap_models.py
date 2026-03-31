from pathlib import Path
import os

from transformers import (
    WhisperProcessor,
    WhisperForConditionalGeneration,
    AutoConfig,
    Wav2Vec2FeatureExtractor,
    AutoTokenizer,
    AutoModelForSequenceClassification,
)

from app.core.config import settings
from app.services.genre_service import Wav2Vec2ForSpeechClassification


def ensure_dir(path: str) -> Path:
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


def is_model_dir_ready(path: Path, required_files: list[str]) -> bool:
    return all((path / file_name).exists() for file_name in required_files)


def bootstrap_whisper() -> None:
    target = ensure_dir(settings.WHISPER_MODEL_PATH)

    required = ["config.json", "model.safetensors", "preprocessor_config.json"]
    if is_model_dir_ready(target, required):
        print(f"[bootstrap] Whisper already exists: {target}")
        return

    print("[bootstrap] Downloading Whisper...")
    processor = WhisperProcessor.from_pretrained(settings.WHISPER_MODEL_ID)
    model = WhisperForConditionalGeneration.from_pretrained(settings.WHISPER_MODEL_ID)
    model.config.forced_decoder_ids = None

    processor.save_pretrained(str(target))
    model.save_pretrained(str(target))
    print(f"[bootstrap] Whisper saved to {target}")


def bootstrap_genre() -> None:
    target = ensure_dir(settings.GENRE_MODEL_PATH)

    required = ["config.json", "model.safetensors", "preprocessor_config.json"]
    if is_model_dir_ready(target, required):
        print(f"[bootstrap] Genre model already exists: {target}")
        return

    print("[bootstrap] Downloading genre model...")
    config = AutoConfig.from_pretrained(settings.GENRE_MODEL_ID)
    feature_extractor = Wav2Vec2FeatureExtractor.from_pretrained(settings.GENRE_MODEL_ID)
    model = Wav2Vec2ForSpeechClassification.from_pretrained(settings.GENRE_MODEL_ID)

    config.save_pretrained(str(target))
    feature_extractor.save_pretrained(str(target))
    model.save_pretrained(str(target))
    print(f"[bootstrap] Genre model saved to {target}")


def bootstrap_mood() -> None:
    target = ensure_dir(settings.MOOD_MODEL_PATH)

    required = ["config.json", "model.safetensors", "tokenizer_config.json", "tokenizer.json"]
    if is_model_dir_ready(target, required):
        print(f"[bootstrap] Mood model already exists: {target}")
        return

    print("[bootstrap] Downloading mood model...")
    tokenizer = AutoTokenizer.from_pretrained(settings.MOOD_MODEL_ID)
    model = AutoModelForSequenceClassification.from_pretrained(settings.MOOD_MODEL_ID)

    tokenizer.save_pretrained(str(target))
    model.save_pretrained(str(target))
    print(f"[bootstrap] Mood model saved to {target}")


def main() -> None:
    ensure_dir(settings.MODELS_DIR if hasattr(settings, "MODELS_DIR") else "/code/models")

    # optional token
    token = os.getenv("HUGGING_FACE_HUB_TOKEN")
    if token:
        os.environ["HF_TOKEN"] = token

    bootstrap_whisper()
    bootstrap_genre()
    bootstrap_mood()

    print("[bootstrap] All models are ready.")


if __name__ == "__main__":
    main()