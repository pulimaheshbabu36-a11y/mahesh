import os
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
    Image
)

DATA_ROOT = os.path.abspath(os.getenv("APP_DATA_DIR", "."))
REPORT_FOLDER = os.path.join(DATA_ROOT, "reports")

os.makedirs(
    REPORT_FOLDER,
    exist_ok=True
)


def safe_filename(filename):
    """
    Convert a filename into a safe report filename.
    """
    name = os.path.basename(filename)

    if "." in name:
        name = name.rsplit(".", 1)[0]

    safe_name = "".join(
        character
        if character.isalnum() or character in ("_", "-")
        else "_"
        for character in name
    )

    return safe_name


def add_page_number(canvas, document):
    """
    Add page number to every PDF page.
    """
    canvas.saveState()

    canvas.setFont(
        "Helvetica",
        8
    )

    canvas.drawCentredString(
        A4[0] / 2,
        0.4 * inch,
        f"Page {document.page}"
    )

    canvas.restoreState()


def create_heading_styles():
    """
    Create styles used throughout the PDF.
    """

    styles = getSampleStyleSheet()

    styles.add(
        ParagraphStyle(
            name="ReportTitle",
            parent=styles["Title"],
            fontSize=24,
            leading=30,
            alignment=TA_CENTER,
            spaceAfter=20
        )
    )

    styles.add(
        ParagraphStyle(
            name="SectionHeading",
            parent=styles["Heading2"],
            fontSize=16,
            leading=20,
            spaceBefore=12,
            spaceAfter=10
        )
    )

    styles.add(
        ParagraphStyle(
            name="SubHeading",
            parent=styles["Heading3"],
            fontSize=12,
            leading=16,
            spaceBefore=8,
            spaceAfter=6
        )
    )

    styles.add(
        ParagraphStyle(
            name="ReportBody",
            parent=styles["BodyText"],
            fontSize=9,
            leading=14,
            spaceAfter=8
        )
    )

    styles.add(
        ParagraphStyle(
            name="SmallText",
            parent=styles["BodyText"],
            fontSize=8,
            leading=11
        )
    )

    return styles


def make_table(data, column_widths=None):
    """
    Create a professional table.
    """

    if not data:
        return Spacer(
            1,
            5
        )

    table = Table(
        data,
        colWidths=column_widths,
        repeatRows=1
    )

    table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.HexColor("#1f2937")
                ),
                (
                    "TEXTCOLOR",
                    (0, 0),
                    (-1, 0),
                    colors.white
                ),
                (
                    "FONTNAME",
                    (0, 0),
                    (-1, 0),
                    "Helvetica-Bold"
                ),
                (
                    "FONTSIZE",
                    (0, 0),
                    (-1, -1),
                    8
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.grey
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP"
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    6
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    6
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    5
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    5
                ),
                (
                    "ROWBACKGROUNDS",
                    (0, 1),
                    (-1, -1),
                    [
                        colors.white,
                        colors.HexColor("#f3f4f6")
                    ]
                )
            ]
        )
    )

    return table


def format_value(value):
    """
    Safely convert values into readable PDF text.
    """

    if value is None:
        return ""

    if isinstance(value, float):
        return f"{value:.4f}"

    if isinstance(value, (list, tuple)):
        return ", ".join(
            str(item)
            for item in value
        )

    if isinstance(value, dict):
        return ", ".join(
            f"{key}: {format_value(item)}"
            for key, item in value.items()
        )

    return str(value)


def add_dictionary_section(
    story,
    title,
    data,
    styles
):
    """
    Add dictionary data to the PDF.
    """

    story.append(
        Paragraph(
            title,
            styles["SectionHeading"]
        )
    )

    if not isinstance(data, dict) or not data:
        story.append(
            Paragraph(
                "No information available.",
                styles["ReportBody"]
            )
        )
        return

    table_data = [
        ["Item", "Value"]
    ]

    for key, value in data.items():

        if isinstance(value, (dict, list)):
            value = format_value(value)

        table_data.append(
            [
                format_value(key),
                format_value(value)
            ]
        )

    story.append(
        make_table(
            table_data,
            column_widths=[
                2.1 * inch,
                4.6 * inch
            ]
        )
    )

    story.append(
        Spacer(
            1,
            10
        )
    )


