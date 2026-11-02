import os


# ============================================================
# AGENT PROGRESS STORAGE
# ============================================================

AGENT_PROGRESS = {}


# ============================================================
# UPDATE PROGRESS
# ============================================================

def update_progress(
    filename,
    status,
    step,
    total,
    message
):

    filename = os.path.basename(
        filename
    )

    AGENT_PROGRESS[filename] = {
        "status": status,
        "step": step,
        "total": total,
        "message": message
    }


# ============================================================
# GET PROGRESS
# ============================================================

def get_progress(
    filename
):

    filename = os.path.basename(
        filename
    )

    return AGENT_PROGRESS.get(
        filename,
        {
            "status": "idle",
            "step": 0,
            "total": 8,
            "message": "Agent has not started."
        }
    )