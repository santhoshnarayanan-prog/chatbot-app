const API = "http://127.0.0.1:8000";

// ── Toast ──────────────────────────────────────────────────────────────────────
function showToast(msg, type = "default") {
    const t = document.getElementById("toast");
    t.textContent = msg;
    t.className = `toast show ${type}`;
    clearTimeout(t._timer);
    t._timer = setTimeout(() => t.classList.remove("show"), 3200);
}

// ── Status helpers ─────────────────────────────────────────────────────────────
function setStatus(id, msg, type = "") {
    const el = document.getElementById(id);
    el.className = `status-msg ${type}`;
    el.innerHTML = msg;
}

// ── Load sources list on page load ─────────────────────────────────────────────
async function loadSources() {
    try {
        const res = await fetch(`${API}/knowledge/sources`);
        const sources = await res.json();

        const list = document.getElementById("sources-list");
        document.getElementById("source-count").textContent = sources.length;

        if (!sources.length) {
            list.innerHTML = `<div class="empty-state">No sources yet. Add documents or websites.</div>`;
            return;
        }

        list.innerHTML = sources.map(s => `
            <div class="source-item" id="source-${s.id}">
                <div class="source-icon ${s.type === 'document' ? 'doc' : 'web'}">
                    ${s.type === 'document' ? docIcon() : webIcon()}
                </div>
                <div class="source-info">
                    <div class="source-name" title="${esc(s.name)}">${esc(s.name)}</div>
                    <div class="source-meta">${esc(s.source)} &bull; ${formatDate(s.added_at)}</div>
                </div>
                <span class="source-chunks">${s.chunks} chunks</span>
                <button class="delete-btn" onclick="deleteSource(${s.id})" title="Remove">
                    ${trashIcon()}
                </button>
            </div>
        `).join("");
    } catch (e) {
        document.getElementById("sources-list").innerHTML =
            `<div class="empty-state" style="color:#dc2626">Could not load sources. Is the server running?</div>`;
    }
}

// ── Upload document ────────────────────────────────────────────────────────────
function handleDrop(event) {
    event.preventDefault();
    document.getElementById("drop-zone").classList.remove("drag-over");
    const file = event.dataTransfer.files[0];
    if (file) uploadFile(file);
}

async function uploadFile(file) {
    if (!file) return;

    const ext = file.name.split(".").pop().toLowerCase();
    if (!["pdf", "docx", "txt"].includes(ext)) {
        showToast("Only PDF, DOCX, TXT supported", "error");
        return;
    }

    setStatus("upload-status", `<span class="spinner"></span>Uploading ${esc(file.name)}…`, "loading");

    const form = new FormData();
    form.append("file", file);

    try {
        const res = await fetch(`${API}/knowledge/upload`, { method: "POST", body: form });
        const data = await res.json();

        if (!res.ok) throw new Error(data.detail || "Upload failed");

        setStatus("upload-status", `✓ Added — ${data.chunks} chunks indexed`, "success");
        showToast(`"${data.name}" indexed successfully`, "success");
        loadSources();
    } catch (e) {
        setStatus("upload-status", `✗ ${e.message}`, "error");
        showToast(e.message, "error");
    }

    // Reset file input so same file can be re-uploaded
    document.getElementById("file-input").value = "";
}

// ── Add website ────────────────────────────────────────────────────────────────
async function addWebsite() {
    const url  = document.getElementById("website-url").value.trim();
    const name = document.getElementById("website-name").value.trim();

    if (!url || !name) {
        showToast("Please enter both URL and a display name", "error");
        return;
    }

    const btn = document.querySelector(".btn-primary");
    btn.disabled = true;
    setStatus("website-status", `<span class="spinner"></span>Crawling ${esc(url)}…`, "loading");

    try {
        const res = await fetch(`${API}/knowledge/website`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ url, name }),
        });
        const data = await res.json();

        if (!res.ok) throw new Error(data.detail || "Crawl failed");

        setStatus("website-status", `✓ Crawled — ${data.chunks} chunks indexed`, "success");
        showToast(`"${data.name}" crawled successfully`, "success");
        document.getElementById("website-url").value  = "";
        document.getElementById("website-name").value = "";
        loadSources();
    } catch (e) {
        setStatus("website-status", `✗ ${e.message}`, "error");
        showToast(e.message, "error");
    }

    btn.disabled = false;
}

// ── Delete source ──────────────────────────────────────────────────────────────
async function deleteSource(id) {
    if (!confirm("Remove this knowledge source? The bot will no longer use it.")) return;

    try {
        const res = await fetch(`${API}/knowledge/sources/${id}`, { method: "DELETE" });
        if (!res.ok) throw new Error("Delete failed");
        document.getElementById(`source-${id}`)?.remove();
        const remaining = document.querySelectorAll(".source-item").length;
        document.getElementById("source-count").textContent = remaining;
        if (!remaining) {
            document.getElementById("sources-list").innerHTML =
                `<div class="empty-state">No sources yet. Add documents or websites.</div>`;
        }
        showToast("Source removed", "default");
    } catch (e) {
        showToast("Failed to delete source", "error");
    }
}

// ── Helpers ────────────────────────────────────────────────────────────────────
function esc(s) {
    return String(s)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;");
}

function formatDate(iso) {
    return new Date(iso).toLocaleDateString("en-IN", { day: "numeric", month: "short", year: "numeric" });
}

function docIcon() {
    return `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>`;
}

function webIcon() {
    return `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg>`;
}

function trashIcon() {
    return `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/><path d="M10 11v6"/><path d="M14 11v6"/><path d="M9 6V4a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2"/></svg>`;
}

// Boot
loadSources();
