const API_BASE = "http://127.0.0.1:8000";

async function uploadFiles() {
    const files = document.getElementById("fileInput").files;
    if (!files.length) return alert("Select files to upload.");

    const uploadBtn = document.getElementById("uploadBtn");
    if (uploadBtn) uploadBtn.disabled = true;
    const statusEl = document.getElementById("uploadStatus");
    if (statusEl) statusEl.innerText = "Uploading...";

    const formData = new FormData();
    for (let file of files) formData.append("files", file);

    try {
        const res = await fetch(`${API_BASE}/upload`, { method: "POST", body: formData });
        if (!res.ok) {
            const text = await res.text();
            if (statusEl) statusEl.innerText = `Upload failed: ${res.status} ${text}`;
            return;
        }
        const data = await res.json();
        if (statusEl) statusEl.innerText = JSON.stringify(data, null, 2);
    } catch (err) {
        if (statusEl) statusEl.innerText = "Upload failed (network error).";
        console.error("Upload error:", err);
    } finally {
        if (uploadBtn) uploadBtn.disabled = false;
    }
}

async function askQuestion() {
    const questionInput = document.getElementById("questionInput");
    const askBtn = document.getElementById("askBtn");
    const chatBox = document.getElementById("chatBox");
    const question = questionInput.value.trim();
    if (!question) return;

    if (askBtn) askBtn.disabled = true;
    chatBox.innerHTML += `<div class="user-msg"><b>You:</b> ${escapeHtml(question)}</div>`;
    questionInput.value = "";
    const loadingId = `loading-${Date.now()}`;
    chatBox.innerHTML += `<div id="${loadingId}" class="assistant-msg"><i>Thinking...</i></div>`;
    chatBox.scrollTop = chatBox.scrollHeight;

    try {
        const res = await fetch(`${API_BASE}/query`, {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({ question })
        });
        if (!res.ok) {
            const text = await res.text();
            document.getElementById(loadingId).innerHTML = `<b>Assistant:</b> Error: ${res.status} ${escapeHtml(text)}`;
            return;
        }
        const data = await res.json();
        document.getElementById(loadingId).outerHTML = `<div class="assistant-msg"><b>Assistant:</b> ${escapeHtml(data.answer)}</div>`;
        if (data.sources && data.sources.length) {
            const s = data.sources.map(src => `<div class="sources">${escapeHtml(src)}</div>`).join("");
            chatBox.innerHTML += s;
        }
        chatBox.scrollTop = chatBox.scrollHeight;
    } catch (err) {
        document.getElementById(loadingId).innerHTML = `<b>Assistant:</b> Request failed.`;
        console.error("Query error:", err);
    } finally {
        if (askBtn) askBtn.disabled = false;
    }
}

function escapeHtml(text) {
    if (typeof text !== "string") return text;
    return text
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;");
}

function clearChat() {
    const chatBox = document.getElementById("chatBox");
    if (chatBox) chatBox.innerHTML = "";
}

async function getReport() {
    const reportBtn = document.getElementById("reportBtn");
    if (reportBtn) reportBtn.disabled = true;
    const reportEl = document.getElementById("report");
    if (reportEl) reportEl.innerText = "Fetching report...";
    try {
        const res = await fetch(`${API_BASE}/report`);
        if (!res.ok) {
            const text = await res.text();
            if (reportEl) reportEl.innerText = `Failed: ${res.status} ${text}`;
            return;
        }
        const data = await res.json();
        if (reportEl) reportEl.innerText = JSON.stringify(data, null, 2);
    } catch (err) {
        if (reportEl) reportEl.innerText = "Failed to fetch report.";
        console.error("Report error:", err);
    } finally {
        if (reportBtn) reportBtn.disabled = false;
    }
}
