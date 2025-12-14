import os
import warnings
import streamlit as st
from faster_whisper import WhisperModel
from openai import OpenAI

warnings.filterwarnings("ignore")

# KONFIGURASI
LOCAL_MODEL_PATH = os.path.join("models", "whisper-large-v3-turbo-ct2-int8")
GROQ_MODEL_ID = "whisper-large-v3-turbo"

TECHNICAL_PROMPT = "Technical interview regarding Machine Learning, Data Science, TensorFlow, Keras, CNN, transfer learning, dropout, overfitting, Python programming, and model optimization."


def get_groq_api_key():
    """Mengambil API Key Groq dari secrets.toml"""
    try:
        if "GROQ_API_KEYS" in st.secrets:
            return st.secrets["GROQ_API_KEYS"][0]
    except Exception:
        return None
    return None


@st.cache_resource(show_spinner=False)
def load_whisper_model():
    if os.path.exists(LOCAL_MODEL_PATH):
        print(f"Local model found at: {LOCAL_MODEL_PATH}")
        device = (
            "cuda" if os.environ.get("CUDA_VISIBLE_DEVICES", None) != "-1" else "cpu"
        )
        try:
            import torch

            if torch.cuda.is_available():
                device = "cuda"
        except ImportError:
            pass
        print(f"DEVICE: {device.upper()}")
        compute_type = "float16" if device == "cuda" else "int8"
        try:
            model = WhisperModel(
                LOCAL_MODEL_PATH, device=device, compute_type=compute_type
            )
            return model, f"LOCAL ({device.upper()})"
        except Exception as e:
            st.error(f"Gagal memuat model lokal: {e}")
            return None, "ERROR"
    else:
        print("Local model not found. Switching to Groq API...")
        api_key = get_groq_api_key()
        if not api_key:
            st.error(
                "Model lokal tidak ditemukan DAN API Key Groq tidak ada di secrets.toml."
            )
            return None, "MISSING CONFIG"
        try:
            client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=api_key)
            return client, "GROQ CLOUD API"
        except Exception as e:
            st.error(f"Gagal inisialisasi Groq: {e}")
            return None, "ERROR"


def transcribe_audio(model_or_client, audio_path):
    """
    Fungsi Transkripsi Sederhana (Tanpa Confidence Score).
    Hanya mengembalikan teks string.
    """
    if model_or_client is None:
        return ""

    try:
        final_text = ""
        if isinstance(model_or_client, OpenAI):
            with open(audio_path, "rb") as file:
                transcription = model_or_client.audio.transcriptions.create(
                    file=(os.path.basename(audio_path), file.read()),
                    model=GROQ_MODEL_ID,
                    language="en",
                    prompt=TECHNICAL_PROMPT,
                    temperature=0.0,
                )
            final_text = transcription.text.strip()
        else:
            segments, info = model_or_client.transcribe(
                audio_path,
                beam_size=5,
                language="en",
                task="transcribe",
                initial_prompt=TECHNICAL_PROMPT,
            )
            # Gabungkan semua segmen teks
            final_text = " ".join([s.text for s in segments]).strip()

        return final_text

    except Exception as e:
        print(f"Error transkripsi: {e}")
        st.error(f"Gagal transkripsi: {str(e)}")
        return ""
