const API_URL = ""; // Same-origin API when deployed or served by FastAPI

let currentFilename = null;
let progressTimer = null;


/* =====================================================
   INITIALIZATION
===================================================== */

document.addEventListener("DOMContentLoaded", () => {

    const fileInput =
        document.getElementById("csvFile");

    const uploadButton =
        document.getElementById("uploadButton");

    const previewButton =
        document.getElementById("previewButton");

    const statisticsButton =
        document.getElementById("statisticsButton");

    const agentButton =
        document.getElementById("agentButton");

    const refreshHistoryButton =
        document.getElementById(
            "refreshHistoryButton"
        );


    if (fileInput) {

        fileInput.addEventListener(
            "change",
            handleFileSelection
        );
    }


    if (uploadButton) {

        uploadButton.addEventListener(
            "click",
            uploadCSV
        );
    }


    if (previewButton) {

        previewButton.addEventListener(
            "click",
            previewCSV
        );
    }


    if (statisticsButton) {

        statisticsButton.addEventListener(
            "click",
            loadStatistics
        );
    }


    if (agentButton) {

        agentButton.addEventListener(
            "click",
            runAgent
        );
    }


    if (refreshHistoryButton) {

        refreshHistoryButton.addEventListener(
            "click",
            loadHistory
        );
    }


    setupDragAndDrop();

    loadHistory();
});


/* =====================================================
   SIDEBAR
===================================================== */

function toggleSidebar() {

    const sidebar =
        document.querySelector(
            ".sidebar"
        );

    if (sidebar) {
        sidebar.classList.toggle(
            "open"
        );
    }
}


function scrollToSection(id) {

    const element =
        document.getElementById(id);

    if (!element) {
        return;
    }

    element.scrollIntoView({
        behavior: "smooth",
        block: "start"
    });


    const sidebar =
        document.querySelector(
            ".sidebar"
        );

    if (sidebar) {
        sidebar.classList.remove(
            "open"
        );
    }
}


/* =====================================================
   DRAG AND DROP
===================================================== */

function setupDragAndDrop() {

    const uploadArea =
        document.getElementById(
            "uploadArea"
        );

    if (!uploadArea) {
        return;
    }


    uploadArea.addEventListener(
        "dragover",
        event => {

            event.preventDefault();

            uploadArea.style.borderColor =
                "#635bff";

            uploadArea.style.background =
                "#faf9ff";
        }
    );


    uploadArea.addEventListener(
        "dragleave",
        () => {

            uploadArea.style.borderColor =
                "";

            uploadArea.style.background =
                "";
        }
    );


    uploadArea.addEventListener(
        "drop",
        event => {

            event.preventDefault();

            uploadArea.style.borderColor =
                "";

            uploadArea.style.background =
                "";

            const files =
                event.dataTransfer.files;

            if (!files.length) {
                return;
            }

            const file =
                files[0];

            if (
                !file.name
                    .toLowerCase()
                    .endsWith(".csv")
            ) {

                showMessage(
                    "uploadMessage",
                    "Please select a CSV file.",
                    "error"
                );

                return;
            }


            const input =
                document.getElementById(
                    "csvFile"
                );

            const dataTransfer =
                new DataTransfer();

            dataTransfer.items.add(file);

            input.files =
                dataTransfer.files;

            handleFileSelection({
                target: input
            });
        }
    );
}


/* =====================================================
   FILE SELECTION
===================================================== */

function handleFileSelection(event) {

    const file =
        event.target.files[0];

    const selectedFile =
        document.getElementById(
            "selectedFile"
        );


    if (!file) {

        if (selectedFile) {
            selectedFile.textContent =
                "No file selected";
        }

        return;
    }


    if (
        !file.name
            .toLowerCase()
            .endsWith(".csv")
    ) {

        showMessage(
            "uploadMessage",
            "Only CSV files are supported.",
            "error"
        );

        event.target.value = "";

        return;
    }


    if (selectedFile) {

        selectedFile.innerHTML =
            `✓ ${escapeHTML(file.name)}`;
    }


    showMessage(
        "uploadMessage",
        "CSV selected. Ready to upload.",
        "info"
    );
}


/* =====================================================
   UPLOAD
===================================================== */

