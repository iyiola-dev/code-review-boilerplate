// ==========================================================================
// Code Review Crew — frontend
// --------------------------------------------------------------------------
// Connects to a deployed ADK agent and streams events into four panels.
// The ADK server assigns an `author` to every event (the sub-agent's name),
// which is how we route output to the right card.
// ==========================================================================

// ---- Config --------------------------------------------------------------
// After you deploy, paste your Cloud Run URL here (no trailing slash).
// Example: "https://code-review-crew-abc123-uc.a.run.app"
const AGENT_URL = "";         // <-- attendees fill this in
const APP_NAME  = "agent";    // must match the folder name next to ui/
const USER_ID   = "workshop-user";

// Map agent names (from agent.py) to the DOM panel IDs.
const AGENT_TO_PANEL = {
  SecurityReviewer:    "security",
  PerformanceReviewer: "performance",
  StyleReviewer:       "style",
  Synthesizer:         "final",
  Critic:              "final",
  Reviser:             "final",
};

// ---- Sample code ---------------------------------------------------------
const SAMPLE = `def login(username, password):
    query = f"SELECT * FROM users WHERE name='{username}' AND pw='{password}'"
    result = db.execute(query)
    for row in result:
        return row`;

// ---- DOM -----------------------------------------------------------------
const codeInput = document.getElementById("code-input");
const reviewBtn = document.getElementById("review-btn");
const sampleBtn = document.getElementById("sample-btn");

sampleBtn.addEventListener("click", () => {
  codeInput.value = SAMPLE;
  codeInput.focus();
});

reviewBtn.addEventListener("click", runReview);

// ---- Main flow -----------------------------------------------------------
async function runReview() {
  const code = codeInput.value.trim();
  if (!code) {
    alert("Paste some code first!");
    return;
  }
  if (!AGENT_URL) {
    alert("AGENT_URL is not set. Edit ui/app.js and paste your Cloud Run URL.");
    return;
  }

  resetPanels();
  reviewBtn.disabled = true;
  reviewBtn.textContent = "crew is reviewing…";

  try {
    const sessionId = await createSession();
    await streamRun(sessionId, code);
  } catch (err) {
    console.error(err);
    setPanel("final", `⚠️ Error: ${err.message}`);
  } finally {
    reviewBtn.disabled = false;
    reviewBtn.textContent = "run the crew →";
    clearWorkingState();
  }
}

// ---- ADK session & streaming --------------------------------------------
async function createSession() {
  // POST /apps/{app}/users/{user}/sessions  → creates with auto ID
  const res = await fetch(
    `${AGENT_URL}/apps/${APP_NAME}/users/${USER_ID}/sessions`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({}),
    }
  );
  if (!res.ok) throw new Error(`Session creation failed: ${res.status}`);
  const data = await res.json();
  return data.id;
}

async function streamRun(sessionId, code) {
  const res = await fetch(`${AGENT_URL}/run_sse`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      appName: APP_NAME,
      userId: USER_ID,
      sessionId: sessionId,
      newMessage: {
        role: "user",
        parts: [{ text: code }],
      },
    }),
  });

  if (!res.ok) throw new Error(`Run failed: ${res.status}`);

  // Parse the SSE stream manually. Each event is `data: {json}\n\n`.
  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { value, done } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });

    // Events are separated by blank lines
    const events = buffer.split("\n\n");
    buffer = events.pop();   // keep any incomplete event in the buffer

    for (const raw of events) {
      if (!raw.startsWith("data:")) continue;
      const json = raw.replace(/^data:\s*/, "").trim();
      if (!json) continue;
      try {
        const event = JSON.parse(json);
        handleEvent(event);
      } catch (e) {
        console.warn("Bad event JSON:", json, e);
      }
    }
  }
}

// ---- Event routing -------------------------------------------------------
function handleEvent(event) {
  const author = event.author;
  const panelId = AGENT_TO_PANEL[author];
  if (!panelId) return;   // ignore events from root/workflow agents

  // Mark this panel as active + working
  markActive(panelId);

  // Extract text from the event's content parts
  const parts = event?.content?.parts ?? [];
  const text = parts.map(p => p.text).filter(Boolean).join("");
  if (!text) return;

  // Writers to the "final" panel (Synthesizer/Critic/Reviser) should REPLACE
  // rather than append — each iteration of the loop produces a new draft.
  if (panelId === "final") {
    setPanel(panelId, text, { author });
  } else {
    setPanel(panelId, text);
  }
}

// ---- DOM helpers ---------------------------------------------------------
function resetPanels() {
  for (const panel of ["security", "performance", "style", "final"]) {
    const el = document.getElementById(`out-${panel}`);
    el.innerHTML = `<p class="placeholder">${
      panel === "final"
        ? "the synthesizer and critic will work here…"
        : "thinking…"
    }</p>`;
    document
      .querySelector(`.agent-card[data-agent="${panel}"]`)
      .classList.remove("active", "working");
  }
}

function clearWorkingState() {
  document.querySelectorAll(".agent-card").forEach(c => c.classList.remove("working"));
}

function markActive(panelId) {
  const card = document.querySelector(`.agent-card[data-agent="${panelId}"]`);
  if (!card) return;
  card.classList.add("active", "working");
}

function setPanel(panelId, text, opts = {}) {
  const el = document.getElementById(`out-${panelId}`);
  const html = renderMarkdownish(text);
  const prefix = opts.author ? `<div class="agent-role" style="margin-bottom:8px">${opts.author}</div>` : "";
  el.innerHTML = prefix + html;
}

// Tiny markdown-ish renderer — ADK agents emit markdown in their text.
// This is intentionally not a full parser; just enough for the demo.
function renderMarkdownish(text) {
  return text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
    .replace(/`([^`]+)`/g, "<code>$1</code>")
    .replace(/^## (.+)$/gm, "<h3>$1</h3>")
    .replace(/^# (.+)$/gm, "<h2>$1</h2>")
    .replace(/\n/g, "<br>");
}
