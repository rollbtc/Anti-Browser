#!/usr/bin/env python3
"""
SimpleBrowser — Core Backend
Handles Chromium downloading, proxy validation, GeoIP matching,
cookie import/export, extension management, and fingerprint generation.
"""

import json
import os
import platform
import shutil
import stat
import subprocess
import sys
import time
import urllib.request
import urllib.error
import zipfile
from pathlib import Path
from typing import Any, Callable

APP_DIR = Path(__file__).resolve().parent
DATA_DIR = APP_DIR / "profile_data"
CHROMIUM_DIR = APP_DIR / "chromium"
EXTENSIONS_DIR = APP_DIR / "user_extensions"
FINGERPRINT_EXT = APP_DIR / "fingerprint_extension"

DATA_DIR.mkdir(exist_ok=True)
CHROMIUM_DIR.mkdir(exist_ok=True)
EXTENSIONS_DIR.mkdir(exist_ok=True)

# ═══════════════════════════════════════════════════════════════════════════════
# COUNTRY / TIMEZONE / LANGUAGE DATA
# ═══════════════════════════════════════════════════════════════════════════════

COUNTRIES = [
    {"code": "US", "name": "United States", "tz": "America/New_York", "lang": "en-US"},
    {"code": "GB", "name": "United Kingdom", "tz": "Europe/London", "lang": "en-GB"},
    {"code": "DE", "name": "Germany", "tz": "Europe/Berlin", "lang": "de-DE"},
    {"code": "FR", "name": "France", "tz": "Europe/Paris", "lang": "fr-FR"},
    {"code": "CA", "name": "Canada", "tz": "America/Toronto", "lang": "en-CA"},
    {"code": "AU", "name": "Australia", "tz": "Australia/Sydney", "lang": "en-AU"},
    {"code": "BR", "name": "Brazil", "tz": "America/Sao_Paulo", "lang": "pt-BR"},
    {"code": "IN", "name": "India", "tz": "Asia/Kolkata", "lang": "hi-IN"},
    {"code": "JP", "name": "Japan", "tz": "Asia/Tokyo", "lang": "ja-JP"},
    {"code": "KR", "name": "South Korea", "tz": "Asia/Seoul", "lang": "ko-KR"},
    {"code": "CN", "name": "China", "tz": "Asia/Shanghai", "lang": "zh-CN"},
    {"code": "RU", "name": "Russia", "tz": "Europe/Moscow", "lang": "ru-RU"},
    {"code": "MX", "name": "Mexico", "tz": "America/Mexico_City", "lang": "es-MX"},
    {"code": "ES", "name": "Spain", "tz": "Europe/Madrid", "lang": "es-ES"},
    {"code": "IT", "name": "Italy", "tz": "Europe/Rome", "lang": "it-IT"},
    {"code": "NL", "name": "Netherlands", "tz": "Europe/Amsterdam", "lang": "nl-NL"},
    {"code": "SE", "name": "Sweden", "tz": "Europe/Stockholm", "lang": "sv-SE"},
    {"code": "NO", "name": "Norway", "tz": "Europe/Oslo", "lang": "nb-NO"},
    {"code": "DK", "name": "Denmark", "tz": "Europe/Copenhagen", "lang": "da-DK"},
    {"code": "FI", "name": "Finland", "tz": "Europe/Helsinki", "lang": "fi-FI"},
    {"code": "PL", "name": "Poland", "tz": "Europe/Warsaw", "lang": "pl-PL"},
    {"code": "UA", "name": "Ukraine", "tz": "Europe/Kiev", "lang": "uk-UA"},
    {"code": "TR", "name": "Turkey", "tz": "Europe/Istanbul", "lang": "tr-TR"},
    {"code": "TH", "name": "Thailand", "tz": "Asia/Bangkok", "lang": "th-TH"},
    {"code": "VN", "name": "Vietnam", "tz": "Asia/Ho_Chi_Minh", "lang": "vi-VN"},
    {"code": "ID", "name": "Indonesia", "tz": "Asia/Jakarta", "lang": "id-ID"},
    {"code": "MY", "name": "Malaysia", "tz": "Asia/Kuala_Lumpur", "lang": "ms-MY"},
    {"code": "PH", "name": "Philippines", "tz": "Asia/Manila", "lang": "en-PH"},
    {"code": "SG", "name": "Singapore", "tz": "Asia/Singapore", "lang": "en-SG"},
    {"code": "HK", "name": "Hong Kong", "tz": "Asia/Hong_Kong", "lang": "zh-HK"},
    {"code": "TW", "name": "Taiwan", "tz": "Asia/Taipei", "lang": "zh-TW"},
    {"code": "NZ", "name": "New Zealand", "tz": "Pacific/Auckland", "lang": "en-NZ"},
    {"code": "ZA", "name": "South Africa", "tz": "Africa/Johannesburg", "lang": "en-ZA"},
    {"code": "NG", "name": "Nigeria", "tz": "Africa/Lagos", "lang": "en-NG"},
    {"code": "EG", "name": "Egypt", "tz": "Africa/Cairo", "lang": "ar-EG"},
    {"code": "AE", "name": "UAE", "tz": "Asia/Dubai", "lang": "ar-AE"},
    {"code": "SA", "name": "Saudi Arabia", "tz": "Asia/Riyadh", "lang": "ar-SA"},
    {"code": "IL", "name": "Israel", "tz": "Asia/Jerusalem", "lang": "he-IL"},
    {"code": "AR", "name": "Argentina", "tz": "America/Argentina/Buenos_Aires", "lang": "es-AR"},
    {"code": "CL", "name": "Chile", "tz": "America/Santiago", "lang": "es-CL"},
    {"code": "CO", "name": "Colombia", "tz": "America/Bogota", "lang": "es-CO"},
    {"code": "PE", "name": "Peru", "tz": "America/Lima", "lang": "es-PE"},
    {"code": "CZ", "name": "Czech Republic", "tz": "Europe/Prague", "lang": "cs-CZ"},
    {"code": "RO", "name": "Romania", "tz": "Europe/Bucharest", "lang": "ro-RO"},
    {"code": "HU", "name": "Hungary", "tz": "Europe/Budapest", "lang": "hu-HU"},
    {"code": "PT", "name": "Portugal", "tz": "Europe/Lisbon", "lang": "pt-PT"},
    {"code": "GR", "name": "Greece", "tz": "Europe/Athens", "lang": "el-GR"},
    {"code": "AT", "name": "Austria", "tz": "Europe/Vienna", "lang": "de-AT"},
    {"code": "CH", "name": "Switzerland", "tz": "Europe/Zurich", "lang": "de-CH"},
    {"code": "BE", "name": "Belgium", "tz": "Europe/Brussels", "lang": "nl-BE"},
    {"code": "IE", "name": "Ireland", "tz": "Europe/Dublin", "lang": "en-IE"},
    {"code": "PK", "name": "Pakistan", "tz": "Asia/Karachi", "lang": "ur-PK"},
    {"code": "BD", "name": "Bangladesh", "tz": "Asia/Dhaka", "lang": "bn-BD"},
]

