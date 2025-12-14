import nltk
from nltk.tokenize import word_tokenize
import librosa
import numpy as np

# Download data NLTK jika belum ada
try:
    nltk.data.find("tokenizers/punkt")
except LookupError:
    nltk.download("punkt", quiet=True)
try:
    nltk.data.find("tokenizers/punkt_tab")
except LookupError:
    nltk.download("punkt_tab", quiet=True)


def calculate_metrics(transcript_text, audio_path, duration_seconds):
    # Hitung Words Per Minute (WPM)
    text = transcript_text.strip()
    words = word_tokenize(text) if text else []
    # Logika: (Jumlah kata / durasi detik) * 60
    wpm = (len(words) / duration_seconds) * 60 if duration_seconds > 0 else 0

    # 2. Deteksi Jeda Panjang (Silence Detection)
    long_pauses = 0
    try:
        y, sr = librosa.load(audio_path, sr=16000)
        non_silent_intervals = librosa.effects.split(y, top_db=25)
        pause_threshold = 2.0
        if len(non_silent_intervals) > 1:
            for i in range(len(non_silent_intervals) - 1):
                end_prev = non_silent_intervals[i][1]
                start_next = non_silent_intervals[i + 1][0]

                silence_seconds = (start_next - end_prev) / sr
                if silence_seconds > pause_threshold:
                    long_pauses += 1
    except Exception as e:
        print(f"Warning NLP: {e}")

    return {
        "text": text,
        "wpm": round(wpm, 1),
        "long_pauses": long_pauses,
        "duration": round(duration_seconds, 2),
    }
