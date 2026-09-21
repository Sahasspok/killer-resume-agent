// Killer Resume Agent - Client App (QA Hardened)
document.addEventListener("DOMContentLoaded", () => {
  // Input elements
  const resumeInput = document.getElementById("resume-input");
  const jdInput = document.getElementById("jd-input");
  const btnLoadSample = document.getElementById("btn-load-sample");
  const btnLoadSamplePdf = document.getElementById("btn-load-sample-pdf");
  const btnClear = document.getElementById("btn-clear");
  const btnAudit = document.getElementById("btn-audit");
  const btnTransform = document.getElementById("btn-transform");

  // PDF Elements
  const pdfDropzone = document.getElementById("pdf-dropzone");
  const pdfFileInput = document.getElementById("pdf-file-input");
  const dropzonePrompt = document.getElementById("dropzone-prompt");
  const loadedPdfPill = document.getElementById("loaded-pdf-pill");
  const pdfDisplayName = document.getElementById("pdf-display-name");
  const pdfDisplayStats = document.getElementById("pdf-display-stats");
  const btnRemovePdf = document.getElementById("btn-remove-pdf");

  // PDF Diagnostic Elements
  const pdfDiagCard = document.getElementById("pdf-diagnostic-card");
  const pdfAtsBadge = document.getElementById("pdf-ats-badge");
  const pdfDiagSelectable = document.getElementById("pdf-diag-selectable");
  const pdfDiagSize = document.getElementById("pdf-diag-size");
  const pdfDiagPages = document.getElementById("pdf-diag-pages");
  const pdfDiagImages = document.getElementById("pdf-diag-images");
  const pdfWarningBanner = document.getElementById("pdf-warning-banner");
  const resumeTextGroup = document.getElementById("resume-text-group");

  // Mode Toggle Buttons
  const tabModePdf = document.getElementById("tab-mode-pdf");
  const tabModeText = document.getElementById("tab-mode-text");

  // Scorecard / Preview Toggle Buttons
  const tabBtnScorecard = document.getElementById("tab-btn-scorecard");
  const tabBtnPreview = document.getElementById("tab-btn-preview");
  const tabScorecard = document.getElementById("tab-scorecard");
  const tabPreview = document.getElementById("tab-preview");

  // Quick XYZ elements
  const quickInput = document.getElementById("quick-bullet-input");
  const btnQuickXyz = document.getElementById("btn-quick-xyz");
  const xyzContainer = document.getElementById("xyz-result-container");
  const xyzResultText = document.getElementById("xyz-result-text");
  const xyzMetricPrompts = document.getElementById("xyz-metric-prompts");

  // Overview elements
  const scoreNum = document.getElementById("overall-score-num");
  const scoreCircle = document.getElementById("overall-score-circle");
  const scoreStatus = document.getElementById("overall-status-text");
  const scoreSummaryBody = document.getElementById("score-summary-body");

  // Output Preview elements
  const outputMarkdown = document.getElementById("output-markdown");
  const btnCopyMarkdown = document.getElementById("btn-copy-markdown");
  const btnDownloadMd = document.getElementById("btn-download-md");
  const btnPrintPdf = document.getElementById("btn-print-pdf");

  let currentPdfBase64 = null;
  let currentPdfFilename = null;

  // Toast Notification System
  function showToast(message, type = "success") {
    const container = document.getElementById("toast-container");
    if (!container) return;
    const toast = document.createElement("div");
    toast.className = `toast ${type}`;
    const icon = type === "success" ? "✓" : (type === "warning" ? "⚠" : "✕");
    toast.innerHTML = `<span>${icon}</span> <span>${message}</span>`;
    container.appendChild(toast);
    setTimeout(() => {
      toast.style.opacity = "0";
      toast.style.transform = "translateY(-10px)";
      setTimeout(() => toast.remove(), 300);
    }, 3500);
  }

  // Toggle Output Tabs (Scorecard vs Output)
  function setOutputTab(target) {
    if (target === "scorecard") {
      tabBtnScorecard.classList.add("active");
      tabBtnPreview.classList.remove("active");
      tabScorecard.classList.add("active");
      tabPreview.classList.remove("active");
    } else {
      tabBtnPreview.classList.add("active");
      tabBtnScorecard.classList.remove("active");
      tabPreview.classList.add("active");
      tabScorecard.classList.remove("active");
    }
  }

  if (tabBtnScorecard) {
    tabBtnScorecard.addEventListener("click", () => setOutputTab("scorecard"));
  }
  if (tabBtnPreview) {
    tabBtnPreview.addEventListener("click", () => setOutputTab("preview"));
  }

  // Toggle Input Modes (Upload PDF vs Edit/Paste Text)
  function setInputMode(mode) {
    if (mode === "pdf") {
      tabModePdf.classList.add("active");
      tabModeText.classList.remove("active");
      pdfDropzone.style.display = "block";
      if (currentPdfBase64) {
        pdfDiagCard.classList.remove("hidden");
      }
      showToast("Switched to PDF Upload mode", "success");
    } else {
      tabModeText.classList.add("active");
      tabModePdf.classList.remove("active");
      pdfDropzone.style.display = "none";
      pdfDiagCard.classList.add("hidden");
      showToast("Switched to Direct Text Edit mode", "success");
    }
  }

  if (tabModePdf) {
    tabModePdf.addEventListener("click", () => setInputMode("pdf"));
  }
  if (tabModeText) {
    tabModeText.addEventListener("click", () => setInputMode("text"));
  }

  // Native File Input Change Handler
  if (pdfFileInput) {
    pdfFileInput.addEventListener("change", (e) => {
      if (e.target.files && e.target.files.length > 0) {
        handleFileSelection(e.target.files[0]);
      }
    });
  }

  // Drag and drop visual cues
  if (pdfDropzone) {
    pdfDropzone.addEventListener("dragover", (e) => {
      e.preventDefault();
      pdfDropzone.classList.add("drag-over");
    });
    pdfDropzone.addEventListener("dragleave", () => {
      pdfDropzone.classList.remove("drag-over");
    });
    pdfDropzone.addEventListener("drop", (e) => {
      pdfDropzone.classList.remove("drag-over");
      // The native file input or drop event handles the transfer
      if (e.dataTransfer && e.dataTransfer.files && e.dataTransfer.files.length > 0) {
        handleFileSelection(e.dataTransfer.files[0]);
      }
    });
  }

  function handleFileSelection(file) {
    if (!file) return;

    if (file.name.toLowerCase().endsWith(".txt") || file.name.toLowerCase().endsWith(".md")) {
      const reader = new FileReader();
      reader.onload = (e) => {
        resumeInput.value = e.target.result;
        showToast(`Loaded text file: ${file.name}`, "success");
      };
      reader.readAsText(file);
      return;
    }

    if (!file.name.toLowerCase().endsWith(".pdf")) {
      showToast("Please upload a .pdf, .md, or .txt file.", "warning");
      return;
    }

    const reader = new FileReader();
    reader.onload = async (e) => {
      const b64 = e.target.result;
      currentPdfBase64 = b64;
      currentPdfFilename = file.name;
      await processPdfBase64(b64, file.name);
    };
    reader.readAsDataURL(file);
  }

  async function processPdfBase64(b64, filename) {
    try {
      showToast("Inspecting PDF ATS compatibility...", "success");
      const resp = await fetch("/api/upload-pdf", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ pdf_base64: b64, filename: filename })
      });
      const diag = await resp.json();

      if (diag.error) {
        showToast(diag.error, "error");
        return;
      }

      // Hide dropzone prompt & overlay input; show loaded pill
      dropzonePrompt.classList.add("hidden");
      pdfFileInput.style.display = "none";
      loadedPdfPill.classList.remove("hidden");
      pdfDisplayName.textContent = filename;
      pdfDisplayStats.textContent = `${diag.file_size_mb} MB • ${diag.page_count} Page(s)`;

      // Render Diagnostic Card
      renderPdfDiagnostics(diag);

      // Auto-populate resume textarea
      resumeInput.value = diag.text || "";
      const charStr = Number(diag.char_count || 0).toLocaleString();
      document.getElementById("resume-input-hint").textContent = `Extracted ${charStr} characters from ${filename}`;

      showToast(`PDF parsed: ${charStr} selectable characters.`, "success");
    } catch (err) {
      console.error(err);
      showToast("Failed to parse PDF.", "error");
    }
  }

  function renderPdfDiagnostics(diag) {
    pdfDiagCard.classList.remove("hidden");
    const charStr = Number(diag.char_count || 0).toLocaleString();
    pdfDiagSelectable.textContent = diag.is_selectable ? `Pass (${charStr} chars)` : "FAIL (0 chars)";
    pdfDiagSelectable.style.color = diag.is_selectable ? "var(--accent-green)" : "var(--accent-rose)";

    pdfDiagSize.textContent = `${diag.file_size_mb} MB`;
    pdfDiagSize.style.color = diag.file_size_mb <= 2.5 ? "var(--accent-green)" : "var(--accent-amber)";

    pdfDiagPages.textContent = `${diag.page_count} Page${diag.page_count > 1 ? 's' : ''}`;
    pdfDiagPages.style.color = diag.page_count <= 2 ? "var(--accent-blue)" : "var(--accent-amber)";

    pdfDiagImages.textContent = `${diag.image_count} Asset(s)`;

    if (diag.ats_status === "PASS") {
      pdfAtsBadge.textContent = "ATS READABLE";
      pdfAtsBadge.className = "diag-status";
      pdfWarningBanner.classList.add("hidden");
    } else {
      pdfAtsBadge.textContent = "ATS BLOCKED";
      pdfAtsBadge.className = "diag-status fail";
      pdfWarningBanner.classList.remove("hidden");
      pdfWarningBanner.innerHTML = `<strong>Rule 1 Alert:</strong> Text trapped in images or unselectable! AI hiring systems will fail to parse this PDF.`;
    }
  }

  // Remove PDF Handler
  if (btnRemovePdf) {
    btnRemovePdf.addEventListener("click", (e) => {
      e.stopPropagation();
      currentPdfBase64 = null;
      currentPdfFilename = null;
      pdfFileInput.value = "";
      pdfFileInput.style.display = "block";
      dropzonePrompt.classList.remove("hidden");
      loadedPdfPill.classList.add("hidden");
      pdfDiagCard.classList.add("hidden");
      document.getElementById("resume-input-hint").textContent = "Direct text edit mode";
      showToast("PDF removed.", "warning");
    });
  }

  // Load Sample PDF
  if (btnLoadSamplePdf) {
    btnLoadSamplePdf.addEventListener("click", async () => {
      try {
        btnLoadSamplePdf.textContent = "Loading PDF...";
        const resp = await fetch("/api/sample");
        const data = await resp.json();

        if (data.sample_pdf_b64) {
          currentPdfBase64 = data.sample_pdf_b64;
          currentPdfFilename = data.sample_pdf_name || "sample_resume.pdf";
          jdInput.value = data.sample_jd || "";
          setInputMode("pdf");
          await processPdfBase64(data.sample_pdf_b64, currentPdfFilename);
          showToast("Loaded Ex-Apple PM Sample PDF & Target JD!", "success");
        } else {
          showToast("Sample PDF not found.", "error");
        }
      } catch (err) {
        console.error(err);
        showToast("Error loading sample PDF.", "error");
      } finally {
        btnLoadSamplePdf.textContent = "Load Sample PDF";
      }
    });
  }

  // Load Text Sample
  if (btnLoadSample) {
    btnLoadSample.addEventListener("click", async () => {
      try {
        btnLoadSample.textContent = "Loading...";
        const resp = await fetch("/api/sample");
        const data = await resp.json();
        resumeInput.value = data.sample_resume || "";
        jdInput.value = data.sample_jd || "";
        showToast("Loaded Text Sample!", "success");
      } catch (err) {
        console.error("Failed to load sample:", err);
        showToast("Error loading sample.", "error");
      } finally {
        btnLoadSample.textContent = "Load Text Sample";
      }
    });
  }

  // Clear workspace
  if (btnClear) {
    btnClear.addEventListener("click", () => {
      resumeInput.value = "";
      jdInput.value = "";
      currentPdfBase64 = null;
      currentPdfFilename = null;
      pdfFileInput.value = "";
      pdfFileInput.style.display = "block";
      dropzonePrompt.classList.remove("hidden");
      loadedPdfPill.classList.add("hidden");
      pdfDiagCard.classList.add("hidden");
      scoreNum.textContent = "--";
      scoreStatus.textContent = "Ready for Audit";
      scoreCircle.style.borderColor = "var(--border-color)";
      scoreSummaryBody.textContent = "Upload your resume PDF or paste text on the left, add a target Job Description, and click Run 5-Rule Audit.";
      showToast("Cleared workspace.", "warning");
    });
  }

  // Run Audit
  if (btnAudit) {
    btnAudit.addEventListener("click", async () => {
      const resume = resumeInput.value.trim();
      const jd = jdInput.value.trim();
      if (!resume && !currentPdfBase64) {
        showToast("Please upload a PDF or paste your resume first!", "warning");
        return;
      }

      try {
        btnAudit.textContent = "Auditing (5 Rules)...";
        btnAudit.disabled = true;

        const payload = {
          resume: resume,
          jd: jd,
          pdf_base64: currentPdfBase64,
          filename: currentPdfFilename
        };

        const resp = await fetch("/api/audit", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload)
        });
        const data = await resp.json();
        renderAuditResults(data);

        setOutputTab("scorecard");
        showToast(`Audit Complete! Score: ${data.composite_score}/100`, "success");
      } catch (err) {
        console.error("Audit error:", err);
        showToast("Failed to run audit.", "error");
      } finally {
        btnAudit.innerHTML = '<span class="btn-icon">⚡</span> Run 5-Rule Audit';
        btnAudit.disabled = false;
      }
    });
  }

  // Generate Killer Resume
  if (btnTransform) {
    btnTransform.addEventListener("click", async () => {
      const resume = resumeInput.value.trim();
      const jd = jdInput.value.trim();
      if (!resume && !currentPdfBase64) {
        showToast("Please upload a PDF or paste your resume first!", "warning");
        return;
      }

      try {
        btnTransform.textContent = "Optimizing Resume...";
        btnTransform.disabled = true;

        const payload = {
          resume: resume,
          jd: jd,
          pdf_base64: currentPdfBase64,
          filename: currentPdfFilename
        };

        const resp = await fetch("/api/transform", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload)
        });
        const data = await resp.json();

        outputMarkdown.textContent = data.optimized_markdown || "";
        document.getElementById("preview-score-delta").textContent = 
          `Initial Score: ${data.initial_score}/100 ➔ Optimized Score: ${data.optimized_score}/100`;

        setOutputTab("preview");
        renderAuditResults(data.post_audit_details || data.audit_details);
        showToast(`Killer Résumé Generated! Score: ${data.optimized_score}/100`, "success");
      } catch (err) {
        console.error("Transform error:", err);
        showToast("Failed to generate killer resume.", "error");
      } finally {
        btnTransform.innerHTML = '<span class="btn-icon">🚀</span> Generate Killer Résumé';
        btnTransform.disabled = false;
      }
    });
  }

  // Quick Bullet Transformer
  if (btnQuickXyz) {
    btnQuickXyz.addEventListener("click", async () => {
      const bullet = quickInput.value.trim();
      if (!bullet) {
        showToast("Enter a rough bullet point first!", "warning");
        return;
      }

      try {
        btnQuickXyz.textContent = "Transforming...";
        const resp = await fetch("/api/clarify", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ bullet: bullet })
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
        showToast("Transformed into Google XYZ formula (+75% interview lift)!", "success");
      } catch (err) {
        console.error(err);
      } finally {
        btnQuickXyz.textContent = "Transform Bullet";
      }
    });
  }

  // Copy Markdown
  if (btnCopyMarkdown) {
    btnCopyMarkdown.addEventListener("click", () => {
      const text = outputMarkdown.textContent;
      if (!text) return;
      navigator.clipboard.writeText(text).then(() => {
        showToast("Copied ATS Markdown to Clipboard!", "success");
      });
    });
  }

  // Download Markdown File
  if (btnDownloadMd) {
    btnDownloadMd.addEventListener("click", () => {
      const text = outputMarkdown.textContent;
      if (!text) {
        showToast("Generate a killer resume first!", "warning");
        return;
      }
      const blob = new Blob([text], { type: "text/markdown;charset=utf-8" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "killer_resume.md";
      a.click();
      URL.revokeObjectURL(url);
      showToast("Downloaded killer_resume.md", "success");
    });
  }

  // Print Selectable PDF
  if (btnPrintPdf) {
    btnPrintPdf.addEventListener("click", () => {
      const text = outputMarkdown.textContent;
      if (!text) {
        showToast("Generate a killer resume first!", "warning");
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
  }

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
    
    if (data.pdf_metadata) {
      const pm = data.pdf_metadata;
      const pmChars = Number(pm.char_count || 0).toLocaleString();
      r1Html += `<div style="margin-top:4px; padding:6px; background:rgba(56,189,248,0.1); border-radius:4px; font-size:11px; color:#38bdf8;">
        <strong>PDF Diagnostic:</strong> ${pm.file_size_mb} MB | ${pm.page_count} page(s) | ${pmChars} selectable characters
      </div>`;
    }

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
    if (!badge) return;
    badge.textContent = `${score}/100`;
    badge.className = "rule-score-badge " + (score >= 80 ? "pass" : (score >= 60 ? "warn" : "fail"));
  }
});
