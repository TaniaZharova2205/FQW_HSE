from pathlib import Path
import time

REQUIRED_DIRS = [
    Path("/code/models/whisper"),
    Path("/code/models/m3hrdadfi-wav2vec"),
    Path("/code/models/mood_model"),
]


def main():
    while True:
        ready = all(path.exists() and any(path.iterdir()) for path in REQUIRED_DIRS)
        if ready:
            print("[wait] models are ready")
            return
        print("[wait] waiting for models...")
        time.sleep(5)


if __name__ == "__main__":
    main()