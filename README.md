# Re:View - AI-Powered Interview Assessment System

**Re:View** adalah sistem penilaian wawancara cerdas yang dirancang untuk membantu HR dan asesor dalam menganalisis jawaban kandidat video secara otomatis, objektif, dan efisien.

Sistem ini menggabungkan teknologi **Speech-to-Text (STT)** untuk transkripsi suara presisi tinggi dan **Large Language Model (LLM)** untuk melakukan penalaran (reasoning) serta penilaian jawaban berdasarkan rubrik teknis yang ketat.

---

## 📋 Fitur Utama

1.  **High-Accuracy Transcription:** Mengubah ucapan kandidat menjadi teks bahasa Inggris menggunakan model Whisper Large-V3-Turbo.
2.  **Automated AI Grading:** Memberikan skor (0-4) dan analisis mendalam mengenai relevansi jawaban kandidat terhadap pertanyaan teknis.
3.  **Non-Verbal Analysis:** Menyediakan metrik kecepatan bicara (*Words Per Minute*) dan deteksi jeda hening (*Silence Detection*) untuk mengukur kelancaran.
4.  **Comprehensive Reporting:** Menghasilkan laporan akhir otomatis dalam format JSON yang siap diintegrasikan.

---

## ⚙️ Petunjuk Setup Environment

Ikuti langkah-langkah berikut untuk menyiapkan lingkungan kerja di komputer lokal Anda:

### 1. Prasyarat Sistem
Pastikan komputer Anda telah terinstal:
* **Python** (Versi 3.8 hingga 3.11 direkomendasikan)
* **Git**
* **FFmpeg** (Wajib untuk pemrosesan audio)

### 2. Instalasi FFmpeg (Wajib)
Aplikasi ini membutuhkan FFmpeg untuk mengekstrak dan memproses audio dari video.
* **Windows:**
    1.  Unduh dari [ffmpeg.org](https://ffmpeg.org/download.html).
    2.  Ekstrak folder dan salin path folder `bin` (contoh: `C:\ffmpeg\bin`).
    3.  Tambahkan path tersebut ke *Environment Variables* > *Path* di Windows Anda.
* **Mac:** `brew install ffmpeg`
* **Linux (Ubuntu/Debian):** `sudo apt-get install ffmpeg`

### 3. Clone Repository
Buka terminal/CMD dan jalankan perintah berikut:
```bash
git clone [https://github.com/USERNAME_ANDA/review-app.git](https://github.com/USERNAME_ANDA/review-app.git)
cd review-app
```

### 4. Instalasi Dependensi Python
Disarankan menggunakan Virtual Environment agar sistem Anda tetap bersih.
```bash
# 1. Buat Virtual Environment
python -m venv venv

# 2. Aktifkan Environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# 3. Install Library yang dibutuhkan
pip install -r requirements.txt
```

### 5. Konfigurasi API Key (Environment)
1. Aplikasi ini menggunakan Groq Cloud API untuk akses model LLM dan Whisper.
2. Buat folder .streamlit/
3. Buka folder .streamlit/ di dalam proyek.
4. Buat file bernama secrets.toml
6. Buka file secrets.toml dengan text editor dan masukkan API Key Groq Anda:
```bash
# .streamlit/secrets.toml
GROQ_API_KEYS = [
    "gsk_masukkan_api_key_anda_disini_xxxxxxxxxxxxx"
]
```
### Cara Menjalankan Aplikasi
Setelah semua konfigurasi selesai, jalankan perintah berikut di terminal (pastikan virtual environment aktif):
```bash
streamlit run app.py
```
Aplikasi akan otomatis terbuka di browser Anda pada alamat: http://localhost:8501.

## Atau dapat menggunakan link berikut ini: 
### https://review-capstone.streamlit.app/. 

Langkah Penggunaan:
1. Pilih Soal: Pilih nomor pertanyaan (1-5) pada dropdown menu.
2. Upload: Unggah file video (.mp4, .mkv) atau audio (.wav) jawaban kandidat.
3. Analisis: Klik tombol merah "Analysis Video".
4. Hasil: Tunggu hingga proses (Ekstraksi -> Transkripsi -> AI Reasoning) selesai 100%. Hasil skor dan analisis akan muncul.
5. Laporan Akhir: Setelah menilai ke-5 soal, klik tombol "Generate Final Report" di bagian bawah untuk mengunduh hasil dalam format JSON.