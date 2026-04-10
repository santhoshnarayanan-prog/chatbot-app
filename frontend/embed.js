/**
 * MCUBE LUNA AI – Embeddable Chat Widget
 *
 * Drop ONE line into any MCUBE panel page:
 *   <script src="http://YOUR_SERVER/embed.js"></script>
 *
 * That's it. A floating chat bubble appears in the bottom-right corner.
 * Clicking it opens/closes the LUNA chat interface in an iframe.
 */
(function () {
    "use strict";

    // ── Config ─────────────────────────────────────────────────────────────────
    // Derive the server base URL from the script tag's own src attribute
    var scriptEl  = document.currentScript || (function () {
        var scripts = document.getElementsByTagName("script");
        return scripts[scripts.length - 1];
    })();
    var scriptSrc = scriptEl ? scriptEl.src : "";
    var BASE_URL  = scriptSrc ? scriptSrc.replace(/\/embed\.js.*$/, "") : "http://127.0.0.1:8000";
    var CHAT_URL  = BASE_URL + "/";     // FastAPI serves index.html at /

    var BUBBLE_SIZE  = 56;
    var WIDGET_W     = 390;
    var WIDGET_H     = 620;
    var MARGIN       = 20;
    var Z            = 2147483640;

    // ── Prevent double-injection ───────────────────────────────────────────────
    if (document.getElementById("mcube-luna-bubble")) return;

    // ── Inject styles ──────────────────────────────────────────────────────────
    var style = document.createElement("style");
    style.textContent = [
        "#mcube-luna-bubble {",
        "  position: fixed;",
        "  bottom: " + MARGIN + "px;",
        "  right: " + MARGIN + "px;",
        "  width: " + BUBBLE_SIZE + "px;",
        "  height: " + BUBBLE_SIZE + "px;",
        "  border-radius: 50%;",
        "  background: linear-gradient(135deg, #2563eb, #3b82f6);",
        "  box-shadow: 0 4px 20px rgba(37,99,235,0.45);",
        "  cursor: pointer;",
        "  z-index: " + Z + ";",
        "  display: flex;",
        "  align-items: center;",
        "  justify-content: center;",
        "  transition: transform 0.2s, box-shadow 0.2s;",
        "  border: none;",
        "  outline: none;",
        "}",
        "#mcube-luna-bubble:hover {",
        "  transform: scale(1.08);",
        "  box-shadow: 0 6px 28px rgba(37,99,235,0.55);",
        "}",
        "#mcube-luna-bubble svg { pointer-events: none; }",
        "#mcube-luna-badge {",
        "  position: absolute;",
        "  top: 2px; right: 2px;",
        "  width: 14px; height: 14px;",
        "  background: #22c55e;",
        "  border: 2px solid white;",
        "  border-radius: 50%;",
        "}",
        "#mcube-luna-container {",
        "  position: fixed;",
        "  bottom: " + (MARGIN + BUBBLE_SIZE + 12) + "px;",
        "  right: " + MARGIN + "px;",
        "  width: " + WIDGET_W + "px;",
        "  height: " + WIDGET_H + "px;",
        "  border-radius: 20px;",
        "  overflow: hidden;",
        "  box-shadow: 0 12px 48px rgba(0,0,0,0.22);",
        "  z-index: " + (Z - 1) + ";",
        "  display: none;",
        "  transform: scale(0.92) translateY(16px);",
        "  transform-origin: bottom right;",
        "  opacity: 0;",
        "  transition: transform 0.25s cubic-bezier(.34,1.56,.64,1), opacity 0.2s ease;",
        "}",
        "#mcube-luna-container.open {",
        "  display: block;",
        "}",
        "#mcube-luna-container.animate {",
        "  transform: scale(1) translateY(0);",
        "  opacity: 1;",
        "}",
        "#mcube-luna-frame {",
        "  width: 100%; height: 100%;",
        "  border: none;",
        "}",
    ].join("\n");
    document.head.appendChild(style);

    // ── Bubble button ──────────────────────────────────────────────────────────
    var bubble = document.createElement("button");
    bubble.id = "mcube-luna-bubble";
    bubble.setAttribute("aria-label", "Open MCUBE LUNA AI chat");
    bubble.innerHTML = [
        // Chat icon when closed
        '<svg id="mcube-icon-chat" width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">',
        '<path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>',
        '</svg>',
        // Close icon when open (hidden by default)
        '<svg id="mcube-icon-close" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2.5" stroke-linecap="round" style="display:none">',
        '<line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>',
        '</svg>',
        // Online indicator
        '<span id="mcube-luna-badge"></span>',
    ].join("");
    document.body.appendChild(bubble);

    // ── Widget iframe container ────────────────────────────────────────────────
    var container = document.createElement("div");
    container.id = "mcube-luna-container";
    container.innerHTML = '<iframe id="mcube-luna-frame" src="' + CHAT_URL + '" allow="microphone" title="MCUBE LUNA AI"></iframe>';
    document.body.appendChild(container);

    // ── Toggle logic ───────────────────────────────────────────────────────────
    var isOpen = false;

    function openWidget() {
        isOpen = true;
        container.style.display = "block";
        document.getElementById("mcube-icon-chat").style.display  = "none";
        document.getElementById("mcube-icon-close").style.display = "block";
        // Trigger animation on next frame
        requestAnimationFrame(function () {
            requestAnimationFrame(function () {
                container.classList.add("animate");
            });
        });
    }

    function closeWidget() {
        isOpen = false;
        container.classList.remove("animate");
        document.getElementById("mcube-icon-chat").style.display  = "block";
        document.getElementById("mcube-icon-close").style.display = "none";
        // Wait for animation to finish before hiding
        setTimeout(function () {
            if (!isOpen) container.style.display = "none";
        }, 250);
    }

    bubble.addEventListener("click", function () {
        isOpen ? closeWidget() : openWidget();
    });

    // ── Close on Escape key ────────────────────────────────────────────────────
    document.addEventListener("keydown", function (e) {
        if (e.key === "Escape" && isOpen) closeWidget();
    });

})();
