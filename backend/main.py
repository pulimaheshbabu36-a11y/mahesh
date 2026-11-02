import os
import traceback
from pathlib import Path

from fastapi import (
    FastAPI,
    UploadFile,
    File,
    HTTPException,
    BackgroundTasks
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from backend.agents.orchestrator import run_agent
from backend.tools.csv_tools import read_csv, inspect_csv, clean_csv
from backend.tools.analysis_tools import generate_insights
from backend.tools.database_tools import (
    initialize_database,
    save_report,
    get_all_reports,
    get_report
)
from backend.tools.agent_progress import (
    get_progress,
    update_progress
)

# ============================================================
# APP CONFIGURATION
# ============================================================

app = FastAPI(
    title="AI CSV Report Generator",
    description="Agentic AI powered CSV analysis and report generation system",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# ============================================================
# FOLDERS
# ============================================================

DATA_ROOT = os.path.abspath(os.getenv("APP_DATA_DIR", "."))
UPLOAD_FOLDER = os.path.join(DATA_ROOT, "backend", "uploads")
REPORT_FOLDER = os.path.join(DATA_ROOT, "reports")
FRONTEND_FOLDER = Path(__file__).resolve().parent.parent / "frontend"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(REPORT_FOLDER, exist_ok=True)

# ============================================================
# DATABASE
# ============================================================

initialize_database()

# ============================================================
# STATIC REPORT FILES
# ============================================================

app.mount(
    "/reports",
    StaticFiles(directory=REPORT_FOLDER),
    name="reports"
)

# ============================================================
# IN-MEMORY AGENT RESULTS
# ============================================================

AGENT_RESULTS = {}


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():
    return FileResponse(str(FRONTEND_FOLDER / "index.html"))


# ============================================================
# UPLOAD CSV
# ============================================================

@app.post("/upload-csv")
async def upload_csv(
    file: UploadFile = File(...)
):

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No file selected."
        )

    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=400,
            detail="Only CSV files are allowed."
        )

    safe_filename = os.path.basename(
        file.filename
    )

    file_path = os.path.join(
        UPLOAD_FOLDER,
        safe_filename
    )

    try:

        contents = await file.read()

        with open(
            file_path,
            "wb"
        ) as output:

            output.write(contents)

        return {
            "success": True,
            "filename": safe_filename,
            "message": "CSV uploaded successfully."
        }

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=f"Upload failed: {str(error)}"
        )


# ============================================================
# PREVIEW CSV
# ============================================================

@app.get("/preview-csv/{filename}")
def preview_csv(filename: str):

    filename = os.path.basename(filename)

    df, error = read_csv(filename)

    if error:
        raise HTTPException(
            status_code=404,
            detail=error
        )

    return {
        "filename": filename,
        "columns": df.columns.tolist(),
        "rows": len(df),
        "preview": df.head(10).fillna("").to_dict(
            orient="records"
        )
    }


# ============================================================
# ANALYZE CSV
# ============================================================

@app.get("/analyze-csv/{filename}")
def analyze_csv(filename: str):

    filename = os.path.basename(filename)

    df, error = read_csv(filename)

    if error:
        raise HTTPException(
            status_code=404,
            detail=error
        )

    inspection = inspect_csv(df)

    return {
        "filename": filename,
        "analysis": inspection
    }


# ============================================================
# CLEAN CSV
# ============================================================

@app.post("/clean-csv/{filename}")
def clean_csv_endpoint(filename: str):

    filename = os.path.basename(filename)

    df, error = read_csv(filename)

    if error:
        raise HTTPException(
            status_code=404,
            detail=error
        )

    result = clean_csv(
        df,
        filename
    )

    return {
        "success": True,
        "result": result
    }


# ============================================================
# GENERATE INSIGHTS
# ============================================================

