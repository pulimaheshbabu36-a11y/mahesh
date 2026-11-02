import json
import os

from dotenv import load_dotenv
from openai import OpenAI


# ============================================================
# ENVIRONMENT
# ============================================================

load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")

if not API_KEY:
    raise ValueError(
        "OPENAI_API_KEY is missing from the .env file."
    )


client = OpenAI(
    api_key=API_KEY
)


# ============================================================
# MODEL
# ============================================================

MODEL_NAME = "gpt-5.6-luna"


# ============================================================
# AVAILABLE AGENT TOOLS
# ============================================================

AGENT_TOOLS = [

    {
        "type": "function",
        "name": "clean_dataset",

        "description": (
            "Clean the dataset by removing duplicate rows, "
            "removing completely empty columns, and filling "
            "missing numeric and categorical values."
        ),

        "parameters": {
            "type": "object",
            "properties": {},
            "additionalProperties": False
        }
    },


    {
        "type": "function",
        "name": "analyze_numeric",

        "description": (
            "Analyze numeric columns using mean, median, "
            "minimum, maximum, standard deviation, quartiles, "
            "IQR and possible outliers."
        ),

        "parameters": {
            "type": "object",
            "properties": {},
            "additionalProperties": False
        }
    },


    {
        "type": "function",
        "name": "analyze_categorical",

        "description": (
            "Analyze categorical columns including unique "
            "values and their frequencies."
        ),

        "parameters": {
            "type": "object",
            "properties": {},
            "additionalProperties": False
        }
    },


    {
        "type": "function",
        "name": "analyze_correlations",

        "description": (
            "Analyze relationships and correlations between "
            "numeric columns."
        ),

        "parameters": {
            "type": "object",
            "properties": {},
            "additionalProperties": False
        }
    },


    {
        "type": "function",
        "name": "analyze_time_series",

        "description": (
            "Analyze trends over time when the dataset "
            "contains a date or datetime column."
        ),

        "parameters": {
            "type": "object",
            "properties": {},
            "additionalProperties": False
        }
    },


    {
        "type": "function",
        "name": "generate_charts",

        "description": (
            "Generate useful visualizations based on the "
            "dataset and completed analysis."
        ),

        "parameters": {
            "type": "object",
            "properties": {},
            "additionalProperties": False
        }
    },


    {
        "type": "function",
        "name": "finish",

        "description": (
            "Finish the workflow when enough useful analysis "
            "has been completed."
        ),

        "parameters": {
            "type": "object",
            "properties": {},
            "additionalProperties": False
        }
    }

]


# ============================================================
# SYSTEM PROMPT
# ============================================================

SYSTEM_PROMPT = """
You are the decision-making agent inside an AI CSV Report
Generator.

Your job is to decide the NEXT useful action.

You do NOT perform the analysis yourself.
Python tools perform the actual analysis.

Inspect:

- Dataset structure
- Rows
- Columns
- Numeric columns
- Categorical columns
- Date/time columns
- Missing values
- Duplicate rows
- Previous actions
- Previous tool results

Choose exactly ONE action.

RULES:

1. Cleaning normally happens before detailed analysis.

2. Do not repeat an action that already completed successfully.

3. Numeric analysis is useful when numeric columns exist.

4. Categorical analysis is useful when categorical columns exist.

5. Correlation analysis requires at least two numeric columns.

6. Time-series analysis requires a date/time column.

7. Charts should normally be generated after useful analysis.

8. Do not repeatedly generate charts.

9. Finish when enough useful evidence has been collected.

10. Do not execute every possible tool blindly.

The objective is useful autonomous analysis.
"""


# ============================================================
# NORMALIZE ACTION
# ============================================================

def normalize_action(action_name):

    mapping = {

        "clean_dataset": "clean",

        "analyze_numeric": "numeric",

        "analyze_categorical": "categorical",

        "analyze_correlations": "correlation",

        "analyze_time_series": "time_series",

        "generate_charts": "charts",

        "finish": "finish"

    }

    return mapping.get(
        action_name,
        action_name
    )


# ============================================================
# GENERATE HUMAN-READABLE REASON
# ============================================================

