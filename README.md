# SimpleBrowser 2.0 🌐

**Advanced Multi-Profile Anti-Detect Browser Manager**  
Inspired by AdsPower and Dolphin Anty

## 🎯 What's New in v2.0

### Major Improvements
✅ **Built-in Chromium Downloader** — No need to install Chrome separately  
✅ **Proxy Validator** — Test proxies before using them  
✅ **Auto-Match Fingerprint** — Automatically configure fingerprint based on proxy IP location  
✅ **Advanced Fingerprint Spoofing** — Canvas, WebGL, Audio, ClientRects, Fonts  
✅ **Pass PixelScan & BrowserLeaks** — Enhanced anti-detection  
✅ **Cookie Import/Export** — Transfer cookies between profiles  
✅ **Extension Manager** — Install and manage Chrome extensions  
✅ **Complete Country/Timezone Database** — 50+ countries with proper timezone/language matching  
✅ **Redesigned UI** — Modern dark theme with tabbed interface  
✅ **Fixed Profile Editor** — Proper scrolling and visible save button  

## 🚀 Quick Start

### Installation
No installation needed! Just run:

```bash
cd simple_browser
python3 app.py
```

### First Run
1. **Download Chromium** — On first launch, the app will offer to download Chrome for Testing automatically (~150MB)
2. **Create a Profile** — Click "➕ New Profile"
3. **Configure** — Set up proxy, fingerprint, and anti-detection settings
4. **Launch** — Click "▶ Open" to start browsing

## ✨ Features

### 🔒 Profile Isolation
Each profile runs in a completely isolated Chrome instance with:
- Separate cookies, cache, and local storage
- Independent browsing history
- Custom extensions per profile
- Isolated user-data directory

### 🌍 Proxy Support
- **HTTP proxies** with authentication
- **SOCKS5 proxies** with authentication
- **Proxy Validator** — Test connectivity and get IP info
- **Auto-Match** — Automatically configure fingerprint to match proxy location

**Proxy Validation** provides:
- IP address
- Country, region, city
- Timezone
- ISP information
- Connection latency

### 🎭 Advanced Fingerprint Spoofing

#### Canvas Fingerprint
- Adds subtle noise to Canvas API calls
- Makes each profile's canvas fingerprint unique
- Prevents tracking via canvas fingerprinting

#### WebGL Fingerprint
- Custom GPU vendor and renderer strings
- Spoofs `UNMASKED_VENDOR_WEBGL` and `UNMASKED_RENDERER_WEBGL`
- Realistic GPU models (NVIDIA, AMD, Intel)

#### Audio Fingerprint
- Adds noise to AudioContext and OfflineAudioContext
- Prevents audio fingerprinting

#### Client Rects Fingerprint
- Adds micro-noise to `getBoundingClientRect()` and `getClientRects()`
- Makes each browser instance unique

#### Navigator Properties
- Platform (Win32, MacIntel, Linux x86_64)
- Hardware concurrency (CPU cores)
- Device memory
- Language and languages array
- Do Not Track setting
- Touch support and max touch points

#### Screen Properties
- Custom screen resolution
- Available width/height (accounts for taskbar)
- Color depth and pixel depth

#### Font Enumeration
- Spoofs font detection APIs
- Returns consistent font list

#### Plugin Spoofing
- Realistic Chrome plugins (PDF Viewer, Native Client)
- Prevents plugin-based fingerprinting

#### WebRTC Protection
- Completely disables WebRTC to prevent IP leaks
- Blocks RTCPeerConnection and related APIs

#### Battery API Protection
- Disables battery status API
- Returns consistent "charging" state

#### Connection API
- Spoofs network information
- Returns consistent 4G connection data

### 🎯 Auto-Match Fingerprint
Enter a proxy and click **"🎯 Auto-Match Fingerprint"** to automatically:
1. Validate the proxy
2. Detect the proxy's country/timezone
3. Set matching user-agent, timezone, and language
4. Ensure fingerprint consistency with proxy location

### 🍪 Cookie Management
- **Export Cookies** — Save cookies as JSON for backup or transfer
- **Import Cookies** — Load cookies from JSON file
- Useful for migrating accounts between profiles

### 🧩 Extension Manager
- **Built-in Fingerprint Shield** — Always active, provides anti-detection
- **Install from .crx** — Load Chrome extensions from .crx files
- **Install from Folder** — Load unpacked extensions
- **Remove Extensions** — Uninstall user extensions