def add_numeric_analysis(
    story,
    numeric_analysis,
    styles
):
    """
    Add numeric analysis to PDF.
    """

    story.append(
        Paragraph(
            "Numerical Analysis",
            styles["SectionHeading"]
        )
    )

    if not numeric_analysis:
        story.append(
            Paragraph(
                "No numerical analysis available.",
                styles["ReportBody"]
            )
        )
        return

    results = numeric_analysis

    if isinstance(numeric_analysis, dict):
        results = numeric_analysis.get(
            "results",
            []
        )

    if not isinstance(results, list):
        story.append(
            Paragraph(
                format_value(results),
                styles["ReportBody"]
            )
        )
        return

    table_data = [
        [
            "Column",
            "Mean",
            "Median",
            "Min",
            "Max",
            "Std Dev",
            "Outliers"
        ]
    ]

    for item in results:

        if not isinstance(item, dict):
            continue

        table_data.append(
            [
                format_value(
                    item.get("column")
                ),
                format_value(
                    item.get("mean")
                ),
                format_value(
                    item.get("median")
                ),
                format_value(
                    item.get("minimum")
                ),
                format_value(
                    item.get("maximum")
                ),
                format_value(
                    item.get("standard_deviation")
                ),
                format_value(
                    item.get("outliers")
                )
            ]
        )

    if len(table_data) > 1:
        story.append(
            make_table(
                table_data,
                column_widths=[
                    1.35 * inch,
                    0.8 * inch,
                    0.8 * inch,
                    0.7 * inch,
                    0.7 * inch,
                    0.9 * inch,
                    0.7 * inch
                ]
            )
        )


def add_categorical_analysis(
    story,
    categorical_analysis,
    styles
):
    """
    Add categorical analysis to PDF.
    """

    story.append(
        Paragraph(
            "Categorical Analysis",
            styles["SectionHeading"]
        )
    )

    if not categorical_analysis:
        story.append(
            Paragraph(
                "No categorical analysis available.",
                styles["ReportBody"]
            )
        )
        return

    results = categorical_analysis

    if isinstance(categorical_analysis, dict):
        results = categorical_analysis.get(
            "results",
            []
        )

    if not isinstance(results, list):
        story.append(
            Paragraph(
                format_value(results),
                styles["ReportBody"]
            )
        )
        return

    table_data = [
        [
            "Column",
            "Unique Values",
            "Most Common",
            "Count"
        ]
    ]

    for item in results:

        if not isinstance(item, dict):
            continue

        table_data.append(
            [
                format_value(
                    item.get("column")
                ),
                format_value(
                    item.get("unique_values")
                ),
                format_value(
                    item.get("most_common")
                ),
                format_value(
                    item.get("most_common_count")
                )
            ]
        )

    if len(table_data) > 1:
        story.append(
            make_table(
                table_data,
                column_widths=[
                    2.0 * inch,
                    1.2 * inch,
                    1.8 * inch,
                    1.0 * inch
                ]
            )
        )


def add_correlation_analysis(
    story,
    correlation_analysis,
    styles
):
    """
    Add correlation analysis.
    """

    story.append(
        Paragraph(
            "Correlation Analysis",
            styles["SectionHeading"]
        )
    )

    if not correlation_analysis:
        story.append(
            Paragraph(
                "No correlation analysis available.",
                styles["ReportBody"]
            )
        )
        return

    strongest = []

    if isinstance(
        correlation_analysis,
        dict
    ):
        strongest = correlation_analysis.get(
            "strongest_relationships",
            []
        )

    if strongest:

        table_data = [
            [
                "Variable 1",
                "Variable 2",
                "Correlation"
            ]
        ]

        for item in strongest:

            if not isinstance(item, dict):
                continue

            table_data.append(
                [
                    format_value(
                        item.get("column_1")
                    ),
                    format_value(
                        item.get("column_2")
                    ),
                    format_value(
                        item.get("correlation")
                    )
                ]
            )

        story.append(
            make_table(
                table_data,
                column_widths=[
                    2.1 * inch,
                    2.1 * inch,
                    1.3 * inch
                ]
            )
        )

    else:

        story.append(
            Paragraph(
                format_value(
                    correlation_analysis
                ),
                styles["ReportBody"]
            )
        )


def add_time_series_analysis(
    story,
    time_series_analysis,
    styles
):
    """
    Add time-series analysis.
    """

    story.append(
        Paragraph(
            "Time-Series Analysis",
            styles["SectionHeading"]
        )
    )

    if not time_series_analysis:
        story.append(
            Paragraph(
                "No time-series analysis available.",
                styles["ReportBody"]
            )
        )
        return

    if isinstance(
        time_series_analysis,
        dict
    ):

        message = time_series_analysis.get(
            "message"
        )

        if message:
            story.append(
                Paragraph(
                    format_value(message),
                    styles["ReportBody"]
                )
            )

        results = time_series_analysis.get(
            "results",
            []
        )

        if results:

            story.append(
                Paragraph(
                    format_value(results),
                    styles["ReportBody"]
                )
            )

    else:

        story.append(
            Paragraph(
                format_value(
                    time_series_analysis
                ),
                styles["ReportBody"]
            )
        )