# Map IANA timezone region prefix → country code
TZ_TO_COUNTRY = {}
for c in COUNTRIES:
    TZ_TO_COUNTRY[c["tz"]] = c["code"]
    # Also map by the region part
    parts = c["tz"].split("/")
    if len(parts) >= 2:
        TZ_TO_COUNTRY[parts[-1]] = c["code"]

# ═══════════════════════════════════════════════════════════════════════════════
# CHROMIUM DOWNLOADER
# ═══════════════════════════════════════════════════════════════════════════════

CHROME_FOR_TESTING_API = (
    "https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions.json"
)

def get_system_platform() -> str:
    s = platform.system().lower()
    m = platform.machine().lower()
    if s == "windows":
        return "win64"
    elif s == "darwin":
        return "mac-arm64" if m == "arm64" else "mac-x64"
    else:
        return "linux64"

def get_chromium_binary_name() -> str:
    s = platform.system().lower()
    if s == "windows":
        return "chrome.exe"
    elif s == "darwin":
        return "Google Chrome for Testing"
    else:
        return "chrome"

def find_existing_chromium() -> str | None:
    """Check if we already downloaded Chromium or can find it on the system."""
    # Check our own download directory first
    plat = get_system_platform()
    if "mac" in plat:
        candidates = [
            CHROMIUM_DIR / "chrome-mac-x64" / "Google Chrome for Testing.app"
                         / "Contents" / "MacOS" / "Google Chrome for Testing",
            CHROMIUM_DIR / "chrome-mac-arm64" / "Google Chrome for Testing.app"
                         / "Contents" / "MacOS" / "Google Chrome for Testing",
        ]
    elif "win" in plat:
        candidates = [
            CHROMIUM_DIR / "chrome-win64" / "chrome.exe",
        ]
    else:
        candidates = [
            CHROMIUM_DIR / "chrome-linux64" / "chrome",
        ]

    for c in candidates:
        if c.exists():
            return str(c)

    # Check system installations
    system_paths = [
        "/usr/bin/google-chrome",
        "/usr/bin/google-chrome-stable",
        "/usr/bin/chromium",
        "/usr/bin/chromium-browser",
        "/snap/bin/chromium",
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Chromium.app/Contents/MacOS/Chromium",
    ]
    for p in system_paths:
        if os.path.isfile(p):
            return p

    # Check PATH
    for name in ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "chrome"):
        found = shutil.which(name)
        if found:
            return found

    return None

def get_latest_chromium_version() -> str:
    """Fetch the latest stable Chrome for Testing version."""
    try:
        req = urllib.request.Request(CHROME_FOR_TESTING_API,
                                    headers={"User-Agent": "SimpleBrowser/2.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
            return data["channels"]["Stable"]["version"]
    except Exception:
        return "131.0.6778.85"  # fallback

def get_chromium_download_url(version: str | None = None) -> tuple[str, str]:
    """Return (url, version) for the Chromium download."""
    if version is None:
        version = get_latest_chromium_version()
    plat = get_system_platform()
    url = f"https://storage.googleapis.com/chrome-for-testing-public/{version}/{plat}/chrome-{plat}.zip"
    return url, version

def download_chromium(progress_cb: Callable[[int, int], None] | None = None,
                      status_cb: Callable[[str], None] | None = None) -> str | None:
    """
    Download and extract Chrome for Testing. Returns path to binary or None.
    progress_cb(bytes_downloaded, total_bytes)
    status_cb(message_string)
    """
    def _status(msg):
        if status_cb:
            status_cb(msg)

    def _progress(dl, total):
        if progress_cb:
            progress_cb(dl, total)

    _status("Fetching latest version info...")
    url, version = get_chromium_download_url()
    _status(f"Downloading Chrome {version}...")

    zip_path = CHROMIUM_DIR / f"chrome-{get_system_platform()}.zip"

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "SimpleBrowser/2.0"})
        with urllib.request.urlopen(req, timeout=300) as resp:
            total = int(resp.headers.get("Content-Length", 0))
            downloaded = 0
            chunk_size = 1024 * 256  # 256KB chunks

            with open(zip_path, "wb") as f:
                while True:
                    chunk = resp.read(chunk_size)
                    if not chunk:
                        break
                    f.write(chunk)
                    downloaded += len(chunk)
                    _progress(downloaded, total)

        _status("Extracting...")
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(CHROMIUM_DIR)

        # Make binary executable on Unix
        binary = find_existing_chromium()
        if binary and platform.system().lower() != "windows":
            st = os.stat(binary)
            os.chmod(binary, st.st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)

        # Clean up zip
        zip_path.unlink(missing_ok=True)

        _status("Done!")
        return binary

    except Exception as e:
        _status(f"Error: {e}")
        return None


# ═══════════════════════════════════════════════════════════════════════════════
# PROXY VALIDATOR
# ═══════════════════════════════════════════════════════════════════════════════

