import json
from openai import OpenAI
from src.rubric_data import RUBRIC_CONFIG
import streamlit as st
from streamlit.runtime.secrets import StreamlitSecretNotFoundError

try:
    if "GROQ_API_KEYS" in st.secrets:
        GROQ_API_KEYS = st.secrets["GROQ_API_KEYS"]
    else:
        raise ValueError("Konfigurasi 'GROQ_API_KEYS' tidak ditemukan di secrets.")
    if not GROQ_API_KEYS:
        raise ValueError("List GROQ_API_KEYS kosong.")

except (FileNotFoundError, StreamlitSecretNotFoundError, ValueError, KeyError) as e:
    st.error("⛔ **Konfigurasi Fatal: API Key Tidak Ditemukan**")
    st.markdown(
        f"""
    Sistem tidak dapat menemukan API Key Groq. 
    
    **Jika di Lokal:**
    Pastikan file `.streamlit/secrets.toml` ada dan berisi:
    ```toml
    GROQ_API_KEYS = ["gsk_key_baru_anda_disini"]
    ```
    
    **Jika di Streamlit Cloud:**
    Masukkan konfigurasi di menu **Advanced Settings > Secrets**.
    
    *Error Detail: {str(e)}*
    """
    )
    st.stop()

MODEL_NAME = "llama-3.3-70b-versatile"


def get_groq_client(api_key):
    return OpenAI(base_url="https://api.groq.com/openai/v1", api_key=api_key)


def call_llm_with_fallback(system_prompt, user_prompt):
    """
    Memanggil LLM dengan mekanisme fallback key dan error handling JSON.
    """
    last_error = None

    for i, api_key in enumerate(GROQ_API_KEYS):
        try:
            client = get_groq_client(api_key)

            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.1,
                response_format={"type": "json_object"},
            )

            # Validasi JSON Parsing
            content = response.choices[0].message.content
            return json.loads(content)

        except json.JSONDecodeError:
            last_error = "Output LLM bukan JSON valid."
            continue
        except Exception as e:
            last_error = str(e)
            print(f"⚠️ Key ke-{i} gagal: {last_error}")
            continue

    raise RuntimeError(
        f"Semua API Key Groq gagal / Limit Habis. Error terakhir: {last_error}"
    )


def run_grading_agent(question_id, transcript, wpm):
    """
    Agent penilai per soal.
    """
    if question_id not in RUBRIC_CONFIG:
        return 0, "Question ID not found"

    config = RUBRIC_CONFIG[question_id]

    system_prompt = """
    You are a Senior Technical Assessor.
    Your task is to grade interview answers.
    You MUST output valid JSON.
    IMPORTANT: The 'reason' field must contain a DEEP, DETAILED ANALYSIS (3-5 sentences). 
    Do not give short summaries. Explain the strengths, missing keywords, and logic gaps clearly in the 'reason'.
    """

    user_prompt = f"""
    ### QUESTION:
    "{config['question']}"
    
    ### RUBRIC CRITERIA:
    {config.get('criteria_text', 'No criteria provided.')}
    
    ### CANDIDATE ANSWER:
    "{transcript}"
    
    ### METRICS:
    - Speaking Rate: {wpm} WPM.
    
    ### TASK:
    1. Score the answer (0-4) based strictly on the rubric.
    2. Write a detailed analysis for the 'reason' field. Explain WHY they got that score. Mention specific technical terms used or missed.
    
    ### REQUIRED JSON OUTPUT:
    {{
        "score": (integer 0-4),
        "reason": (string, detailed analysis paragraph)
    }}
    """

    try:
        result = call_llm_with_fallback(system_prompt, user_prompt)
        # Fallback nilai default jika JSON tidak lengkap key-nya
        return result.get("score", 0), result.get("reason", "No analysis provided.")
    except Exception as e:
        return 0, f"System Error: {str(e)}"


def generate_overall_summary(assessment_results):
    """
    Agent pembuat kesimpulan akhir.
    """
    # Gabungkan semua analisis menjadi satu teks konteks
    combined_analysis = ""
    for res in assessment_results:
        combined_analysis += (
            f"Question {res['id']} Score ({res['score']}/4): {res['reason']}\n\n"
        )

    system_prompt = """
    You are a Lead Interviewer. 
    You are provided with detailed grading notes from 5 technical interview questions.
    Your task is to write one cohesive 'Overall Note' (Conclusion).
    """

    user_prompt = f"""
    ### CANDIDATE PERFORMANCE DATA:
    {combined_analysis}
    
    ### INSTRUCTION:
    Write a professional summary paragraph (approx 50-80 words) concluding the candidate's overall competency, strengths, and areas for improvement based on the data above.
    Do not use bullet points. Write it as a flowing paragraph for a final report.
    
    ### REQUIRED JSON OUTPUT:
    {{
        "overall_summary": "The candidate demonstrated..."
    }}
    """

    try:
        result = call_llm_with_fallback(system_prompt, user_prompt)
        return result.get("overall_summary", "Summary generation failed.")
    except Exception as e:
        return f"Failed to generate summary: {str(e)}"
