import os
import json

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()


# =====================================================
# AI REPORT GENERATOR
# =====================================================

def generate_ai_report(
    dataset_summary
):

    api_key = os.getenv(
        "OPENAI_API_KEY"
    )


    if not api_key:

        return {
            "error":
                "OPENAI_API_KEY is not configured."
        }


    client = OpenAI(
        api_key=api_key
    )


    prompt = f"""
You are an expert data analyst and business
intelligence assistant.

Analyze the following dataset analysis results
and create a professional data analysis report.

DATASET AND ANALYSIS RESULTS:

{json.dumps(
    dataset_summary,
    indent=2,
    default=str
)}


Create the report using EXACTLY these sections:

1. executive_summary
2. dataset_overview
3. data_quality
4. key_findings
5. statistical_findings
6. anomaly_analysis
7. correlation_analysis
8. trend_analysis
9. business_insights
10. recommendations


IMPORTANT RULES:

- Use only information supported by the supplied data.
- Do not invent numbers.
- Do not invent trends.
- Clearly state when an analysis is unavailable.
- Mention important outliers when detected.
- Explain strong correlations carefully.
- Correlation does not prove causation.
- Explain useful trends when time-series information exists.
- Identify unusual or potentially important patterns.
- Keep the language professional but easy to understand.
- Recommendations must be based on observed data.
- Return valid JSON only.


JSON FORMAT:

{{
    "executive_summary": "...",

    "dataset_overview": "...",

    "data_quality": "...",

    "key_findings": [
        "...",
        "...",
        "..."
    ],

    "statistical_findings": [
        "...",
        "...",
        "..."
    ],

    "anomaly_analysis": [
        "...",
        "..."
    ],

    "correlation_analysis": [
        "...",
        "..."
    ],

    "trend_analysis": [
        "...",
        "..."
    ],

    "business_insights": [
        "...",
        "...",
        "..."
    ],

    "recommendations": [
        "...",
        "...",
        "..."
    ]
}}
"""


    try:

        response = client.responses.create(

            model="gpt-5.6-luna",

            input=prompt
        )


        text = response.output_text.strip()


        # ---------------------------------------------
        # Remove markdown JSON fences if returned
        # ---------------------------------------------

        if text.startswith(
            "```json"
        ):

            text = text[
                7:
            ]


        if text.endswith(
            "```"
        ):

            text = text[
                :-3
            ]


        text = text.strip()


        report = json.loads(
            text
        )


        return report


    except json.JSONDecodeError as error:

        return {

            "error":
                "AI returned invalid JSON.",

            "details":
                str(error)
        }


    except Exception as error:

        return {

            "error":
                f"AI report generation failed: {str(error)}"
        }