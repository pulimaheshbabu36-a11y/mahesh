import os
import re

import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


# =====================================================
# REPORT FOLDER
# =====================================================

DATA_ROOT = os.path.abspath(os.getenv("APP_DATA_DIR", "."))
REPORT_FOLDER = os.path.join(DATA_ROOT, "reports")

os.makedirs(
    REPORT_FOLDER,
    exist_ok=True
)


# =====================================================
# SAFE FILE NAME
# =====================================================

def safe_filename(value):

    value = str(value)

    value = re.sub(
        r"[^a-zA-Z0-9_-]+",
        "_",
        value
    )

    return value.strip("_")


# =====================================================
# DETECT DATE COLUMNS
# =====================================================

def detect_date_columns(df):

    date_columns = []

    for column in df.columns:

        if pd.api.types.is_datetime64_any_dtype(
            df[column]
        ):

            date_columns.append(
                column
            )

            continue


        if df[column].dtype == "object":

            converted = pd.to_datetime(
                df[column],
                errors="coerce"
            )

            valid_ratio = (
                converted.notna()
                .mean()
            )

            if valid_ratio >= 0.8:

                date_columns.append(
                    column
                )

    return date_columns


# =====================================================
# DETECT USEFUL CHARTS
# =====================================================

def select_chart_types(df):

    numeric_columns = (
        df.select_dtypes(
            include="number"
        )
        .columns
        .tolist()
    )


    categorical_columns = (
        df.select_dtypes(
            exclude="number"
        )
        .columns
        .tolist()
    )


    date_columns = detect_date_columns(
        df
    )


    chart_plan = []


    # -------------------------------------------------
    # TIME SERIES
    # -------------------------------------------------

    if (
        date_columns
        and numeric_columns
    ):

        chart_plan.append({

            "type":
                "line",

            "date_column":
                date_columns[0],

            "value_column":
                numeric_columns[0],

            "reason":
                "A date column and numeric "
                "column are available."
        })


    # -------------------------------------------------
    # SCATTER
    # -------------------------------------------------

    if len(
        numeric_columns
    ) >= 2:

        chart_plan.append({

            "type":
                "scatter",

            "x_column":
                numeric_columns[0],

            "y_column":
                numeric_columns[1],

            "reason":
                "Two numeric columns can "
                "be compared."
        })


    # -------------------------------------------------
    # CATEGORY BAR
    # -------------------------------------------------

    if (
        categorical_columns
        and numeric_columns
    ):

        chart_plan.append({

            "type":
                "bar",

            "category_column":
                categorical_columns[0],

            "value_column":
                numeric_columns[0],

            "reason":
                "A categorical column and "
                "numeric column are available."
        })


    # -------------------------------------------------
    # HISTOGRAM
    # -------------------------------------------------

    for column in numeric_columns[:3]:

        chart_plan.append({

            "type":
                "histogram",

            "column":
                column,

            "reason":
                "A numeric column can show "
                "its distribution."
        })


    # -------------------------------------------------
    # CORRELATION HEATMAP
    # -------------------------------------------------

    if len(
        numeric_columns
    ) >= 3:

        chart_plan.append({

            "type":
                "heatmap",

            "columns":
                numeric_columns,

            "reason":
                "Multiple numeric columns "
                "allow correlation analysis."
        })


    return chart_plan


# =====================================================
# LINE CHART
# =====================================================

def create_line_chart(
    df,
    date_column,
    value_column
):

    working_df = df.copy()


    working_df[date_column] = (
        pd.to_datetime(
            working_df[date_column],
            errors="coerce"
        )
    )


    working_df = (
        working_df
        .dropna(
            subset=[
                date_column,
                value_column
            ]
        )
        .sort_values(
            date_column
        )
    )


    if working_df.empty:

        return None


    plt.figure(
        figsize=(10, 5)
    )


    plt.plot(
        working_df[date_column],
        working_df[value_column]
    )


    plt.title(
        f"{value_column} Over Time"
    )

    plt.xlabel(
        date_column
    )

    plt.ylabel(
        value_column
    )


    plt.xticks(
        rotation=45
    )


    plt.tight_layout()


    filename = (
        "line_"
        + safe_filename(
            date_column
        )
        + "_"
        + safe_filename(
            value_column
        )
        + ".png"
    )


    path = os.path.join(
        REPORT_FOLDER,
        filename
    )


    plt.savefig(
        path,
        dpi=150
    )

    plt.close()


    return filename


# =====================================================
# SCATTER CHART
# =====================================================

def create_scatter_chart(
    df,
    x_column,
    y_column
):

    working_df = (
        df[
            [
                x_column,
                y_column
            ]
        ]
        .dropna()
    )


    if working_df.empty:

        return None


    plt.figure(
        figsize=(8, 5)
    )


    plt.scatter(
        working_df[x_column],
        working_df[y_column]
    )


    plt.title(
        f"{y_column} vs {x_column}"
    )

    plt.xlabel(
        x_column
    )

    plt.ylabel(
        y_column
    )


    plt.tight_layout()


    filename = (
        "scatter_"
        + safe_filename(
            x_column
        )
        + "_"
        + safe_filename(
            y_column
        )
        + ".png"
    )


    path = os.path.join(
        REPORT_FOLDER,
        filename
    )


    plt.savefig(
        path,
        dpi=150
    )

    plt.close()


    return filename