@app.get("/generate-insights/{filename}")
def generate_insights_endpoint(filename: str):

    filename = os.path.basename(filename)

    df, error = read_csv(filename)

    if error:
        raise HTTPException(
            status_code=404,
            detail=error
        )

    insights = generate_insights(df)

    return {
        "filename": filename,
        "insights": insights
    }


# ============================================================
# DATASET STATISTICS
# ============================================================

@app.get("/dataset-statistics/{filename}")
def dataset_statistics(filename: str):

    filename = os.path.basename(filename)

    df, error = read_csv(filename)

    if error:
        raise HTTPException(
            status_code=404,
            detail=error
        )

    inspection = inspect_csv(df)

    return {
        "filename": filename,
        "rows": inspection.get("rows", 0),
        "columns": inspection.get("columns", 0),
        "missing_values": inspection.get(
            "missing_values",
            0
        ),
        "duplicate_rows": inspection.get(
            "duplicate_rows",
            0
        ),
        "column_names": inspection.get(
            "column_names",
            []
        )
    }


# ============================================================
# AGENT PROGRESS
# ============================================================

@app.get("/agent-progress/{filename}")
def agent_progress(filename: str):

    filename = os.path.basename(filename)

    return get_progress(filename)


# ============================================================
# BACKGROUND AGENT
# ============================================================

def run_agent_background(filename: str):

    filename = os.path.basename(filename)

    try:

        update_progress(
            filename,
            "running",
            1,
            8,
            "AI agent is starting..."
        )

        result = run_agent(filename)

        if not isinstance(result, dict):

            result = {
                "success": False,
                "message": "Agent returned an invalid result.",
                "raw_result": str(result)
            }

        AGENT_RESULTS[filename] = result

        # ----------------------------------------------------
        # Extract dataset information
        # ----------------------------------------------------

        dataset = result.get(
            "dataset",
            {}
        )

        if not isinstance(dataset, dict):
            dataset = {}

        rows = dataset.get(
            "rows",
            0
        )

        columns = dataset.get(
            "columns",
            0
        )

        missing_values = dataset.get(
            "missing_values",
            0
        )

        duplicate_rows = dataset.get(
            "duplicate_rows",
            0
        )

        # ----------------------------------------------------
        # Normalize PDF filename
        # ----------------------------------------------------

        pdf_value = result.get(
            "pdf",
            ""
        )

        if isinstance(pdf_value, dict):

            pdf_file = (
                pdf_value.get("pdf")
                or pdf_value.get("filename")
                or pdf_value.get("file")
                or ""
            )

        else:

            pdf_file = str(
                pdf_value or ""
            )

        # ----------------------------------------------------
        # Normalize Excel filename
        # ----------------------------------------------------

        excel_value = result.get(
            "excel",
            ""
        )

        if isinstance(excel_value, dict):

            excel_file = (
                excel_value.get("excel")
                or excel_value.get("filename")
                or excel_value.get("file")
                or ""
            )

        else:

            excel_file = str(
                excel_value or ""
            )

        # ----------------------------------------------------
        # Save report history
        # ----------------------------------------------------

        try:

            report_id = save_report(
                filename=filename,
                rows=rows,
                columns=columns,
                missing_values=missing_values,
                duplicate_rows=duplicate_rows,
                pdf_file=pdf_file,
                excel_file=excel_file
            )

            AGENT_RESULTS[filename][
                "report_id"
            ] = report_id

        except Exception as database_error:

            AGENT_RESULTS[filename][
                "database_warning"
            ] = str(database_error)

        # ----------------------------------------------------
        # Final progress
        # ----------------------------------------------------

        update_progress(
            filename,
            "completed",
            8,
            8,
            "AI report generation completed successfully."
        )

    except Exception as error:

        error_message = str(error)

        print(
            "\n========== AGENT ERROR =========="
        )

        print(error_message)

        traceback.print_exc()

        print(
            "=================================\n"
        )

        AGENT_RESULTS[filename] = {
            "success": False,
            "error": error_message
        }

        update_progress(
            filename,
            "error",
            0,
            8,
            error_message
        )


