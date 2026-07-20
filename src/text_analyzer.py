def summarize_inspection_notes(text):
    if not text or not text.strip():
        return "No operator or inspection notes provided."
    cleaned = " ".join(text.strip().split())
    if len(cleaned) <= 300:
        return cleaned
    return cleaned[:300] + "..."


def detect_quality_keywords(text):
    text_lower = (text or "").lower()
    keywords = []
    for word in ["scratch", "crack", "dent", "overheat", "vibration", "misalignment", "contamination", "jam", "noise", "burn"]:
        if word in text_lower:
            keywords.append(word)
    return keywords