# =====================================================
# BAR CHART
# =====================================================

def create_bar_chart(
    df,
    category_column,
    value_column
):

    working_df = (
        df[
            [
                category_column,
                value_column
            ]
        ]
        .dropna()
    )


    if working_df.empty:

        return None


    grouped = (
        working_df
        .groupby(
            category_column
        )[value_column]
        .sum()
        .sort_values(
            ascending=False
        )
        .head(10)
    )


    if grouped.empty:

        return None


    plt.figure(
        figsize=(10, 5)
    )


    grouped.plot(
        kind="bar"
    )


    plt.title(
        f"{value_column} by {category_column}"
    )

    plt.xlabel(
        category_column
    )

    plt.ylabel(
        value_column
    )


    plt.xticks(
        rotation=45,
        ha="right"
    )


    plt.tight_layout()


    filename = (
        "bar_"
        + safe_filename(
            category_column
        )
        + "_"
        + safe_filename(
            value_column
        )
        + ".png"
    )


    path = os.path.join(
        REPORT_FOLDER,
        filename
    )


    plt.savefig(
        path,
        dpi=150
    )

    plt.close()


    return filename


# =====================================================
# HISTOGRAM
# =====================================================

def create_histogram(
    df,
    column
):

    series = (
        df[column]
        .dropna()
    )


    if series.empty:

        return None


    plt.figure(
        figsize=(8, 5)
    )


    plt.hist(
        series,
        bins=20
    )


    plt.title(
        f"Distribution of {column}"
    )

    plt.xlabel(
        column
    )

    plt.ylabel(
        "Frequency"
    )


    plt.tight_layout()


    filename = (
        "histogram_"
        + safe_filename(
            column
        )
        + ".png"
    )


    path = os.path.join(
        REPORT_FOLDER,
        filename
    )


    plt.savefig(
        path,
        dpi=150
    )

    plt.close()


    return filename


# =====================================================
# CORRELATION HEATMAP
# =====================================================

def create_correlation_heatmap(
    df,
    columns
):

    if len(columns) < 2:

        return None


    correlation = (
        df[columns]
        .corr()
    )


    plt.figure(
        figsize=(9, 7)
    )


    plt.imshow(
        correlation,
        interpolation="nearest"
    )


    plt.title(
        "Correlation Matrix"
    )


    plt.xticks(
        range(len(columns)),
        columns,
        rotation=45,
        ha="right"
    )


    plt.yticks(
        range(len(columns)),
        columns
    )


    plt.colorbar()


    plt.tight_layout()


    filename = (
        "correlation_heatmap.png"
    )


    path = os.path.join(
        REPORT_FOLDER,
        filename
    )


    plt.savefig(
        path,
        dpi=150
    )

    plt.close()


    return filename


# =====================================================
# MAIN CHART GENERATOR
# =====================================================

def generate_charts(
    df
):

    chart_plan = select_chart_types(
        df
    )


    generated_charts = []


    for chart in chart_plan:

        chart_type = chart["type"]


        try:

            # -----------------------------------------
            # LINE
            # -----------------------------------------

            if chart_type == "line":

                filename = create_line_chart(

                    df,

                    chart[
                        "date_column"
                    ],

                    chart[
                        "value_column"
                    ]
                )


            # -----------------------------------------
            # SCATTER
            # -----------------------------------------

            elif chart_type == "scatter":

                filename = create_scatter_chart(

                    df,

                    chart[
                        "x_column"
                    ],

                    chart[
                        "y_column"
                    ]
                )


            # -----------------------------------------
            # BAR
            # -----------------------------------------

            elif chart_type == "bar":

                filename = create_bar_chart(

                    df,

                    chart[
                        "category_column"
                    ],

                    chart[
                        "value_column"
                    ]
                )


            # -----------------------------------------
            # HISTOGRAM
            # -----------------------------------------

            elif chart_type == "histogram":

                filename = create_histogram(

                    df,

                    chart[
                        "column"
                    ]
                )


            # -----------------------------------------
            # HEATMAP
            # -----------------------------------------

            elif chart_type == "heatmap":

                filename = (
                    create_correlation_heatmap(
                        df,
                        chart["columns"]
                    )
                )


            else:

                filename = None


            if filename:

                generated_charts.append({

                    "filename":
                        filename,

                    "type":
                        chart_type,

                    "reason":
                        chart["reason"]
                })


        except Exception as error:

            generated_charts.append({

                "filename":
                    None,

                "type":
                    chart_type,

                "reason":
                    chart["reason"],

                "error":
                    str(error)
            })


    return generated_charts