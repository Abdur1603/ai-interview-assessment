from datetime import datetime

def generate_final_json(candidate_data, assessment_results, ai_overall_notes=None):
    # Hitung skor total (Logika pembobotan)
    raw_score_sum = sum([res["score"] for res in assessment_results])
    # Skala 100: (Total / 20) * 100
    interview_final_score = (raw_score_sum / 20) * 100

    # Asumsi Project Score 100 (Placeholder)
    project_score = 100
    total_score = (project_score * 0.5) + (interview_final_score * 0.5)

    # Format list score per soal
    scores_list = []
    for res in assessment_results:
        scores_list.append(
            {"id": res["id"], "score": res["score"], "reason": res["reason"]}
        )

    # Tentukan catatan akhir
    final_notes = (
        ai_overall_notes
        if ai_overall_notes
        else f"Candidate achieved {interview_final_score}% in interview session."
    )
    current_time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    output_payload = {
        "assessorProfile": {"id": 1, "name": "xxx", "photoUrl": "xxx"},
        "decision": "PASSED" if interview_final_score >= 70 else "NEED REVIEW",
        "reviewedAt": current_time_str,
        "scoresOverview": {
            "project": project_score,
            "interview": interview_final_score,
            "total": total_score,
        },
        "reviewChecklistResult": {
            "project": [],
            "interviews": {"minScore": 0, "maxScore": 4, "scores": scores_list},
        },
        "Overall notes": final_notes,
    }

    return output_payload