def validate_proxy(proxy_type: str, host: str, port: str,
                   username: str = "", password: str = "",
                   timeout: int = 10) -> dict:
    """
    Validate a proxy by connecting through it and checking IP info.
    Supports HTTP, HTTPS, SOCKS4, and SOCKS5 proxies.
    """
    result = {
        "success": False, "ip": "", "country": "", "country_code": "",
        "region": "", "city": "", "timezone": "", "isp": "",
        "latency_ms": 0, "error": ""
    }

    if not host or not port:
        result["error"] = "Host and port are required"
        return result

    try:
        import socket
        
        # For SOCKS proxies, we need to use socket directly or PySocks
        if proxy_type in ("socks4", "socks5"):
            # Try to use PySocks if available
            try:
                import socks
                
                # Set up SOCKS proxy
                if proxy_type == "socks5":
                    socks.set_default_proxy(socks.SOCKS5, host, int(port), 
                                          username=username or None, 
                                          password=password or None)
                else:  # socks4
                    socks.set_default_proxy(socks.SOCKS4, host, int(port))
                
                # Wrap socket
                socket.socket = socks.socksocket
                
                # Make request
                start = time.time()
                req = urllib.request.Request(
                    "http://ip-api.com/json/?fields=status,message,country,countryCode,regionName,city,timezone,isp,org,query",
                    headers={"User-Agent": "Mozilla/5.0"}
                )
                with urllib.request.urlopen(req, timeout=timeout) as resp:
                    data = json.loads(resp.read())
                    latency = int((time.time() - start) * 1000)
                
                # Reset socket
                socket.socket = socket._socketobject if hasattr(socket, '_socketobject') else socket.socket
                
            except ImportError:
                # PySocks not available, try manual SOCKS5 implementation
                result["error"] = "SOCKS support requires 'pysocks' package. Install with: pip install pysocks"
                return result
        
        else:  # HTTP/HTTPS proxy
            # Build proxy URL
            if username and password:
                proxy_url = f"http://{username}:{password}@{host}:{port}"
            else:
                proxy_url = f"http://{host}:{port}"

            proxy_handler = urllib.request.ProxyHandler({
                "http": proxy_url,
                "https": proxy_url,
            })

            start = time.time()
            opener = urllib.request.build_opener(proxy_handler)
            
            req = urllib.request.Request(
                "http://ip-api.com/json/?fields=status,message,country,countryCode,regionName,city,timezone,isp,org,query",
                headers={"User-Agent": "Mozilla/5.0"}
            )
            with opener.open(req, timeout=timeout) as resp:
                data = json.loads(resp.read())
                latency = int((time.time() - start) * 1000)

        if data.get("status") == "success":
            result.update({
                "success": True,
                "ip": data.get("query", ""),
                "country": data.get("country", ""),
                "country_code": data.get("countryCode", ""),
                "region": data.get("regionName", ""),
                "city": data.get("city", ""),
                "timezone": data.get("timezone", ""),
                "isp": data.get("isp", ""),
                "latency_ms": latency,
            })
        else:
            result["error"] = data.get("message", "Unknown error")

    except urllib.error.URLError as e:
        result["error"] = f"Connection failed: {str(e.reason)}"
    except socket.timeout:
        result["error"] = "Connection timeout"
    except Exception as e:
        result["error"] = f"Error: {str(e)}"

    return result


# ═══════════════════════════════════════════════════════════════════════════════
# GEOIP AUTO-MATCH
# ═══════════════════════════════════════════════════════════════════════════════

def get_country_for_code(code: str) -> dict | None:
    code = code.upper()
    for c in COUNTRIES:
        if c["code"] == code:
            return c
    return None

