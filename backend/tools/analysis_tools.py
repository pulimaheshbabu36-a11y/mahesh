import pandas as pd


# =====================================================
# GENERAL INSIGHTS
# =====================================================

def generate_insights(df):

    insights = []

    insights.append(
        f"The dataset contains {len(df)} rows "
        f"and {len(df.columns)} columns."
    )

    numeric_columns = (
        df.select_dtypes(
            include="number"
        )
        .columns
        .tolist()
    )

    # -------------------------------------------------
    # NUMERIC ANALYSIS
    # -------------------------------------------------

    for column in numeric_columns:

        series = df[column].dropna()

        if series.empty:
            continue

        mean_value = series.mean()
        median_value = series.median()
        minimum = series.min()
        maximum = series.max()
        total = series.sum()
        std_dev = series.std()

        data_range = maximum - minimum

        insights.append(
            f"{column}: "
            f"mean={mean_value:.2f}, "
            f"median={median_value:.2f}, "
            f"minimum={minimum:.2f}, "
            f"maximum={maximum:.2f}, "
            f"total={total:.2f}, "
            f"standard deviation={std_dev:.2f}, "
            f"range={data_range:.2f}."
        )

        # ---------------------------------------------
        # OUTLIER DETECTION
        # ---------------------------------------------

        q1 = series.quantile(0.25)
        q3 = series.quantile(0.75)

        iqr = q3 - q1

        lower_limit = q1 - 1.5 * iqr
        upper_limit = q3 + 1.5 * iqr

        outliers = series[
            (series < lower_limit)
            |
            (series > upper_limit)
        ]

        if len(outliers) > 0:

            insights.append(
                f"{column}: "
                f"{len(outliers)} possible "
                f"outlier values detected."
            )

    # -------------------------------------------------
    # CORRELATION
    # -------------------------------------------------

    if len(numeric_columns) >= 2:

        correlation_matrix = (
            df[numeric_columns]
            .corr()
        )

        for i in range(
            len(numeric_columns)
        ):

            for j in range(
                i + 1,
                len(numeric_columns)
            ):

                column1 = numeric_columns[i]
                column2 = numeric_columns[j]

                correlation = (
                    correlation_matrix
                    .loc[
                        column1,
                        column2
                    ]
                )

                if pd.notna(
                    correlation
                ):

                    insights.append(
                        f"Correlation between "
                        f"{column1} and {column2}: "
                        f"{correlation:.2f}."
                    )

    # -------------------------------------------------
    # CATEGORICAL ANALYSIS
    # -------------------------------------------------

    text_columns = (
        df.select_dtypes(
            exclude="number"
        )
        .columns
        .tolist()
    )

    for column in text_columns:

        series = df[column].dropna()

        if series.empty:
            continue

        value_counts = (
            series.value_counts()
        )

        if not value_counts.empty:

            most_common = (
                value_counts.index[0]
            )

            most_common_count = (
                value_counts.iloc[0]
            )

            unique_values = (
                series.nunique()
            )

            insights.append(
                f"{column}: "
                f"{unique_values} unique values. "
                f"Most common value is "
                f"'{most_common}', "
                f"appearing "
                f"{most_common_count} times."
            )

    # -------------------------------------------------
    # DATA QUALITY
    # -------------------------------------------------

    missing_values = int(
        df.isnull()
        .sum()
        .sum()
    )

    duplicate_rows = int(
        df.duplicated()
        .sum()
    )

    insights.append(
        f"Data quality check: "
        f"{missing_values} missing values "
        f"and {duplicate_rows} duplicate rows."
    )

    return insights


# =====================================================
# NUMERIC ANALYSIS TOOL
# =====================================================

def analyze_numeric_data(df):

    numeric_columns = (
        df.select_dtypes(
            include="number"
        )
        .columns
        .tolist()
    )

    results = []

    for column in numeric_columns:

        series = df[column].dropna()

        if series.empty:
            continue

        q1 = series.quantile(
            0.25
        )

        q3 = series.quantile(
            0.75
        )

        iqr = q3 - q1

        lower_limit = (
            q1 - 1.5 * iqr
        )

        upper_limit = (
            q3 + 1.5 * iqr
        )

        outliers = series[
            (series < lower_limit)
            |
            (series > upper_limit)
        ]

        results.append({

            "column":
                column,

            "count":
                int(series.count()),

            "mean":
                float(series.mean()),

            "median":
                float(series.median()),

            "minimum":
                float(series.min()),

            "maximum":
                float(series.max()),

            "sum":
                float(series.sum()),

            "standard_deviation":
                float(series.std()),

            "range":
                float(
                    series.max()
                    -
                    series.min()
                ),

            "q1":
                float(q1),

            "q3":
                float(q3),

            "iqr":
                float(iqr),

            "outliers":
                int(len(outliers))
        })

    return {

        "analysis_type":
            "numeric",

        "numeric_columns":
            numeric_columns,

        "results":
            results
    }


