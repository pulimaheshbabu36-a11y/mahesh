import sqlite3
import os
from datetime import datetime


# =====================================================
# DATABASE CONFIGURATION
# =====================================================

DATA_ROOT = os.path.abspath(os.getenv("APP_DATA_DIR", "."))
DATABASE_FOLDER = os.path.join(DATA_ROOT, "backend", "database")

DATABASE_PATH = os.path.join(
    DATABASE_FOLDER,
    "reports.db"
)


# =====================================================
# CREATE DATABASE FOLDER
# =====================================================

os.makedirs(
    DATABASE_FOLDER,
    exist_ok=True
)


# =====================================================
# GET DATABASE CONNECTION
# =====================================================

def get_connection():

    connection = sqlite3.connect(
        DATABASE_PATH
    )

    connection.row_factory = (
        sqlite3.Row
    )

    return connection


# =====================================================
# INITIALIZE DATABASE
# =====================================================

def initialize_database():

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS reports (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            filename TEXT NOT NULL,

            rows INTEGER,

            columns INTEGER,

            missing_values INTEGER,

            duplicate_rows INTEGER,

            pdf_file TEXT,

            excel_file TEXT,

            created_at TEXT NOT NULL

        )
        """
    )

    connection.commit()

    connection.close()


# =====================================================
# SAVE REPORT
# =====================================================

def save_report(
    filename,
    rows,
    columns,
    missing_values,
    duplicate_rows,
    pdf_file,
    excel_file
):

    connection = get_connection()

    cursor = connection.cursor()


    created_at = (
        datetime.now()
        .strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    )


    cursor.execute(
        """
        INSERT INTO reports (

            filename,
            rows,
            columns,
            missing_values,
            duplicate_rows,
            pdf_file,
            excel_file,
            created_at

        )

        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,

        (
            filename,
            rows,
            columns,
            missing_values,
            duplicate_rows,
            pdf_file,
            excel_file,
            created_at
        )
    )


    connection.commit()

    report_id = cursor.lastrowid

    connection.close()


    return report_id


# =====================================================
# GET ALL REPORTS
# =====================================================

def get_all_reports():

    connection = get_connection()

    cursor = connection.cursor()


    cursor.execute(
        """
        SELECT *

        FROM reports

        ORDER BY id DESC
        """
    )


    rows = cursor.fetchall()

    connection.close()


    return [
        dict(row)
        for row in rows
    ]


# =====================================================
# GET SINGLE REPORT
# =====================================================

def get_report(
    report_id
):

    connection = get_connection()

    cursor = connection.cursor()


    cursor.execute(
        """
        SELECT *

        FROM reports

        WHERE id = ?
        """,

        (
            report_id,
        )
    )


    row = cursor.fetchone()

    connection.close()


    if row is None:

        return None


    return dict(row)