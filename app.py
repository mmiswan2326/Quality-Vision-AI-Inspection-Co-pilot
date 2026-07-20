import streamlit as st
import pandas as pd
from pathlib import Path
from PIL import Image
from datetime import datetime
from src.utils import predict_visual_defect
from src.defect_risk import calculate_defect_risk, build_human_decision
from src.text_analyzer import summarize_inspection_notes, detect_quality_keywords
from src.report_generator import generate_pdf_report

st.set_page_config(page_title="QualityVision AI", page_icon="🏭", layout="wide")

st.title("🏭 QualityVision AI — Intelligent Manufacturing Quality Inspection Co-Pilot")
st.caption("A simplified, meaningful workflow for factory quality inspection")

with st.expander("Simple Workflow Explanation", expanded=True):
    st.markdown("""
    **Step 1:** Upload product image and inspection notes.  
    **Step 2:** Enter only important batch details.  
    **Step 3:** AI checks image defect + production risk.  
    **Step 4:** Inspector makes final decision.  
    **Step 5:** System generates a complete PDF report.
    """)

col1, col2 = st.columns([1, 1])

with col1:
    st.header("1. Inspection Evidence")
    image_file = st.file_uploader("Upload product/part image", type=["png", "jpg", "jpeg"])
    notes = st.text_area(
        "Operator / Inspection Notes",
        height=150,
        placeholder="Example: Minor scratch observed near product edge. Machine vibration was slightly higher than normal."
    )
    csv_file = st.file_uploader("Optional: Upload batch CSV", type=["csv"])

with col2:
    st.header("2. Batch & Sensor Details")
    st.caption("Only important fields are kept for a clean demo.")
    batch_id = st.text_input("Batch ID", "B001")
    product_type = st.selectbox("Product / Part Type", ["Metal Bearing", "Plastic Cap", "Circuit Board", "Metal Gear", "Packaging Unit", "Other"])
    machine_health = st.selectbox("Machine Health Status", ["Normal", "Warning", "Critical"])
    temperature = st.slider("Machine Temperature", min_value=40, max_value=110, value=72)
    previous_defects = st.number_input("Previous Defects in Recent Batch", min_value=0, max_value=20, value=1)
    
if csv_file is not None:
    df = pd.read_csv(csv_file)

    st.subheader("Uploaded Batch CSV Preview")
    st.dataframe(df.head(), use_container_width=True)

    if "temperature" in df.columns:
        avg_temp = df["temperature"].mean()
        st.metric("Average Temp", round(avg_temp, 2))

    if "defect_count" in df.columns:
        defect_rate = df["defect_count"].mean()
        st.metric("Average Defect Rate", round(defect_rate, 2))

if "analysis_done" not in st.session_state:
    st.session_state.analysis_done = False

if st.button("Run AI Quality Inspection", type="primary"):
    if image_file is None:
        st.error("Please upload a product/part image first.")
        st.stop()

    # Save uploaded image so it can be embedded in PDF report.
    temp_image_path = Path("uploaded_inspection_image.jpg")
    image = Image.open(image_file).convert("RGB")
    image.save(temp_image_path)
    image_file.seek(0)

    image_result = predict_visual_defect(image_file)
    notes_summary = summarize_inspection_notes(notes)
    keywords = detect_quality_keywords(notes)
    risk_result = calculate_defect_risk(
        temperature=temperature,
        previous_defects=previous_defects,
        machine_health=machine_health,
        visual_defect_score=image_result["visual_defect_score"],
    )

    st.session_state.analysis_done = True
    st.session_state.image_result = image_result
    st.session_state.notes_summary = notes_summary
    st.session_state.keywords = keywords
    st.session_state.risk_result = risk_result
    st.session_state.image_path = str(temp_image_path)
    st.session_state.batch_info = {
        "Batch ID": batch_id,
        "Product / Part Type": product_type,
        "Machine Health Status": machine_health,
        "Machine Temperature": f"{temperature} °C",
        "Previous Defects in Recent Batch": previous_defects,
    }

if st.session_state.analysis_done:
    image_result = st.session_state.image_result
    risk_result = st.session_state.risk_result
    notes_summary = st.session_state.notes_summary
    keywords = st.session_state.keywords

    st.header("3. AI Analysis Results")
    m1, m2, m3 = st.columns(3)
    m1.metric("Visual Defect", image_result["defect_label"])
    m2.metric("Confidence", f"{image_result['confidence']}%")
    m3.metric("Batch Risk", f"{risk_result['risk_label']} ({risk_result['risk_score']}/100)")

    left, right = st.columns([1, 1])
    with left:
        st.image(image_result["image"], caption="Uploaded product/part image", use_container_width=True)
    with right:
        st.subheader("AI Recommendation")
        st.info(risk_result["recommendation"])
        st.subheader("Notes Summary")
        st.write(notes_summary)
        if keywords:
            st.write("**Detected quality keywords:** " + ", ".join(keywords))

    st.subheader("Explainable AI — Why this risk score?")
    importance_df = pd.DataFrame({
        "Factor": list(risk_result["feature_importance"].keys()),
        "Influence": list(risk_result["feature_importance"].values()),
    })
    st.bar_chart(importance_df.set_index("Factor"))
    st.caption("Final version can add Grad-CAM heatmap after CNN training.")

    st.header("4. Human-in-the-Loop Review")
    st.write("Inspector ka decision ab final workflow action banata hai — sirf text nahi.")
    decision_type = st.radio(
        "Inspector Decision",
        ["Approve Batch", "Reject Batch", "Hold for Rework", "Modify Recommendation"],
        horizontal=True
    )

    custom_decision = ""
    if decision_type == "Modify Recommendation":
        custom_decision = st.text_area(
            "Write Custom Final Decision",
            placeholder="Example: Approve only 70% units after manual sampling; remaining units go to rework."
        )

    inspector_notes = st.text_area(
        "Inspector Notes",
        placeholder="Example: Checked 10 sample units manually. Defect found on 2 units."
    )

    human_decision = build_human_decision(
        decision_type=decision_type,
        ai_recommendation=risk_result["recommendation"],
        custom_decision=custom_decision,
        inspector_notes=inspector_notes,
    )

    st.subheader("Final Workflow Action")
    status_color = {
        "APPROVED": "success",
        "REJECTED": "error",
        "ON HOLD / REWORK": "warning",
        "MODIFIED BY INSPECTOR": "info",
    }
    getattr(st, status_color.get(human_decision["final_status"], "info"))(f"Final Status: {human_decision['final_status']}")
    st.write("**Final Action:**", human_decision["final_action"])
    st.write("**QA Action:**", human_decision["qa_action"])

    st.header("5. Download Complete PDF Report")
    if st.button("Generate Complete PDF Report"):
        output_path = "QualityVision_AI_Final_Report.pdf"
        generate_pdf_report(
            output_path=output_path,
            batch_info=st.session_state.batch_info,
            image_result=image_result,
            risk_result=risk_result,
            human_decision=human_decision,
            notes_summary=notes_summary,
            image_path=st.session_state.image_path,
        )
        with open(output_path, "rb") as f:
            st.download_button(
                "Download / Open PDF Report",
                f,
                file_name="QualityVision_AI_Final_Report.pdf",
                mime="application/pdf"
            )