Extensions are loaded automatically with every profile launch.

### 🌐 Country & Timezone Database
50+ countries with:
- Proper IANA timezone names
- Language codes (e.g., en-US, de-DE, ja-JP)
- Country codes (ISO 3166-1 alpha-2)

Includes: US, UK, Germany, France, Canada, Australia, Brazil, India, Japan, South Korea, China, Russia, Mexico, Spain, Italy, Netherlands, Sweden, Norway, Denmark, Finland, Poland, Ukraine, Turkey, Thailand, Vietnam, Indonesia, Malaysia, Philippines, Singapore, Hong Kong, Taiwan, New Zealand, South Africa, Nigeria, Egypt, UAE, Saudi Arabia, Israel, Argentina, Chile, Colombia, Peru, Czech Republic, Romania, Hungary, Portugal, Greece, Austria, Switzerland, Belgium, Ireland, Pakistan, Bangladesh

## 🎨 UI Features

### Modern Dark Theme
- Professional dark color scheme
- Easy on the eyes for long sessions
- Clear visual hierarchy

### Tabbed Profile Editor
- **General** — Name, notes, profile ID
- **Proxy** — Proxy configuration with validation
- **Fingerprint** — User-agent, resolution, timezone, language
- **Advanced Spoofing** — Canvas, WebGL, Audio, ClientRects, hardware
- **Cookies** — Import/export functionality

### Profile Management
- Create, edit, duplicate, delete profiles
- Track running instances
- See last used timestamp
- Color-coded status indicators

## 🔧 Technical Details

### Architecture
```
simple_browser/
├── app.py                         # Main UI application
├── core.py                        # Backend logic
├── fingerprint_extension/         # Chrome extension for spoofing
│   ├── manifest.json
│   ├── background.js
│   ├── loader.js
│   └── inject.js                  # Main spoofing engine
├── profile_data/                  # Browser data directories
├── chromium/                      # Downloaded Chromium
├── user_extensions/               # User-installed extensions
└── profiles.json                  # Profile database
```

### Fingerprint Extension
The built-in fingerprint extension runs in Chrome's MAIN world (page context) and intercepts:
- `HTMLCanvasElement.toDataURL()` and `toBlob()`
- `CanvasRenderingContext2D.getImageData()`
- `WebGLRenderingContext.getParameter()`
- `AudioContext.createAnalyser()`
- `Element.getBoundingClientRect()`
- `Navigator` properties
- `Screen` properties
- Font enumeration APIs
- WebRTC APIs
- Battery API
- Connection API

### Chromium Download
Uses **Chrome for Testing** from Google's official CDN:
- Automatically detects your platform (Windows/macOS/Linux)
- Downloads the latest stable version
- Extracts to local `chromium/` directory
- No system installation required

### Proxy Validation
Uses `ip-api.com` to validate proxies and retrieve:
- IP address
- Geolocation (country, region, city)
- Timezone
- ISP information
- Connection latency

## 📊 Comparison with AdsPower/Dolphin Anty

| Feature | SimpleBrowser | AdsPower | Dolphin Anty |
|---------|---------------|----------|--------------|
| **Price** | 🆓 Free | 💰 $5-200/mo | 💰 $89-299/mo |
| **Open Source** | ✅ Yes | ❌ No | ❌ No |
| **Multi-profile** | ✅ | ✅ | ✅ |
| **Proxy support** | ✅ | ✅ | ✅ |
| **Canvas spoofing** | ✅ | ✅ Advanced | ✅ Advanced |
| **WebGL spoofing** | ✅ | ✅ Advanced | ✅ Advanced |
| **Audio spoofing** | ✅ | ✅ Advanced | ✅ Advanced |
| **ClientRects** | ✅ | ✅ | ✅ |
| **Font spoofing** | ✅ | ✅ | ✅ |
| **Auto-match proxy** | ✅ | ✅ | ✅ |
| **Cookie import/export** | ✅ | ✅ | ✅ |
| **Extension manager** | ✅ | ✅ | ✅ |
| **Team collaboration** | ❌ | ✅ Cloud | ✅ Cloud |
| **Built-in automation** | ❌ | ✅ RPA | ✅ |
| **PixelScan pass** | ✅ | ✅ | ✅ |

## 💡 Usage Tips

