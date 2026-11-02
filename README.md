# AI CSV Report Generator

An Agentic AI-powered application that automatically analyzes CSV datasets, generates insights, creates visualizations, and produces professional PDF and Excel reports.

## Project Domain

Agentic AI

## Project Name

AI CSV Report Generator

## Overview

The AI CSV Report Generator is an intelligent data-analysis application.

The user uploads a CSV file and the system automatically:

1. Reads the dataset
2. Inspects data quality
3. Cleans the dataset
4. Performs statistical analysis
5. Analyzes categorical data
6. Detects correlations
7. Performs time-series analysis
8. Generates charts
9. Uses AI to generate insights
10. Generates a professional PDF report
11. Generates an Excel report
12. Stores report history

## Architecture

CSV File
    ↓
FastAPI Backend
    ↓
Agent Decision Engine
    ↓
Python Analysis Tools
    ↓
Tool Results
    ↓
AI Decision
    ↓
Charts and Analysis
    ↓
AI Report
    ↓
PDF + Excel
    ↓
SQLite Report History

## Technologies Used

### Frontend

- HTML
- CSS
- JavaScript

### Backend

- Python
- FastAPI
- Uvicorn

### Data Analysis

- Pandas
- NumPy
- Matplotlib

### AI

- OpenAI API

### Reports

- ReportLab
- OpenPyXL

### Database

- SQLite

## Main Features

### CSV Upload

Users can upload CSV datasets through the web dashboard.

### Data Cleaning

The system can:

- Remove duplicate rows
- Remove completely empty columns
- Fill missing numeric values
- Fill missing categorical values

### Statistical Analysis

The system analyzes:

- Count
- Mean
- Median
- Minimum
- Maximum
- Sum
- Standard deviation
- Range
- Quartiles
- IQR
- Outliers

### Categorical Analysis

The system identifies:

- Unique values
- Value frequencies
- Most common categories

### Correlation Analysis

The system calculates relationships between numeric variables.

### Time-Series Analysis

Date columns are detected and analyzed when available.

### Automatic Charts

The system can generate:

- Line charts
- Bar charts
- Scatter plots
- Histograms
- Correlation heatmaps

### Agentic AI

The agent dynamically decides which analysis tools should be executed based on the uploaded dataset.

### AI Report

The AI generates:

- Executive summary
- Dataset overview
- Data quality analysis
- Key findings
- Statistical findings
- Anomaly analysis
- Correlation analysis
- Trend analysis
- Business insights
- Recommendations

### PDF Report

A professional PDF report is automatically generated.

### Excel Report

The project also supports downloadable Excel reports.

### Report History

Generated reports are stored in SQLite.

## Project Structure

AI CSV REPORT
│
├── .env
├── .gitignore
├── README.md
├── requirements.txt
│
├── backend
│   ├── agents
│   │   ├── __init__.py
│   │   └── orchestrator.py
│   │
│   ├── tools
│   │   ├── __init__.py
│   │   ├── csv_tools.py
│   │   ├── analysis_tools.py
│   │   ├── chart_tools.py
│   │   ├── report_tools.py
│   │   ├── llm_tools.py
│   │   ├── agent_decision.py
│   │   ├── database_tools.py
│   │   └── agent_progress.py
│   │
│   ├── database
│   │   └── reports.db
│   │
│   ├── uploads
│   │
│   └── main.py
│
├── frontend
│   ├── index.html
│   ├── style.css
│   └── script.js
│
├── reports
│
└── venv

## Installation

### 1. Clone or copy the project

Place the project in your desired directory.

### 2. Create virtual environment

```powershell
python -m venv venv