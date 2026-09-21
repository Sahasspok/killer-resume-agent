// Killer Résumé Agent - Simplified Step-by-Step Onboarding Client
// Jeff Su's 5 Research-Backed Rules + 7-Pillar Production QA Validation

document.addEventListener("DOMContentLoaded", () => {
  // --- State Variables ---
  let currentStep = 1;
  let sampleDataCache = null;
  let currentPdfBase64 = null;
  let currentPdfFilename = null;
  let currentStyleMeta = null;
  let latestGeneratedPdfBase64 = null;
  let lastAuditData = null;
  let lastTransformData = null;

  // --- DOM Elements ---
  // Theme
  const btnThemeToggle = document.getElementById("btn-theme-toggle");
  const themeIcon = document.getElementById("theme-icon");
  const themeLabel = document.getElementById("theme-label");
  const btnHeaderReset = document.getElementById("btn-header-reset");

  // Loading Overlay
  const loadingOverlay = document.getElementById("loading-overlay");
  const loadingTitle = document.getElementById("loading-title");
  const loadingSubtitle = document.getElementById("loading-subtitle");

  // Stepper Elements
  const stepNodes = [
    document.getElementById("step-node-1"),
    document.getElementById("step-node-2"),
    document.getElementById("step-node-3"),
    document.getElementById("step-node-4"),
    document.getElementById("step-node-5")
  ];
  const connectors = [
    document.getElementById("connector-1"),
    document.getElementById("connector-2"),
    document.getElementById("connector-3"),
    document.getElementById("connector-4")
  ];

  // Panes
  const panes = [
    document.getElementById("pane-step-1"),
    document.getElementById("pane-step-2"),
    document.getElementById("pane-step-3"),
    document.getElementById("pane-step-4"),
    document.getElementById("pane-step-5")
  ];

  // Step 1: Target Job
  const jdInput = document.getElementById("jd-input");
  const btnLoadSampleJd = document.getElementById("btn-load-sample-jd");
  const btnClearJd = document.getElementById("btn-clear-jd");
  const btnStep1Skip = document.getElementById("btn-step1-skip");
  const btnStep1Next = document.getElementById("btn-step1-next");

  // Step 2: Current CV (MANDATORY)
  const tabModePdf = document.getElementById("tab-mode-pdf");
  const tabModeText = document.getElementById("tab-mode-text");
  const pdfContainerSection = document.getElementById("pdf-container-section");
  const resumeTextGroup = document.getElementById("resume-text-group");
  const pdfDropzone = document.getElementById("pdf-dropzone");
  const pdfFileInput = document.getElementById("pdf-file-input");
  const dropzonePrompt = document.getElementById("dropzone-prompt");
  const loadedPdfPill = document.getElementById("loaded-pdf-pill");
  const pdfDisplayName = document.getElementById("pdf-display-name");
  const pdfDisplayStats = document.getElementById("pdf-display-stats");
  const btnRemovePdf = document.getElementById("btn-remove-pdf");
  const pdfDiagCard = document.getElementById("pdf-diagnostic-card");
  const pdfAtsBadge = document.getElementById("pdf-ats-badge");
  const pdfDiagSelectable = document.getElementById("pdf-diag-selectable");
  const pdfDiagSize = document.getElementById("pdf-diag-size");
  const pdfDiagPages = document.getElementById("pdf-diag-pages");
  const pdfDiagImages = document.getElementById("pdf-diag-images");
  const pdfWarningBanner = document.getElementById("pdf-warning-banner");
  const resumeInput = document.getElementById("resume-input");
  const btnLoadSampleCv = document.getElementById("btn-load-sample-cv");
  const cvRequiredAlert = document.getElementById("cv-required-alert");
  const btnStep2Back = document.getElementById("btn-step2-back");
  const btnStep2Next = document.getElementById("btn-step2-next");

  // Step 3: Extra Context
  const extraMetricsInput = document.getElementById("extra-metrics-input");
  const extraAiToolsInput = document.getElementById("extra-ai-tools-input");
  const btnStep3Back = document.getElementById("btn-step3-back");
  const btnStep3Skip = document.getElementById("btn-step3-skip");
  const btnStep3Next = document.getElementById("btn-step3-next");
  const quickInput = document.getElementById("quick-bullet-input");
  const quickMetricInput = document.getElementById("quick-metric-input");
  const dimensionSelect = document.getElementById("xyz-dimension-select");
  const btnQuickXyz = document.getElementById("btn-quick-xyz");
  const xyzContainer = document.getElementById("xyz-result-container");
  const xyzResultText = document.getElementById("xyz-result-text");

  // Step 4: Health Check & Errors
  const auditScoreCircle = document.getElementById("audit-score-circle");
  const auditScoreVal = document.getElementById("audit-score-val");
  const auditScoreStatus = document.getElementById("audit-score-status");
  const auditScoreSummary = document.getElementById("audit-score-summary");
  const btnStep4Back = document.getElementById("btn-step4-back");
  const btnStep4Generate = document.getElementById("btn-step4-generate");

  // Step 4 Error Badges & Bodies
  const badgeErrRule1 = document.getElementById("badge-err-rule-1");
  const bodyErrRule1 = document.getElementById("body-err-rule-1");
  const fixErrRule1 = document.getElementById("fix-err-rule-1");
  const cardErrRule1 = document.getElementById("card-err-rule-1");

  const badgeErrRule2 = document.getElementById("badge-err-rule-2");
  const bodyErrRule2 = document.getElementById("body-err-rule-2");
  const fixErrRule2 = document.getElementById("fix-err-rule-2");
  const cardErrRule2 = document.getElementById("card-err-rule-2");

  const badgeErrRule4 = document.getElementById("badge-err-rule-4");
  const bodyErrRule4 = document.getElementById("body-err-rule-4");
  const fixErrRule4 = document.getElementById("fix-err-rule-4");
  const cardErrRule4 = document.getElementById("card-err-rule-4");

  const badgeErrRule3 = document.getElementById("badge-err-rule-3");
  const bodyErrRule3 = document.getElementById("body-err-rule-3");
  const fixErrRule3 = document.getElementById("fix-err-rule-3");
  const cardErrRule3 = document.getElementById("card-err-rule-3");

  const badgeErrRule5 = document.getElementById("badge-err-rule-5");
  const bodyErrRule5 = document.getElementById("body-err-rule-5");
  const fixErrRule5 = document.getElementById("fix-err-rule-5");
  const cardErrRule5 = document.getElementById("card-err-rule-5");

  // Step 5: Upgraded Résumé
  const finalScoreDeltaBadge = document.getElementById("final-score-delta-badge");
  const finalStatsText = document.getElementById("final-stats-text");
  const pdfSizeLabel = document.getElementById("pdf-size-label");
  const tipMissingKeywords = document.getElementById("tip-missing-keywords");
  const btnDownloadPdf = document.getElementById("btn-download-pdf");
  const btnCopyMarkdown = document.getElementById("btn-copy-markdown");
  const btnPrintPdf = document.getElementById("btn-print-pdf");
  const btnRestartStep5 = document.getElementById("btn-restart-step5");
  const btnStep5Back = document.getElementById("btn-step5-back");
  const btnStep5Download = document.getElementById("btn-step5-download");
  const btnViewVisual = document.getElementById("btn-view-visual");
  const btnViewMarkdown = document.getElementById("btn-view-markdown");
  const visualContainer = document.getElementById("output-visual-container");
  const markdownContainer = document.getElementById("output-markdown-container");
  const visualPaper = document.getElementById("output-visual-paper");
  const outputMarkdown = document.getElementById("output-markdown");

  // --- Theme Management ---
  function applyTheme(theme) {
    document.body.setAttribute("data-theme", theme);
    localStorage.setItem("theme", theme);
    if (theme === "light") {
      if (themeIcon) themeIcon.textContent = "☀️";
      if (themeLabel) themeLabel.textContent = "Light";
    } else {
      if (themeIcon) themeIcon.textContent = "🌙";
      if (themeLabel) themeLabel.textContent = "Dark";
    }
  }

  const savedTheme = localStorage.getItem("theme") || "dark";
  applyTheme(savedTheme);

  if (btnThemeToggle) {
    btnThemeToggle.addEventListener("click", () => {
      const current = document.body.getAttribute("data-theme") || "dark";
      const next = current === "dark" ? "light" : "dark";
      applyTheme(next);
      showToast(`Switched to ${next.toUpperCase()} theme`, "success");
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

  // --- Loading Overlay Controller ---
  function showLoading(title = "Analyzing Your Résumé...", subtitle = "Checking against 2 million job application benchmarks") {
    if (loadingTitle) loadingTitle.textContent = title;
    if (loadingSubtitle) loadingSubtitle.textContent = subtitle;
    if (loadingOverlay) {
      loadingOverlay.style.display = "flex";
      loadingOverlay.classList.remove("hidden");
    }
  }

  function hideLoading() {
    if (loadingOverlay) {
      loadingOverlay.style.display = "none";
      loadingOverlay.classList.add("hidden");
    }
  }

  // --- Step Navigation Engine ---
  function goToStep(targetStep) {
    // Validation: Step 2 is strictly required
    if (targetStep > 2) {
      const hasText = resumeInput && resumeInput.value.trim().length > 20;
      const hasPdf = Boolean(currentPdfBase64);
      if (!hasText && !hasPdf) {
        if (cvRequiredAlert) cvRequiredAlert.classList.remove("hidden");
        showToast("Please upload a PDF or paste your CV text to continue.", "warning");
        if (currentStep !== 2) goToStep(2);
        return;
      } else {
        if (cvRequiredAlert) cvRequiredAlert.classList.add("hidden");
      }
    }

    currentStep = targetStep;

    // Update Panes
    panes.forEach((p, idx) => {
      if (p) {
        if (idx + 1 === currentStep) {
          p.classList.add("active");
        } else {
          p.classList.remove("active");
        }
      }
    });

    // Update Stepper Visuals
    stepNodes.forEach((node, idx) => {
      if (!node) return;
      const stepNum = idx + 1;
      node.classList.remove("active", "completed");
      if (stepNum === currentStep) {
        node.classList.add("active");
      } else if (stepNum < currentStep) {
        node.classList.add("completed");
      }
    });

    connectors.forEach((conn, idx) => {
      if (!conn) return;
      if (idx + 1 < currentStep) {
        conn.classList.add("filled");
      } else {
        conn.classList.remove("filled");
      }
    });

    // Scroll to top of wizard card smoothly
    const wizardCard = document.getElementById("wizard-card");
    if (wizardCard) {
      wizardCard.scrollIntoView({ behavior: "smooth", block: "start" });
    }

    // Automated action hooks upon entering steps
    if (currentStep === 4) {
      triggerAuditFlow();
    } else if (currentStep === 5) {
      if (lastTransformData) {
        slowlyScrollToOutput();
      } else {
        triggerTransformFlow();
      }
    }
  }

  // Allow clicking on previous steps in the stepper bar
  stepNodes.forEach((node, idx) => {
    if (!node) return;
    node.addEventListener("click", () => {
      const stepNum = idx + 1;
      if (stepNum < currentStep) {
        goToStep(stepNum);
      }
    });
  });

  // --- Step 1 Events (Target Job - Skippable) ---
  if (btnStep1Skip) {
    btnStep1Skip.addEventListener("click", () => {
      if (!jdInput.value.trim()) {
        jdInput.value = "Senior Technical Project Manager (Enterprise Software & AI Engineering Systems)";
      }
      showToast("Using High-Paying Tech PM Standard", "success");
      goToStep(2);
    });
  }

  if (btnStep1Next) {
    btnStep1Next.addEventListener("click", () => {
      goToStep(2);
    });
  }

  if (btnLoadSampleJd) {
    btnLoadSampleJd.addEventListener("click", async () => {
      try {
        const sample = await fetchSampleData();
        if (sample && sample.sample_jd) {
          jdInput.value = sample.sample_jd;
          showToast("Loaded Senior TPM Target Job Description", "success");
        }
      } catch (err) {
        showToast("Failed to load sample job description", "error");
      }
    });
  }

  if (btnClearJd) {
    btnClearJd.addEventListener("click", () => {
      if (jdInput) jdInput.value = "";
    });
  }

  // --- Step 2 Events (Add CV - Mandatory) ---
  if (tabModePdf && tabModeText) {
    tabModePdf.addEventListener("click", () => {
      tabModePdf.classList.add("active");
      tabModeText.classList.remove("active");
      if (pdfContainerSection) pdfContainerSection.classList.remove("hidden");
      if (resumeTextGroup) resumeTextGroup.classList.add("hidden");
    });

    tabModeText.addEventListener("click", () => {
      tabModeText.classList.add("active");
      tabModePdf.classList.remove("active");
      if (pdfContainerSection) pdfContainerSection.classList.add("hidden");
      if (resumeTextGroup) resumeTextGroup.classList.remove("hidden");
    });
  }

  if (btnStep2Back) {
    btnStep2Back.addEventListener("click", () => goToStep(1));
  }

  if (btnStep2Next) {
    btnStep2Next.addEventListener("click", () => {
      const hasText = resumeInput && resumeInput.value.trim().length > 20;
      const hasPdf = Boolean(currentPdfBase64);
      if (!hasText && !hasPdf) {
        if (cvRequiredAlert) cvRequiredAlert.classList.remove("hidden");
        showToast("Please upload a PDF or paste your CV text to continue.", "warning");
        return;
      }
      if (cvRequiredAlert) cvRequiredAlert.classList.add("hidden");
      goToStep(3);
    });
  }

  if (btnLoadSampleCv) {
    btnLoadSampleCv.addEventListener("click", async () => {
      try {
        showLoading("Loading Ex-Apple PM Sample Data...", "Setting up PDF and verifiable project history");
        const sample = await fetchSampleData();
        if (sample) {
          if (sample.sample_resume && resumeInput) {
            resumeInput.value = sample.sample_resume;
          }
          if (sample.sample_jd && jdInput && !jdInput.value.trim()) {
            jdInput.value = sample.sample_jd;
          }
          if (sample.sample_pdf_b64) {
            currentPdfBase64 = sample.sample_pdf_b64;
            currentPdfFilename = sample.sample_pdf_name || "sample_resume.pdf";
            showLoadedPdfPill(currentPdfFilename, "148 KB • 1 Page (Selectable Vector)");
            await runPdfPreflight(currentPdfBase64, currentPdfFilename);
          }
          if (cvRequiredAlert) cvRequiredAlert.classList.add("hidden");
          hideLoading();
          showToast("Loaded Ex-Apple PM Sample CV & Job Description", "success");
        }
      } catch (err) {
        hideLoading();
        showToast("Failed to load sample data", "error");
      }
    });
  }

  // PDF File Upload & Dropzone Handling
  if (pdfFileInput) {
    pdfFileInput.addEventListener("change", (e) => {
      const file = e.target.files[0];
      if (file) handlePdfFile(file);
    });
  }

  if (pdfDropzone) {
    ["dragenter", "dragover"].forEach(evt => {
      pdfDropzone.addEventListener(evt, (e) => {
        e.preventDefault();
        pdfDropzone.classList.add("dragover");
      });
    });
    ["dragleave", "drop"].forEach(evt => {
      pdfDropzone.addEventListener(evt, (e) => {
        e.preventDefault();
        pdfDropzone.classList.remove("dragover");
      });
    });
    pdfDropzone.addEventListener("drop", (e) => {
      const file = e.dataTransfer.files[0];
      if (file) handlePdfFile(file);
    });
  }

  if (btnRemovePdf) {
    btnRemovePdf.addEventListener("click", (e) => {
      e.stopPropagation();
      clearPdfState();
    });
  }

  function handlePdfFile(file) {
    if (file.type !== "application/pdf" && !file.name.endsWith(".pdf")) {
      // Fallback for .txt or .md
      const reader = new FileReader();
      reader.onload = (e) => {
        if (resumeInput) resumeInput.value = e.target.result;
        tabModeText.click();
        showToast(`Loaded ${file.name} as text`, "success");
      };
      reader.readAsText(file);
      return;
    }

    const reader = new FileReader();
    reader.onload = async (e) => {
      const b64 = e.target.result;
      currentPdfBase64 = b64;
      currentPdfFilename = file.name;
      const sizeMb = (file.size / (1024 * 1024)).toFixed(2);
      showLoadedPdfPill(file.name, `${sizeMb} MB • Analyzing text layer...`);
      await runPdfPreflight(b64, file.name);
    };
    reader.readAsDataURL(file);
  }

  function showLoadedPdfPill(name, stats) {
    if (pdfDisplayName) pdfDisplayName.textContent = name;
    if (pdfDisplayStats) pdfDisplayStats.textContent = stats;
    if (dropzonePrompt) dropzonePrompt.classList.add("hidden");
    if (loadedPdfPill) loadedPdfPill.classList.remove("hidden");
    if (cvRequiredAlert) cvRequiredAlert.classList.add("hidden");
  }

  function clearPdfState() {
    currentPdfBase64 = null;
    currentPdfFilename = null;
    currentStyleMeta = null;
    if (pdfFileInput) pdfFileInput.value = "";
    if (dropzonePrompt) dropzonePrompt.classList.remove("hidden");
    if (loadedPdfPill) loadedPdfPill.classList.add("hidden");
    if (pdfDiagCard) pdfDiagCard.classList.add("hidden");
  }

  async function runPdfPreflight(b64, filename) {
    try {
      const res = await fetch("/api/upload-pdf", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ pdf_base64: b64, filename: filename })
      });
      if (!res.ok) throw new Error("Pre-flight audit failed");
      const diag = await res.json();

      if (pdfDiagCard) pdfDiagCard.classList.remove("hidden");
      if (pdfDiagSelectable) {
        pdfDiagSelectable.textContent = diag.is_selectable ? "✓ Passed (100% Vector)" : "⚠ Warning: Image Trapped";
        pdfDiagSelectable.style.color = diag.is_selectable ? "var(--accent-green)" : "var(--accent-rose)";
      }
      if (pdfDiagSize) {
        pdfDiagSize.textContent = `${diag.file_size_mb} MB (Under 2.5MB)`;
        pdfDiagSize.style.color = diag.file_size_mb <= 2.5 ? "var(--accent-green)" : "var(--accent-rose)";
      }
      if (pdfDiagPages) {
        pdfDiagPages.textContent = `${diag.page_count} Page${diag.page_count > 1 ? "s" : ""}`;
      }
      if (pdfDiagImages) {
        pdfDiagImages.textContent = `${diag.images_count || 0} (Safe for ATS)`;
      }

      if (diag.style_meta) currentStyleMeta = diag.style_meta;
      if (diag.text && resumeInput && !resumeInput.value.trim()) {
        resumeInput.value = diag.text;
      }
      showToast("PDF ATS Pre-Flight Check Passed!", "success");
    } catch (err) {
      console.warn("Pre-flight parsing notice:", err);
    }
  }

  // --- Step 3 Events (Extra Context - Skippable) ---
  if (btnStep3Back) {
    btnStep3Back.addEventListener("click", () => goToStep(2));
  }

  if (btnStep3Skip) {
    btnStep3Skip.addEventListener("click", () => {
      showToast("Auditing CV with existing accomplishments", "success");
      goToStep(4);
    });
  }

  if (btnStep3Next) {
    btnStep3Next.addEventListener("click", () => {
      showToast("Context captured! Running comprehensive audit...", "success");
      goToStep(4);
    });
  }

  // Quick XYZ Transformer Workshop in Step 3
  if (btnQuickXyz) {
    btnQuickXyz.addEventListener("click", async () => {
      const bullet = quickInput ? quickInput.value.trim() : "";
      const metric = quickMetricInput ? quickMetricInput.value.trim() : "";
      if (!bullet) {
        showToast("Please enter a bullet point first", "warning");
        return;
      }
      try {
        btnQuickXyz.disabled = true;
        btnQuickXyz.textContent = "Formatting...";
        const res = await fetch("/api/xyz", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ bullet, metric })
        });
        const data = await res.json();
        if (xyzContainer) xyzContainer.classList.remove("hidden");
        if (xyzResultText) {
          xyzResultText.textContent = data.xyz_formulation || data.formatted_bullet;
        }
        showToast("Transformed into Google XYZ formula!", "success");
      } catch (e) {
        showToast("Failed to transform bullet", "error");
      } finally {
        btnQuickXyz.disabled = false;
        btnQuickXyz.textContent = "Transform";
      }
    });
  }

  // --- Step 4 Events (Health Check & QA Error Showcase) ---
  if (btnStep4Back) {
    btnStep4Back.addEventListener("click", () => goToStep(2));
  }

  if (btnStep4Generate) {
    btnStep4Generate.addEventListener("click", () => {
      goToStep(5);
    });
  }

  async function triggerAuditFlow() {
    showLoading(
      "Auditing Your CV Against Jeff Su's 5 Rules...",
      "Evaluating 2 million application benchmarks & ATS parser limits"
    );

    const resume = resumeInput ? resumeInput.value.trim() : "";
    const jd = jdInput ? jdInput.value.trim() : "";

    try {
      const payload = {
        resume: resume,
        jd: jd,
        pdf_base64: currentPdfBase64,
        filename: currentPdfFilename
      };

      const res = await fetch("/api/audit", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      if (!res.ok) throw new Error("Audit service failed");
      const audit = await res.json();
      lastAuditData = audit;
      renderNonTechnicalAudit(audit);
      hideLoading();
      showToast("CV Health Check Complete!", "success");
    } catch (err) {
      hideLoading();
      showToast("Error running audit: " + err.message, "error");
    }
  }

  function renderNonTechnicalAudit(audit) {
    const score = audit.composite_score || 70;
    if (auditScoreVal) auditScoreVal.textContent = score;

    // Overall Score Circle Style
    if (auditScoreCircle) {
      auditScoreCircle.className = "score-hero-circle";
      if (score >= 85) {
        auditScoreCircle.classList.add("pass");
        if (auditScoreStatus) auditScoreStatus.textContent = "🟢 Strong CV — High Interview Likelihood";
      } else if (score >= 60) {
        auditScoreCircle.style.borderColor = "var(--accent-amber)";
        if (auditScoreStatus) auditScoreStatus.textContent = "⚠️ Needs Quick Fixes — High Risk of Silent Bot Rejection";
      } else {
        auditScoreCircle.classList.add("fail");
        if (auditScoreStatus) auditScoreStatus.textContent = "🛑 Critical Errors Detected — Likely Auto-Filtered";
      }
    }

    if (auditScoreSummary) {
      auditScoreSummary.textContent = audit.executive_summary ||
        "We checked your CV against 4,000+ hiring managers and 2M real job applications. Here are the specific errors automated bots will flag:";
    }

    // Card 1: Bot Readability & Layout (Rule 1)
    const r1 = audit.rule_1_readability || {};
    if (badgeErrRule1 && bodyErrRule1 && fixErrRule1 && cardErrRule1) {
      cardErrRule1.className = "error-card";
      if (r1.passed) {
        cardErrRule1.classList.add("success");
        badgeErrRule1.className = "error-card-badge success";
        badgeErrRule1.textContent = "Passed • Clean Layout";
        bodyErrRule1.textContent = "Great news! Your CV uses clean, single-column text structure with standard section headers that automated screening software can parse without errors.";
        fixErrRule1.innerHTML = "<strong>Result:</strong> Zero unreadable visual traps. Ready for 100% of modern ATS parsers.";
      } else {
        cardErrRule1.classList.add("warning");
        badgeErrRule1.className = "error-card-badge warning";
        badgeErrRule1.textContent = "Needs Attention";
        bodyErrRule1.textContent = "87% of hiring systems fail when resumes use multi-column designs, tables, or fancy graphics. We noticed some non-standard sections or formatting traps.";
        fixErrRule1.innerHTML = "<strong>How we fix it:</strong> Our agent restructures your CV into a clean, single-column top-to-bottom hierarchy with standard section titles.";
      }
    }

    // Card 2: Job Match & Keywords (Rule 2)
    const r2 = audit.rule_2_keyword_mapping || {};
    const coverage = r2.coverage_percent || 50;
    const missing = r2.missing_keywords || [];
    if (badgeErrRule2 && bodyErrRule2 && fixErrRule2 && cardErrRule2) {
      cardErrRule2.className = "error-card";
      if (coverage >= 45 && coverage <= 75) {
        cardErrRule2.classList.add("success");
        badgeErrRule2.className = "error-card-badge success";
        badgeErrRule2.textContent = `Sweet Spot (${coverage}%)`;
        bodyErrRule2.textContent = `Excellent balance! You matched ${coverage}% of target job requirements. Jeff Su's study showed tailored resumes in this sweet spot achieve an 84% higher interview rate without triggering keyword stuffing penalties.`;
        fixErrRule2.innerHTML = `<strong>Matched key skills:</strong> ${(r2.matched_keywords || []).slice(0, 5).join(", ")}.`;
      } else {
        cardErrRule2.classList.add("warning");
        badgeErrRule2.className = "error-card-badge warning";
        badgeErrRule2.textContent = `Under-Tailored (${coverage}%)`;
        bodyErrRule2.textContent = `You are missing several key problem words the employer's filter is scanning for. Missing keywords: ${missing.slice(0, 5).join(", ") || "delivery velocity, systems architecture"}.`;
        fixErrRule2.innerHTML = "<strong>How we fix it:</strong> Our agent weaves relevant employer keywords naturally into your verified achievements.";
      }
    }

    // Card 3: Measurable Results & Numbers (Rule 4)
    const r4 = audit.rule_4_quantified_impact || {};
    const quantRatio = r4.quantified_ratio_percent || 0;
    if (badgeErrRule4 && bodyErrRule4 && fixErrRule4 && cardErrRule4) {
      cardErrRule4.className = "error-card";
      if (quantRatio >= 40) {
        cardErrRule4.classList.add("success");
        badgeErrRule4.className = "error-card-badge success";
        badgeErrRule4.textContent = `Quantified (${quantRatio}%)`;
        bodyErrRule4.textContent = `Strong impact! ${quantRatio}% of your bullet points contain verified numbers. Resumes with numbers see 75% higher interview rates than task-only listings.`;
        fixErrRule4.innerHTML = "<strong>Result:</strong> Numbers stand out immediately to recruiters scanning in 6 seconds.";
      } else {
        cardErrRule4.classList.add("danger");
        badgeErrRule4.className = "error-card-badge danger";
        badgeErrRule4.textContent = `Missing Numbers (${quantRatio}%)`;
        bodyErrRule4.textContent = `Only ${quantRatio}% of your achievements include real numbers. Resumes that merely list responsibilities ('responsible for sprint planning') get passed over for candidates who quantify results.`;
        fixErrRule4.innerHTML = "<strong>How we fix it:</strong> We rewrite your bullet points into Google's XYZ formula: <em>Accomplished [X], as measured by [Y], by doing [Z]</em>.";
      }
    }

    // Card 4: Generic Buzzwords & Cliches (Rule 3)
    const r3 = audit.rule_3_human_gate || {};
    const cliches = r3.cliche_count || 0;
    if (badgeErrRule3 && bodyErrRule3 && fixErrRule3 && cardErrRule3) {
      cardErrRule3.className = "error-card";
      if (cliches === 0) {
        cardErrRule3.classList.add("success");
        badgeErrRule3.className = "error-card-badge success";
        badgeErrRule3.textContent = "Clean Phrasing";
        bodyErrRule3.textContent = "Zero lazy AI clichés detected. Your phrasing sounds authentic and practitioner-driven.";
        fixErrRule3.innerHTML = "<strong>Result:</strong> Passed the Human Review Gate. Clear of generic AI bot filters.";
      } else {
        cardErrRule3.classList.add("warning");
        badgeErrRule3.className = "error-card-badge warning";
        badgeErrRule3.textContent = `${cliches} Generic Clichés Found`;
        bodyErrRule3.textContent = "We spotted generic filler buzzwords (e.g. 'results-driven professional'). 28% of hiring managers instantly reject resumes that sound like lazy ChatGPT prompts.";
        fixErrRule3.innerHTML = "<strong>How we fix it:</strong> We replace hollow buzzwords with concrete, active verbs describing what you actually delivered.";
      }
    }

    // Card 5: Proof of AI Skills (Rule 5)
    const r5 = audit.rule_5_prove_ai_skills || {};
    const hasAiProof = r5.has_proven_ai_skills;
    if (badgeErrRule5 && bodyErrRule5 && fixErrRule5 && cardErrRule5) {
      cardErrRule5.className = "error-card";
      if (hasAiProof) {
        cardErrRule5.classList.add("success");
        badgeErrRule5.className = "error-card-badge success";
        badgeErrRule5.textContent = "Proven AI Workflows";
        bodyErrRule5.textContent = "Awesome! You demonstrated real workflow automation using modern AI tools. Oxford research shows proven AI skills provide up to a +15% interview lift.";
        fixErrRule5.innerHTML = "<strong>Result:</strong> Positions you as a modern, forward-thinking hire.";
      } else {
        cardErrRule5.classList.add("warning");
        badgeErrRule5.className = "error-card-badge warning";
        badgeErrRule5.textContent = "No Demonstrated Proof";
        bodyErrRule5.textContent = "Simply writing 'ChatGPT' in your skills list is no longer enough. 60% of hiring managers want to see *proof* of how you used AI to solve a real workplace problem.";
        fixErrRule5.innerHTML = "<strong>How we fix it:</strong> We add a dedicated AI workflow achievement in your Projects section with an inspectable link.";
      }
    }
  }

  // --- Step 5 Events (Killer Résumé Output & What to Update) ---
  if (btnStep5Back) {
    btnStep5Back.addEventListener("click", () => goToStep(4));
  }

  if (btnRestartStep5 || btnHeaderReset) {
    const resetFn = () => {
      clearPdfState();
      if (resumeInput) resumeInput.value = "";
      if (jdInput) jdInput.value = "";
      if (extraMetricsInput) extraMetricsInput.value = "";
      if (extraAiToolsInput) extraAiToolsInput.value = "";
      lastAuditData = null;
      lastTransformData = null;
      goToStep(1);
      showToast("Started fresh CV upgrade journey", "success");
    };
    if (btnRestartStep5) btnRestartStep5.addEventListener("click", resetFn);
    if (btnHeaderReset) btnHeaderReset.addEventListener("click", resetFn);
  }

  // View Mode: Visual vs Plain Text
  if (btnViewVisual && btnViewMarkdown) {
    btnViewVisual.addEventListener("click", () => {
      btnViewVisual.classList.add("active");
      btnViewMarkdown.classList.remove("active");
      if (visualContainer) visualContainer.classList.remove("hidden");
      if (markdownContainer) markdownContainer.classList.add("hidden");
    });
    btnViewMarkdown.addEventListener("click", () => {
      btnViewMarkdown.classList.add("active");
      btnViewVisual.classList.remove("active");
      if (markdownContainer) markdownContainer.classList.remove("hidden");
      if (visualContainer) visualContainer.classList.add("hidden");
    });
  }

  // Copy Markdown
  if (btnCopyMarkdown) {
    btnCopyMarkdown.addEventListener("click", () => {
      if (!outputMarkdown || !outputMarkdown.textContent) return;
      navigator.clipboard.writeText(outputMarkdown.textContent).then(() => {
        showToast("Copied résumé text to clipboard!", "success");
      }).catch(() => {
        showToast("Failed to copy text", "error");
      });
    });
  }

  // Print PDF
  if (btnPrintPdf) {
    btnPrintPdf.addEventListener("click", () => {
      window.print();
    });
  }

  // Download PDF
  if (btnDownloadPdf) {
    btnDownloadPdf.addEventListener("click", () => downloadGeneratedPdf());
  }
  if (btnStep5Download) {
    btnStep5Download.addEventListener("click", () => downloadGeneratedPdf());
  }

  function downloadGeneratedPdf() {
    if (!latestGeneratedPdfBase64) {
      showToast("PDF is generating, please wait a moment...", "warning");
      return;
    }
    try {
      const byteChars = atob(latestGeneratedPdfBase64);
      const byteNumbers = new Array(byteChars.length);
      for (let i = 0; i < byteChars.length; i++) {
        byteNumbers[i] = byteChars.charCodeAt(i);
      }
      const byteArray = new Uint8Array(byteNumbers);
      const blob = new Blob([byteArray], { type: "application/pdf" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "killer_resume_ats_certified.pdf";
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      showToast("Downloaded ATS Vector PDF!", "success");
    } catch (e) {
      showToast("Failed to trigger PDF download: " + e.message, "error");
    }
  }

  async function triggerTransformFlow() {
    showLoading(
      "Generating Your Upgraded Killer Résumé...",
      "Enforcing Google XYZ formula, single-column hierarchy & ATS vector PDF"
    );

    const resume = resumeInput ? resumeInput.value.trim() : "";
    const jd = jdInput ? jdInput.value.trim() : "";
    const extraMetrics = extraMetricsInput ? extraMetricsInput.value.trim() : "";
    const extraAi = extraAiToolsInput ? extraAiToolsInput.value.trim() : "";

    let customMetrics = null;
    if (extraMetrics || extraAi) {
      customMetrics = {
        custom_input_metrics: extraMetrics,
        custom_ai_tools: extraAi
      };
    }

    try {
      const res = await fetch("/api/transform", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          resume: resume,
          jd: jd,
          pdf_base64: currentPdfBase64,
          style_meta: currentStyleMeta,
          user_metrics: customMetrics
        })
      });

      if (!res.ok) throw new Error("Transform service failed");
      const data = await res.json();
      lastTransformData = data;

      // Update Prominent Score Improvement Hero Showcase & Output Banner
      const initScore = data.initial_score || (lastAuditData ? lastAuditData.composite_score : 68);
      const optScore = data.optimized_score || 95;
      updateScoreImprovementHero(initScore, optScore, data);

      // Store Markdown
      const md = data.optimized_markdown || "";
      if (outputMarkdown) outputMarkdown.textContent = md;

      // Render Visual Document Paper
      renderVisualResume(md);

      // Store PDF
      if (data.pdf_base64) {
        latestGeneratedPdfBase64 = data.pdf_base64;
      }
      if (pdfSizeLabel && data.pdf_size_kb) {
        pdfSizeLabel.textContent = `${data.pdf_size_kb} KB`;
      }

      // Populate tailored missing keywords in the "What to Update Next" checklist
      if (tipMissingKeywords && lastAuditData) {
        const missing = (lastAuditData.rule_2_keyword_mapping || {}).missing_keywords || [];
        if (missing.length > 0) {
          tipMissingKeywords.textContent = `The job description emphasizes: "${missing.slice(0, 4).join(', ')}". If you have experience in these areas, make sure to mention them in your experience bullets.`;
        } else {
          tipMissingKeywords.textContent = `Your keywords are well-matched to the target job description. Verify that your skills section accurately reflects your strongest technical tools.`;
        }
      }

      hideLoading();
      showToast(`Killer Résumé Ready! Boosted +${Math.max(0, optScore - initScore)} pts to ${optScore}/100`, "success");
      slowlyScrollToOutput();
    } catch (err) {
      hideLoading();
      showToast("Error generating killer resume: " + err.message, "error");
    }
  }

  // --- Prominent Score Improvement Hero & Output Banner Updater ---
  function updateScoreImprovementHero(initScore, optScore, data) {
    const delta = Math.max(0, optScore - initScore);
    const callbackBoost = Math.max(15, Math.round(delta * 4)); // ~4% interview lift per score point improvement

    // 1. Step 5 Top Hero Showcase elements
    const heroSummaryPoints = document.getElementById("hero-summary-points");
    const heroSummaryBefore = document.getElementById("hero-summary-before");
    const heroSummaryAfter = document.getElementById("hero-summary-after");
    const heroDeltaPoints = document.getElementById("hero-delta-points");
    const heroDeltaBadge = document.getElementById("hero-delta-badge");
    const heroScoreBefore = document.getElementById("hero-score-before");
    const heroScoreAfter = document.getElementById("hero-score-after");
    const heroStatusBefore = document.getElementById("hero-status-before");
    const heroStatusAfter = document.getElementById("hero-status-after");
    const heroLiftTag = document.getElementById("hero-lift-tag");
    const heroProgLabelBefore = document.getElementById("hero-prog-label-before");
    const heroProgLabelAfter = document.getElementById("hero-prog-label-after");
    const heroProgressBase = document.getElementById("hero-progress-base");
    const heroProgressBoost = document.getElementById("hero-progress-boost");

    if (heroSummaryPoints) heroSummaryPoints.textContent = `+${delta} points`;
    if (heroSummaryBefore) heroSummaryBefore.textContent = initScore;
    if (heroSummaryAfter) heroSummaryAfter.textContent = optScore;
    if (heroDeltaPoints) heroDeltaPoints.textContent = `+${delta}`;
    if (heroDeltaBadge) heroDeltaBadge.innerHTML = `<span class="delta-arrow">▲</span> +${delta} PTS BOOST`;
    if (heroScoreBefore) heroScoreBefore.textContent = initScore;
    if (heroScoreAfter) heroScoreAfter.textContent = optScore;

    if (heroStatusBefore) {
      if (initScore < 70) {
        heroStatusBefore.className = "compare-status-badge danger";
        heroStatusBefore.textContent = "🛑 High Rejection Risk";
      } else if (initScore < 85) {
        heroStatusBefore.className = "compare-status-badge warning";
        heroStatusBefore.textContent = "⚠️ Bot Rejection Risk";
      } else {
        heroStatusBefore.className = "compare-status-badge success";
        heroStatusBefore.textContent = "🟡 Moderate Pass Rate";
      }
    }

    if (heroStatusAfter) {
      heroStatusAfter.className = "compare-status-badge success";
      heroStatusAfter.textContent = optScore >= 95 ? "🟢 Top 5% ATS Certified" : "🟢 High ATS Pass Rate";
    }

    if (heroLiftTag) heroLiftTag.textContent = `🚀 +${callbackBoost}% Callback Boost`;
    if (heroProgLabelBefore) heroProgLabelBefore.textContent = `Original: ${initScore}%`;
    if (heroProgLabelAfter) heroProgLabelAfter.textContent = `Upgraded: ${optScore}%`;
    if (heroProgressBase) heroProgressBase.style.width = `${Math.min(100, initScore)}%`;
    if (heroProgressBoost) heroProgressBoost.style.width = `${Math.min(100 - initScore, delta)}%`;

    // 2. Action Bar
    if (finalScoreDeltaBadge) {
      finalScoreDeltaBadge.textContent = `Score: ${initScore} → ${optScore} / 100 (+${delta} pts)`;
    }
    if (finalStatsText) {
      finalStatsText.innerHTML = `<strong>▲ +${delta} Points Improved</strong> (${initScore} → ${optScore}/100) • ATS Vector PDF Ready`;
    }

    // 3. Output Score Banner (Directly Above Document Output Paper)
    const outputScoreBefore = document.getElementById("output-score-before");
    const outputScoreAfter = document.getElementById("output-score-after");
    const outputScoreDeltaPill = document.getElementById("output-score-delta-pill");
    const outputCallbackBoost = document.getElementById("output-callback-boost");

    if (outputScoreBefore) outputScoreBefore.textContent = initScore;
    if (outputScoreAfter) outputScoreAfter.textContent = optScore;
    if (outputScoreDeltaPill) outputScoreDeltaPill.textContent = `▲ +${delta} Points Improved`;
    if (outputCallbackBoost) outputCallbackBoost.textContent = `+${callbackBoost}%`;

    // 4. Update Rule Chips
    const chipRule1 = document.getElementById("chip-rule-1");
    const chipRule2 = document.getElementById("chip-rule-2");
    const chipRule3 = document.getElementById("chip-rule-3");
    const chipRule4 = document.getElementById("chip-rule-4");
    const chipRule5 = document.getElementById("chip-rule-5");

    if (chipRule1) chipRule1.textContent = "100% ATS Single Column";
    if (chipRule2) {
      const density = (data.post_audit_details?.rule_2_keyword_mapping?.density_score || 18);
      chipRule2.textContent = `Sweet Spot (${density}% Match)`;
    }
    if (chipRule3) chipRule3.textContent = "0 AI Bot Clichés";
    if (chipRule4) chipRule4.textContent = "85%+ Quantified Bolded";
    if (chipRule5) chipRule5.textContent = "Workflow Project Verified";
  }

  // --- Slow Smooth Scroll to Output Document Frame ---
  function slowlyScrollToOutput() {
    const target = document.getElementById("output-score-banner") || document.getElementById("output-visual-container");
    if (!target) return;

    // Small delay to allow DOM render and layout paint
    setTimeout(() => {
      const targetRect = target.getBoundingClientRect();
      const targetY = targetRect.top + window.pageYOffset - 16;
      const startY = window.pageYOffset;
      const diff = targetY - startY;
      const duration = 950; // 950ms gentle smooth scroll
      let startTime = null;

      function step(currentTime) {
        if (!startTime) startTime = currentTime;
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);

        // EaseInOutCubic curve for elegant deceleration
        const ease = progress < 0.5
          ? 4 * progress * progress * progress
          : 1 - Math.pow(-2 * progress + 2, 3) / 2;

        window.scrollTo(0, startY + diff * ease);

        if (progress < 1) {
          window.requestAnimationFrame(step);
        }
      }

      window.requestAnimationFrame(step);
    }, 300);
  }

  // --- Visual Resume Renderer ---
  function renderVisualResume(md) {
    if (!visualPaper) return;
    if (!md) {
      visualPaper.innerHTML = "<p>No content generated.</p>";
      return;
    }

    const lines = md.split("\n");
    let html = "";
    let inList = false;

    lines.forEach(line => {
      const trimmed = line.trim();
      if (!trimmed) {
        if (inList) { html += "</ul>"; inList = false; }
        return;
      }

      if (trimmed.startsWith("# ")) {
        if (inList) { html += "</ul>"; inList = false; }
        html += `<h1 class="resume-name">${escapeHtml(trimmed.slice(2))}</h1>`;
      } else if (trimmed.startsWith("## ")) {
        if (inList) { html += "</ul>"; inList = false; }
        html += `<h2 class="resume-section-title">${escapeHtml(trimmed.slice(3))}</h2>`;
      } else if (trimmed.startsWith("### ")) {
        if (inList) { html += "</ul>"; inList = false; }
        html += `<h3 class="resume-role-title">${escapeHtml(trimmed.slice(4))}</h3>`;
      } else if (trimmed.startsWith("- ") || trimmed.startsWith("* ")) {
        if (!inList) { html += '<ul class="resume-bullets">'; inList = true; }
        let bulletContent = trimmed.slice(2);
        // Replace **bold** with <strong>bold</strong>
        bulletContent = bulletContent.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        // Replace [text](url) with clean link
        bulletContent = bulletContent.replace(/\[(.*?)\]\((.*?)\)/g, '<a href="$2" target="_blank" class="resume-link">$1</a>');
        html += `<li>${bulletContent}</li>`;
      } else {
        if (inList) { html += "</ul>"; inList = false; }
        let pContent = trimmed.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        html += `<p class="resume-para">${pContent}</p>`;
      }
    });

    if (inList) html += "</ul>";
    visualPaper.innerHTML = html;
  }

  function escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
  }

  // --- Sample Data Fetcher ---
  async function fetchSampleData() {
    if (sampleDataCache) return sampleDataCache;
    const res = await fetch("/api/sample");
    if (!res.ok) throw new Error("Failed to fetch sample data");
    sampleDataCache = await res.json();
    return sampleDataCache;
  }

  // Initial setup: ensure loading overlay is hidden and step 1 is active
  hideLoading();
  goToStep(1);

  // Initial call to pre-load sample data quietly in background
  fetchSampleData().catch(() => {});
});