### For Multi-Accounting
1. Create a profile for each account
2. Use different proxies (residential recommended)
3. Auto-match fingerprint to proxy location
4. Keep Canvas/WebGL/Audio spoofing enabled

### For Web Scraping
1. Create 5-10 profiles with different fingerprints
2. Rotate between them
3. Use rotating proxies
4. Add random delays between requests

### For Privacy
1. Enable all spoofing options
2. Use WebRTC protection
3. Use residential proxies
4. Test at browserleaks.com and pixelscan.net

### Testing Your Setup
Visit these sites to verify your fingerprint:
- [PixelScan.net](https://pixelscan.net) — Comprehensive fingerprint check
- [BrowserLeaks.com](https://browserleaks.com) — Canvas, WebGL, fonts, etc.
- [CreepJS](https://abrahamjuliot.github.io/creepjs/) — Advanced detection
- [Whoer.net](https://whoer.net) — IP and proxy check

## 🐛 Troubleshooting

### Chromium won't download
- Check your internet connection
- Try downloading manually from Settings
- Ensure you have write permissions

### Profile won't launch
- Check Chromium is installed (Settings → Download)
- Ensure no other Chrome is using the same profile
- Check console for errors

### Proxy validation fails
- Verify proxy credentials
- Test proxy outside SimpleBrowser
- Check if proxy is blocked by firewall

### Fingerprint not passing checks
- Enable all spoofing options (Canvas, WebGL, Audio, ClientRects)
- Use Auto-Match to ensure consistency
- Test with different user-agents
- Check timezone/language match proxy location

### Extensions not loading
- Ensure extension has valid manifest.json
- Check extension is compatible with your Chrome version
- Restart the profile after installing extensions

## 🔐 Privacy & Security

### What SimpleBrowser Does
- Isolates browser profiles completely
- Spoofs browser fingerprints
- Protects against WebRTC leaks
- Disables tracking APIs

### What SimpleBrowser Doesn't Do
- Encrypt your traffic (use HTTPS/VPN)
- Hide your real IP (use proxies)
- Make you anonymous (combine with other tools)
- Bypass advanced bot detection (use responsibly)

## 📝 Requirements

- **Python 3.8+** with tkinter (included in most Python installations)
- **Internet connection** (for Chromium download and proxy validation)
- **~500MB disk space** (Chromium + profiles)

## 🚀 Advanced Usage

### Custom Fingerprint Seeds
Each profile gets unique noise seeds for:
- Canvas noise
- Audio noise
- ClientRects noise

These are stored in the profile and remain consistent across sessions.

### Hardware Fingerprinting
Configure realistic hardware:
- CPU cores (2-32)
- Device memory (2-64 GB)
- Screen resolution
- Color depth

### Platform Consistency
Ensure consistency:
- Windows UA → Win32 platform → Windows fonts
- macOS UA → MacIntel platform → macOS fonts
- Linux UA → Linux x86_64 platform → Linux fonts

## 📚 API & Automation

SimpleBrowser stores profiles in `profiles.json`. You can:
- Programmatically create profiles
- Bulk import/export profiles
- Integrate with automation tools (Selenium, Playwright)

Example: Use Selenium with a SimpleBrowser profile:
```python
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

options = Options()
options.add_argument("--user-data-dir=/path/to/simple_browser/profile_data/p_abc12345")
driver = webdriver.Chrome(options=options)
```

## 🤝 Contributing

SimpleBrowser is open source! Contributions welcome:
- Bug reports
- Feature requests
- Code improvements
- Documentation

## 📄 License

MIT License — Use freely for personal or commercial projects.

## ⚠️ Disclaimer

Use responsibly and in compliance with:
- Terms of service of platforms you access
- Local laws and regulations
- Ethical guidelines

This tool is for legitimate use cases like:
- Managing multiple business accounts
- Web scraping for research
- Testing websites
- Privacy protection

**Not for:**
- Fraud or deception
- Bypassing security measures
- Violating platform policies
- Malicious activities

## 🎓 Credits

Inspired by:
- [AdsPower](https://www.adspower.com/)
- [Dolphin Anty](https://dolphin-anty.com/)
- [Multilogin](https://multilogin.com/)

Built with:
- Python & Tkinter
- Chrome for Testing
- Chrome DevTools Protocol concepts

---

**Made with ❤️ for the privacy-conscious community**

For questions, issues, or feature requests, please open an issue on GitHub.
