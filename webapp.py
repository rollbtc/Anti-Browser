#!/usr/bin/env python3
"""
SimpleBrowser 3.0 — Web-Based Anti-Detect Browser Manager
Modern professional UI with Flask + HTML/CSS/JS
"""

import json
import os
import shutil
import subprocess
import sys
import threading
import time
import uuid
from datetime import datetime
from pathlib import Path

from flask import Flask, render_template, request, jsonify, send_from_directory

# Import core backend
sys.path.insert(0, str(Path(__file__).resolve().parent))
import core

app = Flask(__name__)

APP_DIR = Path(__file__).resolve().parent
DATA_DIR = APP_DIR / "profile_data"
PROFILES_DB = APP_DIR / "profiles.json"

DATA_DIR.mkdir(exist_ok=True)

# Global state
running_procs: dict[str, subprocess.Popen] = {}
chrome_path: str | None = core.find_existing_chromium()

# ═══════════════════════════════════════════════════════════════════════════════
# ROUTES
# ═══════════════════════════════════════════════════════════════════════════════

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/profiles", methods=["GET"])
def get_profiles():
    profiles = core.load_profiles()
    # Add running status
    for p in profiles:
        proc = running_procs.get(p["id"])
        p["running"] = proc is not None and proc.poll() is None
    return jsonify(profiles)

@app.route("/api/profiles", methods=["POST"])
def create_profile():
    data = request.json
    profile = core.new_profile(**data)
    profiles = core.load_profiles()
    profiles.append(profile)
    core.save_profiles(profiles)
    return jsonify(profile)

@app.route("/api/profiles/<profile_id>", methods=["PUT"])
def update_profile(profile_id):
    data = request.json
    profiles = core.load_profiles()
    for i, p in enumerate(profiles):
        if p["id"] == profile_id:
            profiles[i].update(data)
            break
    core.save_profiles(profiles)
    return jsonify({"success": True})

@app.route("/api/profiles/<profile_id>", methods=["DELETE"])
def delete_profile(profile_id):
    # Stop if running
    proc = running_procs.get(profile_id)
    if proc and proc.poll() is None:
        proc.terminate()
        running_procs.pop(profile_id, None)

    # Delete data
    data_dir = DATA_DIR / f"p_{profile_id}"
    if data_dir.exists():
        shutil.rmtree(data_dir, ignore_errors=True)

    profiles = core.load_profiles()
    profiles = [p for p in profiles if p["id"] != profile_id]
    core.save_profiles(profiles)
    return jsonify({"success": True})

@app.route("/api/profiles/<profile_id>/launch", methods=["POST"])
def launch_profile(profile_id):
    global chrome_path
    
    profiles = core.load_profiles()
    profile = next((p for p in profiles if p["id"] == profile_id), None)
    if not profile:
        return jsonify({"error": "Profile not found"}), 404

    # Check if already running
    proc = running_procs.get(profile_id)
    if proc and proc.poll() is None:
        return jsonify({"error": "Profile already running"}), 400

    # Check Chromium
    if not chrome_path:
        return jsonify({"error": "Chromium not available"}), 400

    # Build Chrome arguments for debugging
    chrome_args = core.build_chrome_args(profile, chrome_path)
    
    # Log proxy information
    proxy_info = {
        "type": profile.get("proxy_type", "none"),
        "host": profile.get("proxy_host", ""),
        "port": profile.get("proxy_port", ""),
        "has_auth": bool(profile.get("proxy_user") and profile.get("proxy_pass"))
    }

    # Launch
    proc = core.launch_profile(profile, chrome_path)
    if proc:
        running_procs[profile_id] = proc
        profile["last_used"] = datetime.utcnow().isoformat()
        core.save_profiles(profiles)
        return jsonify({
            "success": True,
            "debug": {
                "chrome_args": chrome_args,
                "proxy_info": proxy_info,
                "pid": proc.pid
            }
        })
    else:
        return jsonify({"error": "Failed to launch"}), 500

@app.route("/api/profiles/<profile_id>/stop", methods=["POST"])
def stop_profile(profile_id):
    proc = running_procs.get(profile_id)
    if proc and proc.poll() is None:
        proc.terminate()
        try:
            proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
            proc.kill()
        running_procs.pop(profile_id, None)
        return jsonify({"success": True})
    return jsonify({"error": "Profile not running"}), 400

@app.route("/api/validate-proxy", methods=["POST"])
def validate_proxy():
    data = request.json
    result = core.validate_proxy(
        data.get("proxy_type", "http"),
        data.get("host", ""),
        data.get("port", ""),
        data.get("username", ""),
        data.get("password", "")
    )
    return jsonify(result)

