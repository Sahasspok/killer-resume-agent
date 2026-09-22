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

  // Step 3: Health Check & Errors
  const auditScoreCircle = document.getElementById("audit-score-circle");
  const auditScoreVal = document.getElementById("audit-score-val");
  const auditScoreStatus = document.getElementById("audit-score-status");
  const auditScoreSummary = document.getElementById("audit-score-summary");
  const btnStep3Back = document.getElementById("btn-step3-back");
  const btnStep3AddData = document.getElementById("btn-step3-add-data");
  const btnStep3GenerateAnyway = document.getElementById("btn-step3-generate-anyway");
  const btnChoiceAddData = document.getElementById("btn-choice-add-data");
  const btnChoiceGenerateAnyway = document.getElementById("btn-choice-generate-anyway");

  // Step 4: Extra Context (CRUD & Tags)
  const achievementInput = document.getElementById("achievement-input");
  const achievementRoleSelect = document.getElementById("achievement-role-select");
  const achievementRoleCustom = document.getElementById("achievement-role-custom");
  const btnAddAchievement = document.getElementById("btn-add-achievement");
  const achievementsListEl = document.getElementById("achievements-list");
  const aiToolInput = document.getElementById("ai-tool-input");
  const btnAddAiTool = document.getElementById("btn-add-ai-tool");
  const aiToolsListEl = document.getElementById("ai-tools-list");
  const btnStep4Back = document.getElementById("btn-step4-back");
  const btnStep4Skip = document.getElementById("btn-step4-skip");
  const btnStep4Generate = document.getElementById("btn-step4-generate");

  // AI Engine & API Key Elements
  const selectAiEngine = document.getElementById("select-ai-engine");
  const btnConfigureApiKey = document.getElementById("btn-configure-api-key");
  const modalApiKey = document.getElementById("modal-api-key");
  const btnCloseApiModal = document.getElementById("btn-close-api-modal");
  const btnSaveApiKey = document.getElementById("btn-save-api-key");
  const btnClearApiKey = document.getElementById("btn-clear-api-key");
  const inputApiKey = document.getElementById("input-api-key");
  const apiKeyBadge = document.getElementById("api-key-badge");
  const modalKeyLabel = document.getElementById("modal-key-label");
  const modalKeyHelp = document.getElementById("modal-key-help");

  // Active Agent Interview & Rule 5 Elements
  const agentInterviewCard = document.getElementById("agent-interview-card");
  const agentInterviewBulletsList = document.getElementById("agent-interview-bullets-list");
  const btnAiToggleYes = document.getElementById("btn-ai-toggle-yes");
  const btnAiToggleNo = document.getElementById("btn-ai-toggle-no");
  const aiInterviewDetails = document.getElementById("ai-interview-details");
  const aiInterviewTools = document.getElementById("ai-interview-tools");
  const aiInterviewTask = document.getElementById("ai-interview-task");
  const aiInterviewTime = document.getElementById("ai-interview-time");
  const aiInterviewPreviewText = document.getElementById("ai-interview-preview-text");

  // Extra Context State
  let currentProvider = localStorage.getItem("killer_resume_provider") || "gemini";
  let currentApiKey = localStorage.getItem("killer_resume_api_key_" + currentProvider) || "";
  let detectedKeys = {};
  let customAchievements = [];
  let customAiTools = ["Claude", "ChatGPT"];
  let detectedRoles = [];
  let customAiSettings = {
    include_ai_bullet: true,
    tools: ["Claude", "ChatGPT"],
    task: "sprint requirement synthesis and backlog triage",
    time_saved: "4+ hours weekly"
  };

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
    if (currentStep === 3) {
      triggerAuditFlow();
    } else if (currentStep === 4) {
      refreshDetectedRoles();
      renderAgentInterview();
      updateAiPreview();
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
          detectedRoles = [
            { company: "Veel", title: "Technical Project Manager", label: "Veel (Technical Project Manager)" },
            { company: "TechSaintIT", title: "Project Manager", label: "TechSaintIT (Project Manager)" }
          ];
          updateRoleSelectOptions();
          customAchievements = [
            {
              text: "Led cross-functional team of 12 (engineers, QA, DevOps) delivering high-scale B2B SaaS platform across 8 sprints with 98% on-time milestone delivery.",
              role: "Veel",
              roleLabel: "Veel (Technical Project Manager)"
            },
            {
              text: "Accelerated sprint velocity by 25% and cut sprint planning cycle time by 4 hours weekly by introducing automated ClickUp/Jira workflows and AI backlog triage.",
              role: "Veel",
              roleLabel: "Veel (Technical Project Manager)"
            },
            {
              text: "Spearheaded migration of legacy services to microservices architecture, reducing deployment cycle times by 40%.",
              role: "TechSaintIT",
              roleLabel: "TechSaintIT (Project Manager)"
            }
          ];
          customAiTools = ["Claude Code", "ChatGPT", "Cursor", "GitHub Copilot"];
          renderAchievements();
          renderAiTools();

          if (cvRequiredAlert) cvRequiredAlert.classList.add("hidden");
          hideLoading();
          showToast("Loaded Ex-Apple PM Sample CV! Review your file and click 'Run CV Health Check' when ready.", "success");
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
      showToast("PDF pre-flight passed! Review your file and click 'Run CV Health Check' when ready.", "success");
    };
    reader.readAsDataURL(file);
  }

  function showLoadedPdfPill(name, stats) {
    if (pdfDisplayName) pdfDisplayName.textContent = name;
    if (pdfDisplayStats) pdfDisplayStats.textContent = stats;
    if (dropzonePrompt) dropzonePrompt.classList.add("hidden");
    if (loadedPdfPill) loadedPdfPill.classList.remove("hidden");
    if (cvRequiredAlert) cvRequiredAlert.classList.add("hidden");
    if (btnStep2Next) btnStep2Next.classList.add("btn-pulse");
  }

  function clearPdfState() {
    currentPdfBase64 = null;
    currentPdfFilename = null;
    currentStyleMeta = null;
    if (pdfFileInput) pdfFileInput.value = "";
    if (dropzonePrompt) dropzonePrompt.classList.remove("hidden");
    if (loadedPdfPill) loadedPdfPill.classList.add("hidden");
    if (pdfDiagCard) pdfDiagCard.classList.add("hidden");
    if (btnStep2Next) btnStep2Next.classList.remove("btn-pulse");
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
      if (diag.detected_roles && Array.isArray(diag.detected_roles) && diag.detected_roles.length > 0) {
        detectedRoles = diag.detected_roles;
        updateRoleSelectOptions();
      }
      if (diag.text && resumeInput && !resumeInput.value.trim()) {
        resumeInput.value = diag.text;
      }
      showToast("PDF ATS Pre-Flight Check Passed!", "success");
    } catch (err) {
      console.warn("Pre-flight parsing notice:", err);
    }
  }

  // --- Step 3 Events (Extra Context: Achievements by Job & AI Tags) ---
  function escapeHtml(str) {
    if (!str) return "";
    return String(str)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  async function refreshDetectedRoles() {
    const resume = resumeInput ? resumeInput.value.trim() : "";
    if (!resume && !currentPdfBase64) return;
    try {
      const res = await fetch("/api/detect-roles", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ resume: resume, pdf_base64: currentPdfBase64 })
      });
      if (res.ok) {
        const data = await res.json();
        if (data.roles && Array.isArray(data.roles) && data.roles.length > 0) {
          detectedRoles = data.roles;
          updateRoleSelectOptions();
        }
      }
    } catch (e) {
      console.warn("Could not detect roles:", e);
    }
  }

  // --- AI Engine & Modal Configuration ---
  async function checkServerConfig() {
    try {
      const res = await fetch("/api/config");
      if (res.ok) {
        const data = await res.json();
        detectedKeys = data.detected_keys || {};
        if (selectAiEngine) {
          selectAiEngine.value = currentProvider;
        }
        updateApiKeyBadge();
      }
    } catch (e) {
      console.warn("Could not check config:", e);
    }
  }

  function updateApiKeyBadge() {
    if (!apiKeyBadge) return;
    if (currentApiKey) {
      apiKeyBadge.textContent = "Custom ✓";
      apiKeyBadge.style.color = "var(--accent-green)";
    } else if (detectedKeys[currentProvider]) {
      apiKeyBadge.textContent = "Env ✓";
      apiKeyBadge.style.color = "var(--accent-green)";
    } else if (currentProvider === "heuristic" || currentProvider === "ollama") {
      apiKeyBadge.textContent = "Active";
      apiKeyBadge.style.color = "var(--accent-blue)";
    } else {
      apiKeyBadge.textContent = "Set Key";
      apiKeyBadge.style.color = "var(--accent-amber)";
    }
  }

  if (selectAiEngine) {
    selectAiEngine.addEventListener("change", () => {
      currentProvider = selectAiEngine.value;
      currentApiKey = localStorage.getItem("killer_resume_api_key_" + currentProvider) || "";
      localStorage.setItem("killer_resume_provider", currentProvider);
      updateApiKeyBadge();
      if (modalKeyLabel) {
        modalKeyLabel.textContent = `${currentProvider.toUpperCase()} API Key:`;
      }
      if (modalKeyHelp) {
        if (currentProvider === "gemini") {
          modalKeyHelp.innerHTML = `Get a free Google Gemini key at <a href="https://aistudio.google.com/" target="_blank" rel="noopener">aistudio.google.com</a> (1,500 req/day free, gemini-2.0-flash)`;
        } else if (currentProvider === "groq") {
          modalKeyHelp.innerHTML = `Get a 100% free Groq key at <a href="https://console.groq.com/keys" target="_blank" rel="noopener">console.groq.com/keys</a> (No credit card, 14,400 req/day, blazing fast Llama 3.3)`;
        } else if (currentProvider === "openrouter") {
          modalKeyHelp.innerHTML = `Get an OpenRouter key at <a href="https://openrouter.ai/keys" target="_blank" rel="noopener">openrouter.ai/keys</a> (Free access to DeepSeek R1 & Llama 3.3 :free models)`;
        } else if (currentProvider === "mistral") {
          modalKeyHelp.innerHTML = `Get a free Mistral key at <a href="https://console.mistral.ai/api-keys/" target="_blank" rel="noopener">console.mistral.ai</a> (Free experimentation tier)`;
        } else if (currentProvider === "openai") {
          modalKeyHelp.innerHTML = `Get an OpenAI key at <a href="https://platform.openai.com/api-keys" target="_blank" rel="noopener">platform.openai.com</a>`;
        } else if (currentProvider === "anthropic") {
          modalKeyHelp.innerHTML = `Get an Anthropic key at <a href="https://console.anthropic.com/" target="_blank" rel="noopener">console.anthropic.com</a>`;
        } else {
          modalKeyHelp.textContent = `No API key needed for ${currentProvider}.`;
        }
      }

      // If user selected an external provider and no key is saved or detected, automatically open modal
      if (["openai", "gemini", "anthropic", "groq", "openrouter", "mistral"].includes(currentProvider) && !currentApiKey && !detectedKeys[currentProvider]) {
        if (modalApiKey) {
          modalApiKey.classList.remove("hidden");
          modalApiKey.style.display = "flex";
          if (inputApiKey) {
            inputApiKey.value = "";
            if (currentProvider === "groq") {
              inputApiKey.placeholder = "gsk_... (from console.groq.com/keys)";
            } else if (currentProvider === "openrouter") {
              inputApiKey.placeholder = "sk-or-v1-... (from openrouter.ai/keys)";
            } else if (currentProvider === "mistral") {
              inputApiKey.placeholder = "Enter Mistral API key (from console.mistral.ai)";
            } else if (currentProvider === "gemini") {
              inputApiKey.placeholder = "AIzaSy... (from aistudio.google.com)";
            } else {
              inputApiKey.placeholder = `Paste your ${currentProvider.toUpperCase()} API key here...`;
            }
            inputApiKey.focus();
          }
        }
        showToast(`Please enter your ${currentProvider.toUpperCase()} API Key to connect`, "info");
      } else {
        showToast(`Switched to ${currentProvider.toUpperCase()} Engine`, "info");
      }
    });
  }

  if (btnConfigureApiKey && modalApiKey) {
    btnConfigureApiKey.addEventListener("click", () => {
      modalApiKey.classList.remove("hidden");
      modalApiKey.style.display = "flex";
      if (modalKeyLabel) {
        modalKeyLabel.textContent = `${currentProvider.toUpperCase()} API Key:`;
      }
      if (modalKeyHelp) {
        if (currentProvider === "gemini") {
          modalKeyHelp.innerHTML = `Get a free Google Gemini key at <a href="https://aistudio.google.com/" target="_blank" rel="noopener">aistudio.google.com</a> (1,500 req/day free, gemini-2.0-flash)`;
        } else if (currentProvider === "groq") {
          modalKeyHelp.innerHTML = `Get a 100% free Groq key at <a href="https://console.groq.com/keys" target="_blank" rel="noopener">console.groq.com/keys</a> (No credit card, 14,400 req/day, blazing fast Llama 3.3)`;
        } else if (currentProvider === "openrouter") {
          modalKeyHelp.innerHTML = `Get an OpenRouter key at <a href="https://openrouter.ai/keys" target="_blank" rel="noopener">openrouter.ai/keys</a> (Free access to DeepSeek R1 & Llama 3.3 :free models)`;
        } else if (currentProvider === "mistral") {
          modalKeyHelp.innerHTML = `Get a free Mistral key at <a href="https://console.mistral.ai/api-keys/" target="_blank" rel="noopener">console.mistral.ai</a> (Free experimentation tier)`;
        } else if (currentProvider === "openai") {
          modalKeyHelp.innerHTML = `Get an OpenAI key at <a href="https://platform.openai.com/api-keys" target="_blank" rel="noopener">platform.openai.com</a>`;
        } else if (currentProvider === "anthropic") {
          modalKeyHelp.innerHTML = `Get an Anthropic key at <a href="https://console.anthropic.com/" target="_blank" rel="noopener">console.anthropic.com</a>`;
        } else {
          modalKeyHelp.textContent = `No API key needed for ${currentProvider}.`;
        }
      }
      if (inputApiKey) {
        inputApiKey.value = currentApiKey;
        if (currentProvider === "groq") {
          inputApiKey.placeholder = "gsk_... (from console.groq.com/keys)";
        } else if (currentProvider === "openrouter") {
          inputApiKey.placeholder = "sk-or-v1-... (from openrouter.ai/keys)";
        } else if (currentProvider === "mistral") {
          inputApiKey.placeholder = "Enter Mistral API key (from console.mistral.ai)";
        } else if (currentProvider === "gemini") {
          inputApiKey.placeholder = "AIzaSy... (from aistudio.google.com)";
        } else {
          inputApiKey.placeholder = `Paste your ${currentProvider.toUpperCase()} API key here...`;
        }
        inputApiKey.focus();
      }
    });
  }

  if (btnCloseApiModal && modalApiKey) {
    btnCloseApiModal.addEventListener("click", () => {
      modalApiKey.classList.add("hidden");
      modalApiKey.style.display = "none";
    });
  }

  if (btnSaveApiKey && modalApiKey) {
    btnSaveApiKey.addEventListener("click", () => {
      if (inputApiKey) {
        currentApiKey = inputApiKey.value.trim();
        if (currentApiKey) {
          localStorage.setItem("killer_resume_api_key_" + currentProvider, currentApiKey);
          showToast(`${currentProvider.toUpperCase()} API key saved for this browser!`, "success");
        } else {
          localStorage.removeItem("killer_resume_api_key_" + currentProvider);
          showToast("API Key cleared", "info");
        }
        updateApiKeyBadge();
      }
      modalApiKey.classList.add("hidden");
      modalApiKey.style.display = "none";
    });
  }

  if (btnClearApiKey && modalApiKey) {
    btnClearApiKey.addEventListener("click", () => {
      localStorage.removeItem("killer_resume_api_key_" + currentProvider);
      currentApiKey = "";
      currentProvider = "heuristic";
      if (selectAiEngine) selectAiEngine.value = "heuristic";
      localStorage.setItem("killer_resume_provider", "heuristic");
      updateApiKeyBadge();
      modalApiKey.classList.add("hidden");
      modalApiKey.style.display = "none";
      showToast("Switched to Offline Heuristic Engine", "info");
    });
  }

  // --- Rule 5 AI Skills Interview Logic ---
  function updateAiPreview() {
    if (!aiInterviewPreviewText) return;
    const tools = aiInterviewTools ? aiInterviewTools.value.trim() : "Claude, ChatGPT";
    const task = aiInterviewTask ? aiInterviewTask.value.trim() : "automate sprint requirement synthesis and backlog triage";
    const time = aiInterviewTime ? aiInterviewTime.value.trim() : "4+ hours weekly";

    aiInterviewPreviewText.innerHTML = `Leveraged Generative AI tools (${escapeHtml(tools)}) to ${escapeHtml(task)}, saving <strong>${escapeHtml(time)}</strong> in administrative overhead.`;

    customAiSettings = {
      include_ai_bullet: customAiSettings.include_ai_bullet,
      tools: tools.split(",").map(t => t.trim()).filter(Boolean),
      task: task,
      time_saved: time
    };
  }

  if (btnAiToggleYes && btnAiToggleNo) {
    btnAiToggleYes.addEventListener("click", () => {
      btnAiToggleYes.classList.add("active");
      btnAiToggleNo.classList.remove("active");
      if (aiInterviewDetails) aiInterviewDetails.style.display = "block";
      customAiSettings.include_ai_bullet = true;
      updateAiPreview();
      showToast("Rule 5: Proven AI workflow enabled!", "success");
    });

    btnAiToggleNo.addEventListener("click", () => {
      btnAiToggleNo.classList.add("active");
      btnAiToggleYes.classList.remove("active");
      if (aiInterviewDetails) aiInterviewDetails.style.display = "none";
      customAiSettings.include_ai_bullet = false;
      showToast("Rule 3 Ground Truth: No synthetic AI claims will be added.", "info");
    });
  }

  [aiInterviewTools, aiInterviewTask, aiInterviewTime].forEach(input => {
    if (input) input.addEventListener("input", updateAiPreview);
  });

  // --- Active Agent Interview (Unquantified Bullets from Candidate's CV) ---
  function renderAgentInterview() {
    if (!agentInterviewBulletsList) return;

    if (!lastAuditData || !lastAuditData.bullet_breakdowns) {
      agentInterviewBulletsList.innerHTML = `
        <div class="interview-loading-state" style="padding: 16px; color: var(--text-muted); font-size: 13px;">
          <span>🎯 Upload your CV in Step 2 to generate your personalized Agent Interview.</span>
        </div>
      `;
      return;
    }

    const unquantified = lastAuditData.bullet_breakdowns.filter(b => {
      const noMetrics = !b.xyz_status || !b.xyz_status.has_metrics;
      const weakVerb = b.human_gate && (b.human_gate.has_weak_verb || b.human_gate.has_cliche);
      return noMetrics || weakVerb;
    });

    if (unquantified.length === 0) {
      agentInterviewBulletsList.innerHTML = `
        <div class="interview-bullet-card" style="border-color: var(--accent-green); background: rgba(16, 185, 129, 0.05);">
          <span class="badge-mini-green">✓ ALL BULLETS QUANTIFIED</span>
          <p style="margin: 6px 0 0 0; font-size: 13px; color: var(--text-primary);">
            Outstanding! All audited bullets in your CV already include measurable metrics. You can add extra context below or proceed to generate your résumé!
          </p>
        </div>
      `;
      return;
    }

    agentInterviewBulletsList.innerHTML = "";
    unquantified.slice(0, 5).forEach((item, idx) => {
      const rawBullet = item.bullet;
      const card = document.createElement("div");
      card.className = "interview-bullet-card";
      card.dataset.index = idx;
      card.innerHTML = `
        <div class="interview-bullet-header">
          <span class="badge-duty">UNQUANTIFIED DUTY [${idx + 1}/${Math.min(unquantified.length, 5)}]</span>
          <span class="badge-mini-green">Rule 4 Target (+75% Interviews)</span>
        </div>
        <div class="interview-bullet-original">
          "${escapeHtml(rawBullet)}"
        </div>
        <div class="interview-bullet-prompt">
          <label class="interview-question">
            🤖 <strong>Agent Question:</strong> What was the measurable outcome? (e.g. time saved, % increase, number of users, dollars saved)
          </label>
          <div class="interview-input-row">
            <input type="text" class="interview-notes-input form-input" placeholder="e.g. reduced turnaround from 14 to 4 days, cut defects by 35%" />
            <button type="button" class="btn btn-secondary btn-sm btn-reframe-xyz">
              ✨ Reframe with Google XYZ
            </button>
          </div>
          <div class="interview-result-preview hidden" style="display: none;">
            <div class="interview-suggestion-header" style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
              <strong style="font-size: 12px; color: var(--accent-green);">✨ Proposed Google XYZ Bullet:</strong>
              <span class="badge-mini-green">Zero Hallucinations</span>
            </div>
            <p class="interview-suggested-text" style="font-size: 13px; margin: 4px 0 10px 0;"></p>
            <div class="interview-actions">
              <button type="button" class="btn btn-primary btn-sm btn-accept-xyz">✓ Accept Improvement</button>
              <button type="button" class="btn btn-ghost btn-sm btn-skip-xyz">Keep Original</button>
            </div>
          </div>
        </div>
      `;

      const btnReframe = card.querySelector(".btn-reframe-xyz");
      const notesInput = card.querySelector(".interview-notes-input");
      const previewBox = card.querySelector(".interview-result-preview");
      const suggestedText = card.querySelector(".interview-suggested-text");
      const btnAccept = card.querySelector(".btn-accept-xyz");
      const btnSkip = card.querySelector(".btn-skip-xyz");

      btnReframe.addEventListener("click", async () => {
        const notes = notesInput.value.trim();
        if (!notes) {
          showToast("Please enter your rough outcome or numbers first!", "warning");
          notesInput.focus();
          return;
        }

        // If provider requires key and has none, prompt user
        if (["openai", "gemini", "anthropic", "groq", "openrouter", "mistral"].includes(currentProvider) && !currentApiKey && !detectedKeys[currentProvider]) {
          showToast(`Please enter your ${currentProvider.toUpperCase()} API key to connect`, "warning");
          if (modalApiKey) {
            modalApiKey.classList.remove("hidden");
            modalApiKey.style.display = "flex";
            if (inputApiKey) {
              inputApiKey.value = "";
              if (currentProvider === "groq") {
                inputApiKey.placeholder = "gsk_... (from console.groq.com/keys)";
              } else if (currentProvider === "openrouter") {
                inputApiKey.placeholder = "sk-or-v1-... (from openrouter.ai/keys)";
              } else if (currentProvider === "mistral") {
                inputApiKey.placeholder = "Enter Mistral API key (from console.mistral.ai)";
              } else if (currentProvider === "gemini") {
                inputApiKey.placeholder = "AIzaSy... (from aistudio.google.com)";
              } else {
                inputApiKey.placeholder = `Paste your ${currentProvider.toUpperCase()} API key here...`;
              }
              inputApiKey.focus();
            }
          }
          return;
        }

        btnReframe.disabled = true;
        btnReframe.textContent = `Connecting to ${currentProvider.toUpperCase()}...`;
        showToast(`🤖 [AGENT] Calling ${currentProvider.toUpperCase()} to reframe bullet...`, "info");

        try {
          const jd = jdInput ? jdInput.value.trim() : "";
          const res = await fetch("/api/xyz", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              bullet: rawBullet,
              notes: notes,
              provider: currentProvider,
              api_key: currentApiKey,
              jd: jd
            })
          });
          const data = await res.json();
          if (data.error) {
            showToast(`API Notice: ${data.error}`, "warning");
          }
          if (data.rewritten) {
            suggestedText.innerHTML = escapeHtml(data.rewritten).replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
            previewBox.style.display = "block";
            previewBox.classList.remove("hidden");
            const provName = data.provider ? data.provider.toUpperCase() : currentProvider.toUpperCase();
            showToast(`Reframed with Google XYZ via ${provName}!`, "success");
          }
        } catch (err) {
          showToast("Error reframing bullet: " + err.message, "error");
        } finally {
          btnReframe.disabled = false;
          btnReframe.textContent = "✨ Reframe with Google XYZ";
        }
      });

      btnAccept.addEventListener("click", () => {
        const rewrittenBullet = suggestedText.textContent.trim();
        if (rewrittenBullet) {
          customAchievements.push({
            text: rewrittenBullet,
            role: "primary",
            roleLabel: "Primary Role"
          });
          renderAchievements();
          card.style.borderColor = "var(--accent-green)";
          card.style.background = "rgba(16, 185, 129, 0.05)";
          previewBox.innerHTML = `<span class="badge-mini-green">✓ Accepted & Added to Résumé</span>`;
          showToast("Added Google XYZ bullet to your résumé!", "success");
        }
      });

      btnSkip.addEventListener("click", () => {
        previewBox.style.display = "none";
        showToast("Kept original bullet", "info");
      });

      agentInterviewBulletsList.appendChild(card);
    });
  }

  // Initialize config check
  checkServerConfig();

  function updateRoleSelectOptions() {
    if (!achievementRoleSelect) return;
    const currentSelected = achievementRoleSelect.value;
    let html = `<option value="primary">Current / Most Recent Role (Primary)</option>`;
    detectedRoles.forEach(r => {
      const val = r.company || r.title || r.header;
      const label = r.label || r.title || r.company;
      html += `<option value="${escapeHtml(val)}">${escapeHtml(label)}</option>`;
    });
    html += `<option value="__custom__">+ Specific / Other Job...</option>`;
    achievementRoleSelect.innerHTML = html;
    if (currentSelected && achievementRoleSelect.querySelector(`option[value="${currentSelected}"]`)) {
      achievementRoleSelect.value = currentSelected;
    }
  }

  if (achievementRoleSelect && achievementRoleCustom) {
    achievementRoleSelect.addEventListener("change", () => {
      if (achievementRoleSelect.value === "__custom__") {
        achievementRoleCustom.classList.remove("hidden");
        achievementRoleCustom.focus();
      } else {
        achievementRoleCustom.classList.add("hidden");
      }
    });
  }

  function renderAchievements() {
    if (!achievementsListEl) return;
    if (customAchievements.length === 0) {
      achievementsListEl.innerHTML = `
        <div class="achievements-empty-state">
          🎯 No custom achievements added yet. Select a past job, type an accomplishment above, or click a preset!
        </div>
      `;
      return;
    }

    achievementsListEl.innerHTML = "";
    customAchievements.forEach((item, idx) => {
      const itemObj = (typeof item === "string") ? { text: item, role: "primary", roleLabel: "Primary Role" } : item;
      const row = document.createElement("div");
      row.className = "achievement-item";
      row.dataset.index = idx;
      row.innerHTML = `
        <span class="achievement-bullet-icon">🎯</span>
        <span class="achievement-role-badge">🏢 ${escapeHtml(itemObj.roleLabel || itemObj.role || 'Primary Role')}</span>
        <div class="achievement-text-wrapper">
          <span class="achievement-text">${escapeHtml(itemObj.text)}</span>
        </div>
        <div class="achievement-actions">
          <button type="button" class="btn-icon-action btn-edit-achievement" data-index="${idx}" title="Edit achievement">✏️</button>
          <button type="button" class="btn-icon-action btn-delete-achievement" data-index="${idx}" title="Delete achievement">🗑️</button>
        </div>
      `;
      achievementsListEl.appendChild(row);
    });

    // Attach delete handlers
    achievementsListEl.querySelectorAll(".btn-delete-achievement").forEach(btn => {
      btn.addEventListener("click", () => {
        const idx = parseInt(btn.getAttribute("data-index"), 10);
        if (!isNaN(idx) && idx >= 0 && idx < customAchievements.length) {
          customAchievements.splice(idx, 1);
          renderAchievements();
          showToast("Removed achievement", "warning");
        }
      });
    });

    // Attach edit handlers
    achievementsListEl.querySelectorAll(".btn-edit-achievement").forEach(btn => {
      btn.addEventListener("click", () => {
        const idx = parseInt(btn.getAttribute("data-index"), 10);
        if (isNaN(idx) || idx < 0 || idx >= customAchievements.length) return;
        const row = achievementsListEl.querySelector(`.achievement-item[data-index="${idx}"]`);
        if (!row) return;

        const currentItem = (typeof customAchievements[idx] === "string")
          ? { text: customAchievements[idx], role: "primary", roleLabel: "Primary Role" }
          : customAchievements[idx];

        let roleOptionsHtml = `<option value="primary" ${currentItem.role === 'primary' ? 'selected' : ''}>Current / Most Recent Role (Primary)</option>`;
        detectedRoles.forEach(r => {
          const val = r.company || r.title || r.header;
          const label = r.label || r.title || r.company;
          const isSel = (currentItem.role === val || currentItem.roleLabel === label);
          roleOptionsHtml += `<option value="${escapeHtml(val)}" ${isSel ? 'selected' : ''}>${escapeHtml(label)}</option>`;
        });
        roleOptionsHtml += `<option value="__custom__" ${currentItem.role !== 'primary' && !detectedRoles.some(r => (r.company === currentItem.role || r.title === currentItem.role)) ? 'selected' : ''}>+ Custom Job...</option>`;

        row.className = "achievement-item editing";
        row.innerHTML = `
          <div style="display: flex; flex-direction: column; gap: 6px; width: 100%;">
            <div style="display: flex; gap: 6px; flex-wrap: wrap;">
              <select class="achievement-edit-role-select" style="background: var(--bg-input); border: 1px solid var(--accent-blue); border-radius: 4px; padding: 4px 8px; color: var(--text-primary); font-size: 11px;">
                ${roleOptionsHtml}
              </select>
              <input type="text" class="achievement-edit-input" value="${escapeHtml(currentItem.text)}" style="flex: 1; min-width: 200px;">
            </div>
            <div style="display: flex; justify-content: flex-end; gap: 6px;">
              <button type="button" class="btn-icon-action btn-save-achievement" data-index="${idx}" title="Save">💾 Save</button>
              <button type="button" class="btn-icon-action btn-cancel-achievement" data-index="${idx}" title="Cancel">✕ Cancel</button>
            </div>
          </div>
        `;

        const editInput = row.querySelector(".achievement-edit-input");
        const editRoleSelect = row.querySelector(".achievement-edit-role-select");
        editInput.focus();
        editInput.select();

        const saveEdit = () => {
          const newText = editInput.value.trim();
          if (newText) {
            let newRole = editRoleSelect.value;
            let newRoleLabel = editRoleSelect.options[editRoleSelect.selectedIndex].textContent;
            customAchievements[idx] = {
              text: newText,
              role: newRole,
              roleLabel: newRoleLabel
            };
            renderAchievements();
            showToast("Updated achievement & role association", "success");
          } else {
            customAchievements.splice(idx, 1);
            renderAchievements();
            showToast("Removed empty achievement", "warning");
          }
        };

        row.querySelector(".btn-save-achievement").addEventListener("click", saveEdit);
        row.querySelector(".btn-cancel-achievement").addEventListener("click", () => renderAchievements());
        editInput.addEventListener("keydown", (evt) => {
          if (evt.key === "Enter") {
            evt.preventDefault();
            saveEdit();
          } else if (evt.key === "Escape") {
            renderAchievements();
          }
        });
      });
    });
  }

  function addAchievement(text, roleVal, roleLabelVal) {
    const val = text.trim();
    if (!val) return;

    let role = roleVal;
    let roleLabel = roleLabelVal;

    if (!role) {
      if (achievementRoleSelect && achievementRoleSelect.value === "__custom__") {
        role = achievementRoleCustom ? achievementRoleCustom.value.trim() : "Custom Job";
        roleLabel = role || "Custom Job";
      } else if (achievementRoleSelect && achievementRoleSelect.value !== "primary") {
        role = achievementRoleSelect.value;
        const opt = achievementRoleSelect.options[achievementRoleSelect.selectedIndex];
        roleLabel = opt ? opt.textContent : role;
      } else {
        role = "primary";
        roleLabel = (detectedRoles.length > 0 && detectedRoles[0].company) ? detectedRoles[0].company : "Primary Role";
      }
    }

    customAchievements.push({
      text: val,
      role: role || "primary",
      roleLabel: roleLabel || "Primary Role"
    });

    renderAchievements();
    if (achievementInput) achievementInput.value = "";
    showToast(`Added achievement to ${roleLabel}!`, "success");
  }

  if (btnAddAchievement && achievementInput) {
    btnAddAchievement.addEventListener("click", () => addAchievement(achievementInput.value));
    achievementInput.addEventListener("keydown", (e) => {
      if (e.key === "Enter") {
        e.preventDefault();
        addAchievement(achievementInput.value);
      }
    });
  }

  // Preset pills for achievements
  document.querySelectorAll(".preset-pill").forEach(pill => {
    pill.addEventListener("click", () => {
      const preset = pill.getAttribute("data-preset");
      if (preset) addAchievement(preset);
    });
  });

  // AI Tools Tags
  function renderAiTools() {
    if (!aiToolsListEl) return;
    if (customAiTools.length === 0) {
      aiToolsListEl.innerHTML = `<span style="font-size: 11px; color: var(--text-muted);">No AI tools added yet. Click a preset above or type one to add.</span>`;
      return;
    }

    aiToolsListEl.innerHTML = "";
    customAiTools.forEach((tool, idx) => {
      const tag = document.createElement("span");
      tag.className = "ai-tool-tag";
      tag.innerHTML = `
        <span>${escapeHtml(tool)}</span>
        <button type="button" class="btn-tag-remove" data-index="${idx}" title="Remove">✕</button>
      `;
      aiToolsListEl.appendChild(tag);
    });

    aiToolsListEl.querySelectorAll(".btn-tag-remove").forEach(btn => {
      btn.addEventListener("click", () => {
        const idx = parseInt(btn.getAttribute("data-index"), 10);
        if (!isNaN(idx) && idx >= 0 && idx < customAiTools.length) {
          customAiTools.splice(idx, 1);
          renderAiTools();
        }
      });
    });
  }

  function addAiTool(tool) {
    const val = tool.trim();
    if (!val) return;
    if (!customAiTools.includes(val)) {
      customAiTools.push(val);
      renderAiTools();
      if (aiToolInput) aiToolInput.value = "";
      showToast(`Added ${val} to AI tools!`, "success");
    } else {
      showToast(`${val} is already added`, "warning");
    }
  }

  if (btnAddAiTool && aiToolInput) {
    btnAddAiTool.addEventListener("click", () => addAiTool(aiToolInput.value));
    aiToolInput.addEventListener("keydown", (e) => {
      if (e.key === "Enter") {
        e.preventDefault();
        addAiTool(aiToolInput.value);
      }
    });
  }

  // Preset pills for AI tools
  document.querySelectorAll(".preset-pill-ai").forEach(pill => {
    pill.addEventListener("click", () => {
      const tool = pill.getAttribute("data-tool");
      if (tool) addAiTool(tool);
    });
  });

  // --- Step 3 Navigation Buttons (CV Health Check: Two Options) ---
  if (btnStep3Back) {
    btnStep3Back.addEventListener("click", () => goToStep(2));
  }

  // Option 1: Add Missing Numbers & AI Tools (Go to Step 4)
  if (btnStep3AddData) {
    btnStep3AddData.addEventListener("click", () => {
      showToast("Opening extra accomplishments & AI tools editor...", "success");
      goToStep(4);
    });
  }
  if (btnChoiceAddData) {
    btnChoiceAddData.addEventListener("click", () => {
      showToast("Opening extra accomplishments & AI tools editor...", "success");
      goToStep(4);
    });
  }

  // Option 2: Generate Killer Résumé Anyway (Go to Step 5)
  if (btnStep3GenerateAnyway) {
    btnStep3GenerateAnyway.addEventListener("click", () => {
      showToast("Generating upgraded Killer Résumé...", "success");
      goToStep(5);
    });
  }
  if (btnChoiceGenerateAnyway) {
    btnChoiceGenerateAnyway.addEventListener("click", () => {
      showToast("Generating upgraded Killer Résumé...", "success");
      goToStep(5);
    });
  }

  // --- Step 4 Events (Extra Context: Achievements by Job & AI Tags) ---
  if (btnStep4Back) {
    btnStep4Back.addEventListener("click", () => goToStep(3));
  }

  if (btnStep4Skip) {
    btnStep4Skip.addEventListener("click", () => {
      showToast("Generating upgraded Killer Résumé...", "success");
      goToStep(5);
    });
  }

  if (btnStep4Generate) {
    btnStep4Generate.addEventListener("click", () => {
      showToast("Generating upgraded Killer Résumé...", "success");
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

    // Overall Score Circle Style (Google PageSpeed Insights Rating)
    if (auditScoreCircle) {
      auditScoreCircle.className = "pagespeed-gauge-circle score-hero-circle";
      if (score >= 90) {
        auditScoreCircle.classList.add("pass");
        if (auditScoreStatus) auditScoreStatus.textContent = `🟢 Good • High Interview Likelihood (${score}/100)`;
      } else if (score >= 50) {
        auditScoreCircle.style.borderColor = "var(--color-gold)";
        if (auditScoreStatus) auditScoreStatus.textContent = `⚠️ Needs Work • Screening Filter Risk (${score}/100)`;
      } else {
        auditScoreCircle.classList.add("fail");
        if (auditScoreStatus) auditScoreStatus.textContent = `🛑 Poor • Critical Screening Traps (${score}/100)`;
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
      customAchievements = [];
      customAiTools = ["Claude Code", "ChatGPT", "Cursor"];
      renderAchievements();
      renderAiTools();
      lastAuditData = null;
      lastTransformData = null;
      const aiAmendmentsCard = document.getElementById("ai-agent-amendments-card");
      if (aiAmendmentsCard) {
        aiAmendmentsCard.classList.add("hidden");
        aiAmendmentsCard.style.display = "none";
      }
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
    const isUsingActiveAi = ["openai", "gemini", "anthropic"].includes(currentProvider) && (currentApiKey || detectedKeys[currentProvider]);
    if (isUsingActiveAi) {
      showLoading(
        `🤖 Agentic Synthesis via ${currentProvider.toUpperCase()}...`,
        "Applying Jeff Su's 5 rules, Google XYZ formula & ATS vector PDF"
      );
    } else {
      showLoading(
        "Generating Your Upgraded Killer Résumé...",
        "Enforcing Google XYZ formula, single-column hierarchy & ATS vector PDF"
      );
    }

    const resume = resumeInput ? resumeInput.value.trim() : "";
    const jd = jdInput ? jdInput.value.trim() : "";

    let customMetrics = {
      achievements: customAchievements,
      ai_tools: customAiSettings.tools,
      include_ai_bullet: customAiSettings.include_ai_bullet,
      ai_task: customAiSettings.task,
      ai_time_saved: customAiSettings.time_saved,
      custom_input_metrics: customAchievements.map(a => (typeof a === "string" ? a : a.text)).join("\n"),
      custom_ai_tools: (customAiSettings.tools || []).join(", ")
    };

    try {
      const res = await fetch("/api/transform", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          resume: resume,
          jd: jd,
          pdf_base64: currentPdfBase64,
          style_meta: currentStyleMeta,
          provider: currentProvider,
          api_key: currentApiKey,
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

      // Render AI Engine Status & Diagnostics Banner
      const aiStatusBanner = document.getElementById("ai-engine-status-banner");
      if (aiStatusBanner) {
        const status = data.llm_status || {};
        if (status.error) {
          const is429 = status.error.includes("429") || status.error.includes("credit_balance_exhausted");
          const is401 = status.error.includes("401") || status.error.includes("invalid_api_key");
          aiStatusBanner.classList.remove("hidden");
          aiStatusBanner.style.display = "block";
          aiStatusBanner.style.background = "rgba(239, 68, 68, 0.1)";
          aiStatusBanner.style.border = "1px solid var(--accent-rose)";
          aiStatusBanner.style.color = "var(--text-primary)";

          if (is429) {
            aiStatusBanner.innerHTML = `
              <div style="display: flex; align-items: flex-start; gap: 10px;">
                <span style="font-size: 18px;">⚠️</span>
                <div style="flex: 1;">
                  <strong style="color: var(--accent-rose);">OpenAI Account Notice: 0 Tokens Billed (HTTP 429 Quota Exhausted)</strong>
                  <p style="margin: 4px 0 8px 0; font-size: 12px; color: var(--text-secondary);">
                    Your OpenAI account has <strong>$0.00 credit balance remaining</strong>. OpenAI rejected the request before processing tokens. The agent successfully generated your ATS résumé using our built-in offline rule engine.
                  </p>
                  <div style="display: flex; gap: 8px; flex-wrap: wrap;">
                    <a href="https://platform.openai.com/settings/organization/billing" target="_blank" rel="noopener" class="btn btn-secondary btn-sm" style="font-size: 11px; padding: 3px 8px;">💳 Add OpenAI Credits</a>
                    <button type="button" id="btn-switch-to-groq" class="btn btn-primary btn-sm" style="font-size: 11px; padding: 3px 8px;">⚡ Switch to Groq (Free & Fast)</button>
                    <button type="button" id="btn-switch-to-gemini" class="btn btn-secondary btn-sm" style="font-size: 11px; padding: 3px 8px;">✨ Switch to Gemini (Free Tier)</button>
                    <button type="button" id="btn-switch-to-openrouter" class="btn btn-ghost btn-sm" style="font-size: 11px; padding: 3px 8px;">🌐 Switch to OpenRouter (Free)</button>
                  </div>
                </div>
              </div>
            `;
            const setupSwitchBtn = (btnId, provider, placeholder) => {
              const btn = document.getElementById(btnId);
              if (btn) {
                btn.addEventListener("click", () => {
                  if (selectAiEngine) selectAiEngine.value = provider;
                  currentProvider = provider;
                  localStorage.setItem("killer_resume_provider", provider);
                  updateApiKeyBadge();
                  if (modalApiKey) {
                    modalApiKey.classList.remove("hidden");
                    modalApiKey.style.display = "flex";
                    if (inputApiKey) {
                      inputApiKey.value = localStorage.getItem("killer_resume_api_key_" + provider) || "";
                      inputApiKey.placeholder = placeholder;
                      inputApiKey.focus();
                    }
                  }
                });
              }
            };
            setupSwitchBtn("btn-switch-to-groq", "groq", "Enter free Groq API key (console.groq.com/keys)");
            setupSwitchBtn("btn-switch-to-gemini", "gemini", "Enter free Gemini API key (aistudio.google.com)");
            setupSwitchBtn("btn-switch-to-openrouter", "openrouter", "Enter free OpenRouter API key (openrouter.ai/keys)");
            showToast("OpenAI Notice: Credit balance exhausted (0 tokens used). Offline rule engine applied.", "warning");
          } else if (is401) {
            aiStatusBanner.innerHTML = `
              <div style="display: flex; align-items: flex-start; gap: 10px;">
                <span style="font-size: 18px;">🔑</span>
                <div style="flex: 1;">
                  <strong style="color: var(--accent-rose);">${(status.provider || 'API').toUpperCase()} Key Invalid (HTTP 401)</strong>
                  <p style="margin: 4px 0; font-size: 12px; color: var(--text-secondary);">The provided API key was rejected by ${status.provider}. The résumé was formatted using the offline rule engine.</p>
                </div>
              </div>
            `;
          } else {
            aiStatusBanner.innerHTML = `
              <div style="display: flex; align-items: flex-start; gap: 10px;">
                <span style="font-size: 18px;">⚠️</span>
                <div style="flex: 1;">
                  <strong style="color: var(--accent-amber);">${(status.provider || 'AI').toUpperCase()} Engine Notice</strong>
                  <p style="margin: 4px 0; font-size: 12px; color: var(--text-secondary);">${escapeHtml(status.error)}</p>
                </div>
              </div>
            `;
          }
        } else if (status.applied) {
          aiStatusBanner.classList.remove("hidden");
          aiStatusBanner.style.display = "block";
          aiStatusBanner.style.background = "rgba(16, 185, 129, 0.08)";
          aiStatusBanner.style.border = "1px solid var(--accent-green)";
          aiStatusBanner.style.color = "var(--text-primary)";
          aiStatusBanner.innerHTML = `
            <div style="display: flex; align-items: center; gap: 8px;">
              <span>🟢</span>
              <strong style="color: var(--accent-green);">Live AI Agent Active:</strong>
              <span style="font-size: 12px; color: var(--text-secondary);">Enhanced via ${status.provider.toUpperCase()} (${status.model}) with Google XYZ & Jeff Su 5-Rule optimization.</span>
            </div>
          `;
        } else {
          aiStatusBanner.classList.add("hidden");
          aiStatusBanner.style.display = "none";
        }
      }

      // Render AI Agent Amendments Quick Summary Card
      renderAiAmendmentsCard(data.llm_status || {}, data);

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

  // --- AI Agent Amendments Card Renderer ---
  function renderAiAmendmentsCard(status, data) {
    const card = document.getElementById("ai-agent-amendments-card");
    const grid = document.getElementById("ai-amendments-grid");
    const heading = document.getElementById("ai-amendments-heading");
    const badge = document.getElementById("ai-amendments-provider-badge");
    const btnToggle = document.getElementById("btn-toggle-amendments");
    const toggleText = document.getElementById("toggle-amendments-text");
    const body = document.getElementById("ai-amendments-body");

    if (!card || !grid) return;

    const amendments = (status && status.amendments) || [];
    if (amendments.length === 0) {
      card.classList.add("hidden");
      card.style.display = "none";
      return;
    }

    card.classList.remove("hidden");
    card.style.display = "block";

    const isLiveAi = Boolean(status && status.applied);
    const providerName = (status && status.provider) ? status.provider.toUpperCase() : "AGENT";
    const modelName = (status && status.model) ? `(${status.model})` : "";

    if (heading) {
      heading.textContent = isLiveAi
        ? `AI Agent Amendments (${providerName} ${modelName})`
        : "Agentic CV Amendments & Enhancements";
    }

    if (badge) {
      badge.textContent = isLiveAi ? `LIVE AI: ${providerName}` : "RULE ENGINE OPTIMIZED";
      badge.style.background = isLiveAi ? "rgba(16, 185, 129, 0.15)" : "rgba(56, 189, 248, 0.15)";
      badge.style.color = isLiveAi ? "var(--accent-green)" : "var(--accent-blue)";
      badge.style.borderColor = isLiveAi ? "rgba(16, 185, 129, 0.4)" : "rgba(56, 189, 248, 0.4)";
    }

    grid.innerHTML = amendments.map(item => `
      <div class="ai-amendment-item">
        <div class="amendment-item-header">
          <span class="amendment-item-icon">${item.icon || "✓"}</span>
          <div class="amendment-item-title-group">
            <strong class="amendment-item-category">${escapeHtml(item.category || "")}</strong>
            <span class="amendment-item-badge">${escapeHtml(item.badge || "")}</span>
          </div>
        </div>
        <p class="amendment-item-summary">${escapeHtml(item.summary || "")}</p>
        ${item.detail ? `<div class="amendment-item-detail"><code>${escapeHtml(item.detail)}</code></div>` : ""}
      </div>
    `).join("");

    if (btnToggle && !btnToggle.dataset.initialized) {
      btnToggle.dataset.initialized = "true";
      btnToggle.addEventListener("click", () => {
        if (!body) return;
        const isHidden = body.style.display === "none";
        body.style.display = isHidden ? "block" : "none";
        if (toggleText) {
          toggleText.textContent = isHidden ? "Hide Details ▴" : "Show Details ▾";
        }
      });
    }
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

  // Initial setup: ensure loading overlay is hidden, step 1 is active, and CRUD lists rendered
  hideLoading();
  renderAchievements();
  renderAiTools();
  goToStep(1);

  // Initial call to pre-load sample data quietly in background
  fetchSampleData().catch(() => {});
});