async function uploadCSV() {

    const fileInput =
        document.getElementById(
            "csvFile"
        );


    if (
        !fileInput ||
        !fileInput.files.length
    ) {

        showMessage(
            "uploadMessage",
            "Please select a CSV file first.",
            "error"
        );

        return;
    }


    const file =
        fileInput.files[0];


    const formData =
        new FormData();

    formData.append(
        "file",
        file
    );


    const button =
        document.getElementById(
            "uploadButton"
        );


    setButtonLoading(
        button,
        true,
        "Uploading..."
    );


    try {

        const response =
            await fetch(
                `${API_URL}/upload-csv`,
                {
                    method: "POST",
                    body: formData
                }
            );


        const data =
            await response.json();


        if (!response.ok) {

            throw new Error(
                data.detail ||
                "Upload failed."
            );
        }


        currentFilename =
            data.filename ||
            file.name;


        showMessage(
            "uploadMessage",
            `✓ ${currentFilename} uploaded successfully.`,
            "success"
        );


        enableActionButtons();

        resetReport();

        await previewCSV();

        await loadStatistics();

        await loadHistory();


    } catch (error) {

        console.error(error);

        showMessage(
            "uploadMessage",
            error.message,
            "error"
        );


    } finally {

        setButtonLoading(
            button,
            false,
            "Upload Dataset"
        );
    }
}


/* =====================================================
   PREVIEW
===================================================== */

async function previewCSV() {

    if (!currentFilename) {
        return;
    }


    try {

        const response =
            await fetch(
                `${API_URL}/preview-csv/${encodeURIComponent(currentFilename)}`
            );


        const data =
            await response.json();


        if (!response.ok) {

            throw new Error(
                data.detail ||
                "Preview failed."
            );
        }


        renderCSVPreview(data);

        updateKPIs(data);

        showReport();


    } catch (error) {

        console.error(error);

        showMessage(
            "uploadMessage",
            error.message,
            "error"
        );
    }
}


/* =====================================================
   STATISTICS
===================================================== */

async function loadStatistics() {

    if (!currentFilename) {
        return;
    }


    try {

        const response =
            await fetch(
                `${API_URL}/dataset-statistics/${encodeURIComponent(currentFilename)}`
            );


        const data =
            await response.json();


        if (!response.ok) {

            throw new Error(
                data.detail ||
                "Statistics failed."
            );
        }


        updateKPIs(data);

        showReport();


    } catch (error) {

        console.error(error);

    }
}


/* =====================================================
   RUN AGENT
===================================================== */

async function runAgent() {

    if (!currentFilename) {

        showMessage(
            "uploadMessage",
            "Upload a CSV file first.",
            "error"
        );

        return;
    }


    resetAgentUI();


    const button =
        document.getElementById(
            "agentButton"
        );


    setButtonLoading(
        button,
        true,
        "Running Agent..."
    );


    setAgentStatus(
        "running",
        "Running"
    );


    setProgress(
        0,
        8,
        "Starting autonomous analysis..."
    );


    showReport();


    try {

        monitorAgentProgress();


        const response =
            await fetch(
                `${API_URL}/run-agent/${encodeURIComponent(currentFilename)}`,
                {
                    method: "POST"
                }
            );


        const data =
            await response.json();


        if (!response.ok) {

            throw new Error(
                data.detail ||
                "Agent could not be started."
            );
        }


        updateAgentActivity(
            data.message ||
            "Agent started."
        );


    } catch (error) {

        console.error(error);

        stopProgressPolling();


        setAgentStatus(
            "error",
            "Error"
        );


        updateAgentActivity(
            error.message
        );


        setButtonLoading(
            button,
            false,
            "Run AI Agent"
        );
    }
}


/* =====================================================
   PROGRESS
===================================================== */

function monitorAgentProgress() {

    stopProgressPolling();

    progressTimer =
        setInterval(
            checkAgentProgress,
            1000
        );

    checkAgentProgress();
}


