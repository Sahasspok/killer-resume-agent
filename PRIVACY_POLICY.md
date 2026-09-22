# Privacy Policy for Killer Resume Agent

**Effective Date:** September 22, 2026  
**Last Updated:** September 22, 2026  

This Privacy Policy explains how **Killer Resume Agent** ("we", "our", or "the extension") handles user information when you use our browser extension and web application.

---

### 1. Single Purpose & Commitment to Privacy
Killer Resume Agent is designed with a single purpose: to help job seekers transform, calibrate, and optimize technical resumes into high-impact, ATS-certified career artifacts using the Google X-Y-Z formula and AI-assisted screening audits.

We respect your privacy. We do **not** sell, monetize, or harvest your personal information, resumes, or job descriptions.

---

### 2. Information We Handle
When you use Killer Resume Agent, the extension processes the following data solely to perform resume optimization:

1. **Resume Data**: Any text, PDF, or markdown document you upload or paste into the extension, including your name, contact information, employment history, and education.
2. **Job Description Data**: Job postings or requirements you paste or import from the active tab.
3. **API Keys & Preferences**: User-provided API keys (e.g., Google Gemini, Groq, OpenRouter, Mistral) and local preferences (e.g., selected AI model, custom achievements).

---

### 3. How We Use and Store Your Data
- **Local Storage Only**: Your settings, preferences, and custom achievements are stored strictly on your local device using Chrome's `chrome.storage.local` API. They are never transmitted to our servers.
- **No Developer Database or Tracking**: We do not maintain an external database of user resumes, identities, or analytics. Your resume data stays on your machine.
- **Direct API Processing**: When you request resume optimization, your resume text and target job description are transmitted directly to your selected AI provider (such as Google Gemini, Groq, OpenRouter, or Mistral) or processed locally on your local backend server (`localhost:5050`). These requests are governed by the respective AI provider's privacy policies and enterprise terms.

---

### 4. Permissions Justification
- **`storage`**: Used exclusively to store your chosen AI model, API keys, and custom achievements locally on your device.
- **`activeTab`**: Used only when you explicitly invoke the extension to read job description text from the active job posting page (e.g., LinkedIn, Greenhouse, Lever, Indeed) to tailor your resume.
- **Host Permissions**: Used solely to connect to your local backend server (`localhost:5050`) for vector PDF generation and to communicate with AI API endpoints (Google Gemini, Groq, OpenRouter, Mistral) using your credentials.

---

### 5. Third-Party Sharing & Disclosure
- We **do not sell, rent, or trade** user data to any third parties or data brokers.
- We do **not** use user data for targeted advertising, creditworthiness determination, or lending purposes.
- The only data transmission occurs between your browser and the specific AI provider API endpoint you choose to communicate with.

---

### 6. Data Retention & Deletion
Because all data is processed on-demand and stored locally:
- You can delete your stored data at any time by clearing your browser cache/storage or uninstalling the extension.
- No historical copies of your resumes are retained by us.

---

### 7. Changes to This Policy
We may update this Privacy Policy from time to time. Any updates will be reflected in this repository with an updated effective date.

---

### 8. Contact Us
If you have any questions or concerns regarding this Privacy Policy, please open an issue on GitHub:  
**Repository**: [https://github.com/Sahasspok/killer-resume-agent](https://github.com/Sahasspok/killer-resume-agent)
