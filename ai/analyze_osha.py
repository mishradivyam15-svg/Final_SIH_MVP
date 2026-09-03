import pandas as pd


FILE_PATH = "data/raw/OSHA/January2015toNovember2025.csv"


def analyze_osha():
    df = pd.read_csv(FILE_PATH, low_memory=False)

    print("\nDataset shape:")
    print(df.shape)

    print("\nUnique EventTitle values:")
    print(df["EventTitle"].nunique())

    print("\nTop EventTitle categories:")
    print(df["EventTitle"].value_counts().head(30).to_string())

    print("\nTop SourceTitle categories:")
    print(df["SourceTitle"].value_counts().head(30).to_string())

    print("\nNarrative length statistics:")
    narrative_length = df["Final Narrative"].str.len()

    print(narrative_length.describe())

    print("\nDate range:")
    print("Start:", df["EventDate"].min())
    print("End:", df["EventDate"].max())


if __name__ == "__main__":
    analyze_osha()