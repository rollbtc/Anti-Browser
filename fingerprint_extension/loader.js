// loader.js — Runs in ISOLATED world at document_start
// Fetches fingerprint config and injects the main spoofing script into MAIN world

(async function() {
  // Get config from background script
  let config;
  try {
    config = await chrome.runtime.sendMessage({ type: "GET_FINGERPRINT_CONFIG" });
  } catch (e) {
    // Fallback: use default config
    config = {
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

  if (!config) {
    config = {
      canvas_spoof: "noise",
      canvas_noise_seed: Math.random(),
    };
  }

  // Inject config into page context
  const configScript = document.createElement("script");
  configScript.textContent = `
    window.__SB_FINGERPRINT_CONFIG__ = ${JSON.stringify(config)};
  `;
  (document.head || document.documentElement).appendChild(configScript);
  configScript.remove();

  // Inject the main spoofing script
  const script = document.createElement("script");
  script.src = chrome.runtime.getURL("inject.js");
  script.onload = function() {
    this.remove();
  };
  (document.head || document.documentElement).appendChild(script);
})();