def auto_match_fingerprint(proxy_info: dict) -> dict:
    """
    Given proxy validation results, return matching fingerprint settings.
    """
    cc = proxy_info.get("country_code", "US")
    country = get_country_for_code(cc) or COUNTRIES[0]  # fallback to US

    # Build user-agent matching the country's common platform
    import random
    chrome_ver = random.randint(125, 131)

    ua_templates = {
        "windows": f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome_ver}.0.0.0 Safari/537.36",
        "mac":     f"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome_ver}.0.0.0 Safari/537.36",
        "linux":   f"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome_ver}.0.0.0 Safari/537.36",
    }
    platform_choice = random.choice(["windows", "windows", "windows", "mac", "linux"])
    user_agent = ua_templates[platform_choice]

    # Match timezone from the proxy's detected timezone
    tz = proxy_info.get("timezone", country["tz"])

    return {
        "user_agent": user_agent,
        "timezone": tz,
        "language": country["lang"],
        "country": country["name"],
        "country_code": cc,
        "platform": platform_choice,
        "chrome_version": chrome_ver,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# FINGERPRINT GENERATION
# ═══════════════════════════════════════════════════════════════════════════════

import random

# Realistic WebGL vendors and renderers (2024-2025)
WEBGL_VENDORS = [
    ("Google Inc. (NVIDIA)", "ANGLE (NVIDIA, NVIDIA GeForce RTX 4090 Direct3D11 vs_5_0 ps_5_0, D3D11)"),
    ("Google Inc. (NVIDIA)", "ANGLE (NVIDIA, NVIDIA GeForce RTX 4080 Direct3D11 vs_5_0 ps_5_0, D3D11)"),
    ("Google Inc. (NVIDIA)", "ANGLE (NVIDIA, NVIDIA GeForce RTX 4070 Ti Direct3D11 vs_5_0 ps_5_0, D3D11)"),
    ("Google Inc. (NVIDIA)", "ANGLE (NVIDIA, NVIDIA GeForce RTX 3080 Direct3D11 vs_5_0 ps_5_0, D3D11)"),
    ("Google Inc. (NVIDIA)", "ANGLE (NVIDIA, NVIDIA GeForce RTX 3070 Direct3D11 vs_5_0 ps_5_0, D3D11)"),
    ("Google Inc. (NVIDIA)", "ANGLE (NVIDIA, NVIDIA GeForce GTX 1660 Ti Direct3D11 vs_5_0 ps_5_0, D3D11)"),
    ("Google Inc. (AMD)", "ANGLE (AMD, AMD Radeon RX 7900 XTX Direct3D11 vs_5_0 ps_5_0, D3D11)"),
    ("Google Inc. (AMD)", "ANGLE (AMD, AMD Radeon RX 6800 XT Direct3D11 vs_5_0 ps_5_0, D3D11)"),
    ("Google Inc. (AMD)", "ANGLE (AMD, AMD Radeon RX 580 Direct3D11 vs_5_0 ps_5_0, D3D11)"),
    ("Google Inc. (Intel)", "ANGLE (Intel, Intel(R) UHD Graphics 770 Direct3D11 vs_5_0 ps_5_0, D3D11)"),
    ("Google Inc. (Intel)", "ANGLE (Intel, Intel(R) Iris(R) Xe Graphics Direct3D11 vs_5_0 ps_5_0, D3D11)"),
    ("Google Inc. (Apple)", "ANGLE (Apple, Apple M2 Pro, OpenGL 4.1)"),
    ("Google Inc. (Apple)", "ANGLE (Apple, Apple M1 Max, OpenGL 4.1)"),
]

# Common screen resolutions (2024-2025)
SCREEN_RESOLUTIONS = [
    (1920, 1080), (2560, 1440), (1366, 768), (1536, 864),
    (1440, 900), (1280, 720), (1680, 1050), (1920, 1200),
    (3840, 2160), (1600, 900), (1280, 800), (1280, 1024),
    (2560, 1600), (3440, 1440), (2560, 1080),
]

COLOR_DEPTHS = [24, 32]
PIXEL_DEPTHS = [24, 32]

# Realistic CPU core counts (2024-2025)
HARDWARE_CONCURRENCY = [4, 6, 8, 12, 16, 20, 24, 32]

# Realistic RAM sizes in GB (2024-2025)
DEVICE_MEMORY = [8, 16, 32, 64]

PLATFORM_INFO = {
    "windows": {
        "platform": "Win32",
        "vendor": "Google Inc.",
        "oscpu_values": ["Windows NT 10.0; Win64; x64"],
    },
    "mac": {
        "platform": "MacIntel",
        "vendor": "Apple Computer, Inc.",
        "oscpu_values": ["Intel Mac OS X 10_15_7"],
    },
    "linux": {
        "platform": "Linux x86_64",
        "vendor": "Google Inc.",
        "oscpu_values": ["Linux x86_64"],
    },
}

def generate_fingerprint(user_agent: str = "", platform_name: str = "",
                         resolution: str = "", language: str = "",
                         timezone: str = "") -> dict:
    """Generate a complete browser fingerprint."""
    import random

    # Detect platform from UA or use provided
    if not platform_name:
        if "Windows" in user_agent:
            platform_name = "windows"
        elif "Macintosh" in user_agent:
            platform_name = "mac"
        else:
            platform_name = random.choice(["windows", "windows", "mac", "linux"])

    pinfo = PLATFORM_INFO.get(platform_name, PLATFORM_INFO["windows"])

    # Resolution
    if resolution and "x" in resolution:
        w, h = map(int, resolution.split("x"))
    else:
        w, h = random.choice(SCREEN_RESOLUTIONS)

    # WebGL
    webgl_vendor, webgl_renderer = random.choice(WEBGL_VENDORS)

    # Canvas noise seed (unique per profile)
    canvas_noise_seed = random.random()

    # Audio noise
    audio_noise = random.uniform(-0.0001, 0.0001)

    return {
        "platform": pinfo["platform"],
        "vendor": pinfo["vendor"],
        "screen_width": w,
        "screen_height": h,
        "avail_width": w,
        "avail_height": h - random.choice([0, 40, 48, 72]),  # taskbar
        "color_depth": random.choice(COLOR_DEPTHS),
        "pixel_depth": random.choice(PIXEL_DEPTHS),
        "hardware_concurrency": random.choice(HARDWARE_CONCURRENCY),
        "device_memory": random.choice(DEVICE_MEMORY),
        "webgl_vendor": webgl_vendor,
        "webgl_renderer": webgl_renderer,
        "canvas_noise_seed": canvas_noise_seed,
        "audio_noise": audio_noise,
        "client_rects_noise": random.uniform(-0.1, 0.1),
        "language": language or "en-US",
        "timezone": timezone or "America/New_York",
        "user_agent": user_agent,
        "do_not_track": random.choice([None, "1"]),
        "touch_support": random.choice([False, False, False, True]),
        "max_touch_points": random.choice([0, 0, 0, 5, 10]),
    }


# ═══════════════════════════════════════════════════════════════════════════════
# COOKIE IMPORT / EXPORT
# ═══════════════════════════════════════════════════════════════════════════════

def export_cookies(profile_id: str, output_path: str) -> bool:
    """Export cookies from a profile's Chrome data dir as JSON."""
    profile_dir = DATA_DIR / f"p_{profile_id}" / "Default"
    cookie_db = profile_dir / "Cookies"

    if not cookie_db.exists():
        return False

    try:
        import sqlite3
        conn = sqlite3.connect(str(cookie_db))
        cursor = conn.cursor()
        cursor.execute("""
            SELECT host_key, name, value, path, expires_utc, is_secure, is_httponly, samesite
            FROM cookies
        """)
        cookies = []
        for row in cursor.fetchall():
            cookies.append({
                "domain": row[0],
                "name": row[1],
                "value": row[2],
                "path": row[3],
                "expires": row[4],
                "secure": bool(row[5]),
                "httpOnly": bool(row[6]),
                "sameSite": ["no_restriction", "lax", "strict"][min(row[7], 2)] if row[7] else "lax",
            })
        conn.close()

        with open(output_path, "w") as f:
            json.dump(cookies, f, indent=2)
        return True
    except Exception:
        return False


def export_cookies_text(profile_id: str, output_path: str) -> bool:
    """Export cookies in Netscape format (text file)."""
    profile_dir = DATA_DIR / f"p_{profile_id}" / "Default"
    cookie_db = profile_dir / "Cookies"

    if not cookie_db.exists():
        return False

    try:
        import sqlite3
        conn = sqlite3.connect(str(cookie_db))
        cursor = conn.cursor()
        cursor.execute("""
            SELECT host_key, name, value, path, expires_utc, is_secure, is_httponly
            FROM cookies
        """)
        
        with open(output_path, "w") as f:
            f.write("# Netscape HTTP Cookie File\n")
            f.write("# This file was generated by SimpleBrowser\n\n")
            
            for row in cursor.fetchall():
                domain = row[0]
                flag = "TRUE" if domain.startswith(".") else "FALSE"
                path = row[3]
                secure = "TRUE" if row[5] else "FALSE"
                expires = str(row[4])
                name = row[1]
                value = row[2]
                
                f.write(f"{domain}\t{flag}\t{path}\t{secure}\t{expires}\t{name}\t{value}\n")
        
        conn.close()
        return True
    except Exception:
        return False


def import_cookies(profile_id: str, input_path: str) -> bool:
    """Import cookies into a profile's Chrome data dir from JSON."""
    profile_dir = DATA_DIR / f"p_{profile_id}" / "Default"
    cookie_db = profile_dir / "Cookies"

    if not cookie_db.exists():
        return False

    try:
        with open(input_path, "r") as f:
            cookies = json.load(f)

        import sqlite3
        conn = sqlite3.connect(str(cookie_db))
        cursor = conn.cursor()

        for c in cookies:
            samesite = {"no_restriction": 0, "lax": 1, "strict": 2}.get(c.get("sameSite", "lax"), 1)
            cursor.execute("""
                INSERT OR REPLACE INTO cookies
                (host_key, name, value, path, expires_utc, is_secure, is_httponly, samesite)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                c["domain"], c["name"], c["value"], c["path"],
                c.get("expires", 0), int(c.get("secure", False)),
                int(c.get("httpOnly", False)), samesite
            ))

        conn.commit()
        conn.close()
        return True
    except Exception:
        return False


def import_cookies_text(profile_id: str, input_path: str) -> bool:
    """Import cookies from Netscape format (text file)."""
    profile_dir = DATA_DIR / f"p_{profile_id}" / "Default"
    cookie_db = profile_dir / "Cookies"

    if not cookie_db.exists():
        return False

    try:
        import sqlite3
        conn = sqlite3.connect(str(cookie_db))
        cursor = conn.cursor()

        with open(input_path, "r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                
                parts = line.split("\t")
                if len(parts) >= 7:
                    domain = parts[0]
                    path = parts[2]
                    secure = 1 if parts[3] == "TRUE" else 0
                    expires = int(parts[4]) if parts[4].isdigit() else 0
                    name = parts[5]
                    value = parts[6]
                    
                    cursor.execute("""
                        INSERT OR REPLACE INTO cookies
                        (host_key, name, value, path, expires_utc, is_secure, is_httponly, samesite)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (domain, name, value, path, expires, secure, 0, 1))

        conn.commit()
        conn.close()
        return True
    except Exception:
        return False


# ═══════════════════════════════════════════════════════════════════════════════
# EXTENSION MANAGER
# ═══════════════════════════════════════════════════════════════════════════════

def list_installed_extensions() -> list[dict]:
    """List extensions in the user_extensions directory."""
    exts = []
    if EXTENSIONS_DIR.exists():
        for d in EXTENSIONS_DIR.iterdir():
            if d.is_dir():
                manifest = d / "manifest.json"
                if manifest.exists():
                    try:
                        m = json.loads(manifest.read_text())
                        exts.append({
                            "id": d.name,
                            "name": m.get("name", d.name),
                            "version": m.get("version", "?"),
                            "description": m.get("description", ""),
                            "path": str(d),
                        })
                    except Exception:
                        exts.append({
                            "id": d.name, "name": d.name,
                            "version": "?", "description": "", "path": str(d),
                        })
    return exts


def install_extension_from_crx(crx_path: str) -> dict | None:
    """
    Install a CRX extension by extracting it to user_extensions/.
    Returns extension info dict or None on failure.
    """
    try:
        import tempfile
        ext_id = Path(crx_path).stem
        dest = EXTENSIONS_DIR / ext_id
        dest.mkdir(parents=True, exist_ok=True)

        # CRX files have a header before the zip data
        with open(crx_path, "rb") as f:
            magic = f.read(4)
            if magic == b"Cr24":
                # CRX format: skip header
                version = int.from_bytes(f.read(4), "little")
                if version == 3:
                    header_size = int.from_bytes(f.read(4), "little")
                    f.seek(12 + header_size)
                elif version == 2:
                    pk_len = int.from_bytes(f.read(4), "little")
                    sig_len = int.from_bytes(f.read(4), "little")
                    f.seek(16 + pk_len + sig_len)
                else:
                    f.seek(0)
            else:
                f.seek(0)

            # Write remaining as zip
            zip_data = f.read()

        with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as tmp:
            tmp.write(zip_data)
            tmp_path = tmp.name

        with zipfile.ZipFile(tmp_path, "r") as zf:
            zf.extractall(dest)

        os.unlink(tmp_path)

        # Read manifest
        manifest = dest / "manifest.json"
        if manifest.exists():
            m = json.loads(manifest.read_text())
            return {
                "id": ext_id,
                "name": m.get("name", ext_id),
                "version": m.get("version", "?"),
                "path": str(dest),
            }
        return {"id": ext_id, "name": ext_id, "version": "?", "path": str(dest)}

    except Exception:
        return None


def install_extension_from_folder(folder_path: str) -> dict | None:
    """Install an extension by copying its folder."""
    try:
        src = Path(folder_path)
        ext_id = src.name
        dest = EXTENSIONS_DIR / ext_id
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(src, dest)

        manifest = dest / "manifest.json"
        if manifest.exists():
            m = json.loads(manifest.read_text())
            return {
                "id": ext_id,
                "name": m.get("name", ext_id),
                "version": m.get("version", "?"),
                "path": str(dest),
            }
        return {"id": ext_id, "name": ext_id, "version": "?", "path": str(dest)}
    except Exception:
        return None


def uninstall_extension(ext_id: str) -> bool:
    """Remove an extension."""
    ext_dir = EXTENSIONS_DIR / ext_id
    if ext_dir.exists():
        shutil.rmtree(ext_dir)
        return True
    return False


def get_extension_load_paths() -> list[str]:
    """Get all extension paths for Chrome --load-extension flag."""
    paths = []
    # Always include the built-in fingerprint extension
    if FINGERPRINT_EXT.exists() and (FINGERPRINT_EXT / "manifest.json").exists():
        paths.append(str(FINGERPRINT_EXT))
        print(f"[Extensions] Loaded: fingerprint_extension", file=sys.stderr)

    # Add window lock extension
    window_lock_ext = APP_DIR / "window_lock_extension"
    if window_lock_ext.exists() and (window_lock_ext / "manifest.json").exists():
        paths.append(str(window_lock_ext))
        print(f"[Extensions] Loaded: window_lock_extension", file=sys.stderr)

    # Add virtual camera extension
    virtual_camera_ext = APP_DIR / "virtual_camera_extension"
    if virtual_camera_ext.exists() and (virtual_camera_ext / "manifest.json").exists():
        paths.append(str(virtual_camera_ext))
        print(f"[Extensions] Loaded: virtual_camera_extension", file=sys.stderr)

    # Add proxy auth extension if it exists
    proxy_auth_ext = DATA_DIR / "proxy_auth_extension"
    if proxy_auth_ext.exists() and (proxy_auth_ext / "manifest.json").exists():
        paths.append(str(proxy_auth_ext))
        print(f"[Extensions] Loaded: proxy_auth_extension", file=sys.stderr)

    # Add user-installed extensions
    for ext in list_installed_extensions():
        paths.append(ext["path"])
        print(f"[Extensions] Loaded: {ext['name']}", file=sys.stderr)

    return paths


# ═══════════════════════════════════════════════════════════════════════════════
# PROFILE MODEL
# ═══════════════════════════════════════════════════════════════════════════════

PROFILES_DB = APP_DIR / "profiles.json"

def load_profiles() -> list[dict]:
    if PROFILES_DB.exists():
        try:
            return json.loads(PROFILES_DB.read_text())
        except Exception:
            return []
    return []

def save_profiles(profiles: list[dict]) -> None:
    PROFILES_DB.write_text(json.dumps(profiles, indent=2))


def new_profile(name: str = "New Profile", **overrides) -> dict:
    import uuid
    # Use recent Chrome versions (2024-2025)
    chrome_ver = random.randint(128, 132)
    ua_templates = [
        f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome_ver}.0.0.0 Safari/537.36",
        f"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome_ver}.0.0.0 Safari/537.36",
        f"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome_ver}.0.0.0 Safari/537.36",
    ]
    colors = ["#4F8EF7", "#7C5CFC", "#22C55E", "#F59E0B", "#EF4444",
              "#EC4899", "#06B6D4", "#8B5CF6", "#10B981", "#F97316"]
    res = random.choice(SCREEN_RESOLUTIONS)

    fp = generate_fingerprint(
        user_agent=random.choice(ua_templates),
        resolution=f"{res[0]}x{res[1]}",
        language="en-US",
        timezone="America/New_York"
    )

    from datetime import datetime
    profile = {
        "id": str(uuid.uuid4())[:8],
        "name": name,
        "color": random.choice(colors),
        "proxy_type": "none",
        "proxy_host": "",
        "proxy_port": "",
        "proxy_user": "",
        "proxy_pass": "",
        "user_agent": fp["user_agent"],
        "resolution": f"{fp['screen_width']}x{fp['screen_height']}",
        "timezone": fp["timezone"],
        "language": fp["language"],
        "webrtc": "disabled",
        "canvas_spoof": "noise",
        "webgl_spoof": "custom",
        "audio_spoof": "noise",
        "client_rects_spoof": "noise",
        "font_spoof": "custom",
        "webgl_vendor": fp["webgl_vendor"],
        "webgl_renderer": fp["webgl_renderer"],
        "platform": fp["platform"],
        "vendor": fp["vendor"],
        "hardware_concurrency": fp["hardware_concurrency"],
        "device_memory": fp["device_memory"],
        "color_depth": fp["color_depth"],
        "pixel_depth": fp["pixel_depth"],
        "canvas_noise_seed": fp["canvas_noise_seed"],
        "audio_noise": fp["audio_noise"],
        "client_rects_noise": fp["client_rects_noise"],
        "do_not_track": fp["do_not_track"],
        "touch_support": fp["touch_support"],
        "max_touch_points": fp["max_touch_points"],
        "notes": "",
        "extensions": [],
        "created_at": datetime.utcnow().isoformat(),
        "last_used": None,
    }
    profile.update(overrides)
    return profile


