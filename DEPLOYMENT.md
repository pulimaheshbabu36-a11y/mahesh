# Deployment Guide — AI CSV Report Generator

## Hosting layout
This package is configured as one Render Python web service. FastAPI serves both the dashboard and API on the same domain, so the browser does not call localhost.

## Before pushing to GitHub
- Never upload `.env`, API keys, `.venv`, local CSV uploads, generated reports, or SQLite files.
- The `.gitignore` in this package excludes these files.
- Because the source ZIP you supplied included `.env`, revoke the old OpenAI API key and create a replacement before deployment.

## GitHub
1. Create a new GitHub repository.
2. Extract this deployment ZIP.
3. Upload/push the contents of this folder to the repository root (the `backend`, `frontend`, `requirements.txt`, and `render.yaml` should be at the top level).
4. Confirm `.env` is NOT in the repository.

## Render
1. Sign in to Render and choose New > Blueprint.
2. Connect the GitHub repository containing `render.yaml`.
3. Review the service configuration and deploy.
4. In the Render service dashboard, open Environment and add `OPENAI_API_KEY` with your newly created key.
5. Trigger a redeploy after saving the environment variable.
6. Open the public Render URL. `/health` should return `{"status":"ok"}` and `/` should show the dashboard.

## Storage note
The included free-tier configuration stores uploaded CSVs, generated reports and SQLite under `/tmp/ai-csv-report-data`. This is temporary storage and can be cleared when the service restarts or redeploys. For durable data, attach a paid Render persistent disk mounted at `/var/data` and change `APP_DATA_DIR` to `/var/data` in the service environment.

## Important
- The service start command is `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`.
- The OpenAI key is configured in Render environment variables, not in GitHub.
- Do not commit local customer datasets or generated reports.
- Test CSV upload, preview, agent execution, chart display, PDF download, Excel download and report history after deployment.
