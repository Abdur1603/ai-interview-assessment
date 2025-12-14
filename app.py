import streamlit as st
import os
import sys
import json
from pathlib import Path

# SETUP PATH
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

# IMPORT MODUL
from src.audio_processing import (
    extract_audio,
    get_audio_duration,
    fix_video_for_streaming,
)
from src.transcription import load_whisper_model, transcribe_audio
from src.nlp_analysis import calculate_metrics
from src.agent_engine import run_grading_agent, generate_overall_summary
from src.grading_engine import generate_final_json
from src.rubric_data import RUBRIC_CONFIG

st.set_page_config(page_title="Re:View", layout="wide")

TEMP_DIR = current_dir / "temp"
os.makedirs(TEMP_DIR, exist_ok=True)

# SESSION STATE
if "assessment_results" not in st.session_state:
    st.session_state["assessment_results"] = []

# UI HEADER
st.title("Re:View")
st.caption("Reinforced Interview")

# SIDEBAR
with st.sidebar:
    st.header("System Status")
    with st.spinner("Initializing Model..."):
        model, device_name = load_whisper_model()

    if not model:
        st.error("❌ Model Error")
        st.stop()

    st.divider()
    st.subheader("Progress")
    completed_ids = [r["id"] for r in st.session_state["assessment_results"]]
    for i in range(1, 6):
        status = "✅" if i in completed_ids else "⬜"
        st.write(f"{status} Soal {i}")

    if st.button("Reset Data"):
        st.session_state["assessment_results"] = []
        st.rerun()

# MAIN FLOW

# Pilih Soal
q_id = st.selectbox(
    "Pilih Soal Wawancara:",
    options=[1, 2, 3, 4, 5],
    format_func=lambda x: f"Q{x}: {RUBRIC_CONFIG[x]['question'][:80]}...",
)
st.info(f"**Soal Lengkap:** {RUBRIC_CONFIG[q_id]['question']}")

# Upload
uploaded_file = st.file_uploader(
    "Upload Video/Audio Jawaban", type=["mp4", "wav", "mkv"]
)

if uploaded_file:
    # Save & Process Files
    input_path = TEMP_DIR / uploaded_file.name
    audio_path = TEMP_DIR / "temp_audio.wav"
    with open(input_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    # Preview
    col_media, col_res = st.columns([1, 2])
    with col_media:
        if input_path.suffix.lower() in [".mp4", ".mkv", ".mov"]:
            fixed_path = TEMP_DIR / f"fixed_{uploaded_file.name}"
            if not fixed_path.exists():
                fix_video_for_streaming(str(input_path), str(fixed_path))
            st.video(str(fixed_path))
        else:
            st.audio(str(input_path))

    # Action Button
    with col_res:
        if st.button("Analysis Video", type="primary"):
            progress = st.progress(0)
            status = st.empty()

            try:
                # Ekstraksi Audio
                status.text("1/3 Mengekstrak Audio...")
                if not extract_audio(str(input_path), str(audio_path)):
                    st.error("Gagal ekstrak audio")
                    st.stop()
                progress.progress(30)

                # Transkripsi
                status.text("2/3 Mendengarkan & Transkripsi...")
                transcript = transcribe_audio(model, str(audio_path))
                duration = get_audio_duration(str(audio_path))
                nlp_metrics = calculate_metrics(transcript, str(audio_path), duration)
                progress.progress(60)

                # Agentic Reasoning (LLM)
                status.text("3/3 Agentic AI sedang menilai (Reasoning)...")
                score, deep_analysis = run_grading_agent(
                    q_id, transcript, nlp_metrics["wpm"]
                )
                progress.progress(100)
                status.success("Selesai!")

                # Simpan Hasil ke Session State
                st.session_state["assessment_results"] = [
                    r for r in st.session_state["assessment_results"] if r["id"] != q_id
                ]

                # Masukkan data lengkap untuk ditampilkan nanti
                result_data = {
                    "id": q_id,
                    "score": score,
                    "reason": deep_analysis,
                    "transcript": transcript,
                    "metrics": nlp_metrics,
                }
                st.session_state["assessment_results"].append(result_data)
                st.session_state["assessment_results"].sort(key=lambda x: x["id"])

                # VISUALISASI HASIL LANGSUNG
                st.divider()
                st.subheader(f"📊 Hasil Analisis (Soal {q_id})")

                # Metrics Row
                m1, m2, m3 = st.columns(3)
                m1.metric(
                    "AI Score", f"{score}/4", delta="Pass" if score >= 3 else "Low"
                )
                m2.metric("Kecepatan (WPM)", f"{nlp_metrics['wpm']}")
                m3.metric("Jeda Panjang", f"{nlp_metrics['long_pauses']}x")

                # Analysis & Transcript Tabs
                tab1, tab2 = st.tabs(["📝 Transkrip", "🧠 AI Reasoning"])

                with tab1:
                    st.text_area("Hasil Transkripsi:", value=transcript, height=200)

                with tab2:
                    st.markdown(f"**Alasan Penilaian:**")
                    st.info(deep_analysis)

            except Exception as e:
                st.error(f"System Error: {e}")

# BAGIAN REPORT VIEW-
# Menampilkan hasil terakhir yang tersimpan di session state (agar tidak hilang saat refresh)
if st.session_state["assessment_results"] and not uploaded_file:
    # Hanya tampilkan jika user tidak sedang upload file baru
    pass

# BAGIAN GENERATE JSON
st.divider()
st.subheader("📥 Final Output")

# Cek Kelengkapan Data
graded_ids = [res["id"] for res in st.session_state["assessment_results"]]
missing_ids = [i for i in range(1, 6) if i not in graded_ids]
is_complete = len(missing_ids) == 0

# Logika Tampilan Proteksi
if not is_complete:
    st.error(f"⛔ AKSES DITOLAK: Anda baru menilai {len(graded_ids)} dari 5 soal.")

    missing_str = ", ".join([f"Soal {i}" for i in missing_ids])
    st.markdown(
        f"""
    **Laporan lengkap tidak dapat dibuat sebelum semua soal dinilai.**
    
    Target yang belum selesai:
    <div style="background-color: #ffcccc; padding: 10px; border-radius: 5px; color: #990000; font-weight: bold;">
        ❌ {missing_str}
    </div>
    """,
        unsafe_allow_html=True,
    )

    st.button(
        "📥 Generate Final Report (JSON)",
        disabled=True,
        help="Selesaikan semua soal dulu!",
    )

else:
    st.success("✅ Semua 5 soal telah dinilai. Siap generate laporan.")

    if st.button("📥 Generate Final Report (JSON)", type="primary"):

        with st.spinner("Membuat kesimpulan akhir..."):
            from src.agent_engine import generate_overall_summary

            # Generate Overall Summary
            overall_summary = generate_overall_summary(
                st.session_state["assessment_results"]
            )

            # Generate Payload
            payload = generate_final_json(
                {},
                st.session_state["assessment_results"],
                ai_overall_notes=overall_summary,
            )

        st.balloons()
        st.subheader("Preview Hasil JSON:")
        st.json(payload)

        json_str = json.dumps(payload, indent=2)
        st.download_button(
            label="💾 Download File JSON",
            data=json_str,
            file_name="final_assessment_result.json",
            mime="application/json",
        )