# =====================================================
# CATEGORICAL ANALYSIS TOOL
# =====================================================

def analyze_categorical_data(df):

    categorical_columns = (
        df.select_dtypes(
            exclude="number"
        )
        .columns
        .tolist()
    )

    results = []

    for column in categorical_columns:

        series = (
            df[column]
            .dropna()
            .astype(str)
        )

        if series.empty:
            continue

        value_counts = (
            series.value_counts()
        )

        top_values = []

        for value, count in (
            value_counts.head(10)
            .items()
        ):

            top_values.append({

                "value":
                    str(value),

                "count":
                    int(count),

                "percentage":
                    round(
                        (
                            count
                            /
                            len(series)
                        )
                        * 100,
                        2
                    )
            })

        results.append({

            "column":
                column,

            "unique_values":
                int(
                    series.nunique()
                ),

            "most_common":
                str(
                    value_counts.index[0]
                ),

            "most_common_count":
                int(
                    value_counts.iloc[0]
                ),

            "top_values":
                top_values
        })

    return {

        "analysis_type":
            "categorical",

        "categorical_columns":
            categorical_columns,

        "results":
            results
    }


# =====================================================
# CORRELATION ANALYSIS TOOL
# =====================================================

def analyze_correlations(df):

    numeric_columns = (
        df.select_dtypes(
            include="number"
        )
        .columns
        .tolist()
    )

    if len(numeric_columns) < 2:

        return {

            "analysis_type":
                "correlation",

            "message":
                "At least two numeric columns "
                "are required.",

            "correlations":
                {}
        }


    correlation_matrix = (
        df[numeric_columns]
        .corr()
        .round(3)
    )


    relationships = []

    for i in range(
        len(numeric_columns)
    ):

        for j in range(
            i + 1,
            len(numeric_columns)
        ):

            column1 = (
                numeric_columns[i]
            )

            column2 = (
                numeric_columns[j]
            )

            value = (
                correlation_matrix
                .loc[
                    column1,
                    column2
                ]
            )

            if pd.notna(value):

                relationships.append({

                    "column_1":
                        column1,

                    "column_2":
                        column2,

                    "correlation":
                        float(value),

                    "absolute_correlation":
                        float(abs(value))
                })


    relationships.sort(
        key=lambda x:
            x["absolute_correlation"],
        reverse=True
    )


    return {

        "analysis_type":
            "correlation",

        "numeric_columns":
            numeric_columns,

        "correlations":
            correlation_matrix
            .to_dict(),

        "strongest_relationships":
            relationships[:10]
    }


# =====================================================
# TIME SERIES ANALYSIS TOOL
# =====================================================

def analyze_time_series(df):

    date_columns = []

    for column in df.columns:

        if pd.api.types.is_datetime64_any_dtype(
            df[column]
        ):

            date_columns.append(
                column
            )

        elif df[column].dtype == "object":

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


    if not date_columns:

        return {

            "analysis_type":
                "time_series",

            "date_columns":
                [],

            "message":
                "No suitable date column found.",

            "results":
                []
        }


    numeric_columns = (
        df.select_dtypes(
            include="number"
        )
        .columns
        .tolist()
    )


    if not numeric_columns:

        return {

            "analysis_type":
                "time_series",

            "date_columns":
                date_columns,

            "message":
                "Date column found, but "
                "no numeric column is available.",

            "results":
                []
        }


    date_column = date_columns[0]

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
                date_column
            ]
        )
        .sort_values(
            date_column
        )
    )


    results = []

    for column in numeric_columns:

        series = working_df[
            [date_column, column]
        ].dropna()

        if series.empty:
            continue

        results.append({

            "date_column":
                date_column,

            "value_column":
                column,

            "start_date":
                str(
                    series[
                        date_column
                    ].min()
                ),

            "end_date":
                str(
                    series[
                        date_column
                    ].max()
                ),

            "minimum":
                float(
                    series[column].min()
                ),

            "maximum":
                float(
                    series[column].max()
                ),

            "average":
                float(
                    series[column].mean()
                ),

            "total":
                float(
                    series[column].sum()
                )
        })


    return {

        "analysis_type":
            "time_series",

        "date_columns":
            date_columns,

        "results":
            results
    }