from pathlib import Path

import pymupdf
import pandas as pd


INPUT_DIR = Path("data/raw/OISD")
OUTPUT_PATH = "data/processed/oisd_reports.csv"


def extract_text_from_pdf(pdf_path):
    document = pymupdf.open(pdf_path)

    pages = []

    for page in document:
        pages.append(page.get_text())

    document.close()

    return "\n".join(pages)


def extract_oisd_reports():

    records = []

    for pdf_path in sorted(INPUT_DIR.glob("*.pdf")):

        text = extract_text_from_pdf(pdf_path)

        records.append({
            "report_id": pdf_path.stem,
            "source": "OISD",
            "filename": pdf_path.name,
            "narrative": text,
        })

    df = pd.DataFrame(records)

    df.to_csv(
        OUTPUT_PATH,
        index=False
    )

    print("\nOISD reports:", len(df))

    print("\nReports:")

    for _, row in df.iterrows():
        print(
            f"- {row['report_id']} "
            f"({len(row['narrative'])} characters)"
        )

    print("\n\nOISD TEXT PREVIEW")

    for _, row in df.iterrows():

        print("\n" + "=" * 80)
        print(row["report_id"])
        print("=" * 80)

        print(row["narrative"][:2500])


if __name__ == "__main__":
    extract_oisd_reports()