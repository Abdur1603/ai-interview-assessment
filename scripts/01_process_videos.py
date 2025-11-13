import ffmpeg
import librosa
import os
from pathlib import Path
from tqdm import tqdm

# --- Konfigurasi ---
PROJECT_ROOT = Path(__file__).parent.parent

RAW_VIDEO_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_AUDIO_DIR = PROJECT_ROOT / "data" / "processed" / "audio"
TARGET_SAMPLE_RATE = 16000  # Target SR untuk model Whisper
# --------------------

def extract_audio(video_path, audio_path):
    """
    Mengekstrak audio dari file video menggunakan ffmpeg-python.
    """
    try:
        (
            ffmpeg
            .input(str(video_path))
            .output(str(audio_path), ac=1, ar=TARGET_SAMPLE_RATE) # ac=1 (mono), ar=16k
            .overwrite_output()
            .run(quiet=True) # quiet=True agar tidak ada output console dari ffmpeg
        )
        return True
    except ffmpeg.Error as e:
        print(f"Error ffmpeg saat memproses {video_path}: {e.stderr.decode()}")
        return False

def resample_and_clean(audio_path, target_path, sr=TARGET_SAMPLE_RATE):
    """
    Memuat audio, memastikan mono dan sample rate yang benar menggunakan Librosa.
    Ini adalah langkah verifikasi ganda jika ffmpeg gagal.
    """
    try:
        # Muat audio, pastikan mono=True dan sr=TARGET_SAMPLE_RATE
        y, s = librosa.load(audio_path, sr=sr, mono=True)
        
        # Simpan ulang file yang sudah bersih
        # (Fungsi ini digantikan oleh ffmpeg langsung, tapi bagus untuk verifikasi)
        # librosa.output.write_wav(target_path, y, s)
        
        # Untuk saat ini, kita anggap ffmpeg sudah menangani ini.
        # Jika Anda ingin pembersihan tambahan (misal: trim silence), tambahkan di sini.
        pass
        
    except Exception as e:
        print(f"Error librosa saat memproses {audio_path}: {e}")

def main():
    print("Memulai proses ekstraksi dan pembersihan audio...")
    
    # 1. Pastikan folder output ada
    PROCESSED_AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    
    # 2. Cari semua file video di data/raw
    # Kita cari ekstensi video umum
    video_files = list(RAW_VIDEO_DIR.glob("*.mp4")) + \
                  list(RAW_VIDEO_DIR.glob("*.avi")) + \
                  list(RAW_VIDEO_DIR.glob("*.mov")) + \
                  list(RAW_VIDEO_DIR.glob("*.mkv")) + \
                  list(RAW_VIDEO_DIR.glob("*.webm"))

    if not video_files:
        print(f"Tidak ada file video yang ditemukan di {RAW_VIDEO_DIR}")
        return

    print(f"Ditemukan {len(video_files)} file video. Memulai pemrosesan...")

    # 3. Proses setiap file
    for video_path in tqdm(video_files, desc="Memproses Video"):
        # Tentukan nama file output .wav
        # misal: video1.mp4 -> video1.wav
        output_filename = video_path.stem + ".wav"
        output_path = PROCESSED_AUDIO_DIR / output_filename
        
        if output_path.exists():
            print(f"File {output_filename} sudah ada, dilewati.")
            continue
            
        # Ekstrak audio
        success = extract_audio(video_path, output_path)
        
        if success:
            # (Opsional) Verifikasi dengan Librosa
            # resample_and_clean(output_path, output_path)
            pass
        
    print("-" * 30)
    print("Proses selesai.")
    print(f"Semua audio yang telah diproses disimpan di: {PROCESSED_AUDIO_DIR}")

if __name__ == "__main__":
    main()