async function checkAgentProgress() {

    if (!currentFilename) {
        return;
    }


    try {

        const response =
            await fetch(
                `${API_URL}/agent-progress/${encodeURIComponent(currentFilename)}`
            );


        const data =
            await response.json();


        if (!response.ok) {
            return;
        }


        const step =
            Number(data.step || 0);

        const total =
            Number(data.total || 8);

        const status =
            data.status || "running";

        const message =
            data.message ||
            "Processing...";


        setProgress(
            step,
            total,
            message
        );


        updateAgentActivity(
            message
        );


        if (
            status === "completed" ||
            status === "error"
        ) {

            stopProgressPolling();


            if (
                status === "completed"
            ) {

                setAgentStatus(
                    "completed",
                    "Completed"
                );


                setProgress(
                    total,
                    total,
                    "Analysis completed successfully."
                );


                const button =
                    document.getElementById(
                        "agentButton"
                    );


                setButtonLoading(
                    button,
                    false,
                    "Run AI Agent"
                );


                await loadFinalReport();

                await loadHistory();


            } else {

                setAgentStatus(
                    "error",
                    "Error"
                );


                const button =
                    document.getElementById(
                        "agentButton"
                    );


                setButtonLoading(
                    button,
                    false,
                    "Run AI Agent"
                );
            }
        }


    } catch (error) {

        console.error(
            "Progress error:",
            error
        );
    }
}


function stopProgressPolling() {

    if (progressTimer) {

        clearInterval(
            progressTimer
        );

        progressTimer = null;
    }
}


/* =====================================================
   FINAL REPORT
===================================================== */

async function loadFinalReport() {

    if (!currentFilename) {
        return;
    }


    try {

        const response =
            await fetch(
                `${API_URL}/agent-result/${encodeURIComponent(currentFilename)}`
            );


        const data =
            await response.json();


        if (!response.ok) {

            throw new Error(
                data.detail ||
                "Report unavailable."
            );
        }


        if (
            data.status === "pending" ||
            data.status === "running"
        ) {
            return;
        }


        renderCompleteReport(data);

        enableDownloads();


    } catch (error) {

        console.error(error);

        showMessage(
            "uploadMessage",
            error.message,
            "error"
        );
    }
}


/* =====================================================
   COMPLETE REPORT
===================================================== */

function renderCompleteReport(
    result
) {

    showReport();


    if (result.dataset) {

        renderDatasetOverview(
            result.dataset
        );
    }


    if (result.insights) {

        renderInsights(
            result.insights
        );
    }


    if (result.analysis) {

        renderAnalysisResults(
            result.analysis
        );
    }


    if (result.ai_report) {

        renderAIReport(
            result.ai_report
        );
    }


    if (result.charts) {

        renderCharts(
            result.charts
        );
    }


    if (result.actions) {

        renderAgentWorkflow(
            result.actions
        );
    }


    if (result.tool_results) {

        renderToolResults(
            result.tool_results
        );
    }


    updateKPIs(result);
}


/* =====================================================
   DATASET OVERVIEW
===================================================== */

function renderDatasetOverview(
    dataset
) {

    const container =
        document.getElementById(
            "datasetOverview"
        );


    if (!container) {
        return;
    }


    const rows =
        dataset.rows ?? 0;

    const columns =
        dataset.columns ?? 0;

    const missing =
        dataset.missing_values ?? 0;

    const duplicates =
        dataset.duplicate_rows ?? 0;

    const names =
        dataset.column_names || [];


    container.innerHTML = `

        <div class="statistics-grid">

            <div class="stat-card">
                <h4>Rows</h4>
                <strong>${formatValue(rows)}</strong>
            </div>

            <div class="stat-card">
                <h4>Columns</h4>
                <strong>${formatValue(columns)}</strong>
            </div>

            <div class="stat-card">
                <h4>Missing Values</h4>
                <strong>${formatValue(missing)}</strong>
            </div>

            <div class="stat-card">
                <h4>Duplicate Rows</h4>
                <strong>${formatValue(duplicates)}</strong>
            </div>

        </div>

        <div class="analysis-subsection">

            <h5>
                Dataset Columns
            </h5>

            <div class="insight-list">

                ${
                    names.length
                        ? names.map(
                            column => `
                                <div class="insight-item">
                                    ${escapeHTML(column)}
                                </div>
                            `
                        ).join("")
                        : "<div>No columns available.</div>"
                }

            </div>

        </div>
    `;
}


/* =====================================================
   CSV PREVIEW
===================================================== */