# ============================================================
# START AGENT
# ============================================================

@app.post("/run-agent/{filename}")
def start_agent(
    filename: str,
    background_tasks: BackgroundTasks
):

    filename = os.path.basename(filename)

    file_path = os.path.join(
        UPLOAD_FOLDER,
        filename
    )

    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=404,
            detail="CSV file not found."
        )

    AGENT_RESULTS.pop(
        filename,
        None
    )

    update_progress(
        filename,
        "running",
        0,
        8,
        "Agent queued for execution..."
    )

    background_tasks.add_task(
        run_agent_background,
        filename
    )

    return {
        "success": True,
        "filename": filename,
        "message": "AI agent started in background."
    }


# ============================================================
# GET AGENT RESULT
# ============================================================

@app.get("/agent-result/{filename}")
def agent_result(filename: str):

    filename = os.path.basename(filename)

    if filename not in AGENT_RESULTS:

        progress = get_progress(
            filename
        )

        if progress.get("status") == "running":

            return {
                "status": "running",
                "message": "Agent is still processing."
            }

        raise HTTPException(
            status_code=404,
            detail="Agent result not available."
        )

    return AGENT_RESULTS[filename]


# ============================================================
# DOWNLOAD PDF
# ============================================================

@app.get("/download-report/{filename}")
def download_report(filename: str):

    filename = os.path.basename(filename)

    base_name = os.path.splitext(
        filename
    )[0]

    pdf_filename = (
        f"{base_name}_report.pdf"
    )

    pdf_path = os.path.join(
        REPORT_FOLDER,
        pdf_filename
    )

    if not os.path.exists(pdf_path):

        raise HTTPException(
            status_code=404,
            detail="PDF report not found."
        )

    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename=pdf_filename
    )


# ============================================================
# DOWNLOAD EXCEL
# ============================================================

@app.get("/download-excel/{filename}")
def download_excel(filename: str):

    filename = os.path.basename(filename)

    base_name = os.path.splitext(
        filename
    )[0]

    cleaned_filename = (
        f"cleaned_{filename}"
    )

    cleaned_path = os.path.join(
        UPLOAD_FOLDER,
        cleaned_filename
    )

    original_path = os.path.join(
        UPLOAD_FOLDER,
        filename
    )

    source_path = (
        cleaned_path
        if os.path.exists(cleaned_path)
        else original_path
    )

    if not os.path.exists(source_path):

        raise HTTPException(
            status_code=404,
            detail="CSV file not found."
        )

    excel_filename = (
        f"{base_name}_cleaned.xlsx"
    )

    excel_path = os.path.join(
        REPORT_FOLDER,
        excel_filename
    )

    try:

        import pandas as pd

        df = pd.read_csv(
            source_path
        )

        df.to_excel(
            excel_path,
            index=False
        )

        return FileResponse(
            excel_path,
            media_type=(
                "application/vnd.openxmlformats-"
                "officedocument.spreadsheetml.sheet"
            ),
            filename=excel_filename
        )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=f"Excel generation failed: {str(error)}"
        )


# ============================================================
# REPORT HISTORY
# ============================================================

@app.get("/report-history")
def report_history():

    try:

        reports = get_all_reports()

        return reports

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=f"Unable to load report history: {str(error)}"
        )


# ============================================================
# SINGLE REPORT HISTORY
# ============================================================

@app.get("/report-history/{report_id}")
def single_report_history(
    report_id: int
):

    report = get_report(
        report_id
    )

    if report is None:

        raise HTTPException(
            status_code=404,
            detail="Report not found."
        )

    return report

@app.get("/health")
def health():
    return {"status": "ok"}


# Serve the frontend after registering API routes.
app.mount(
    "/",
    StaticFiles(directory=str(FRONTEND_FOLDER), html=True),
    name="frontend"
)