def add_tool_results(
    story,
    tool_results,
    styles
):
    """
    Add agent tool results.
    """

    if not tool_results:
        return

    story.append(
        PageBreak()
    )

    story.append(
        Paragraph(
            "Agent Tool Results",
            styles["SectionHeading"]
        )
    )

    for index, item in enumerate(
        tool_results,
        start=1
    ):

        if not isinstance(item, dict):
            continue

        tool_name = item.get(
            "tool",
            "Unknown Tool"
        )

        story.append(
            Paragraph(
                f"{index}. {format_value(tool_name)}",
                styles["SubHeading"]
            )
        )

        result = item.get(
            "result",
            {}
        )

        if isinstance(result, dict):

            for key, value in result.items():

                if key in (
                    "results",
                    "correlations"
                ):
                    continue

                story.append(
                    Paragraph(
                        f"<b>{format_value(key)}:</b> "
                        f"{format_value(value)}",
                        styles["ReportBody"]
                    )
                )

        else:

            story.append(
                Paragraph(
                    format_value(result),
                    styles["ReportBody"]
                )
            )


def add_ai_report(
    story,
    ai_report,
    styles
):
    """
    Add AI-generated report sections.
    """

    story.append(
        PageBreak()
    )

    story.append(
        Paragraph(
            "AI Generated Report",
            styles["SectionHeading"]
        )
    )

    if not ai_report:
        story.append(
            Paragraph(
                "AI report was not available.",
                styles["ReportBody"]
            )
        )
        return

    if isinstance(ai_report, dict):

        section_order = [
            "executive_summary",
            "dataset_overview",
            "data_quality",
            "key_findings",
            "statistical_findings",
            "anomaly_analysis",
            "correlation_analysis",
            "trend_analysis",
            "business_insights",
            "recommendations"
        ]

        display_names = {
            "executive_summary": "Executive Summary",
            "dataset_overview": "Dataset Overview",
            "data_quality": "Data Quality",
            "key_findings": "Key Findings",
            "statistical_findings": "Statistical Findings",
            "anomaly_analysis": "Anomaly Analysis",
            "correlation_analysis": "Correlation Analysis",
            "trend_analysis": "Trend Analysis",
            "business_insights": "Business Insights",
            "recommendations": "Recommendations"
        }

        used = set()

        for key in section_order:

            if key not in ai_report:
                continue

            used.add(key)

            story.append(
                Paragraph(
                    display_names.get(
                        key,
                        key.replace(
                            "_",
                            " "
                        ).title()
                    ),
                    styles["SubHeading"]
                )
            )

            value = ai_report.get(key)

            if isinstance(value, list):

                for item in value:

                    story.append(
                        Paragraph(
                            f"• {format_value(item)}",
                            styles["ReportBody"]
                        )
                    )

            elif isinstance(value, dict):

                for sub_key, sub_value in value.items():

                    story.append(
                        Paragraph(
                            f"<b>{format_value(sub_key)}:</b> "
                            f"{format_value(sub_value)}",
                            styles["ReportBody"]
                        )
                    )

            else:

                story.append(
                    Paragraph(
                        format_value(value),
                        styles["ReportBody"]
                    )
                )

        for key, value in ai_report.items():

            if key in used:
                continue

            story.append(
                Paragraph(
                    key.replace(
                        "_",
                        " "
                    ).title(),
                    styles["SubHeading"]
                )
            )

            story.append(
                Paragraph(
                    format_value(value),
                    styles["ReportBody"]
                )
            )

    else:

        story.append(
            Paragraph(
                format_value(ai_report),
                styles["ReportBody"]
            )
        )


def add_charts(
    story,
    charts,
    styles
):
    """
    Add generated charts to the PDF.
    """

    if not charts:
        return

    story.append(
        PageBreak()
    )

    story.append(
        Paragraph(
            "Generated Visualizations",
            styles["SectionHeading"]
        )
    )

    for chart in charts:

        if isinstance(chart, dict):

            filename = chart.get(
                "filename",
                ""
            )

            chart_type = chart.get(
                "type",
                "Chart"
            )

            reason = chart.get(
                "reason",
                ""
            )

        else:

            filename = str(chart)
            chart_type = "Chart"
            reason = ""

        chart_path = os.path.join(
            REPORT_FOLDER,
            os.path.basename(filename)
        )

        if not os.path.exists(chart_path):
            continue

        story.append(
            Paragraph(
                format_value(
                    chart_type
                ).title(),
                styles["SubHeading"]
            )
        )

        if reason:
            story.append(
                Paragraph(
                    format_value(reason),
                    styles["SmallText"]
                )
            )

        story.append(
            Spacer(
                1,
                5
            )
        )

        image = Image(
            chart_path
        )

        image.drawHeight = 3.2 * inch

        image.drawWidth = 6.2 * inch

        story.append(
            image
        )

        story.append(
            Spacer(
                1,
                15
            )
        )