function renderCSVPreview(
    data
) {

    const container =
        document.getElementById(
            "csvPreview"
        );


    if (!container) {
        return;
    }


    const columns =
        data.columns || [];

    const preview =
        data.preview || [];


    if (!columns.length) {

        container.innerHTML =
            "<p>No preview available.</p>";

        return;
    }


    let html = `

        <div class="table-wrapper">

            <table>

                <thead>

                    <tr>

    `;


    columns.forEach(
        column => {

            html += `
                <th>
                    ${escapeHTML(column)}
                </th>
            `;
        }
    );


    html += `

                    </tr>

                </thead>

                <tbody>

    `;


    preview.forEach(
        row => {

            html += "<tr>";


            columns.forEach(
                column => {

                    html += `
                        <td>
                            ${escapeHTML(
                                row[column] ?? ""
                            )}
                        </td>
                    `;
                }
            );


            html += "</tr>";
        }
    );


    html += `

                </tbody>

            </table>

        </div>

    `;


    container.innerHTML =
        html;
}


/* =====================================================
   INSIGHTS
===================================================== */

function renderInsights(
    data
) {

    const container =
        document.getElementById(
            "insights"
        );


    if (!container) {
        return;
    }


    let items = [];


    if (Array.isArray(data)) {

        items = data;

    } else if (
        typeof data === "string"
    ) {

        items = [data];

    } else if (
        data &&
        typeof data === "object"
    ) {

        items =
            Object.entries(data)
                .map(
                    ([key, value]) => ({
                        title: key,
                        value: value
                    })
                );
    }


    if (!items.length) {

        container.innerHTML =
            "<p>No insights generated.</p>";

        return;
    }


    container.innerHTML = `

        <div class="insight-list">

            ${
                items.map(
                    item => {

                        if (
                            typeof item === "string"
                        ) {

                            return `
                                <div class="insight-item">
                                    ${escapeHTML(item)}
                                </div>
                            `;
                        }


                        return `
                            <div class="insight-item">

                                <strong>
                                    ${escapeHTML(
                                        item.title ||
                                        "Insight"
                                    )}
                                </strong>

                                <span>
                                    ${escapeHTML(
                                        item.value
                                    )}
                                </span>

                            </div>
                        `;
                    }
                ).join("")
            }

        </div>
    `;
}


/* =====================================================
   AI REPORT
===================================================== */

function renderAIReport(
    data
) {

    const container =
        document.getElementById(
            "aiReport"
        );


    if (!container) {
        return;
    }


    if (
        !data ||
        typeof data !== "object"
    ) {

        container.innerHTML =
            `<p>${escapeHTML(
                data ||
                "No AI report generated."
            )}</p>`;

        return;
    }


    const sections = [

        [
            "executive_summary",
            "Executive Summary"
        ],

        [
            "dataset_overview",
            "Dataset Overview"
        ],

        [
            "data_quality",
            "Data Quality"
        ],

        [
            "key_findings",
            "Key Findings"
        ],

        [
            "statistical_findings",
            "Statistical Findings"
        ],

        [
            "anomaly_analysis",
            "Anomaly Analysis"
        ],

        [
            "correlation_analysis",
            "Correlation Analysis"
        ],

        [
            "trend_analysis",
            "Trend Analysis"
        ],

        [
            "business_insights",
            "Business Insights"
        ],

        [
            "recommendations",
            "Recommendations"
        ]
    ];


    let html = "";


    sections.forEach(
        ([key, title]) => {

            if (
                data[key] === undefined ||
                data[key] === null
            ) {
                return;
            }


            html += `

                <div class="ai-report-section">

                    <h4>
                        ${escapeHTML(title)}
                    </h4>

                    ${formatAIContent(
                        data[key]
                    )}

                </div>

            `;
        }
    );


    if (!html) {

        html = `
            <div class="ai-report-section">
                ${formatAIContent(data)}
            </div>
        `;
    }


    container.innerHTML =
        html;
}