def generate_reason(
    action,
    dataset_info,
    completed_actions
):

    dataset_info = dataset_info or {}

    column_names = dataset_info.get(
        "column_names",
        []
    )

    rows = dataset_info.get(
        "rows",
        0
    )

    columns = dataset_info.get(
        "columns",
        len(column_names)
    )

    numeric_columns = dataset_info.get(
        "numeric_columns",
        []
    )

    categorical_columns = dataset_info.get(
        "categorical_columns",
        []
    )

    date_columns = dataset_info.get(
        "date_columns",
        []
    )

    missing_values = dataset_info.get(
        "missing_values",
        0
    )

    duplicate_rows = dataset_info.get(
        "duplicate_rows",
        0
    )


    if action == "clean":

        if missing_values > 0 and duplicate_rows > 0:

            return (
                f"The dataset contains {missing_values} "
                f"missing values and {duplicate_rows} "
                "duplicate rows. Cleaning is required "
                "before detailed analysis."
            )

        if missing_values > 0:

            return (
                f"The dataset contains {missing_values} "
                "missing values. Cleaning is required "
                "before detailed analysis."
            )

        if duplicate_rows > 0:

            return (
                f"The dataset contains {duplicate_rows} "
                "duplicate rows. Cleaning is useful "
                "before detailed analysis."
            )

        return (
            "The dataset should be validated and cleaned "
            "before detailed analysis."
        )


    if action == "numeric":

        return (
            f"The dataset contains "
            f"{len(numeric_columns)} numeric column(s). "
            "Numeric analysis can identify averages, "
            "ranges, distributions and possible outliers."
        )


    if action == "categorical":

        return (
            f"The dataset contains "
            f"{len(categorical_columns)} categorical "
            "column(s). Categorical analysis can identify "
            "frequencies, dominant categories and unique "
            "values."
        )


    if action == "correlation":

        return (
            f"The dataset contains "
            f"{len(numeric_columns)} numeric columns. "
            "Correlation analysis can identify relationships "
            "between numerical variables."
        )


    if action == "time_series":

        return (
            f"The dataset contains "
            f"{len(date_columns)} date/time column(s). "
            "Time-series analysis can identify trends "
            "and changes over time."
        )


    if action == "charts":

        return (
            "Useful statistical and structural analysis has "
            "been completed. Visualizations can now summarize "
            "important patterns in the dataset."
        )


    if action == "finish":

        return (
            f"The agent has completed sufficient analysis "
            f"for the {rows}-row, {columns}-column dataset. "
            "The available analysis results can now be "
            "used to generate the final report."
        )


    return (
        "The agent selected this action based on the "
        "current dataset state and completed analysis."
    )


# ============================================================
# DECISION FUNCTION
# ============================================================

def decide_next_action(
    dataset_info,
    previous_actions,
    previous_results
):

    previous_actions = (
        previous_actions or []
    )

    previous_results = (
        previous_results or []
    )


    # --------------------------------------------------------
    # Find completed actions
    # --------------------------------------------------------

    completed_actions = []


    for action in previous_actions:

        if isinstance(action, dict):

            action_name = action.get(
                "action",
                action.get(
                    "name",
                    ""
                )
            )

        else:

            action_name = str(
                action
            )


        action_name = normalize_action(
            action_name
        )


        if action_name:

            completed_actions.append(
                action_name
            )


    completed_actions = list(
        dict.fromkeys(
            completed_actions
        )
    )


    # --------------------------------------------------------
    # Agent context
    # --------------------------------------------------------

    context = {

        "dataset": dataset_info,

        "completed_actions":
            completed_actions,

        "previous_results":
            previous_results[-6:]

    }


    user_prompt = f"""
Current agent state:

{json.dumps(
    context,
    indent=2,
    default=str
)}

Choose the single most useful NEXT action.

Do not repeat a successfully completed action.

Use the dataset structure to determine which analysis
is actually useful.

Choose finish when enough evidence has been collected.
"""


    # --------------------------------------------------------
    # Ask AI agent
    # --------------------------------------------------------

    try:

        response = client.responses.create(

            model=MODEL_NAME,

            instructions=SYSTEM_PROMPT,

            input=user_prompt,

            tools=AGENT_TOOLS,

            tool_choice="required"

        )

    except Exception as error:

        print(
            "Agent decision error:",
            error
        )

        reason = (
            "The AI decision service returned an error. "
            "The agent is safely stopping the decision "
            "loop."
        )

        return {

            "action": "finish",

            "arguments": {},

            "reason": reason

        }


    # --------------------------------------------------------
    # Read AI tool call
    # --------------------------------------------------------

    for output in response.output:

        if getattr(
            output,
            "type",
            None
        ) != "function_call":

            continue


        action_name = output.name


        try:

            arguments = json.loads(
                output.arguments or "{}"
            )

        except Exception:

            arguments = {}


        action = normalize_action(
            action_name
        )


        # ----------------------------------------------------
        # Prevent repeated actions
        # ----------------------------------------------------

        if (
            action != "finish"
            and action in completed_actions
        ):

            print(
                "Repeated action detected:",
                action
            )

            action = "finish"


        # ----------------------------------------------------
        # Generate explanation
        # ----------------------------------------------------

        reason = generate_reason(

            action,

            dataset_info,

            completed_actions

        )


        print(
            "\n========================================"
        )

        print(
            "AGENT DECISION"
        )

        print(
            "Action:",
            action
        )

        print(
            "Reason:",
            reason
        )

        print(
            "========================================\n"
        )


        return {

            "action": action,

            "arguments": arguments,

            "reason": reason

        }


    # --------------------------------------------------------
    # Safe fallback
    # --------------------------------------------------------

    reason = (
        "The agent did not return a valid tool decision, "
        "so the workflow is being safely completed."
    )


    return {

        "action": "finish",

        "arguments": {},

        "reason": reason

    }