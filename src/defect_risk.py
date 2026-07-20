def machine_health_score(machine_health):
    mapping = {
        "Normal": 0.10,
        "Warning": 0.55,
        "Critical": 0.90,
    }
    return mapping.get(machine_health, 0.30)


def calculate_defect_risk(temperature, previous_defects, machine_health, visual_defect_score):
    """Meaningful demo defect risk scoring using only valuable fields."""
    score = 0

    # Temperature influence
    if temperature >= 90:
        score += 30
    elif temperature >= 80:
        score += 20
    elif temperature >= 70:
        score += 10
    else:
        score += 5

    # Machine health influence
    mh = machine_health_score(machine_health)
    score += int(mh * 30)

    # Previous defect history influence
    if previous_defects >= 5:
        score += 25
    elif previous_defects >= 2:
        score += 15
    elif previous_defects >= 1:
        score += 8

    # Image model influence
    score += int(visual_defect_score * 30)
    score = min(score, 100)

    if score >= 75:
        label = "Critical Risk"
        recommendation = "Do not release. Quarantine batch and start root-cause analysis."
    elif score >= 55:
        label = "High Risk"
        recommendation = "Hold batch for manual inspection and possible rework."
    elif score >= 35:
        label = "Medium Risk"
        recommendation = "Inspect sample units before approval."
    else:
        label = "Low Risk"
        recommendation = "Batch can be approved if inspector confirms no visible issue."

    return {
        "risk_score": score,
        "risk_label": label,
        "recommendation": recommendation,
        "feature_importance": {
            "Visual Defect Evidence": visual_defect_score,
            "Machine Health": mh,
            "Temperature": min(temperature / 100, 1.0),
            "Previous Defects": min(previous_defects / 6, 1.0),
        }
    }


def build_human_decision(decision_type, ai_recommendation, custom_decision="", inspector_notes=""):
    """Turns inspector selection into a meaningful final workflow action."""
    if decision_type == "Approve Batch":
        final_status = "APPROVED"
        final_action = "Release batch for packaging/shipment. Keep report for QA record."
        qa_action = "No rework required. Continue normal monitoring."
    elif decision_type == "Reject Batch":
        final_status = "REJECTED"
        final_action = "Quarantine batch immediately. Stop release and inform production manager."
        qa_action = "Start root-cause analysis and document defect category."
    elif decision_type == "Hold for Rework":
        final_status = "ON HOLD / REWORK"
        final_action = "Send batch to rework station. Re-inspection required before approval."
        qa_action = "Create rework ticket and assign responsible technician."
    else:
        final_status = "MODIFIED BY INSPECTOR"
        final_action = custom_decision.strip() if custom_decision.strip() else "Inspector modified the AI recommendation. Follow inspector notes."
        qa_action = "Supervisor review recommended if modification conflicts with AI risk level."

    return {
        "decision_type": decision_type,
        "final_status": final_status,
        "ai_recommendation": ai_recommendation,
        "final_action": final_action,
        "qa_action": qa_action,
        "inspector_notes": inspector_notes.strip() if inspector_notes.strip() else "No additional inspector notes."
    }
