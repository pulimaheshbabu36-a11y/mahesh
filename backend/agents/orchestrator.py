import os
import pandas as pd

from backend.tools.csv_tools import (
    read_csv,
    inspect_csv,
    clean_csv
)

from backend.tools.analysis_tools import (
    generate_insights,
    analyze_numeric_data,
    analyze_categorical_data,
    analyze_correlations,
    analyze_time_series
)

from backend.tools.chart_tools import (
    generate_charts
)

from backend.tools.llm_tools import (
    generate_ai_report
)

from backend.tools.report_tools import (
    generate_pdf_report
)

from backend.tools.agent_decision import (
    decide_next_action
)

from backend.tools.agent_progress import (
    update_progress
)


# ============================================================
# AGENT CONFIGURATION
# ============================================================

MAX_STEPS = 8


# ============================================================
# RUN AGENT
# ============================================================

def run_agent(filename):

    filename = os.path.basename(
        filename
    )

    # --------------------------------------------------------
    # Initial state
    # --------------------------------------------------------

    actions = []

    tool_results = []

    cleaning_result = {}

    analysis_results = {}

    charts = []

    ai_report = {}

    dataset_info = {}

    df = None


    try:

        # ====================================================
        # STEP 1
        # READ DATASET
        # ====================================================

        update_progress(
            filename,
            "running",
            1,
            MAX_STEPS,
            "Reading CSV dataset..."
        )


        df, error = read_csv(
            filename
        )


        if error:

            update_progress(
                filename,
                "error",
                1,
                MAX_STEPS,
                error
            )

            return {
                "status": "error",
                "filename": filename,
                "message": error
            }


        # ====================================================
        # DATASET INFORMATION
        # ====================================================

        inspection = inspect_csv(
            df
        )


        # Detect column types

        numeric_columns = (
            df.select_dtypes(
                include="number"
            ).columns.tolist()
        )


        categorical_columns = (
            df.select_dtypes(
                exclude="number"
            ).columns.tolist()
        )


        # Detect date columns

        date_columns = []


        for column in df.columns:

            try:

                converted = pd.to_datetime(
                    df[column],
                    errors="coerce"
                )

                valid_ratio = (
                    converted.notna().mean()
                )


                if valid_ratio >= 0.7:

                    date_columns.append(
                        column
                    )

            except Exception:

                pass


        dataset_info = {

            "rows":
                inspection.get(
                    "rows",
                    len(df)
                ),

            "columns":
                inspection.get(
                    "columns",
                    len(df.columns)
                ),

            "column_names":
                inspection.get(
                    "column_names",
                    df.columns.tolist()
                ),

            "missing_values":
                inspection.get(
                    "missing_values",
                    0
                ),

            "duplicate_rows":
                inspection.get(
                    "duplicate_rows",
                    0
                ),

            "numeric_columns":
                numeric_columns,

            "categorical_columns":
                categorical_columns,

            "date_columns":
                date_columns

        }


        # ====================================================
        # AGENT LOOP
        # ====================================================

        for step in range(
            MAX_STEPS
        ):

            update_progress(
                filename,
                "running",
                step + 1,
                MAX_STEPS,
                "AI agent is deciding the next action..."
            )


            # ------------------------------------------------
            # Ask AI agent
            # ------------------------------------------------

            decision = decide_next_action(

                dataset_info,

                actions,

                tool_results

            )


            action = decision.get(
                "action",
                "finish"
            )


            reason = decision.get(
                "reason",
                "Agent selected this action based on the current dataset."
            )


            print(
                "\n========================================"
            )

            print(
                "AGENT STEP:",
                step + 1
            )

            print(
                "ACTION:",
                action
            )

            print(
                "REASON:",
                reason
            )

            print(
                "========================================\n"
            )


            # ------------------------------------------------
            # Save agent decision
            # ------------------------------------------------

            decision_record = {

                "step":
                    step + 1,

                "action":
                    action,

                "reason":
                    reason,

                "status":
                    "selected"

            }


            # =================================================
            # FINISH
            # =================================================

            if action == "finish":

                decision_record[
                    "status"
                ] = "completed"


                actions.append(
                    decision_record
                )

                break


            # =================================================
            # CLEAN DATASET
            # =================================================

            if action == "clean":

                update_progress(
                    filename,
                    "running",
                    step + 1,
                    MAX_STEPS,
                    "Cleaning dataset..."
                )


                cleaning_result = clean_csv(
                    df,
                    filename
                )


                tool_results.append({

                    "step":
                        step + 1,

                    "tool":
                        "clean_dataset",

                    "action":
                        "clean",

                    "result":
                        cleaning_result

                })


                decision_record[
                    "status"
                ] = "completed"


                actions.append(
                    decision_record
                )

                continue


            # =================================================
            # NUMERIC ANALYSIS
            # =================================================

            if action == "numeric":

                update_progress(
                    filename,
                    "running",
                    step + 1,
                    MAX_STEPS,
                    "Running numeric analysis..."
                )


                numeric_result = (
                    analyze_numeric_data(
                        df
                    )
                )


                analysis_results[
                    "numeric"
                ] = numeric_result


                tool_results.append({

                    "step":
                        step + 1,

                    "tool":
                        "analyze_numeric",

                    "action":
                        "numeric",

                    "result":
                        numeric_result

                })


                decision_record[
                    "status"
                ] = "completed"


                actions.append(
                    decision_record
                )

                continue


            # =================================================
            # CATEGORICAL ANALYSIS
            # =================================================

            if action == "categorical":

                update_progress(
                    filename,
                    "running",
                    step + 1,
                    MAX_STEPS,
                    "Running categorical analysis..."
                )


                categorical_result = (
                    analyze_categorical_data(
                        df
                    )
                )


                analysis_results[
                    "categorical"
                ] = categorical_result


                tool_results.append({

                    "step":
                        step + 1,

                    "tool":
                        "analyze_categorical",

                    "action":
                        "categorical",

                    "result":
                        categorical_result

                })


                decision_record[
                    "status"
                ] = "completed"


                actions.append(
                    decision_record
                )

                continue


            # =================================================
            # CORRELATION ANALYSIS
            # =================================================

            if action == "correlation":

                update_progress(
                    filename,
                    "running",
                    step + 1,
                    MAX_STEPS,
                    "Running correlation analysis..."
                )


                correlation_result = (
                    analyze_correlations(
                        df
                    )
                )


                analysis_results[
                    "correlation"
                ] = correlation_result


                tool_results.append({

                    "step":
                        step + 1,

                    "tool":
                        "analyze_correlations",

                    "action":
                        "correlation",

                    "result":
                        correlation_result

                })


                decision_record[
                    "status"
                ] = "completed"


                actions.append(
                    decision_record
                )

                continue


            # =================================================
            # TIME SERIES ANALYSIS
            # =================================================

            if action == "time_series":

                update_progress(
                    filename,
                    "running",
                    step + 1,
                    MAX_STEPS,
                    "Running time-series analysis..."
                )


                time_series_result = (
                    analyze_time_series(
                        df
                    )
                )


                analysis_results[
                    "time_series"
                ] = time_series_result


                tool_results.append({

                    "step":
                        step + 1,

                    "tool":
                        "analyze_time_series",

                    "action":
                        "time_series",

                    "result":
                        time_series_result

                })


                decision_record[
                    "status"
                ] = "completed"


                actions.append(
                    decision_record
                )

                continue


            # =================================================
            # CHART GENERATION
            # =================================================

            if action == "charts":

                update_progress(
                    filename,
                    "running",
                    step + 1,
                    MAX_STEPS,
                    "Generating charts..."
                )


                charts = generate_charts(
                    df
                )


                tool_results.append({

                    "step":
                        step + 1,

                    "tool":
                        "generate_charts",

                    "action":
                        "charts",

                    "result":
                        charts

                })


                decision_record[
                    "status"
                ] = "completed"


                actions.append(
                    decision_record
                )

                continue


            # =================================================
            # UNKNOWN ACTION
            # =================================================

            decision_record[
                "status"
            ] = "skipped"


            decision_record[
                "reason"
            ] = (
                f"Unknown agent action: {action}"
            )


            actions.append(
                decision_record
            )


        # ====================================================
        # FALLBACK ANALYSIS
        # ====================================================

        # If the agent did not perform numeric analysis
        # but numeric columns exist.

        if (
            numeric_columns
            and
            "numeric"
            not in analysis_results
        ):

            update_progress(
                filename,
                "running",
                MAX_STEPS,
                MAX_STEPS,
                "Completing numeric analysis..."
            )


            numeric_result = (
                analyze_numeric_data(
                    df
                )
            )


            analysis_results[
                "numeric"
            ] = numeric_result


            tool_results.append({

                "step":
                    "fallback",

                "tool":
                    "analyze_numeric",

                "action":
                    "numeric",

                "result":
                    numeric_result

            })


        # ====================================================
        # FALLBACK CATEGORICAL
        # ====================================================

        if (
            categorical_columns
            and
            "categorical"
            not in analysis_results
        ):

            categorical_result = (
                analyze_categorical_data(
                    df
                )
            )


            analysis_results[
                "categorical"
            ] = categorical_result


            tool_results.append({

                "step":
                    "fallback",

                "tool":
                    "analyze_categorical",

                "action":
                    "categorical",

                "result":
                    categorical_result

            })


        # ====================================================
        # FALLBACK CORRELATION
        # ====================================================

        if (
            len(numeric_columns) >= 2
            and
            "correlation"
            not in analysis_results
        ):

            correlation_result = (
                analyze_correlations(
                    df
                )
            )


            analysis_results[
                "correlation"
            ] = correlation_result


            tool_results.append({

                "step":
                    "fallback",

                "tool":
                    "analyze_correlations",

                "action":
                    "correlation",

                "result":
                    correlation_result

            })


        # ====================================================
        # FALLBACK TIME SERIES
        # ====================================================

        if (
            date_columns
            and
            "time_series"
            not in analysis_results
        ):

            time_series_result = (
                analyze_time_series(
                    df
                )
            )


            analysis_results[
                "time_series"
            ] = time_series_result


            tool_results.append({

                "step":
                    "fallback",

                "tool":
                    "analyze_time_series",

                "action":
                    "time_series",

                "result":
                    time_series_result

            })


        # ====================================================
        # FALLBACK CHARTS
        # ====================================================

        if not charts:

            update_progress(
                filename,
                "running",
                MAX_STEPS,
                MAX_STEPS,
                "Generating final visualizations..."
            )


            charts = generate_charts(
                df
            )


            tool_results.append({

                "step":
                    "fallback",

                "tool":
                    "generate_charts",

                "action":
                    "charts",

                "result":
                    charts

            })


        # ====================================================
        # RULE-BASED INSIGHTS
        # ====================================================

        update_progress(
            filename,
            "running",
            MAX_STEPS,
            MAX_STEPS,
            "Generating data insights..."
        )


        insights = generate_insights(
            df
        )


        # ====================================================
        # REPORT DATA
        # ====================================================

        report_data = {

            "filename":
                filename,

            "dataset":
                dataset_info,

            "cleaning":
                cleaning_result,

            "insights":
                insights,

            "analysis":
                analysis_results,

            "tool_results":
                tool_results,

            "actions":
                actions,

            "charts":
                charts

        }


        # ====================================================
        # AI REPORT
        # ====================================================

        update_progress(
            filename,
            "running",
            MAX_STEPS,
            MAX_STEPS,
            "Generating AI report..."
        )


        ai_report = generate_ai_report(
            report_data
        )


        # ====================================================
        # PDF
        # ====================================================

        update_progress(
            filename,
            "running",
            MAX_STEPS,
            MAX_STEPS,
            "Generating professional PDF..."
        )


        pdf_result = generate_pdf_report(
            filename=filename,
            dataset_info=dataset_info,
            cleaning_result=cleaning_result,
            insights=insights,
            analysis_results=analysis_results,
            ai_report=ai_report,
            charts=charts
        )


        # ====================================================
        # PDF FILE NAME
        # ====================================================

        pdf_file = pdf_result


        if isinstance(
            pdf_result,
            dict
        ):

            pdf_file = pdf_result.get(
                "pdf",
                ""
            )


        # ====================================================
        # FINAL RESULT
        # ====================================================

        result = {

            "status":
                "completed",

            "filename":
                filename,

            "dataset":
                dataset_info,

            "cleaning":
                cleaning_result,

            "insights":
                insights,

            "analysis":
                analysis_results,

            "actions":
                actions,

            "tool_results":
                tool_results,

            "charts":
                charts,

            "ai_report":
                ai_report,

            "pdf":
                pdf_file

        }


        # ====================================================
        # COMPLETED
        # ====================================================

        update_progress(
            filename,
            "completed",
            MAX_STEPS,
            MAX_STEPS,
            "Report generated successfully."
        )


        return result


    except Exception as error:

        error_message = str(
            error
        )


        print(
            "\n========================================"
        )

        print(
            "AGENT ERROR:"
        )

        print(
            error_message
        )

        print(
            "========================================\n"
        )


        update_progress(
            filename,
            "error",
            MAX_STEPS,
            MAX_STEPS,
            error_message
        )


        return {

            "status":
                "error",

            "filename":
                filename,

            "message":
                error_message,

            "dataset":
                dataset_info,

            "actions":
                actions,

            "tool_results":
                tool_results

        }