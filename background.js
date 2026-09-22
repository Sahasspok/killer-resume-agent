// Background service worker for Killer Resume Agent
// Clicking the extension icon in the Chrome toolbar opens the full application in a new tab.

chrome.action.onClicked.addListener(() => {
  chrome.tabs.create({
    url: chrome.runtime.getURL("web/index.html")
  });
});