function formatAIContent(
    value
) {

    if (
        value === null ||
        value === undefined
    ) {
        return "";
    }


    if (Array.isArray(value)) {

        return `
            <ul>

                ${
                    value.map(
                        item =>
                            `<li>${escapeHTML(
                                typeof item === "object"
                                    ? JSON.stringify(item)
                                    : item
                            )}</li>`
                    ).join("")
                }

            </ul>
        `;
    }


    if (
        typeof value === "object"
    ) {

        return `

            <ul>

                ${
                    Object.entries(value)
                        .map(
                            ([key, item]) => `
                                <li>

                                    <strong>
                                        ${escapeHTML(key)}:
                                    </strong>

                                    ${escapeHTML(
                                        typeof item === "object"
                                            ? JSON.stringify(item)
                                            : item
                                    )}

                                </li>
                            `
                        )
                        .join("")
                }

            </ul>

        `;
    }


    return `
        <p>
            ${escapeHTML(value)}
        </p>
    `;
}


/* =====================================================
   ANALYSIS
===================================================== */

function renderAnalysisResults(
    analysis
) {

    if (!analysis) {
        return;
    }


    if (analysis.numeric) {

        renderNumericAnalysis(
            analysis.numeric
        );
    }


    if (analysis.categorical) {

        renderCategoricalAnalysis(
            analysis.categorical
        );
    }


    if (analysis.correlations) {

        renderCorrelationAnalysis(
            analysis.correlations
        );
    }


    if (analysis.time_series) {

        renderTimeSeriesAnalysis(
            analysis.time_series
        );
    }
}


function renderNumericAnalysis(
    data
) {

    const container =
        document.getElementById(
            "numericAnalysis"
        );


    if (!container) {
        return;
    }


    if (
        !data ||
        !Object.keys(data).length
    ) {

        container.innerHTML =
            "<p>No numeric analysis available.</p>";

        return;
    }


    let html = `

        <div class="table-wrapper">

            <table>

                <thead>

                    <tr>

                        <th>Column</th>
                        <th>Count</th>
                        <th>Mean</th>
                        <th>Median</th>
                        <th>Min</th>
                        <th>Max</th>
                        <th>Std</th>

                    </tr>

                </thead>

                <tbody>

    `;


    Object.entries(data).forEach(
        ([column, values]) => {

            html += `

                <tr>

                    <td>
                        ${escapeHTML(column)}
                    </td>

                    <td>
                        ${formatValue(values.count)}
                    </td>

                    <td>
                        ${formatValue(values.mean)}
                    </td>

                    <td>
                        ${formatValue(values.median)}
                    </td>

                    <td>
                        ${formatValue(values.min)}
                    </td>

                    <td>
                        ${formatValue(values.max)}
                    </td>

                    <td>
                        ${formatValue(values.std)}
                    </td>

                </tr>

            `;
        }
    );


    html += `

                </tbody>

            </table>

        </div>

    `;


    container.innerHTML =
        html;
}


function renderCategoricalAnalysis(
    data
) {

    const container =
        document.getElementById(
            "categoricalAnalysis"
        );


    if (!container) {
        return;
    }


    if (
        !data ||
        !Object.keys(data).length
    ) {

        container.innerHTML =
            "<p>No categorical analysis available.</p>";

        return;
    }


    let html = "";


    Object.entries(data).forEach(
        ([column, values]) => {

            html += `

                <div class="stat-card">

                    <h4>
                        ${escapeHTML(column)}
                    </h4>

                    <p>
                        Unique values:
                        ${formatValue(
                            values.unique_values
                        )}
                    </p>

                </div>

            `;
        }
    );


    container.innerHTML = `

        <div class="statistics-grid">

            ${html}

        </div>

    `;
}


function renderCorrelationAnalysis(
    data
) {

    const container =
        document.getElementById(
            "correlationAnalysis"
        );


    if (!container) {
        return;
    }


    if (
        !data ||
        !Object.keys(data).length
    ) {

        container.innerHTML =
            "<p>No correlation analysis available.</p>";

        return;
    }


    let html = `

        <div class="table-wrapper">

            <table>

                <thead>

                    <tr>

                        <th>Variable</th>
                        <th>Correlation</th>

                    </tr>

                </thead>

                <tbody>

    `;


    Object.entries(data).forEach(
        ([key, value]) => {

            html += `

                <tr>

                    <td>
                        ${escapeHTML(key)}
                    </td>

                    <td>
                        ${formatValue(value)}
                    </td>

                </tr>

            `;
        }
    );


    html += `

                </tbody>

            </table>

        </div>

    `;


    container.innerHTML =
        html;
}


