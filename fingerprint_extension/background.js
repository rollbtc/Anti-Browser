// background.js — Service Worker for SimpleBrowser Fingerprint Shield
// Reads the fingerprint config and makes it available to content scripts.

let fingerprintConfig = null;

// Listen for messages from content scripts requesting config
chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  if (msg.type === "GET_FINGERPRINT_CONFIG") {
    if (fingerprintConfig) {
      sendResponse(fingerprintConfig);
    } else {
      // Load config from the profile directory
      loadConfig().then(config => {
        fingerprintConfig = config;
        sendResponse(config);
      }).catch(() => {
        sendResponse(null);
      });
      return true; // async response
    }
  }
  return true;
});

async function loadConfig() {
  // Try to fetch the config file via the file:// protocol
  // The config is written by the Python app to the profile data dir
  try {
    // Use chrome.storage as a fallback
    const stored = await chrome.storage.local.get("fingerprint_config");
    if (stored.fingerprint_config) {
      return stored.fingerprint_config;
    }
  } catch (e) {}

  // Return default config
  return {
    canvas_spoof: "noise",
    canvas_noise_seed: Math.random(),
    webgl_spoof: "custom",
    webgl_vendor: "Google Inc. (NVIDIA)",
    webgl_renderer: "ANGLE (NVIDIA, NVIDIA GeForce GTX 1080 Ti Direct3D11 vs_5_0 ps_5_0, D3D11)",
    audio_spoof: "noise",
    audio_noise: 0.00001,
    client_rects_spoof: "noise",
    client_rects_noise: 0.05,
    font_spoof: "custom",
    platform: "Win32",
    vendor: "Google Inc.",
    hardware_concurrency: 8,
    device_memory: 8,
    color_depth: 24,
    pixel_depth: 24,
    screen_width: 1920,
    screen_height: 1080,
    language: "en-US",
    timezone: "America/New_York",
    do_not_track: null,
    touch_support: false,
    max_touch_points: 0,
    webrtc: "disabled",
  };
}

// Initialize
loadConfig().then(config => {
  fingerprintConfig = config;
});
