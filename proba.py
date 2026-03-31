from transformers import WhisperProcessor, WhisperForConditionalGeneration
import torch

processor = WhisperProcessor.from_pretrained("models/whisper")
model = WhisperForConditionalGeneration.from_pretrained("models/whisper")

import librosa
import torch

def load_audio_with_torchaudio(audio_path: str) -> tuple[torch.Tensor, int]:
    audio, sample_rate = librosa.load(audio_path, sr=16000, mono=True)
    waveform = torch.tensor(audio, dtype=torch.float32).unsqueeze(0)
    return waveform, sample_rate

waveform_en, sample_rate_en = load_audio_with_torchaudio("storage/music/09000f45d32b4310b66bdb34f261aa6d.mp3")

def split_audio(waveform, sample_rate, language, chunk_length_s=30, overlap_s=5):
    chunk_size = int(chunk_length_s * sample_rate)
    overlap = int(overlap_s * sample_rate)

    chunks = []
    i = 0
    while i < waveform.shape[1]:
        chunk = waveform[:, i:i+chunk_size]
        chunks.append(chunk)
        i += chunk_size - overlap

    transcriptions = []
    for chunk in chunks:
        input_features = processor(
            chunk.squeeze().numpy(),
            sampling_rate=sample_rate,
            return_tensors="pt"
        ).input_features.to("cuda" if torch.cuda.is_available() else "cpu")
        input_features = input_features.to(model.dtype)
        with torch.no_grad():
            predicted_ids = model.generate(
                                input_features,
                                num_beams=5,
                                language=language,
                                task="transcribe",
                                forced_decoder_ids=processor.get_decoder_prompt_ids(
                                    language=language,
                                    task="transcribe"
                                )
                            )

        text = processor.batch_decode(predicted_ids, skip_special_tokens=True)[0]
        transcriptions.append(text)

    full_transcription = " ".join(transcriptions)
    return full_transcription

full_transcription_en = split_audio(waveform_en, sample_rate_en, "en")
print(full_transcription_en)