# ═══════════════════════════════════════════════════════════════════════════════
# CHROME LAUNCHER
# ═══════════════════════════════════════════════════════════════════════════════

def write_fingerprint_config(profile_id: str, profile: dict) -> str:
    """Write fingerprint config JSON that the extension reads."""
    config_dir = DATA_DIR / f"p_{profile_id}" / "Default"
    config_dir.mkdir(parents=True, exist_ok=True)
    config_path = DATA_DIR / f"p_{profile_id}" / "fingerprint_config.json"

    config = {
        "canvas_spoof": profile.get("canvas_spoof", "noise"),
        "canvas_noise_seed": profile.get("canvas_noise_seed", 0.5),
        "webgl_spoof": profile.get("webgl_spoof", "custom"),
        "webgl_vendor": profile.get("webgl_vendor", ""),
        "webgl_renderer": profile.get("webgl_renderer", ""),
        "audio_spoof": profile.get("audio_spoof", "noise"),
        "audio_noise": profile.get("audio_noise", 0.00001),
        "client_rects_spoof": profile.get("client_rects_spoof", "noise"),
        "client_rects_noise": profile.get("client_rects_noise", 0.05),
        "font_spoof": profile.get("font_spoof", "custom"),
        "platform": profile.get("platform", "Win32"),
        "vendor": profile.get("vendor", "Google Inc."),
        "hardware_concurrency": profile.get("hardware_concurrency", 8),
        "device_memory": profile.get("device_memory", 8),
        "color_depth": profile.get("color_depth", 24),
        "pixel_depth": profile.get("pixel_depth", 24),
        "screen_width": int(profile.get("resolution", "1920x1080").split("x")[0]),
        "screen_height": int(profile.get("resolution", "1920x1080").split("x")[1]),
        "language": profile.get("language", "en-US"),
        "timezone": profile.get("timezone", "UTC"),
        "user_agent": profile.get("user_agent", ""),
        "do_not_track": profile.get("do_not_track"),
        "touch_support": profile.get("touch_support", False),
        "max_touch_points": profile.get("max_touch_points", 0),
        "webrtc": profile.get("webrtc", "disabled"),
    }

    config_path.write_text(json.dumps(config, indent=2))
    return str(config_path)