def generate_pdf_report(
    filename,
    dataset_info=None,
    cleaning_result=None,
    analysis_results=None,
    ai_report=None,
    charts=None,
    **kwargs
):
    """
    Generate the final professional PDF report.

    The function accepts dataset_info and the other named
    arguments used by the Agentic AI orchestrator.
    """

    try:

        safe_name = safe_filename(
            filename
        )

        pdf_filename = (
            safe_name +
            "_report.pdf"
        )

        pdf_path = os.path.join(
            REPORT_FOLDER,
            pdf_filename
        )

        styles = create_heading_styles()

        document = SimpleDocTemplate(
            pdf_path,
            pagesize=A4,
            rightMargin=40,
            leftMargin=40,
            topMargin=40,
            bottomMargin=40
        )

        story = []

        # -------------------------------------------------
        # COVER PAGE
        # -------------------------------------------------

        story.append(
            Spacer(
                1,
                1.5 * inch
            )
        )

        story.append(
            Paragraph(
                "AI CSV Report Generator",
                styles["ReportTitle"]
            )
        )

        story.append(
            Paragraph(
                "Automated Agentic AI Data Analysis Report",
                styles["SectionHeading"]
            )
        )

        story.append(
            Spacer(
                1,
                20
            )
        )

        story.append(
            Paragraph(
                f"<b>Dataset:</b> "
                f"{format_value(filename)}",
                styles["ReportBody"]
            )
        )

        story.append(
            Paragraph(
                "<b>Generated by:</b> "
                "Agentic AI CSV Analysis System",
                styles["ReportBody"]
            )
        )

        story.append(
            Spacer(
                1,
                1.5 * inch
            )
        )

        story.append(
            Paragraph(
                "This report contains automated dataset "
                "inspection, analysis, visualization and "
                "AI-generated insights.",
                styles["ReportBody"]
            )
        )

        story.append(
            PageBreak()
        )

        # -------------------------------------------------
        # DATASET OVERVIEW
        # -------------------------------------------------

        add_dictionary_section(
            story,
            "Dataset Overview",
            dataset_info,
            styles
        )

        # -------------------------------------------------
        # CLEANING INFORMATION
        # -------------------------------------------------

        add_dictionary_section(
            story,
            "Data Cleaning",
            cleaning_result,
            styles
        )

        # -------------------------------------------------
        # ANALYSIS RESULTS
        # -------------------------------------------------

        if isinstance(
            analysis_results,
            dict
        ):

            numeric_analysis = (
                analysis_results.get(
                    "numeric"
                )
                or analysis_results.get(
                    "analyze_numeric"
                )
            )

            categorical_analysis = (
                analysis_results.get(
                    "categorical"
                )
                or analysis_results.get(
                    "analyze_categorical"
                )
            )

            correlation_analysis = (
                analysis_results.get(
                    "correlation"
                )
                or analysis_results.get(
                    "analyze_correlations"
                )
            )

            time_series_analysis = (
                analysis_results.get(
                    "time_series"
                )
                or analysis_results.get(
                    "analyze_time_series"
                )
            )

        else:

            numeric_analysis = None
            categorical_analysis = None
            correlation_analysis = None
            time_series_analysis = None

        add_numeric_analysis(
            story,
            numeric_analysis,
            styles
        )

        add_categorical_analysis(
            story,
            categorical_analysis,
            styles
        )

        add_correlation_analysis(
            story,
            correlation_analysis,
            styles
        )

        add_time_series_analysis(
            story,
            time_series_analysis,
            styles
        )

        # -------------------------------------------------
        # AGENT TOOL RESULTS
        # -------------------------------------------------

        add_tool_results(
            story,
            analysis_results
            if isinstance(
                analysis_results,
                list
            )
            else None,
            styles
        )

        # -------------------------------------------------
        # AI REPORT
        # -------------------------------------------------

        add_ai_report(
            story,
            ai_report,
            styles
        )

        # -------------------------------------------------
        # CHARTS
        # -------------------------------------------------

        add_charts(
            story,
            charts,
            styles
        )

        # -------------------------------------------------
        # BUILD PDF
        # -------------------------------------------------

        document.build(
            story,
            onFirstPage=add_page_number,
            onLaterPages=add_page_number
        )

        return {
            "pdf": pdf_filename,
            "path": pdf_path,
            "message": (
                "Professional PDF report "
                "generated successfully."
            )
        }

    except Exception as error:

        return {
            "pdf": None,
            "path": None,
            "message": (
                "PDF generation failed."
            ),
            "error": str(error)
        }