@app.route("/api/auto-match", methods=["POST"])
def auto_match():
    data = request.json
    result = core.validate_proxy(
        data.get("proxy_type", "http"),
        data.get("host", ""),
        data.get("port", ""),
        data.get("username", ""),
        data.get("password", "")
    )
    if result["success"]:
        matched = core.auto_match_fingerprint(result)
        return jsonify({
            "success": True,
            "proxy_info": result,
            "fingerprint": matched
        })
    return jsonify({"success": False, "error": result["error"]})

@app.route("/api/chromium/status", methods=["GET"])
def chromium_status():
    global chrome_path
    chrome_path = core.find_existing_chromium()
    return jsonify({
        "available": chrome_path is not None,
        "path": chrome_path
    })

@app.route("/api/chromium/download", methods=["POST"])
def download_chromium():
    global chrome_path
    
    def download_thread():
        global chrome_path
        chrome_path = core.download_chromium()
    
    thread = threading.Thread(target=download_thread)
    thread.start()
    return jsonify({"success": True, "message": "Download started"})

@app.route("/api/countries", methods=["GET"])
def get_countries():
    return jsonify(core.COUNTRIES)

@app.route("/api/export-cookies/<profile_id>", methods=["POST"])
def export_cookies(profile_id):
    data = request.json
    output_path = data.get("path")
    format_type = data.get("format", "json")  # json or text
    
    if not output_path:
        return jsonify({"error": "No path provided"}), 400
    
    if format_type == "text":
        # Export as Netscape format
        success = core.export_cookies_text(profile_id, output_path)
    else:
        success = core.export_cookies(profile_id, output_path)
    
    return jsonify({"success": success})

@app.route("/api/import-cookies/<profile_id>", methods=["POST"])
def import_cookies(profile_id):
    data = request.json
    input_path = data.get("path")
    format_type = data.get("format", "json")  # json or text
    
    if not input_path:
        return jsonify({"error": "No path provided"}), 400
    
    if format_type == "text":
        success = core.import_cookies_text(profile_id, input_path)
    else:
        success = core.import_cookies(profile_id, input_path)
    
    return jsonify({"success": success})

@app.route("/api/export-profile/<profile_id>", methods=["GET"])
def export_profile(profile_id):
    profiles = core.load_profiles()
    profile = next((p for p in profiles if p["id"] == profile_id), None)
    if not profile:
        return jsonify({"error": "Profile not found"}), 404
    
    return jsonify(profile)

@app.route("/api/import-profile", methods=["POST"])
def import_profile():
    data = request.json
    profiles = core.load_profiles()
    
    # Generate new ID to avoid conflicts
    import uuid
    data["id"] = str(uuid.uuid4())[:8]
    data["created_at"] = datetime.utcnow().isoformat()
    
    profiles.append(data)
    core.save_profiles(profiles)
    
    return jsonify({"success": True, "profile": data})

@app.route("/api/extensions", methods=["GET"])
def list_extensions():
    return jsonify(core.list_installed_extensions())

@app.route("/api/extensions/import", methods=["POST"])
def import_extension():
    """Import an extension from CRX file or unpacked folder."""
    import tempfile
    
    # Check if file was uploaded (CRX file)
    if 'file' in request.files:
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        # Save uploaded file to temp location
        with tempfile.NamedTemporaryFile(delete=False, suffix='.crx') as tmp:
            file.save(tmp.name)
            ext_path = tmp.name
            ext_type = "crx"
    else:
        # Folder import via JSON
        data = request.json
        ext_path = data.get("path")
        ext_type = data.get("type", "auto")
        
        if not ext_path:
            return jsonify({"error": "No path provided"}), 400
        
        if not os.path.exists(ext_path):
            return jsonify({"error": "Path does not exist"}), 400
        
        # Auto-detect type
        if ext_type == "auto":
            if os.path.isfile(ext_path) and ext_path.endswith(".crx"):
                ext_type = "crx"
            elif os.path.isdir(ext_path):
                ext_type = "folder"
            else:
                return jsonify({"error": "Cannot determine extension type. Use .crx file or folder."}), 400
    
    # Import based on type
    result = None
    try:
        if ext_type == "crx":
            result = core.install_extension_from_crx(ext_path)
        elif ext_type == "folder":
            result = core.install_extension_from_folder(ext_path)
        else:
            return jsonify({"error": f"Unknown extension type: {ext_type}"}), 400
        
        if result:
            return jsonify({"success": True, "extension": result})
        else:
            return jsonify({"success": False, "error": "Failed to import extension"}), 500
    finally:
        # Clean up temp file if it was uploaded
        if 'file' in request.files and os.path.exists(ext_path):
            try:
                os.unlink(ext_path)
            except:
                pass

if __name__ == "__main__":
    print("\n" + "="*60)
    print("  SimpleBrowser 3.0 — Anti-Detect Browser Manager")
    print("="*60)
    print("\n  Starting web server...")
    print("  Open your browser to: http://localhost:5000")
    print("\n" + "="*60 + "\n")
    
    app.run(host="0.0.0.0", port=5000, debug=False)
