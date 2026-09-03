import pandas as pd

FILE_PATH = "data/raw/OSHA/January2015toNovember2025.csv"


def inspect_dataset():
    df = pd.read_csv(FILE_PATH)

    print("\nDataset shape:")
    print(df.shape)

    print("\nColumns:")
    for column in df.columns:
        print("-", column)

    print("\nMissing values:")
    print(df.isnull().sum())

    print("\nSample narratives:")
    print(df["Final Narrative"].head(10).to_string())

    print("\nEvent types:")
    print(df["EventTitle"].value_counts().head(20))


if __name__ == "__main__":
    inspect_dataset()