// Mobile User Agent Changer Extension
// Changes the user agent to simulate mobile device

const mobileUserAgents = [
  "Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Mobile/15E148 Safari/604.1",
  "Mozilla/5.0 (Linux; Android 11; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36",
  "Mozilla/5.0 (Linux; Android 10; SM-A205U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36"
];

// Select a random mobile user agent
const selectedUserAgent = mobileUserAgents[Math.floor(Math.random() * mobileUserAgents.length)];

console.log("Mobile User Agent Extension loaded with UA:", selectedUserAgent);

// Intercept and modify requests
chrome.webRequest.onBeforeSendHeaders.addListener(
  function(details) {
    for (let i = 0; i < details.requestHeaders.length; ++i) {
      if (details.requestHeaders[i].name.toLowerCase() === 'user-agent') {
        details.requestHeaders[i].value = selectedUserAgent;
        break;
      }
    }
    return { requestHeaders: details.requestHeaders };
  },
  { urls: ["<all_urls>"] },
  ["blocking", "requestHeaders"]
);

// Also handle the case where User-Agent header might not exist
chrome.webRequest.onBeforeSendHeaders.addListener(
  function(details) {
    let hasUserAgent = false;
    for (let i = 0; i < details.requestHeaders.length; ++i) {
      if (details.requestHeaders[i].name.toLowerCase() === 'user-agent') {
        hasUserAgent = true;
        break;
      }
    }
    
    if (!hasUserAgent) {
      details.requestHeaders.push({
        name: 'User-Agent',
        value: selectedUserAgent
      });
    }
    
    return { requestHeaders: details.requestHeaders };
  },
  { urls: ["<all_urls>"] },
  ["blocking", "requestHeaders"]
);
