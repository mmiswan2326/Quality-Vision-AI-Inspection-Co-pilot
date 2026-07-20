# QualityVision AI — Updated Manufacturing Quality Inspection Co-Pilot

This is the improved version of the Manufacturing Quality Inspection Co-Pilot.

## What changed in this updated version?

### 1. Simplified Batch & Sensor Details
The previous version had too many input fields. This version keeps only high-value fields:

- Batch ID
- Product / Part Type
- Machine Health Status
- Temperature
- Previous Defects

These fields are easier to explain in a demo and more meaningful for quality inspection.

### 2. Better Human-in-the-Loop Workflow
Inspector decisions now actually change the final result:

- **Approve Batch** → batch is released for packaging/shipment
- **Reject Batch** → batch is quarantined and root-cause analysis is required
- **Hold for Rework** → rework action is required before approval
- **Modify Recommendation** → inspector writes a custom final decision

### 3. Improved PDF Report
The PDF report is now more complete and arranged properly. It includes:

- Executive summary
- Batch details
- Uploaded image preview
- Operator notes summary
- AI analysis
- Explainable AI feature influence
- Human inspector final decision
- Final recommendation/action plan

## Run

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Demo Flow

1. Upload a product image.
2. Add operator notes.
3. Fill simplified batch details.
4. Click **Run AI Quality Inspection**.
5. Select inspector decision.
6. Generate and download PDF report.