function renderTimeSeriesAnalysis(
    data
) {

    const container =
        document.getElementById(
            "timeSeriesAnalysis"
        );


    if (!container) {
        return;
    }


    if (
        !data ||
        !Object.keys(data).length
    ) {

        container.innerHTML =
            "<p>No time-series analysis available.</p>";

        return;
    }


    let html = "";


    Object.entries(data).forEach(
        ([key, value]) => {

            html += `

                <div class="stat-card">

                    <h4>
                        ${escapeHTML(key)}
                    </h4>

                    <pre>
${escapeHTML(
    JSON.stringify(
        value,
        null,
        2
    )
)}
                    </pre>

                </div>

            `;
        }
    );


    container.innerHTML = `

        <div class="statistics-grid">

            ${html}

        </div>

    `;
}


/* =====================================================
   AGENT WORKFLOW
===================================================== */

function renderAgentWorkflow(
    actions
) {

    const container =
        document.getElementById(
            "agentWorkflow"
        );


    if (!container) {
        return;
    }


    if (!Array.isArray(actions)) {

        container.innerHTML =
            "<p>No agent workflow available.</p>";

        return;
    }


    container.innerHTML = `

        <div class="workflow-list">

            ${
                actions.map(
                    (action, index) => {

                        const name =
                            typeof action === "string"
                                ? action
                                : action.action ||
                                  action.tool ||
                                  action.name ||
                                  "Action";


                        const args =
                            typeof action === "object"
                                ? action.arguments ||
                                  action.args ||
                                  ""
                                : "";


                        return `

                            <div class="workflow-item">

                                <div class="workflow-number">
                                    ${index + 1}
                                </div>

                                <div class="workflow-content">

                                    <strong>
                                        ${escapeHTML(name)}
                                    </strong>

                                    <span>
                                        ${
                                            args
                                                ? escapeHTML(
                                                    JSON.stringify(args)
                                                )
                                                : "Action executed successfully."
                                        }
                                    </span>

                                </div>

                            </div>

                        `;
                    }
                ).join("")
            }

        </div>

    `;
}


/* =====================================================
   TOOL RESULTS
===================================================== */

function renderToolResults(
    results
) {

    const container =
        document.getElementById(
            "toolResults"
        );


    if (!container) {
        return;
    }


    if (
        !results ||
        typeof results !== "object"
    ) {

        container.innerHTML =
            "<p>No tool results available.</p>";

        return;
    }


    let html = "";


    Object.entries(results).forEach(
        ([tool, result]) => {

            html += `

                <div class="stat-card">

                    <h4>
                        ${escapeHTML(tool)}
                    </h4>

                    <pre>
${escapeHTML(
    JSON.stringify(
        result,
        null,
        2
    )
)}
                    </pre>

                </div>

            `;
        }
    );


    container.innerHTML = `

        <div class="statistics-grid">

            ${html}

        </div>

    `;
}


/* =====================================================
   CHARTS
===================================================== */

function renderCharts(
    charts
) {

    const container =
        document.getElementById(
            "chartsContainer"
        );


    if (!container) {
        return;
    }


    if (
        !Array.isArray(charts) ||
        !charts.length
    ) {

        container.innerHTML =
            "<p>No charts generated.</p>";

        return;
    }


    container.innerHTML = `

        ${
            charts.map(
                chart => {

                    const filename =
                        typeof chart === "string"
                            ? chart
                            : chart.filename;


                    const title =
                        typeof chart === "object"
                            ? chart.type ||
                              "Generated Chart"
                            : "Generated Chart";


                    const reason =
                        typeof chart === "object"
                            ? chart.reason || ""
                            : "";


                    return `

                        <div class="chart-card">

                            <h4>
                                ${escapeHTML(title)}
                            </h4>

                            <img
                                src="${API_URL}/reports/${encodeURIComponent(filename)}"
                                alt="${escapeHTML(title)}"
                            >

                            ${
                                reason
                                    ? `
                                        <p>
                                            ${escapeHTML(reason)}
                                        </p>
                                    `
                                    : ""
                            }

                        </div>

                    `;
                }
            ).join("")
        }

    `;
}


/* =====================================================
   HISTORY
===================================================== */

