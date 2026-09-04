import re
import unicodedata


def normalize_text(text):
    """
    Clean a safety narrative without removing safety-critical information.
    """

    if text is None:
        return ""

    text = str(text)

    # Normalize unicode characters
    text = unicodedata.normalize("NFKC", text)

    # Replace line breaks and tabs with spaces
    text = re.sub(r"[\r\n\t]+", " ", text)

    # Remove repeated whitespace
    text = re.sub(r"\s+", " ", text)

    # Remove spaces before punctuation
    text = re.sub(r"\s+([,.!?;:])", r"\1", text)

    return text.strip()


def preprocess_report(report):
    """
    Preprocess one safety report.

    Expected input:
        {
            "report_id": ...,
            "narrative": ...
        }
    """

    cleaned_narrative = normalize_text(report.get("narrative", ""))

    return {
        **report,
        "narrative": cleaned_narrative,
    }