def build_chrome_args(profile: dict, chrome_path: str) -> list[str]:
    """Build Chrome launch arguments with deep fingerprint protection."""
    profile_dir = DATA_DIR / f"p_{profile['id']}"
    profile_dir.mkdir(parents=True, exist_ok=True)

    width, height = profile.get("resolution", "1920x1080").split("x")
    timezone = profile.get("timezone", "America/New_York")
    language = profile.get("language", "en-US")

    args = [
        chrome_path,
        f"--user-data-dir={profile_dir}",
        f"--window-size={width},{height}",
        f"--window-position=0,0",
        
        # Deep timezone spoofing (browser-level)
        f"--timezone={timezone}",
        
        # Language and locale
        f"--lang={language}",
        
        # Disable features that leak information
        "--disable-features=TranslateUI,MediaStreamTrackUseInk",
        "--disable-background-timer-throttling",
        "--disable-renderer-backgrounding",
        "--disable-backgrounding-occluded-windows",
        
        # Security and sandbox
        "--no-sandbox",
        "--disable-dev-shm-usage",
        
        # Anti-detection
        "--disable-blink-features=AutomationControlled",
        "--disable-infobars",
        "--no-first-run",
        "--no-default-browser-check",
        
        # Window management (lock size)
        "--disable-features=WindowCapture,DesktopCapture",
        "--disable-popup-blocking",
        "--disable-prompt-on-repost",
        
        # Network
        "--disable-translate",
        "--metrics-recording-only",
        "--safebrowsing-disable-auto-update",
        
        # GPU
        "--disable-gpu-sandbox",
    ]

    # WebRTC protection
    if profile.get("webrtc") == "disabled":
        args.append("--disable-webrtc-multiple-routes")

    # Extensions
    ext_paths = get_extension_load_paths()
    if ext_paths:
        args.append(f"--load-extension={','.join(ext_paths)}")
        args.append("--disable-extensions-except=" + ",".join(ext_paths))

    # Proxy configuration
    ptype = profile.get("proxy_type", "none")
    if ptype in ("http", "socks5") and profile.get("proxy_host"):
        proxy_host = profile['proxy_host']
        proxy_port = profile.get('proxy_port', '80')
        proxy_user = profile.get('proxy_user', '')
        proxy_pass = profile.get('proxy_pass', '')
        
        if proxy_user and proxy_pass:
            proxy_str = f"{ptype}://{proxy_host}:{proxy_port}"
            args.append(f"--proxy-server={proxy_str}")
            write_proxy_auth_extension(proxy_user, proxy_pass)
        else:
            if ptype == "socks5":
                proxy_str = f"socks5://{proxy_host}:{proxy_port}"
            else:
                proxy_str = f"http://{proxy_host}:{proxy_port}"
            args.append(f"--proxy-server={proxy_str}")
        
        args.append("--proxy-bypass-list=localhost;127.0.0.1")

    return args