async function loadHistory() {

    const container =
        document.getElementById(
            "historyContainer"
        );


    if (!container) {
        return;
    }


    try {

        const response =
            await fetch(
                `${API_URL}/report-history`
            );


        const data =
            await response.json();


        if (!response.ok) {

            throw new Error(
                data.detail ||
                "History unavailable."
            );
        }


        const history =
            Array.isArray(data)
                ? data
                : data.reports || [];


        renderHistory(history);


    } catch (error) {

        console.error(error);

        container.innerHTML = `

            <div class="message error show">

                Unable to load report history.

            </div>

        `;
    }
}


function renderHistory(
    history
) {

    const container =
        document.getElementById(
            "historyContainer"
        );


    if (!container) {
        return;
    }


    if (!history.length) {

        container.innerHTML = `

            <div class="report-empty">

                <div class="empty-icon">
                    ◷
                </div>

                <h3>
                    No reports yet
                </h3>

                <p>
                    Generate your first AI report
                    to see it here.
                </p>

            </div>

        `;

        return;
    }


    container.innerHTML = `

        <div class="history-list">

            ${
                history.map(
                    item => {

                        const filename =
                            item.filename || "";

                        const date =
                            item.created_at || "";

                        const id =
                            item.id || "";


                        return `

                            <div class="history-item">

                                <div class="history-main">

                                    <strong>
                                        ${escapeHTML(filename)}
                                    </strong>

                                    <span>
                                        Report #${escapeHTML(id)}
                                        &nbsp; • &nbsp;
                                        ${escapeHTML(date)}
                                    </span>

                                </div>


                                <div class="history-actions">

                                    <button
                                        class="download-btn pdf"
                                        onclick="downloadHistoryPDF('${escapeJS(filename)}')"
                                    >
                                        PDF
                                    </button>

                                </div>

                            </div>

                        `;
                    }
                ).join("")
            }

        </div>

    `;
}


function downloadHistoryPDF(
    filename
) {

    if (!filename) {
        return;
    }


    window.open(
        `${API_URL}/download-report/${encodeURIComponent(filename)}`,
        "_blank"
    );
}


/* =====================================================
   DOWNLOADS
===================================================== */

function enableDownloads() {

    const pdfButton =
        document.getElementById(
            "downloadPdfButton"
        );

    const excelButton =
        document.getElementById(
            "downloadExcelButton"
        );


    if (pdfButton) {

        pdfButton.disabled = false;

        pdfButton.onclick =
            downloadPDF;
    }


    if (excelButton) {

        excelButton.disabled = false;

        excelButton.onclick =
            downloadExcel;
    }
}


function downloadPDF() {

    if (!currentFilename) {
        return;
    }


    window.open(
        `${API_URL}/download-report/${encodeURIComponent(currentFilename)}`,
        "_blank"
    );
}


function downloadExcel() {

    if (!currentFilename) {
        return;
    }


    window.open(
        `${API_URL}/download-excel/${encodeURIComponent(currentFilename)}`,
        "_blank"
    );
}


/* =====================================================
   KPI
===================================================== */

function updateKPIs(
    data
) {

    if (!data) {
        return;
    }


    const dataset =
        data.dataset || data;


    setText(
        "kpiRows",
        dataset.rows ?? "—"
    );


    setText(
        "kpiColumns",
        dataset.columns ?? "—"
    );


    setText(
        "kpiMissing",
        dataset.missing_values ?? "—"
    );


    setText(
        "kpiDuplicates",
        dataset.duplicate_rows ?? "—"
    );


    if (
        Array.isArray(data.actions)
    ) {

        setText(
            "kpiSteps",
            data.actions.length
        );
    }


    if (
        Array.isArray(data.charts)
    ) {

        setText(
            "kpiCharts",
            data.charts.length
        );
    }
}


/* =====================================================
   UI
===================================================== */

function showReport() {

    const empty =
        document.getElementById(
            "reportEmpty"
        );

    const content =
        document.getElementById(
            "reportContent"
        );


    if (empty) {
        empty.style.display = "none";
    }


    if (content) {
        content.classList.add(
            "active"
        );
    }
}


