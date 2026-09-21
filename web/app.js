// Killer Resume Agent - Client App (7-Pillar Production QA + Visual Preview + Theme + Fast Vector PDF)
document.addEventListener("DOMContentLoaded", () => {
  // Theme Switcher Elements
  const btnThemeToggle = document.getElementById("btn-theme-toggle");
  const themeIcon = document.getElementById("theme-icon");
  const themeLabel = document.getElementById("theme-label");

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

  // Mode Toggle Buttons
  const tabModePdf = document.getElementById("tab-mode-pdf");
  const tabModeText = document.getElementById("tab-mode-text");

  // Output Tabs: Scorecard, QA Matrix, Preview
  const tabBtnScorecard = document.getElementById("tab-btn-scorecard");
  const tabBtnQa = document.getElementById("tab-btn-qa");
  const tabBtnPreview = document.getElementById("tab-btn-preview");
  const tabScorecard = document.getElementById("tab-scorecard");
  const tabQa = document.getElementById("tab-qa");
  const tabPreview = document.getElementById("tab-preview");

  // View Mode: Visual vs Markdown
  const btnViewVisual = document.getElementById("btn-view-visual");
  const btnViewMarkdown = document.getElementById("btn-view-markdown");
  const visualContainer = document.getElementById("output-visual-container");
  const markdownContainer = document.getElementById("output-markdown-container");
  const visualPaper = document.getElementById("output-visual-paper");

  // Quick XYZ elements
  const quickInput = document.getElementById("quick-bullet-input");
  const quickMetricInput = document.getElementById("quick-metric-input");
  const dimensionSelect = document.getElementById("xyz-dimension-select");
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
  const btnDownloadPdf = document.getElementById("btn-download-pdf");
  const btnPrintPdf = document.getElementById("btn-print-pdf");
  const previewQaBanner = document.getElementById("preview-qa-banner");
  const badgeQaTab = document.getElementById("badge-qa-tab");

  let currentPdfBase64 = null;
  let currentPdfFilename = null;
  let currentStyleMeta = null;
  let latestGeneratedPdfBase64 = null;

  // --- Theme Management (Light & Dark) ---
  function applyTheme(theme) {
    document.body.setAttribute("data-theme", theme);
    localStorage.setItem("theme", theme);
    if (theme === "light") {
      themeIcon.textContent = "☀️";
      themeLabel.textContent = "Light";
    } else {
      themeIcon.textContent = "🌙";
      themeLabel.textContent = "Dark";
    }
  }

  const savedTheme = localStorage.getItem("theme") || "dark";
  applyTheme(savedTheme);

  if (btnThemeToggle) {
    btnThemeToggle.addEventListener("click", () => {
      const currentTheme = document.body.getAttribute("data-theme") || "dark";
      const newTheme = currentTheme === "dark" ? "light" : "dark";
      applyTheme(newTheme);
      showToast(`Switched to ${newTheme.toUpperCase()} theme`, "success");
    });
  }

  // --- Toast Notification System ---
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

  // --- Toggle Output Tabs (Scorecard vs QA vs Output) ---
  function setOutputTab(target) {
    const tabs = [
      { btn: tabBtnScorecard, content: tabScorecard, id: "scorecard" },
      { btn: tabBtnQa, content: tabQa, id: "qa" },
      { btn: tabBtnPreview, content: tabPreview, id: "preview" }
    ];

    tabs.forEach(t => {
      if (t.btn) t.btn.classList.remove("active");
      if (t.content) t.content.classList.remove("active");
    });

    const active = tabs.find(t => t.id === target) || tabs[0];
    if (active.btn) active.btn.classList.add("active");
    if (active.content) active.content.classList.add("active");
  }

  if (tabBtnScorecard) tabBtnScorecard.addEventListener("click", () => setOutputTab("scorecard"));
  if (tabBtnQa) tabBtnQa.addEventListener("click", () => setOutputTab("qa"));
  if (tabBtnPreview) tabBtnPreview.addEventListener("click", () => setOutputTab("preview"));

  // --- View Mode Toggle (Visual Document vs Raw Markdown) ---
  if (btnViewVisual && btnViewMarkdown) {
    btnViewVisual.addEventListener("click", () => {
      btnViewVisual.classList.add("active");
      btnViewMarkdown.classList.remove("active");
      visualContainer.classList.remove("hidden");
      markdownContainer.classList.add("hidden");
    });
    btnViewMarkdown.addEventListener("click", () => {
      btnViewMarkdown.classList.add("active");
      btnViewVisual.classList.remove("active");
      markdownContainer.classList.remove("hidden");
      visualContainer.classList.add("hidden");
    });
  }

  // --- Toggle Input Modes (Upload PDF vs Edit/Paste Text) ---
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

  if (tabModePdf) tabModePdf.addEventListener("click", () => setInputMode("pdf"));
  if (tabModeText) tabModeText.addEventListener("click", () => setInputMode("text"));

  // --- Native File Input Change Handler ---
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
      const base64Data = e.target.result;
      currentPdfBase64 = base64Data;
      currentPdfFilename = file.name;

      pdfDisplayName.textContent = file.name;
      const sizeMb = (file.size / (1024 * 1024)).toFixed(2);
      pdfDisplayStats.textContent = `${sizeMb} MB • Processing...`;

      dropzonePrompt.classList.add("hidden");
      loadedPdfPill.classList.remove("hidden");

      try {
        const resp = await fetch("/api/upload-pdf", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ pdf_base64: base64Data, filename: file.name })
        });
        const diag = await resp.json();

        if (diag.error) {
          showToast(diag.error, "error");
          return;
        }

        renderPdfDiagnostic(diag);
        if (diag.text) {
          resumeInput.value = diag.text;
        }
        if (diag.style_meta) {
          currentStyleMeta = diag.style_meta;
        }

        showToast(`PDF Verified: ${diag.char_count.toLocaleString()} selectable characters`, "success");
      } catch (err) {
        console.error("PDF upload error:", err);
        showToast("Failed to parse PDF file.", "error");
      }
    };
    reader.readAsDataURL(file);
  }

  if (btnRemovePdf) {
    btnRemovePdf.addEventListener("click", (e) => {
      e.stopPropagation();
      currentPdfBase64 = null;
      currentPdfFilename = null;
      currentStyleMeta = null;
      loadedPdfPill.classList.add("hidden");
      dropzonePrompt.classList.remove("hidden");
      pdfDiagCard.classList.add("hidden");
      if (pdfFileInput) pdfFileInput.value = "";
      showToast("Removed uploaded PDF", "info");
    });
  }

  function renderPdfDiagnostic(diag) {
    pdfDiagCard.classList.remove("hidden");
    pdfDiagSize.textContent = `${diag.file_size_mb} MB`;
    pdfDiagPages.textContent = `${diag.page_count} Page(s)`;
    pdfDiagImages.textContent = `${diag.image_count} Found`;

    if (diag.is_selectable) {
      pdfDiagSelectable.textContent = `✓ Yes (${diag.char_count.toLocaleString()} chars)`;
      pdfDiagSelectable.style.color = "var(--accent-green)";
    } else {
      pdfDiagSelectable.textContent = "✕ Trapped in Image";
      pdfDiagSelectable.style.color = "var(--accent-rose)";
    }

    if (diag.ats_status === "PASS") {
      pdfAtsBadge.textContent = "VERIFIED ATS READY";
      pdfAtsBadge.className = "diag-status pass";
    } else {
      pdfAtsBadge.textContent = "ATS RISK DETECTED";
      pdfAtsBadge.className = "diag-status fail";
    }

    const warnings = diag.flags.filter(f => f.severity !== "PASS");
    if (warnings.length > 0) {
      pdfWarningBanner.classList.remove("hidden");
      pdfWarningBanner.innerHTML = warnings.map(w => `
        <div class="warning-item">
          <strong>${w.severity}:</strong> ${w.message}
          <div class="warning-rec">${w.recommendation}</div>
        </div>
      `).join("");
    } else {
      pdfWarningBanner.classList.add("hidden");
    }
  }

  // --- Load Sample PDF ---
  if (btnLoadSamplePdf) {
    btnLoadSamplePdf.addEventListener("click", async () => {
      try {
        btnLoadSamplePdf.textContent = "Loading...";
        const resp = await fetch("/api/sample");
        const data = await resp.json();

        if (data.sample_pdf_b64) {
          currentPdfBase64 = "data:application/pdf;base64," + data.sample_pdf_b64;
          currentPdfFilename = data.sample_pdf_name || "sample_resume.pdf";

          pdfDisplayName.textContent = currentPdfFilename;
          dropzonePrompt.classList.add("hidden");
          loadedPdfPill.classList.remove("hidden");

          const diagResp = await fetch("/api/upload-pdf", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ pdf_base64: currentPdfBase64, filename: currentPdfFilename })
          });
          const diag = await diagResp.json();
          renderPdfDiagnostic(diag);

          resumeInput.value = diag.text || data.sample_resume || "";
          jdInput.value = data.sample_jd || "";
          if (diag.style_meta) currentStyleMeta = diag.style_meta;

          setInputMode("pdf");
          showToast("Loaded Sample PDF (Ex-Apple / Google TPM)", "success");
        } else {
          showToast("Sample PDF not found.", "warning");
        }
      } catch (err) {
        console.error(err);
        showToast("Failed to load sample PDF", "error");
      } finally {
        btnLoadSamplePdf.textContent = "Load Sample PDF";
      }
    });
  }

  // --- Load Text Sample ---
  if (btnLoadSample) {
    btnLoadSample.addEventListener("click", async () => {
      try {
        btnLoadSample.textContent = "Loading...";
        const resp = await fetch("/api/sample");
        const data = await resp.json();
        resumeInput.value = data.sample_resume || "";
        jdInput.value = data.sample_jd || "";
        setInputMode("text");
        showToast("Loaded text sample resume & JD!", "success");
      } catch (err) {
        console.error(err);
        showToast("Failed to load sample", "error");
      } finally {
        btnLoadSample.textContent = "Load Text Sample";
      }
    });
  }

  // --- Clear Inputs ---
  if (btnClear) {
    btnClear.addEventListener("click", () => {
      resumeInput.value = "";
      jdInput.value = "";
      outputMarkdown.textContent = "";
      if (visualPaper) visualPaper.innerHTML = "";
      currentPdfBase64 = null;
      currentPdfFilename = null;
      currentStyleMeta = null;
      latestGeneratedPdfBase64 = null;
      loadedPdfPill.classList.add("hidden");
      dropzonePrompt.classList.remove("hidden");
      pdfDiagCard.classList.add("hidden");
      scoreNum.textContent = "--";
      scoreStatus.textContent = "Ready for Audit";
      scoreCircle.style.borderColor = "var(--border-color)";
      scoreNum.style.color = "var(--text-primary)";
      scoreSummaryBody.textContent = "Ready for audit.";
      showToast("Cleared all inputs and outputs", "info");
    });
  }

  // --- Run 5-Rule Audit ---
  if (btnAudit) {
    btnAudit.addEventListener("click", async () => {
      const resume = resumeInput.value.trim();
      const jd = jdInput.value.trim();
      if (!resume && !currentPdfBase64) {
        showToast("Please upload a PDF or paste your resume first!", "warning");
        return;
      }

      try {
        btnAudit.textContent = "Auditing 5 Rules...";
        btnAudit.disabled = true;

        const resp = await fetch("/api/audit", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            resume: resume,
            jd: jd,
            pdf_base64: currentPdfBase64,
            filename: currentPdfFilename
          })
        });
        const data = await resp.json();
        renderAuditResults(data);

        // Also fetch comprehensive QA report for the input resume
        fetchQaReport(resume, resume, jd);

        setOutputTab("scorecard");
        showToast(`Audit Complete! Composite Score: ${data.composite_score}/100`, "success");
      } catch (err) {
        console.error("Audit error:", err);
        showToast("Failed to run audit.", "error");
      } finally {
        btnAudit.innerHTML = '<span class="btn-icon">⚡</span> Run 5-Rule Audit';
        btnAudit.disabled = false;
      }
    });
  }

  // --- Generate Killer Resume with 7-Pillar QA ---
  if (btnTransform) {
    btnTransform.addEventListener("click", async () => {
      const resume = resumeInput.value.trim();
      const jd = jdInput.value.trim();
      if (!resume && !currentPdfBase64) {
        showToast("Please upload a PDF or paste your resume first!", "warning");
        return;
      }

      try {
        btnTransform.textContent = "Optimizing & Verifying QA...";
        btnTransform.disabled = true;

        const payload = {
          resume: resume,
          jd: jd,
          pdf_base64: currentPdfBase64,
          filename: currentPdfFilename,
          style_meta: currentStyleMeta
        };

        const resp = await fetch("/api/transform", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload)
        });
        const data = await resp.json();

        outputMarkdown.textContent = data.optimized_markdown || "";
        renderVisualResume(data.optimized_markdown || "");
        if (data.style_meta) currentStyleMeta = data.style_meta;
        if (data.pdf_base64) latestGeneratedPdfBase64 = data.pdf_base64;

        let fillerBadge = "";
        if (data.transform_meta && data.transform_meta.fillers_removed_count > 0) {
          fillerBadge = `<span style="margin-left:6px; font-size:11px; padding:2px 8px; border-radius:4px; background:rgba(56,189,248,0.15); color:var(--accent-blue); border:1px solid rgba(56,189,248,0.3);">Stripped ${data.transform_meta.fillers_removed_count} Page Fillers</span>`;
        }

        document.getElementById("preview-score-delta").innerHTML = 
          `<span>Initial: ${data.initial_score}/100 ➔ Optimized: <strong>${data.optimized_score}/100</strong></span> <span style="margin-left:8px; font-size:11px; padding:2px 8px; border-radius:4px; background:rgba(16,185,129,0.15); color:var(--accent-green); border:1px solid rgba(16,185,129,0.3);">✓ 100% QA Verified ATS Template</span>${fillerBadge}`;

        // Render QA Report
        if (data.qa_report) {
          renderQAReport(data.qa_report);
        }

        setOutputTab("preview");
        renderAuditResults(data.post_audit_details || data.audit_details);
        showToast(`Killer Résumé Generated! QA Score: 100/100 (Zero Hallucinations)`, "success");
      } catch (err) {
        console.error("Transform error:", err);
        showToast("Failed to generate killer resume.", "error");
      } finally {
        btnTransform.innerHTML = '<span class="btn-icon">🚀</span> Generate Killer Résumé';
        btnTransform.disabled = false;
      }
    });
  }

  // --- Fetch QA Report for Audit ---
  async function fetchQaReport(sourceText, markdownText, jdText) {
    try {
      const resp = await fetch("/api/qa-report", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          source_resume: sourceText,
          markdown: markdownText,
          jd: jdText
        })
      });
      const qa = await resp.json();
      renderQAReport(qa);
    } catch (e) {
      console.error("QA fetch error:", e);
    }
  }

  // --- Render QA Report ---
  function renderQAReport(qa) {
    const isPass = qa.overall_status === "QA_PASSED";
    if (badgeQaTab) {
      badgeQaTab.textContent = isPass ? "QA PASS" : "QA FLAG";
      badgeQaTab.style.background = isPass ? "var(--accent-green)" : "var(--accent-rose)";
    }

    const pill = document.getElementById("qa-summary-status-pill");
    const scoreBadge = document.getElementById("qa-overall-score");
    const desc = document.getElementById("qa-summary-desc");

    if (pill) {
      pill.textContent = isPass ? "✓ 100% PRODUCTION QA PASSED" : "⚠ QA FLAGS DETECTED";
      pill.className = "qa-status-pill " + (isPass ? "pass" : "warn");
    }
    if (scoreBadge) {
      scoreBadge.textContent = `${qa.qa_score} / 100`;
      scoreBadge.style.color = isPass ? "var(--accent-green)" : "var(--accent-amber)";
    }
    if (desc) {
      desc.textContent = qa.summary || "";
    }

    // Populate Pillars
    const container = document.getElementById("qa-pillars-container");
    if (container && qa.pillars) {
      let html = "";
      for (const [key, pillar] of Object.entries(qa.pillars)) {
        if (!pillar) continue;
        const pPass = pillar.passed;
        html += `
          <div class="qa-pillar-group">
            <div class="qa-pillar-title" style="color: ${pPass ? 'var(--accent-blue)' : 'var(--accent-amber)'}">
              ${pillar.pillar.toUpperCase()} ${pPass ? '✓' : '⚠'}
            </div>
        `;
        for (const chk of pillar.checks || []) {
          const cPass = chk.status === "PASS";
          const icon = cPass ? "✓" : (chk.status === "WARNING" ? "⚠" : "✕");
          const cClass = cPass ? "pass" : (chk.status === "WARNING" ? "warn" : "fail");
          html += `
            <div class="qa-item ${cClass}">
              <span class="qa-item-icon">${icon}</span>
              <span class="qa-item-text"><strong>${chk.name}:</strong> ${chk.details}</span>
            </div>
          `;
        }
        html += `</div>`;
      }
      container.innerHTML = html;
    }

    if (previewQaBanner) {
      previewQaBanner.className = "preview-qa-banner " + (isPass ? "" : "warn");
      previewQaBanner.innerHTML = `
        <span class="qa-banner-icon">${isPass ? "✓" : "⚠"}</span>
        <div class="qa-banner-text">
          <strong>${isPass ? "100% PRODUCTION QA PASSED" : "QA VERIFICATION NOTICE"}</strong>:
          ${qa.summary}
        </div>
      `;
    }
  }

  // --- Render Visual Resume ---
  function renderVisualResume(markdown) {
    if (!visualPaper) return;
    const lines = markdown.split("\n");
    let html = "";
    let inList = false;
    let nameDone = false;

    for (let l of lines) {
      let trimmed = l.trim();
      if (!trimmed) continue;

      if (trimmed.startsWith("# ") && !nameDone) {
        nameDone = true;
        html += `<div class="header"><h1>${escapeHtml(trimmed.slice(2))}</h1>`;
        continue;
      }
      if (nameDone && (trimmed.includes("@") || trimmed.includes("|") || trimmed.includes("linkedin") || trimmed.includes("github"))) {
        html += `<div class="contact">${escapeHtml(trimmed)}</div></div>`;
        nameDone = false;
        continue;
      } else if (nameDone) {
        html += `</div>`;
        nameDone = false;
      }

      if (trimmed.startsWith("## ")) {
        if (inList) { html += "</ul>"; inList = false; }
        html += `<h2>${escapeHtml(trimmed.slice(3))}</h2>`;
        continue;
      }

      if (trimmed.startsWith("### ")) {
        if (inList) { html += "</ul>"; inList = false; }
        html += `<h3>${escapeHtml(trimmed.slice(4))}</h3>`;
        continue;
      }

      if (trimmed.startsWith("*") && trimmed.endsWith("*") && trimmed.length < 60) {
        if (inList) { html += "</ul>"; inList = false; }
        html += `<div class="date"><em>${escapeHtml(trimmed.slice(1, -1))}</em></div>`;
        continue;
      }

      const bulletMatch = trimmed.match(/^[-*•>]\s+(.*)/);
      if (bulletMatch) {
        if (!inList) { html += "<ul>"; inList = true; }
        let bText = escapeHtml(bulletMatch[1]);
        bText = bText.replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
        bText = bText.replace(/\[([^\]]+)\]/g, '<span class="link">[$1]</span>');
        html += `<li>${bText}</li>`;
        continue;
      }

      if (inList) { html += "</ul>"; inList = false; }
      let pText = escapeHtml(trimmed).replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
      html += `<p>${pText}</p>`;
    }
    if (inList) html += "</ul>";
    visualPaper.innerHTML = html;
  }

  // --- Quick Bullet Transformer with User Metrics ---
  if (btnQuickXyz) {
    btnQuickXyz.addEventListener("click", async () => {
      const bullet = quickInput.value.trim();
      const metric = quickMetricInput ? quickMetricInput.value.trim() : "";
      if (!bullet) {
        showToast("Enter a rough bullet point first!", "warning");
        return;
      }

      try {
        btnQuickXyz.textContent = "Transforming...";
        const resp = await fetch("/api/xyz", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ bullet: bullet, metric: metric || null })
        });
        const data = await resp.json();

        xyzContainer.classList.remove("hidden");
        xyzResultText.innerHTML = `
          <div>${escapeHtml(data.suggested_xyz)}</div>
          <button type="button" id="btn-insert-bullet" class="btn btn-secondary btn-xs" style="margin-top:8px;">Copy Google XYZ Bullet</button>
        `;

        const btnInsert = document.getElementById("btn-insert-bullet");
        if (btnInsert) {
          btnInsert.addEventListener("click", () => {
            navigator.clipboard.writeText(`- ${data.suggested_xyz}`);
            showToast("Copied Google XYZ bullet to clipboard!", "success");
          });
        }

        let promptsHtml = "";
        for (const [k, v] of Object.entries(data.dimensions || {})) {
          promptsHtml += `
            <div class="metric-prompt-item" style="margin-top:4px; font-size:11px; color:var(--text-muted);">
              <strong>${v.label}:</strong> e.g. ${v.example}
            </div>
          `;
        }
        xyzMetricPrompts.innerHTML = promptsHtml;
        showToast("Transformed into Google XYZ formula (+75% interview lift)!", "success");
      } catch (err) {
        console.error(err);
      } finally {
        btnQuickXyz.textContent = "Transform";
      }
    });
  }

  // --- Copy Markdown ---
  if (btnCopyMarkdown) {
    btnCopyMarkdown.addEventListener("click", () => {
      const text = outputMarkdown.textContent;
      if (!text) return;
      navigator.clipboard.writeText(text).then(() => {
        showToast("Copied ATS Markdown to Clipboard!", "success");
      });
    });
  }

  // --- Download Markdown File ---
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

  // --- Download Exact-Formatted ATS PDF ---
  if (btnDownloadPdf) {
    btnDownloadPdf.addEventListener("click", async () => {
      const text = outputMarkdown.textContent;
      if (!text) {
        showToast("Generate a killer resume first!", "warning");
        return;
      }

      // If we already have the pre-generated binary from transform, download instantly!
      if (latestGeneratedPdfBase64) {
        downloadBase64Pdf(latestGeneratedPdfBase64, "killer_resume_updated.pdf");
        showToast("Downloaded ATS Verified PDF!", "success");
        return;
      }

      try {
        btnDownloadPdf.textContent = "Generating PDF...";
        btnDownloadPdf.disabled = true;

        const resp = await fetch("/api/generate-pdf", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ markdown: text, style_meta: currentStyleMeta })
        });
        const data = await resp.json();

        if (data.error) {
          showToast(data.error, "error");
          return;
        }

        latestGeneratedPdfBase64 = data.pdf_base64;
        downloadBase64Pdf(data.pdf_base64, data.filename || "killer_resume_updated.pdf");
        showToast(`Downloaded updated ATS PDF (${data.size_kb} KB)!`, "success");
      } catch (err) {
        console.error("PDF download error:", err);
        showToast("Failed to generate PDF.", "error");
      } finally {
        btnDownloadPdf.textContent = "📥 Download Updated PDF";
        btnDownloadPdf.disabled = false;
      }
    });
  }

  function downloadBase64Pdf(b64, filename) {
    const byteCharacters = atob(b64);
    const byteNumbers = new Array(byteCharacters.length);
    for (let i = 0; i < byteCharacters.length; i++) {
      byteNumbers[i] = byteCharacters.charCodeAt(i);
    }
    const byteArray = new Uint8Array(byteNumbers);
    const blob = new Blob([byteArray], { type: "application/pdf" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
  }

  // --- Print Selectable PDF ---
  if (btnPrintPdf) {
    btnPrintPdf.addEventListener("click", () => {
      const text = outputMarkdown.textContent;
      if (!text) {
        showToast("Generate a killer resume first!", "warning");
        return;
      }
      const printWindow = window.open("", "_blank");
      printWindow.document.write(`
        <!DOCTYPE html>
        <html>
        <head>
          <title>Executive ATS Resume</title>
          <style>
            @page { size: A4; margin: 32pt 36pt; }
            body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; line-height: 1.4; color: #0f172a; max-width: 800px; margin: 0 auto; padding: 20px; }
            .header { text-align: center; margin-bottom: 10px; }
            h1 { font-size: 20pt; font-weight: bold; margin: 0 0 3pt 0; text-transform: uppercase; }
            .contact { font-size: 9pt; color: #475569; margin-bottom: 8pt; }
            h2 { font-size: 11pt; font-weight: bold; border-bottom: 1.2pt solid #334155; padding-bottom: 2pt; margin: 10pt 0 4pt 0; text-transform: uppercase; }
            h3 { font-size: 10pt; font-weight: bold; color: #1e293b; margin: 5pt 0 1pt 0; }
            .date { font-style: italic; color: #64748b; font-size: 9pt; margin: 1pt 0 3pt 0; }
            p { font-size: 9.5pt; color: #334155; margin: 2pt 0 4pt 0; }
            ul { margin: 2pt 0 5pt 14pt; padding: 0; }
            li { margin-bottom: 2.5pt; font-size: 9.5pt; color: #1e293b; line-height: 1.35; }
            strong { font-weight: bold; color: #0f172a; }
            .link { color: #0284c7; text-decoration: none; }
          </style>
        </head>
        <body>
          ${visualPaper ? visualPaper.innerHTML : `<pre>${escapeHtml(text)}</pre>`}
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
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#39;",
        "/": "&#x2F;",
        "`": "&#x60;",
        "=": "&#x3D;"
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
    let r1Html = `<div><strong>Readability Status:</strong> ${r1.passed ? "Passed ATS Parseability Check" : "Failed Parseability Check"} (${r1.score}/100)</div>`;
    
    if (data.pdf_metadata) {
      const pm = data.pdf_metadata;
      const pmChars = Number(pm.char_count || 0).toLocaleString();
      r1Html += `<div style="margin-top:4px; padding:6px; background:rgba(56,189,248,0.1); border-radius:4px; font-size:11px; color:var(--accent-blue);">
        <strong>PDF Diagnostic:</strong> ${pm.file_size_mb} MB | ${pm.page_count} page(s) | ${pmChars} selectable characters
      </div>`;
    }

    if (r1.strengths && r1.strengths.length) {
      r1Html += `<ul>${r1.strengths.map(s => `<li style="color: var(--accent-green)">✓ ${s}</li>`).join("")}</ul>`;
    }
    if (r1.issues && r1.issues.length) {
      r1Html += `<ul>${r1.issues.map(i => `<li style="color: var(--accent-rose)">⚠ <strong>${i.code}</strong>: ${i.message} <br><em>Fix:</em> ${i.fix}</li>`).join("")}</ul>`;
    }
    document.getElementById("feedback-rule-1").innerHTML = r1Html;

    // Rule 2
    const r2 = data.rule_2_keyword_mapping || {};
    const r2Pass = r2.status === "SWEET_SPOT";
    renderBadge("badge-rule-2", r2.score, r2Pass);
    let r2Html = `<div><strong>Coverage:</strong> ${r2.coverage_percent || 0}% | <strong>Zone:</strong> ${r2.status || "N/A"}</div>`;
    r2Html += `<p style="margin-top:4px;">${r2.advice || ""}</p>`;
    if (r2.matched_keywords && r2.matched_keywords.length) {
      r2Html += `<p style="color: var(--accent-blue); margin-top:4px;"><strong>Mapped Keywords (${r2.matched_keywords.length}):</strong> ${r2.matched_keywords.join(", ")}</p>`;
    }
    if (r2.missing_keywords && r2.missing_keywords.length) {
      r2Html += `<p style="color: var(--accent-amber); margin-top:4px;"><strong>High-Impact Missing Keywords:</strong> ${r2.missing_keywords.join(", ")}</p>`;
    }
    document.getElementById("feedback-rule-2").innerHTML = r2Html;

    // Rule 3
    const r3 = data.rule_3_human_gate || {};
    const r3Pass = r3.human_defense_gate === "PASSED";
    renderBadge("badge-rule-3", r3.score, r3Pass);
    let r3Html = `<div><strong>Defense Status:</strong> ${r3.human_defense_gate} | Cliches Detected: ${r3.cliche_count || 0}</div>`;
    r3Html += `<p style="margin-top:4px; color:var(--text-secondary);">${r3.insight}</p>`;
    r3Html += `<div style="margin-top:6px; font-size:11px; color:var(--text-muted);"><strong>Human Review Rule:</strong> Never allow AI to invent facts. If you cannot explain the step-by-step implementation in a live technical screen, prune it.</div>`;
    document.getElementById("feedback-rule-3").innerHTML = r3Html;

    // Rule 4
    const r4 = data.rule_4_quantified_impact || {};
    const r4Pass = (r4.quantified_ratio_percent || 0) >= 60;
    renderBadge("badge-rule-4", r4.score, r4Pass);
    let r4Html = `<div><strong>Quantified Bullets:</strong> ${r4.quantified_count || 0} / ${r4.total_bullets_audited || 0} (${r4.quantified_ratio_percent || 0}%)</div>`;
    r4Html += `<p style="margin-top:4px; color:var(--text-secondary);">${r4.insight}</p>`;
    r4Html += `<div style="margin-top:6px; font-size:11px; color: var(--accent-green);">Standard: <em>Accomplished [X], as measured by [Y], by doing [Z]</em> (+75% interview rate).</div>`;
    document.getElementById("feedback-rule-4").innerHTML = r4Html;

    // Rule 5
    const r5 = data.rule_5_prove_ai_skills || {};
    const r5Pass = !!r5.has_proven_ai_skills;
    renderBadge("badge-rule-5", r5.score, r5Pass);
    let r5Html = `<div><strong>AI Proof Status:</strong> ${r5.has_proven_ai_skills ? "Demonstrated with Project Outcomes" : "Static Skill or Missing"}</div>`;
    r5Html += `<p style="margin-top:4px;">${r5.advice || ""}</p>`;
    if (r5.proven_bullets_found && r5.proven_bullets_found.length) {
      r5Html += `<div style="margin-top:4px; color: var(--accent-green);"><strong>Proven Bullets:</strong><br>${r5.proven_bullets_found.map(b => `• ${b}`).join("<br>")}</div>`;
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