def write_proxy_auth_extension(username: str, password: str):
    """Create a temporary extension to handle proxy authentication."""
    auth_ext_dir = DATA_DIR / "proxy_auth_extension"
    auth_ext_dir.mkdir(parents=True, exist_ok=True)
    
    # Create manifest
    manifest = {
        "manifest_version": 3,
        "name": "Proxy Auth",
        "version": "1.0",
        "background": {
            "service_worker": "background.js"
        },
        "permissions": ["webRequest", "webRequestAuthProvider"],
        "host_permissions": ["<all_urls>"]
    }
    
    with open(auth_ext_dir / "manifest.json", "w") as f:
        json.dump(manifest, f, indent=2)
    
    # Create background script (Manifest V3 compatible)
    background_js = f"""
// Proxy authentication handler for Manifest V3
chrome.webRequest.onAuthRequired.addListener(
    function(details, callback) {{
        console.log('[Proxy Auth] Authentication required for:', details.url);
        callback({{
            authCredentials: {{
                username: {json.dumps(username)},
                password: {json.dumps(password)}
            }}
        }});
    }},
    {{urls: ["<all_urls>"]}},
    ['asyncBlocking']
);

console.log('[Proxy Auth] Extension loaded');
"""
    
    with open(auth_ext_dir / "background.js", "w") as f:
        f.write(background_js)
    
    print(f"[SimpleBrowser] Proxy auth extension created at: {auth_ext_dir}", file=sys.stderr)


