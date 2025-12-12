const API_BASE = "http://127.0.0.1:8000";

async function uploadFiles() {
    const files = document.getElementById("fileInput").files;
    if (!files.length) return alert("Select files to upload.");
    const uploadBtn = document.getElementById("uploadBtn");
    uploadBtn.disabled = true;
    document.getElementById("uploadStatus").innerText = "Uploading...";
    const formData = new FormData();
    for (let file of files) formData.append("files", file);

    try {
        const res = await fetch(`${API_BASE}/upload`, { method: "POST", body: formData });
        if (!res.ok) {
            const text = await res.text();
            document.getElementById("uploadStatus").innerText = `Upload failed: ${res.status} ${text}`;
            return;
        }
        const data = await res.json();
        document.getElementById("uploadStatus").innerText = JSON.stringify(data, null, 2);
    } catch (err) {
        document.getElementById("uploadStatus").innerText = "Upload failed.";
        console.error("upload error", err);
    } finally {
        uploadBtn.disabled = false;
    }
}

async function askQuestion() {
    const questionInput = document.getElementById("questionInput");
    const askBtn = document.getElementById("askBtn");
    const chatBox = document.getElementById("chatBox");
    const question = questionInput.value.trim();
    if (!question) return;
    askBtn.disabled = true;
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
            const s = data.sources.map(s => `<div class="sources">${escapeHtml(s)}</div>`).join("");
            chatBox.innerHTML += s;
        }
        chatBox.scrollTop = chatBox.scrollHeight;
    } catch (err) {
        document.getElementById(loadingId).innerHTML = `<b>Assistant:</b> Request failed.`;
        console.error("ask error", err);
    } finally {
        askBtn.disabled = false;
    }
}

function clearChat() {
    document.getElementById("chatBox").innerHTML = "";
}

async function getReport() {
    try {
        const res = await fetch(`${API_BASE}/report`);
        const data = await res.json();
        document.getElementById("report").innerText = JSON.stringify(data, null, 2);
    } catch (e) {
        document.getElementById("report").innerText = "Failed to fetch report.";
    }
}

function escapeHtml(text) {
    return (text + "")
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;");
}
