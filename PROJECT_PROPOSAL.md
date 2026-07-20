# QualityVision AI — Updated Project Proposal

## Title

QualityVision AI: Multimodal Manufacturing Quality Inspection Co-Pilot

## Updated Workflow

1. User uploads product image.
2. User enters operator notes.
3. User enters only important batch details:
   - Batch ID
   - Product / Part Type
   - Machine Health Status
   - Temperature
   - Previous Defects
4. AI predicts visual defect class and batch risk.
5. Inspector makes a meaningful final decision.
6. System generates a complete PDF inspection report.

## Why this workflow is better

The new workflow is simpler, easier to demo, and more meaningful for judges. It avoids unnecessary fields and focuses only on evidence that affects quality decisions.

## Human Decision Logic

- Approve Batch: release for shipment/packaging.
- Reject Batch: quarantine and start root-cause analysis.
- Hold for Rework: send to rework and re-inspect.
- Modify Recommendation: inspector creates custom final action.
