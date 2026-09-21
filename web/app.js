document.addEventListener("DOMContentLoaded", () => {
  const resumeInput = document.getElementById("resume-input");
  const jdInput = document.getElementById("jd-input");
  const btnLoadSample = document.getElementById("btn-load-sample");
  const btnClear = document.getElementById("btn-clear");
  const btnAudit = document.getElementById("btn-audit");
  const btnTransform = document.getElementById("btn-transform");

  // Quick XYZ
  const quickInput = document.getElementById("quick-bullet-input");
  const btnQuickXyz = document.getElementById("btn-quick-xyz");
  const xyzContainer = document.getElementById("xyz-result-container");
  const xyzResultText = document.getElementById("xyz-result-text");
  const xyzMetricPrompts = document.getElementById("xyz-metric-prompts");

  // Tabs
  const tabBtns = document.querySelectorAll(".tab-btn");
  const tabScorecard = document.getElementById("tab-scorecard");
  const tabPreview = document.getElementById("tab-preview");

  // Overview elements
  const scoreNum = document.getElementById("overall-score-num");
  const scoreCircle = document.getElementById("overall-score-circle");
  const scoreStatus = document.getElementById("overall-status-text");
  const scoreSummaryBody = document.getElementById("score-summary-body");

  // Output Preview
  const outputMarkdown = document.getElementById("output-markdown");
  const btnCopyMarkdown = document.getElementById("btn-copy-markdown");
  const btnPrintPdf = document.getElementById("btn-print-pdf");

  // Tab switching
  tabBtns.forEach(btn => {
    btn.addEventListener("click", () => {
      tabBtns.forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      const target = btn.dataset.tab;
      if (target === "scorecard") {
        tabScorecard.classList.add("active");
        tabPreview.classList.remove("active");
      } else {
        tabScorecard.classList.remove("active");
        tabPreview.classList.add("active");
      }
    });
  });

  // Load sample data
  btnLoadSample.addEventListener("click", async () => {
    try {
      btnLoadSample.textContent = "Loading...";
      const resp = await fetch("/api/sample");
      const data = await resp.json();
      resumeInput.value = data.sample_resume || "";
      jdInput.value = data.sample_jd || "";
      btnLoadSample.textContent = "Loaded Ex-Apple Sample!";
      setTimeout(() => { btnLoadSample.textContent = "Load Ex-Apple PM Sample"; }, 2000);
    } catch (err) {
      console.error("Failed to load sample:", err);
      alert("Error loading sample data.");
      btnLoadSample.textContent = "Load Ex-Apple PM Sample";
    }
  });

  // Clear inputs
  btnClear.addEventListener("click", () => {
    resumeInput.value = "";
    jdInput.value = "";
    scoreNum.textContent = "--";
    scoreStatus.textContent = "Run Audit to Inspect";
    scoreCircle.style.borderColor = "var(--border-color)";
    scoreSummaryBody.textContent = "Paste your resume and target job description on the left, then click Run 5-Rule Audit.";
  });

  // Run Audit
  btnAudit.addEventListener("click", async () => {
    const resume = resumeInput.value.trim();
    const jd = jdInput.value.trim();
    if (!resume) {
      alert("Please paste your resume or rough notes first!");
      return;
    }

    try {
      btnAudit.textContent = "Auditing (5 Rules)...";
      btnAudit.disabled = true;

      const resp = await fetch("/api/audit", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ resume, jd })
      });
      const data = await resp.json();
      renderAuditResults(data);

      // Switch to scorecard tab
      tabBtns[0].click();
    } catch (err) {
      console.error("Audit error:", err);
      alert("Failed to run audit.");
    } finally {
      btnAudit.innerHTML = '<span class="btn-icon">⚡</span> Run 5-Rule Audit';
      btnAudit.disabled = false;
    }
  });

  // Generate Killer Resume
  btnTransform.addEventListener("click", async () => {
    const resume = resumeInput.value.trim();
    const jd = jdInput.value.trim();
    if (!resume) {
      alert("Please paste your resume or rough notes first!");
      return;
    }

    try {
      btnTransform.textContent = "Optimizing Resume...";
      btnTransform.disabled = true;

      const resp = await fetch("/api/transform", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ resume, jd })
      });
      const data = await resp.json();

      outputMarkdown.textContent = data.optimized_markdown || "";
      document.getElementById("preview-score-delta").textContent = 
        `Initial Score: ${data.initial_score}/100 ➔ Optimized Score: ${data.optimized_score}/100`;

      // Switch to preview tab
      tabBtns[1].click();
      renderAuditResults(data.post_audit_details || data.audit_details);
    } catch (err) {
      console.error("Transform error:", err);
      alert("Failed to generate killer resume.");
    } finally {
      btnTransform.innerHTML = '<span class="btn-icon">🚀</span> Generate Killer Résumé';
      btnTransform.disabled = false;
    }
  });

  // Quick Bullet Transformer
  btnQuickXyz.addEventListener("click", async () => {
    const bullet = quickInput.value.trim();
    if (!bullet) return;

    try {
      btnQuickXyz.textContent = "Transforming...";
      const resp = await fetch("/api/clarify", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ bullet })
      });
      const data = await resp.json();

      xyzContainer.classList.remove("hidden");
      xyzResultText.textContent = data.xyz.suggested_xyz;

      let promptsHtml = "";
      for (const [k, v] of Object.entries(data.dimensions || {})) {
        promptsHtml += `
          <div class="metric-prompt-item">
            <strong>${k.replace("_", " ")}:</strong>
            ${v.example}
          </div>
        `;
      }
      xyzMetricPrompts.innerHTML = promptsHtml;
    } catch (err) {
      console.error(err);
    } finally {
      btnQuickXyz.textContent = "Transform Bullet";
    }
  });

  // Copy Markdown
  btnCopyMarkdown.addEventListener("click", () => {
    const text = outputMarkdown.textContent;
    if (!text) return;
    navigator.clipboard.writeText(text).then(() => {
      btnCopyMarkdown.textContent = "Copied to Clipboard!";
      setTimeout(() => { btnCopyMarkdown.textContent = "Copy Markdown"; }, 2000);
    });
  });

  // Print PDF
  btnPrintPdf.addEventListener("click", () => {
    const text = outputMarkdown.textContent;
    if (!text) {
      alert("Generate a killer resume first!");
      return;
    }
    const printWindow = window.open("", "_blank");
    printWindow.document.write(`
      <html>
      <head>
        <title>Selectable ATS Resume</title>
        <style>
          body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; line-height: 1.45; color: #111; max-width: 800px; margin: 40px auto; padding: 0 20px; }
          h1 { font-size: 24px; margin-bottom: 4px; }
          h2 { font-size: 16px; border-bottom: 1px solid #ddd; padding-bottom: 4px; margin-top: 20px; text-transform: uppercase; letter-spacing: 0.05em; }
          h3 { font-size: 14px; margin-bottom: 2px; }
          ul { margin: 6px 0 12px 20px; padding: 0; }
          li { margin-bottom: 4px; font-size: 13px; }
          p { margin: 4px 0; font-size: 13px; }
          pre { white-space: pre-wrap; font-family: inherit; font-size: 13px; }
        </style>
      </head>
      <body>
        <pre>${escapeHtml(text)}</pre>
        <script>
          window.onload = function() { window.print(); }
        </script>
      </body>
      </html>
    `);
    printWindow.document.close();
  });

  function escapeHtml(string) {
    return String(string).replace(/[&<>"'`=\/]/g, function (s) {
      return {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#39;',
        '/': '&#x2F;',
        '`': '&#x60;',
        '=': '&#x3D;'
      }[s];
    });
  }

  function renderAuditResults(data) {
    const score = data.composite_score || 0;
    scoreNum.textContent = score;

    if (score >= 80) {
      scoreCircle.style.borderColor = "var(--accent-green)";
      scoreNum.style.color = "var(--accent-green)";
      scoreStatus.textContent = "KILLER RESUME READY";
      scoreStatus.style.color = "var(--accent-green)";
    } else if (score >= 60) {
      scoreCircle.style.borderColor = "var(--accent-amber)";
      scoreNum.style.color = "var(--accent-amber)";
      scoreStatus.textContent = "NEEDS REFINEMENT";
      scoreStatus.style.color = "var(--accent-amber)";
    } else {
      scoreCircle.style.borderColor = "var(--accent-rose)";
      scoreNum.style.color = "var(--accent-rose)";
      scoreStatus.textContent = "ATS FILTER RISK";
      scoreStatus.style.color = "var(--accent-rose)";
    }

    scoreSummaryBody.textContent = data.executive_summary || "";

    // Rule 1
    const r1 = data.rule_1_readability || {};
    renderBadge("badge-rule-1", r1.score, r1.passed);
    let r1Html = `<div><strong>Readability Status:</strong> ${r1.passed ? 'Passed ATS Parseability Check' : 'Failed Parseability Check'} (${r1.score}/100)</div>`;
    if (r1.strengths && r1.strengths.length) {
      r1Html += `<ul>${r1.strengths.map(s => `<li style="color: #34d399">✓ ${s}</li>`).join('')}</ul>`;
    }
    if (r1.issues && r1.issues.length) {
      r1Html += `<ul>${r1.issues.map(i => `<li style="color: #fb7185">⚠ <strong>${i.code}</strong>: ${i.message} <br><em>Fix:</em> ${i.fix}</li>`).join('')}</ul>`;
    }
    document.getElementById("feedback-rule-1").innerHTML = r1Html;

    // Rule 2
    const r2 = data.rule_2_keyword_mapping || {};
    const r2Pass = r2.status === "SWEET_SPOT";
    renderBadge("badge-rule-2", r2.score, r2Pass);
    let r2Html = `<div><strong>Coverage:</strong> ${r2.coverage_percent || 0}% | <strong>Zone:</strong> ${r2.status || 'N/A'}</div>`;
    r2Html += `<p style="margin-top:4px;">${r2.advice || ''}</p>`;
    if (r2.matched_keywords && r2.matched_keywords.length) {
      r2Html += `<p style="color: #38bdf8; margin-top:4px;"><strong>Mapped Keywords (${r2.matched_keywords.length}):</strong> ${r2.matched_keywords.join(', ')}</p>`;
    }
    if (r2.missing_keywords && r2.missing_keywords.length) {
      r2Html += `<p style="color: #fbbf24; margin-top:4px;"><strong>High-Impact Missing Keywords:</strong> ${r2.missing_keywords.join(', ')}</p>`;
    }
    document.getElementById("feedback-rule-2").innerHTML = r2Html;

    // Rule 3
    const r3 = data.rule_3_human_gate || {};
    const r3Pass = r3.human_defense_gate === "PASSED";
    renderBadge("badge-rule-3", r3.score, r3Pass);
    let r3Html = `<div><strong>Defense Status:</strong> ${r3.human_defense_gate} | Cliches Detected: ${r3.cliche_count || 0}</div>`;
    r3Html += `<p style="margin-top:4px; color:var(--text-secondary);">${r3.insight}</p>`;
    r3Html += `<div style="margin-top:6px; font-size:11px; color:#cbd5e1;"><strong>Human Review Rule:</strong> Never allow AI to invent facts. If you cannot explain the step-by-step implementation in a live technical screen, prune it.</div>`;
    document.getElementById("feedback-rule-3").innerHTML = r3Html;

    // Rule 4
    const r4 = data.rule_4_quantified_impact || {};
    const r4Pass = (r4.quantified_ratio_percent || 0) >= 60;
    renderBadge("badge-rule-4", r4.score, r4Pass);
    let r4Html = `<div><strong>Quantified Bullets:</strong> ${r4.quantified_count || 0} / ${r4.total_bullets_audited || 0} (${r4.quantified_ratio_percent || 0}%)</div>`;
    r4Html += `<p style="margin-top:4px; color:var(--text-secondary);">${r4.insight}</p>`;
    r4Html += `<div style="margin-top:6px; font-size:11px; color: #a7f3d0;">Standard: <em>Accomplished [X], as measured by [Y], by doing [Z]</em> (+75% interview rate).</div>`;
    document.getElementById("feedback-rule-4").innerHTML = r4Html;

    // Rule 5
    const r5 = data.rule_5_prove_ai_skills || {};
    const r5Pass = !!r5.has_proven_ai_skills;
    renderBadge("badge-rule-5", r5.score, r5Pass);
    let r5Html = `<div><strong>AI Proof Status:</strong> ${r5.has_proven_ai_skills ? 'Demonstrated with Project Outcomes' : 'Static Skill or Missing'}</div>`;
    r5Html += `<p style="margin-top:4px;">${r5.advice || ''}</p>`;
    if (r5.proven_bullets_found && r5.proven_bullets_found.length) {
      r5Html += `<div style="margin-top:4px; color: #34d399;"><strong>Proven Bullets:</strong><br>${r5.proven_bullets_found.map(b => `• ${b}`).join('<br>')}</div>`;
    }
    document.getElementById("feedback-rule-5").innerHTML = r5Html;
  }

  function renderBadge(elementId, score, isPass) {
    const badge = document.getElementById(elementId);
    badge.textContent = `${score}/100`;
    badge.className = "rule-score-badge " + (score >= 80 ? "pass" : (score >= 60 ? "warn" : "fail"));
  }
});
