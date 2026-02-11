// ✅ Helper show/hide
function show(el) { el.classList.remove("hidden"); }
function hide(el) { el.classList.add("hidden"); }

// ✅ Score grid renderer
function scoreGrid(s) {
  return `
    <div class="grid">
      <div class="metric"><b>Overall</b><br>${s.overall}</div>
      <div class="metric"><b>Clarity</b><br>${s.clarity}</div>
      <div class="metric"><b>Concise</b><br>${s.conciseness}</div>
      <div class="metric"><b>Richness</b><br>${s.richness}</div>
      <div class="metric"><b>Formality</b><br>${s.formality}</div>
    </div>
    <p><b>Avg sentence length:</b> ${s.avg_sentence_len} words</p>
  `;
}

// ✅ Feature table renderer
function featureTable(features) {
  let rows = "";
  for (const [k, v] of Object.entries(features)) {
    rows += `<tr><td>${k}</td><td>${Number(v).toFixed(4)}</td></tr>`;
  }
  return `
    <table>
      <thead><tr><th>Feature</th><th>Value</th></tr></thead>
      <tbody>${rows}</tbody>
    </table>
  `;
}

// =====================
// ✅ TAB SWITCHING (NEW HTML)
// =====================
const tabButtons = document.querySelectorAll(".tab");
const analyzerPanel = document.getElementById("panel-analyzer");
const rewritePanel = document.getElementById("panel-rewrite");

tabButtons.forEach(btn => {
  btn.addEventListener("click", () => {
    tabButtons.forEach(b => b.classList.remove("active"));
    btn.classList.add("active");

    const tab = btn.dataset.tab;
    if (tab === "analyzer") {
      analyzerPanel.classList.add("active");
      rewritePanel.classList.remove("active");
    } else {
      rewritePanel.classList.add("active");
      analyzerPanel.classList.remove("active");
    }
  });
});

// =====================
// ✅ ANALYZE
// =====================
const analyzeBtn = document.getElementById("analyzeBtn");
const analyzeText = document.getElementById("analyzeText");
const analyzeResult = document.getElementById("analyzeResult");

analyzeBtn.addEventListener("click", async () => {
  hide(analyzeResult);

  const text = analyzeText.value.trim();
  if (!text) {
    analyzeResult.innerHTML = "❌ Please paste some text.";
    show(analyzeResult);
    return;
  }

  analyzeResult.innerHTML = "⏳ Analyzing...";
  show(analyzeResult);

  try {
    const res = await fetch("/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text })
    });

    const data = await res.json();

    if (!data.ok) {
      analyzeResult.innerHTML = `❌ ${data.error || "Error"} (tokens: ${data.tokens ?? "?"})`;
      return;
    }

    // ✅ If your backend returns summary + scores + coach tips, show them
    // Otherwise fallback to probability display
    if (data.scores) {
      const summaryBlock = data.summary
        ? `<h3>Summary</h3><div class="summary">${data.summary}</div>`
        : "";

      const flags = (data.coach?.flags || []).map(f => `<li>${f}</li>`).join("");
      const tips  = (data.coach?.tips  || []).map(t => `<li>${t}</li>`).join("");

      analyzeResult.innerHTML = `
        ${summaryBlock}
        <h2>Writing Scores</h2>
        ${scoreGrid(data.scores)}
        <h3>Flags</h3>
        <ul>${flags || "<li>None</li>"}</ul>
        <h3>Suggestions</h3>
        <ul>${tips || "<li>None</li>"}</ul>

        <details style="margin-top:12px;">
          <summary>Show technical details</summary>
          <p><b>Model style score:</b> ${(data.style_score * 100).toFixed(1)}%</p>
          ${featureTable(data.features)}
        </details>
      `;
    } else {
      // ✅ Simple fallback (for minimal backend)
      analyzeResult.innerHTML = `
        <h3>Result</h3>
        <p><b>Model style probability:</b> ${(data.probability * 100).toFixed(1)}%</p>
        <details style="margin-top:12px;">
          <summary>Show extracted features</summary>
          ${featureTable(data.features)}
        </details>
      `;
    }

  } catch (e) {
    analyzeResult.innerHTML = `❌ Error: ${e}`;
  }
});

// =====================
// ✅ COMPARE (REWRITE COACH)
// =====================
const compareBtn = document.getElementById("compareBtn");
const originalText = document.getElementById("originalText");
const revisedText = document.getElementById("revisedText");
const compareResult = document.getElementById("compareResult");

compareBtn.addEventListener("click", async () => {
  hide(compareResult);

  const original = originalText.value.trim();
  const revised = revisedText.value.trim();

  if (!original || !revised) {
    compareResult.innerHTML = "❌ Please paste both Original and Revised text.";
    show(compareResult);
    return;
  }

  compareResult.innerHTML = "⏳ Comparing...";
  show(compareResult);

  try {
    const res = await fetch("/compare", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ original, revised })
    });

    const data = await res.json();

    if (!data.ok) {
      compareResult.innerHTML = `❌ ${data.error || "Error"}`;
      return;
    }

    // If your backend returns before/after score objects:
    if (data.before && data.after) {
      const b = data.before.scores;
      const a = data.after.scores;
      const d = data.delta;

      compareResult.innerHTML = `
        <h2>Before vs After</h2>

        <h3>Before</h3>
        ${scoreGrid(b)}

        <h3>After</h3>
        ${scoreGrid(a)}

        <h3>Change (After − Before)</h3>
        <ul>
          <li><b>Overall:</b> ${d.overall}</li>
          <li><b>Clarity:</b> ${d.clarity}</li>
          <li><b>Conciseness:</b> ${d.conciseness}</li>
          <li><b>Richness:</b> ${d.richness}</li>
          <li><b>Formality:</b> ${d.formality}</li>
          <li><b>Avg sentence length:</b> ${d.avg_sentence_len}</li>
        </ul>

        <details style="margin-top:12px;">
          <summary>Show technical details</summary>
          <h4>Before Features</h4>
          ${featureTable(data.before.features)}
          <h4>After Features</h4>
          ${featureTable(data.after.features)}
        </details>
      `;
    } else {
      // ✅ Minimal backend compare
      compareResult.innerHTML = `
        <h3>Rewrite Coach</h3>
        <p><b>Original style probability:</b> ${(data.original_prob * 100).toFixed(1)}%</p>
        <p><b>Revised style probability:</b> ${(data.revised_prob * 100).toFixed(1)}%</p>

        <details style="margin-top:12px;">
          <summary>Show features</summary>
          <h4>Original</h4>
          ${featureTable(data.original_features)}
          <h4>Revised</h4>
          ${featureTable(data.revised_features)}
        </details>
      `;
    }

  } catch (e) {
    compareResult.innerHTML = `❌ Error: ${e}`;
  }
});