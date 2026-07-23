// inject.js — SimpleBrowser Fingerprint Shield (runs in MAIN world)
// Spoofs Canvas, WebGL, AudioContext, ClientRects, Navigator, Screen, Fonts, Plugins
// Designed to pass PixelScan, CreepJS, and BrowserLeaks checks

(function() {
  "use strict";

  // Load config from window
  const config = window.__SB_FINGERPRINT_CONFIG__ || {};

  console.log('[Fingerprint Shield] Config loaded:', config);

  // ═══════════════════════════════════════════════════════════════════════════
  // UTILITY: Seeded random for consistent noise
  // ═══════════════════════════════════════════════════════════════════════════

  function seededRandom(seed) {
    let s = seed;
    return function() {
      s = (s * 9301 + 49297) % 233280;
      return s / 233280;
    };
  }

  const canvasRng = seededRandom((config.canvas_noise_seed || 0.5) * 1000000);

  // ═══════════════════════════════════════════════════════════════════════════
  // SCREEN SPOOFING - Enhanced
  // ═══════════════════════════════════════════════════════════════════════════

  if (config.screen_width && config.screen_height) {
    try {
      const availWidth = config.avail_width || config.screen_width;
      const availHeight = config.avail_height || (config.screen_height - 40);

      // Store original descriptors to make our overrides look native
      const originalScreenDescriptors = {
        width: Object.getOwnPropertyDescriptor(Screen.prototype, 'width'),
        height: Object.getOwnPropertyDescriptor(Screen.prototype, 'height'),
        availWidth: Object.getOwnPropertyDescriptor(Screen.prototype, 'availWidth'),
        availHeight: Object.getOwnPropertyDescriptor(Screen.prototype, 'availHeight'),
        colorDepth: Object.getOwnPropertyDescriptor(Screen.prototype, 'colorDepth'),
        pixelDepth: Object.getOwnPropertyDescriptor(Screen.prototype, 'pixelDepth')
      };

      // Override Screen properties with native-looking getters
      const screenOverrides = {
        width: config.screen_width,
        height: config.screen_height,
        availWidth: availWidth,
        availHeight: availHeight,
        colorDepth: config.color_depth || 24,
        pixelDepth: config.pixel_depth || 24
      };

      // Apply overrides to Screen.prototype
      Object.keys(screenOverrides).forEach(prop => {
        try {
          Object.defineProperty(Screen.prototype, prop, {
            get: function() {
              return screenOverrides[prop];
            },
            set: undefined,
            configurable: false,
            enumerable: originalScreenDescriptors[prop]?.enumerable ?? true
          });
        } catch (e) {
          // Property might already be non-configurable
        }
      });

      // Override window dimensions with native-looking getters
      const windowOverrides = {
        outerWidth: config.screen_width,
        outerHeight: config.screen_height,
        innerWidth: config.screen_width,
        innerHeight: config.screen_height
      };

      Object.keys(windowOverrides).forEach(prop => {
        try {
          const originalDescriptor = Object.getOwnPropertyDescriptor(window, prop);
          Object.defineProperty(window, prop, {
            get: function() {
              return windowOverrides[prop];
            },
            set: undefined,
            configurable: false,
            enumerable: originalDescriptor?.enumerable ?? true
          });
        } catch (e) {
          // Property might already be non-configurable
        }
      });

      // Also override devicePixelRatio if needed
      if (config.device_pixel_ratio) {
        try {
          Object.defineProperty(window, 'devicePixelRatio', {
            get: function() {
              return config.device_pixel_ratio;
            },
            set: undefined,
            configurable: false,
            enumerable: true
          });
        } catch (e) {}
      }

      console.log(`[SimpleBrowser] Screen spoofed: ${config.screen_width}x${config.screen_height}`);
    } catch (e) {
      console.warn("[SimpleBrowser] Screen spoof failed to initialize:", e);
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // TIMEZONE SPOOFING - Enhanced
  // ═══════════════════════════════════════════════════════════════════════════

  if (config.timezone) {
    try {
      // Calculate timezone offset in minutes
      const targetDate = new Date();
      const targetString = targetDate.toLocaleString('en-US', { timeZone: config.timezone });
      const targetTime = new Date(targetString).getTime();
      const localTime = targetDate.getTime();
      const offset = Math.round((localTime - targetTime) / 60000);
      
      console.log(`[SimpleBrowser] Timezone offset calculated: ${offset} minutes for ${config.timezone}`);

      // Store original methods
      const originalGetTimezoneOffset = Date.prototype.getTimezoneOffset;
      const originalToString = Date.prototype.toString;
      const originalToDateString = Date.prototype.toDateString;
      const originalToTimeString = Date.prototype.toTimeString;
      const originalToLocaleString = Date.prototype.toLocaleString;
      const originalToLocaleDateString = Date.prototype.toLocaleDateString;
      const originalToLocaleTimeString = Date.prototype.toLocaleTimeString;

      // Override getTimezoneOffset with native-looking function
      Object.defineProperty(Date.prototype, 'getTimezoneOffset', {
        value: function() {
          return offset;
        },
        writable: true,
        configurable: true,
        enumerable: false
      });

      // Override toString to show correct timezone
      Object.defineProperty(Date.prototype, 'toString', {
        value: function() {
          const str = originalToString.call(this);
          // Replace timezone abbreviation with target timezone
          return str.replace(/\(.*\)/, `(${config.timezone})`);
        },
        writable: true,
        configurable: true,
        enumerable: false
      });

      // Override toTimeString
      Object.defineProperty(Date.prototype, 'toTimeString', {
        value: function() {
          const str = originalToTimeString.call(this);
          return str.replace(/\(.*\)/, `(${config.timezone})`);
        },
        writable: true,
        configurable: true,
        enumerable: false
      });

      // Override toLocaleString to use target timezone
      Object.defineProperty(Date.prototype, 'toLocaleString', {
        value: function(locales, options) {
          options = options || {};
          if (!options.timeZone) {
            options.timeZone = config.timezone;
          }
          return originalToLocaleString.call(this, locales, options);
        },
        writable: true,
        configurable: true,
        enumerable: false
      });

      // Override toLocaleDateString
      Object.defineProperty(Date.prototype, 'toLocaleDateString', {
        value: function(locales, options) {
          options = options || {};
          if (!options.timeZone) {
            options.timeZone = config.timezone;
          }
          return originalToLocaleDateString.call(this, locales, options);
        },
        writable: true,
        configurable: true,
        enumerable: false
      });

      // Override toLocaleTimeString
      Object.defineProperty(Date.prototype, 'toLocaleTimeString', {
        value: function(locales, options) {
          options = options || {};
          if (!options.timeZone) {
            options.timeZone = config.timezone;
          }
          return originalToLocaleTimeString.call(this, locales, options);
        },
        writable: true,
        configurable: true,
        enumerable: false
      });

      // Override Intl.DateTimeFormat
      const originalDateTimeFormat = Intl.DateTimeFormat;
      const DateTimeFormatWrapper = function(locales, options) {
        options = options || {};
        if (!options.timeZone) {
          options.timeZone = config.timezone;
        }
        return new originalDateTimeFormat(locales, options);
      };
      
      // Make wrapper look like original
      DateTimeFormatWrapper.prototype = originalDateTimeFormat.prototype;
      DateTimeFormatWrapper.supportedLocalesOf = originalDateTimeFormat.supportedLocalesOf;
      
      Object.defineProperty(Intl, 'DateTimeFormat', {
        value: DateTimeFormatWrapper,
        writable: true,
        configurable: true,
        enumerable: true
      });

      console.log('[SimpleBrowser] Timezone spoofed successfully');
    } catch (e) {
      console.warn('[SimpleBrowser] Timezone spoof failed:', e);
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // CANVAS SPOOFING
  // ═══════════════════════════════════════════════════════════════════════════

  if (config.canvas_spoof !== "off") {
    try {
      const origToDataURL = HTMLCanvasElement.prototype.toDataURL;
      const origToBlob = HTMLCanvasElement.prototype.toBlob;
      const origGetImageData = CanvasRenderingContext2D.prototype.getImageData;

      function addCanvasNoise(canvas) {
        try {
          const ctx = canvas.getContext("2d");
          if (!ctx) return;
          const imageData = origGetImageData.call(ctx, 0, 0, canvas.width, canvas.height);
          const data = imageData.data;

          for (let i = 0; i < data.length; i += 4) {
            data[i] = Math.max(0, Math.min(255, data[i] + Math.floor((canvasRng() - 0.5) * 2)));
            data[i + 1] = Math.max(0, Math.min(255, data[i + 1] + Math.floor((canvasRng() - 0.5) * 2)));
            data[i + 2] = Math.max(0, Math.min(255, data[i + 2] + Math.floor((canvasRng() - 0.5) * 2)));
          }

          ctx.putImageData(imageData, 0, 0);
        } catch (e) {
          // Silently fail
        }
      }

      HTMLCanvasElement.prototype.toDataURL = function(...args) {
        try {
          addCanvasNoise(this);
        } catch (e) {}
        return origToDataURL.apply(this, args);
      };

      HTMLCanvasElement.prototype.toBlob = function(...args) {
        try {
          addCanvasNoise(this);
        } catch (e) {}
        return origToBlob.apply(this, args);
      };

      CanvasRenderingContext2D.prototype.getImageData = function(...args) {
        const imageData = origGetImageData.apply(this, args);
        try {
          const data = imageData.data;
          for (let i = 0; i < data.length; i += 4) {
            data[i] = Math.max(0, Math.min(255, data[i] + Math.floor((canvasRng() - 0.5) * 2)));
            data[i + 1] = Math.max(0, Math.min(255, data[i + 1] + Math.floor((canvasRng() - 0.5) * 2)));
            data[i + 2] = Math.max(0, Math.min(255, data[i + 2] + Math.floor((canvasRng() - 0.5) * 2)));
          }
        } catch (e) {}
        return imageData;
      };
    } catch (e) {
      console.warn("[SimpleBrowser] Canvas spoof failed to initialize:", e);
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // WEBGL SPOOFING
  // ═══════════════════════════════════════════════════════════════════════════

  if (config.webgl_spoof !== "off") {
    try {
      const origGetParam = WebGLRenderingContext.prototype.getParameter;
      WebGLRenderingContext.prototype.getParameter = function(parameter) {
        try {
          if (parameter === 0x9245) {
            return config.webgl_vendor || "Google Inc. (NVIDIA)";
          }
          if (parameter === 0x9246) {
            return config.webgl_renderer || "ANGLE (NVIDIA, NVIDIA GeForce GTX 1080 Ti Direct3D11 vs_5_0 ps_5_0, D3D11)";
          }
        } catch (e) {}
        return origGetParam.call(this, parameter);
      };

      if (typeof WebGL2RenderingContext !== "undefined") {
        WebGL2RenderingContext.prototype.getParameter = function(parameter) {
          try {
            if (parameter === 0x9245) {
              return config.webgl_vendor || "Google Inc. (NVIDIA)";
            }
            if (parameter === 0x9246) {
              return config.webgl_renderer || "ANGLE (NVIDIA, NVIDIA GeForce GTX 1080 Ti Direct3D11 vs_5_0 ps_5_0, D3D11)";
            }
          } catch (e) {}
          return origGetParam.call(this, parameter);
        };
      }
    } catch (e) {
      console.warn("[SimpleBrowser] WebGL spoof failed to initialize:", e);
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // AUDIO CONTEXT SPOOFING
  // ═══════════════════════════════════════════════════════════════════════════

  if (config.audio_spoof !== "off") {
    try {
      const audioNoise = config.audio_noise || 0.00001;

      if (typeof AudioContext !== "undefined") {
        const origCreateAnalyser = AudioContext.prototype.createAnalyser;

        AudioContext.prototype.createAnalyser = function() {
          const analyser = origCreateAnalyser.call(this);
          try {
            const origGetFloat = analyser.getFloatFrequencyData;
            analyser.getFloatFrequencyData = function(array) {
              origGetFloat.call(this, array);
              for (let i = 0; i < array.length; i++) {
                array[i] = array[i] + (Math.random() - 0.5) * audioNoise;
              }
            };
          } catch (e) {}
          return analyser;
        };
      }

      if (typeof OfflineAudioContext !== "undefined") {
        const origStartRendering = OfflineAudioContext.prototype.startRendering;
        OfflineAudioContext.prototype.startRendering = function() {
          return origStartRendering.call(this).then(buffer => {
            try {
              const data = buffer.getChannelData(0);
              for (let i = 0; i < data.length; i++) {
                data[i] = data[i] + (Math.random() - 0.5) * audioNoise;
              }
            } catch (e) {}
            return buffer;
          });
        };
      }
    } catch (e) {
      console.warn("[SimpleBrowser] Audio spoof failed to initialize:", e);
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // CLIENT RECTS SPOOFING
  // ═══════════════════════════════════════════════════════════════════════════

  if (config.client_rects_spoof !== "off") {
    try {
      const rectNoise = config.client_rects_noise || 0.05;

      const origGetBoundingClientRect = Element.prototype.getBoundingClientRect;
      Element.prototype.getBoundingClientRect = function() {
        const rect = origGetBoundingClientRect.call(this);
        try {
          const noise = () => (Math.random() - 0.5) * rectNoise;
          return new DOMRect(
            rect.x + noise(),
            rect.y + noise(),
            rect.width + noise(),
            rect.height + noise()
          );
        } catch (e) {
          return rect;
        }
      };
    } catch (e) {
      console.warn("[SimpleBrowser] Client rects spoof failed to initialize:", e);
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // NAVIGATOR SPOOFING
  // ═══════════════════════════════════════════════════════════════════════════

  try {
    const navigatorOverrides = {};

    if (config.platform) navigatorOverrides.platform = config.platform;
    if (config.vendor) navigatorOverrides.vendor = config.vendor;
    if (config.hardware_concurrency !== undefined) navigatorOverrides.hardwareConcurrency = config.hardware_concurrency;
    if (config.device_memory !== undefined) navigatorOverrides.deviceMemory = config.device_memory;
    if (config.language) {
      navigatorOverrides.language = config.language;
      navigatorOverrides.languages = [config.language, "en"];
    }
    if (config.do_not_track !== undefined && config.do_not_track !== null) {
      navigatorOverrides.doNotTrack = config.do_not_track;
    }
    if (config.max_touch_points !== undefined) {
      navigatorOverrides.maxTouchPoints = config.max_touch_points;
    }

    Object.keys(navigatorOverrides).forEach(key => {
      try {
        Object.defineProperty(Navigator.prototype, key, {
          get: function() { return navigatorOverrides[key]; },
          configurable: true
        });
      } catch (e) {}
    });
  } catch (e) {
    console.warn("[SimpleBrowser] Navigator spoof failed to initialize:", e);
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // SCREEN SPOOFING
  // ═══════════════════════════════════════════════════════════════════════════

  if (config.screen_width && config.screen_height) {
    try {
      const availWidth = config.avail_width || config.screen_width;
      const availHeight = config.avail_height || (config.screen_height - 40);

      Object.defineProperty(Screen.prototype, "width", {
        get: () => config.screen_width,
        configurable: false
      });
      Object.defineProperty(Screen.prototype, "height", {
        get: () => config.screen_height,
        configurable: false
      });
      Object.defineProperty(Screen.prototype, "availWidth", {
        get: () => availWidth,
        configurable: false
      });
      Object.defineProperty(Screen.prototype, "availHeight", {
        get: () => availHeight,
        configurable: false
      });
      Object.defineProperty(Screen.prototype, "colorDepth", {
        get: () => config.color_depth || 24,
        configurable: false
      });
      Object.defineProperty(Screen.prototype, "pixelDepth", {
        get: () => config.pixel_depth || 24,
        configurable: false
      });
      
      // Also override window dimensions
      Object.defineProperty(window, "outerWidth", {
        get: () => config.screen_width,
        configurable: false
      });
      Object.defineProperty(window, "outerHeight", {
        get: () => config.screen_height,
        configurable: false
      });
      Object.defineProperty(window, "innerWidth", {
        get: () => config.screen_width,
        configurable: false
      });
      Object.defineProperty(window, "innerHeight", {
        get: () => config.screen_height,
        configurable: false
      });
      
      console.log(`[SimpleBrowser] Screen spoofed: ${config.screen_width}x${config.screen_height}`);
    } catch (e) {
      console.warn("[SimpleBrowser] Screen spoof failed to initialize:", e);
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // TIMEZONE SPOOFING
  // ═══════════════════════════════════════════════════════════════════════════

  if (config.timezone) {
    try {
      // Calculate timezone offset
      const targetDate = new Date();
      const targetString = targetDate.toLocaleString('en-US', { timeZone: config.timezone });
      const targetTime = new Date(targetString).getTime();
      const localTime = targetDate.getTime();
      const offset = Math.round((localTime - targetTime) / 60000);
      
      // Override Date.prototype.getTimezoneOffset
      const originalGetTimezoneOffset = Date.prototype.getTimezoneOffset;
      Date.prototype.getTimezoneOffset = function() {
        return offset;
      };
      
      // Override Intl.DateTimeFormat
      const originalDateTimeFormat = Intl.DateTimeFormat;
      Intl.DateTimeFormat = function(locales, options) {
        options = options || {};
        if (!options.timeZone) {
          options.timeZone = config.timezone;
        }
        return new originalDateTimeFormat(locales, options);
      };
      Intl.DateTimeFormat.prototype = originalDateTimeFormat.prototype;
      Intl.DateTimeFormat.supportedLocalesOf = originalDateTimeFormat.supportedLocalesOf;
      
      console.log(`[SimpleBrowser] Timezone spoofed: ${config.timezone} (offset: ${offset}min)`);
    } catch (e) {
      console.warn("[SimpleBrowser] Timezone spoof failed to initialize:", e);
    }
  }

  console.log("[SimpleBrowser] Fingerprint Shield active");
})();