function resetReport() {

    const empty =
        document.getElementById(
            "reportEmpty"
        );

    const content =
        document.getElementById(
            "reportContent"
        );


    if (empty) {
        empty.style.display = "block";
    }


    if (content) {
        content.classList.remove(
            "active"
        );
    }


    const sections = [

        "datasetOverview",
        "csvPreview",
        "insights",
        "numericAnalysis",
        "categoricalAnalysis",
        "correlationAnalysis",
        "timeSeriesAnalysis",
        "agentWorkflow",
        "toolResults",
        "aiReport",
        "chartsContainer"

    ];


    sections.forEach(
        id => {

            const element =
                document.getElementById(
                    id
                );


            if (element) {
                element.innerHTML = "";
            }
        }
    );
}


function resetAgentUI() {

    stopProgressPolling();


    setProgress(
        0,
        8,
        "Preparing AI agent..."
    );


    setAgentStatus(
        "",
        "Starting"
    );


    updateAgentActivity(
        "Initializing autonomous workflow..."
    );


    const pdf =
        document.getElementById(
            "downloadPdfButton"
        );

    const excel =
        document.getElementById(
            "downloadExcelButton"
        );


    if (pdf) {
        pdf.disabled = true;
    }


    if (excel) {
        excel.disabled = true;
    }
}


function enableActionButtons() {

    [
        "previewButton",
        "statisticsButton",
        "agentButton"
    ].forEach(
        id => {

            const button =
                document.getElementById(
                    id
                );


            if (button) {
                button.disabled = false;
            }
        }
    );
}


function setAgentStatus(
    type,
    text
) {

    const badge =
        document.getElementById(
            "agentStatusBadge"
        );


    if (!badge) {
        return;
    }


    badge.className =
        "agent-status-badge";


    if (type) {
        badge.classList.add(type);
    }


    badge.textContent =
        text;
}


function setProgress(
    step,
    total,
    message
) {

    const bar =
        document.getElementById(
            "agentProgressBar"
        );

    const text =
        document.getElementById(
            "agentProgressText"
        );


    const safeTotal =
        total > 0
            ? total
            : 1;


    const percentage =
        Math.min(
            100,
            Math.max(
                0,
                (step / safeTotal) * 100
            )
        );


    if (bar) {

        bar.style.width =
            `${percentage}%`;
    }


    if (text) {

        text.textContent =
            `${step} / ${total} steps`;
    }
}


function updateAgentActivity(
    message
) {

    const element =
        document.getElementById(
            "agentActivity"
        );


    if (element) {

        element.textContent =
            message || "";
    }
}


function showMessage(
    id,
    message,
    type = "info"
) {

    const element =
        document.getElementById(id);


    if (!element) {
        return;
    }


    element.className =
        `message ${type} show`;


    element.textContent =
        message;
}


function setButtonLoading(
    button,
    loading,
    text
) {

    if (!button) {
        return;
    }


    button.disabled =
        loading;


    if (loading) {

        button.innerHTML =
            `<span class="loading"></span>${text}`;

    } else {

        button.textContent =
            text;
    }
}


/* =====================================================
   HELPERS
===================================================== */

function setText(
    id,
    value
) {

    const element =
        document.getElementById(id);


    if (element) {

        element.textContent =
            value;
    }
}


function formatValue(
    value
) {

    if (
        value === null ||
        value === undefined
    ) {
        return "—";
    }


    if (
        typeof value === "number"
    ) {

        return Number.isInteger(value)
            ? value.toLocaleString()
            : value.toFixed(2);
    }


    return escapeHTML(value);
}


function escapeHTML(
    value
) {

    if (
        value === null ||
        value === undefined
    ) {
        return "";
    }


    return String(value)
        .replace(
            /&/g,
            "&amp;"
        )
        .replace(
            /</g,
            "&lt;"
        )
        .replace(
            />/g,
            "&gt;"
        )
        .replace(
            /"/g,
            "&quot;"
        )
        .replace(
            /'/g,
            "&#039;"
        );
}


function escapeJS(
    value
) {

    return String(value)
        .replace(
            /\\/g,
            "\\\\"
        )
        .replace(
            /'/g,
            "\\'"
        );
}


/* =====================================================
   CLEANUP
===================================================== */

window.addEventListener(
    "beforeunload",
    () => {

        stopProgressPolling();

    }
);