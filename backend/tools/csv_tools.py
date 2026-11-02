import os
import pandas as pd


DATA_ROOT = os.path.abspath(os.getenv("APP_DATA_DIR", "."))
UPLOAD_FOLDER = os.path.join(DATA_ROOT, "backend", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def read_csv(filename):
    file_path = os.path.join(
        UPLOAD_FOLDER,
        os.path.basename(filename)
    )

    if not os.path.exists(file_path):
        return None, "CSV file not found"

    df = pd.read_csv(file_path)

    return df, None


def inspect_csv(df):

    return {
        "rows": len(df),
        "columns": len(df.columns),
        "column_names": df.columns.tolist(),
        "missing_values": int(
            df.isnull().sum().sum()
        ),
        "duplicate_rows": int(
            df.duplicated().sum()
        )
    }


def clean_csv(df, filename):

    original_rows = len(df)

    # Remove completely empty columns
    df = df.dropna(
        axis=1,
        how="all"
    )

    # Remove duplicate rows
    duplicates_removed = int(
        df.duplicated().sum()
    )

    df = df.drop_duplicates()

    # Fill numeric missing values
    numeric_columns = df.select_dtypes(
        include="number"
    ).columns

    for column in numeric_columns:

        if df[column].isnull().any():

            df[column] = df[column].fillna(
                df[column].median()
            )

    # Fill text missing values
    text_columns = df.select_dtypes(
        exclude="number"
    ).columns

    for column in text_columns:

        if df[column].isnull().any():

            mode = df[column].mode()

            if not mode.empty:
                df[column] = df[column].fillna(
                    mode[0]
                )

    cleaned_filename = (
        "cleaned_" + os.path.basename(filename)
    )

    cleaned_path = os.path.join(
        UPLOAD_FOLDER,
        cleaned_filename
    )

    df.to_csv(
        cleaned_path,
        index=False
    )

    return {
        "filename": cleaned_filename,
        "original_rows": original_rows,
        "cleaned_rows": len(df),
        "duplicates_removed": duplicates_removed
    }