def launch_profile(profile: dict, chrome_path: str) -> subprocess.Popen | None:
    """Launch Chrome for a profile with window locking via CDP."""
    import sys
    import json
    import time
    import threading
    
    # Write fingerprint config for the extension
    write_fingerprint_config(profile["id"], profile)

    args = build_chrome_args(profile, chrome_path)
    
    # Enable Chrome DevTools Protocol for window locking
    debug_port = 9222 + hash(profile["id"]) % 1000  # Unique port per profile
    args.append(f"--remote-debugging-port={debug_port}")
    
    # Log launch information
    print(f"[SimpleBrowser] Launching profile: {profile['id']}", file=sys.stderr)
    print(f"[SimpleBrowser] Chrome path: {chrome_path}", file=sys.stderr)
    print(f"[SimpleBrowser] CDP port: {debug_port}", file=sys.stderr)
    print(f"[SimpleBrowser] Arguments ({len(args)}):", file=sys.stderr)
    for i, arg in enumerate(args[:15]):
        print(f"  [{i}] {arg}", file=sys.stderr)
    if len(args) > 15:
        print(f"  ... and {len(args) - 15} more", file=sys.stderr)
    
    # Log proxy information
    proxy_type = profile.get("proxy_type", "none")
    if proxy_type != "none":
        print(f"[SimpleBrowser] Proxy: {proxy_type.upper()} {profile.get('proxy_host')}:{profile.get('proxy_port')}", file=sys.stderr)
        if profile.get("proxy_user"):
            print(f"[SimpleBrowser] Proxy auth: enabled", file=sys.stderr)
    
    try:
        kwargs = {}
        env = os.environ.copy()
        env["TZ"] = profile.get("timezone", "UTC")

        if sys.platform == "win32":
            kwargs["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP
        else:
            kwargs["start_new_session"] = True

        kwargs["env"] = env
        kwargs["stderr"] = subprocess.PIPE
        
        proc = subprocess.Popen(args, **kwargs)
        
        # Wait for Chrome to start
        print(f"[SimpleBrowser] Waiting for Chrome to start...", file=sys.stderr)
        time.sleep(3)
        
        if proc.poll() is not None:
            stderr_output = proc.stderr.read().decode('utf-8', errors='ignore')
            print(f"[SimpleBrowser] Chrome exited immediately with code {proc.returncode}", file=sys.stderr)
            if stderr_output:
                print(f"[SimpleBrowser] Stderr: {stderr_output}", file=sys.stderr)
            return None
        
        print(f"[SimpleBrowser] Chrome launched successfully (PID: {proc.pid})", file=sys.stderr)
        
        # Set window lock via CDP (with error handling)
        width, height = profile.get("resolution", "1920x1080").split("x")
        try:
            set_window_lock_via_cdp(debug_port, int(width), int(height))
            
            # Start continuous window monitoring thread
            monitor_thread = threading.Thread(
                target=continuous_window_lock,
                args=(debug_port, int(width), int(height), proc),
                daemon=True
            )
            monitor_thread.start()
            print(f"[SimpleBrowser] Window lock monitor started", file=sys.stderr)
            
        except Exception as e:
            print(f"[SimpleBrowser] Warning: Failed to set window lock via CDP: {e}", file=sys.stderr)
            print(f"[SimpleBrowser] Window will not be locked, but profile is running", file=sys.stderr)
        
        return proc
        
    except Exception as e:
        print(f"[SimpleBrowser] Launch error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        return None


def continuous_window_lock(debug_port: int, target_width: int, target_height: int, proc: subprocess.Popen):
    """Continuously monitor and lock window size."""
    import urllib.request
    import json
    import time
    
    print(f"[WindowLock] Starting continuous monitor for {target_width}x{target_height}", file=sys.stderr)
    
    # Wait for Chrome to be ready
    time.sleep(2)
    
    ws_url = None
    
    # Get WebSocket URL
    for attempt in range(5):
        try:
            url = f"http://localhost:{debug_port}/json"
            req = urllib.request.Request(url, headers={'User-Agent': 'SimpleBrowser'})
            with urllib.request.urlopen(req, timeout=5) as resp:
                response_text = resp.read().decode('utf-8')
                if response_text.strip().startswith('['):
                    targets = json.loads(response_text)
                    for target in targets:
                        if target.get("type") == "page":
                            ws_url = target.get("webSocketDebuggerUrl")
                            break
                if ws_url:
                    break
        except Exception as e:
            print(f"[WindowLock] Attempt {attempt + 1} failed: {e}", file=sys.stderr)
            time.sleep(1)
    
    if not ws_url:
        print(f"[WindowLock] Failed to get WebSocket URL, monitor not started", file=sys.stderr)
        return
    
    print(f"[WindowLock] WebSocket URL: {ws_url}", file=sys.stderr)
    
    try:
        import websocket
    except ImportError:
        print(f"[WindowLock] websocket-client not installed, monitor not started", file=sys.stderr)
        return
    
    # Continuous monitoring loop
    check_interval = 0.5  # Check every 500ms
    msg_id = 1
    
    while proc.poll() is None:  # While Chrome is running
        try:
            # Connect to WebSocket
            ws = websocket.create_connection(ws_url, timeout=2)
            
            # Get current window bounds
            msg = {
                "id": msg_id,
                "method": "Browser.getWindowForTarget",
                "params": {}
            }
            ws.send(json.dumps(msg))
            response = json.loads(ws.recv())
            
            if "result" in response and "windowId" in response["result"]:
                window_id = response["result"]["windowId"]
                
                # Get current bounds
                msg_id += 1
                msg = {
                    "id": msg_id,
                    "method": "Browser.getWindowBounds",
                    "params": {"windowId": window_id}
                }
                ws.send(json.dumps(msg))
                response = json.loads(ws.recv())
                
                if "result" in response and "bounds" in response["result"]:
                    bounds = response["result"]["bounds"]
                    current_width = bounds.get("width", 0)
                    current_height = bounds.get("height", 0)
                    
                    # Check if window size changed
                    if current_width != target_width or current_height != target_height:
                        print(f"[WindowLock] Window size changed to {current_width}x{current_height}, resetting to {target_width}x{target_height}", file=sys.stderr)
                        
                        # Reset window bounds
                        msg_id += 1
                        msg = {
                            "id": msg_id,
                            "method": "Browser.setWindowBounds",
                            "params": {
                                "windowId": window_id,
                                "bounds": {
                                    "width": target_width,
                                    "height": target_height
                                }
                            }
                        }
                        ws.send(json.dumps(msg))
                        ws.recv()  # Wait for response
            
            ws.close()
            
        except Exception as e:
            # Connection error, Chrome might be closed
            if proc.poll() is not None:
                break
            time.sleep(1)
        
        time.sleep(check_interval)
    
    print(f"[WindowLock] Monitor stopped (Chrome closed)", file=sys.stderr)


def set_window_lock_via_cdp(debug_port: int, width: int, height: int):
    """Set window lock dimensions via Chrome DevTools Protocol."""
    import urllib.request
    import json
    import time
    
    print(f"[CDP] Setting window lock to {width}x{height} on port {debug_port}", file=sys.stderr)
    
    # Retry logic for CDP connection
    max_retries = 5
    retry_delay = 1
    
    for attempt in range(max_retries):
        try:
            # Wait for CDP to be ready
            time.sleep(retry_delay)
            
            # Get the first page target
            url = f"http://localhost:{debug_port}/json"
            print(f"[CDP] Attempt {attempt + 1}/{max_retries}: Fetching {url}", file=sys.stderr)
            
            req = urllib.request.Request(url, headers={'User-Agent': 'SimpleBrowser'})
            with urllib.request.urlopen(req, timeout=5) as resp:
                response_text = resp.read().decode('utf-8')
                
                # Check if response is JSON
                if not response_text.strip().startswith('['):
                    print(f"[CDP] Warning: Response is not JSON (got HTML or error page)", file=sys.stderr)
                    print(f"[CDP] Response preview: {response_text[:100]}", file=sys.stderr)
                    raise ValueError("Response is not JSON")
                
                targets = json.loads(response_text)
                
                if not targets:
                    print(f"[CDP] Warning: No targets found", file=sys.stderr)
                    raise ValueError("No targets found")
                
                page_target = None
                for target in targets:
                    if target.get("type") == "page":
                        page_target = target
                        break
                
                if not page_target:
                    print(f"[CDP] Warning: No page target found", file=sys.stderr)
                    raise ValueError("No page target found")
                
                ws_url = page_target.get("webSocketDebuggerUrl")
                print(f"[CDP] Found page target: {ws_url}", file=sys.stderr)
                
                # Try to import websocket
                try:
                    import websocket
                except ImportError:
                    print(f"[CDP] Warning: websocket-client not installed", file=sys.stderr)
                    print(f"[CDP] Install with: pip install websocket-client", file=sys.stderr)
                    print(f"[CDP] Window lock will not work, but profile is running", file=sys.stderr)
                    return
                
                # Connect via WebSocket
                print(f"[CDP] Connecting to WebSocket...", file=sys.stderr)
                ws = websocket.create_connection(ws_url, timeout=5)
                
                # Set chrome.storage.local via Runtime.evaluate
                js_code = f"""
                chrome.storage.local.set({{
                    windowWidth: {width},
                    windowHeight: {height},
                    windowLocked: true
                }}, function() {{
                    console.log('[WindowLock] Storage set: {width}x{height}');
                }});
                """
                
                # Send CDP command
                msg = {
                    "id": 1,
                    "method": "Runtime.evaluate",
                    "params": {
                        "expression": js_code,
                        "returnByValue": True
                    }
                }
                
                ws.send(json.dumps(msg))
                response = ws.recv()
                print(f"[CDP] Window lock set successfully: {width}x{height}", file=sys.stderr)
                
                ws.close()
                return  # Success, exit function
                
        except urllib.error.URLError as e:
            print(f"[CDP] Connection error (attempt {attempt + 1}): {e}", file=sys.stderr)
            if attempt < max_retries - 1:
                print(f"[CDP] Retrying in {retry_delay} seconds...", file=sys.stderr)
                continue
            else:
                print(f"[CDP] Failed after {max_retries} attempts", file=sys.stderr)
                raise
                
        except Exception as e:
            print(f"[CDP] Error (attempt {attempt + 1}): {e}", file=sys.stderr)
            if attempt < max_retries - 1:
                print(f"[CDP] Retrying in {retry_delay} seconds...", file=sys.stderr)
                retry_delay *= 1.5  # Exponential backoff
                continue
            else:
                print(f"[CDP] Failed after {max_retries} attempts", file=sys.stderr)
                raise
    
    print(f"[CDP] Window lock setup failed, but profile is running", file=sys.stderr)
