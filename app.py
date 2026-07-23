#!/usr/bin/env python3
"""
SimpleBrowser 2.0 — Advanced Multi-Profile Anti-Detect Browser
Inspired by AdsPower and Dolphin Anty
"""

import json
import os
import shutil
import subprocess
import sys
import threading
import time
import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
import uuid

# Import core backend
sys.path.insert(0, str(Path(__file__).resolve().parent))
import core

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

APP_DIR = Path(__file__).resolve().parent
DATA_DIR = APP_DIR / "profile_data"
PROFILES_DB = APP_DIR / "profiles.json"

DATA_DIR.mkdir(exist_ok=True)

# ═══════════════════════════════════════════════════════════════════════════════
# COLOR PALETTE (Modern Dark Theme)
# ═══════════════════════════════════════════════════════════════════════════════

BG          = "#0f1419"
BG_SIDEBAR  = "#1a1f2e"
BG_CARD     = "#1e2530"
BG_INPUT    = "#252d3a"
BG_HOVER    = "#2d3544"
FG          = "#e6edf3"
FG_DIM      = "#8b949e"
FG_MUTED    = "#6e7681"
ACCENT      = "#58a6ff"
ACCENT2     = "#a371f7"
SUCCESS     = "#3fb950"
WARNING     = "#d29922"
DANGER      = "#f85149"
BORDER      = "#30363d"

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN APPLICATION
# ═══════════════════════════════════════════════════════════════════════════════

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("SimpleBrowser 2.0 — Anti-Detect Browser Manager")
        self.configure(bg=BG)
        self.geometry("1280x800")
        self.minsize(1100, 700)

        self.profiles: list[dict] = core.load_profiles()
        self.chrome_path: str | None = core.find_existing_chromium()
        self.running_procs: dict[str, subprocess.Popen] = {}

        self._apply_style()
        self._build_layout()
        self._render_profile_list()

        # Check Chromium on first run
        if not self.chrome_path:
            self.after(500, self._check_chromium)

        self.after(2000, self._poll_running)

    def _check_chromium(self):
        """Check if Chromium is available, offer to download if not."""
        if not self.chrome_path:
            if messagebox.askyesno(
                "Chromium Not Found",
                "No Chrome/Chromium detected.\n\n"
                "Would you like to download Chrome for Testing automatically?\n"
                "(~150MB download)"
            ):
                self._download_chromium()

    def _download_chromium(self):
        """Download Chromium with progress dialog."""
        dialog = tk.Toplevel(self)
        dialog.title("Downloading Chromium")
        dialog.configure(bg=BG)
        dialog.geometry("500x200")
        dialog.transient(self)
        dialog.grab_set()

        ttk.Label(dialog, text="Downloading Chrome for Testing...",
                  style="Title.TLabel").pack(pady=(30, 10))

        status_var = tk.StringVar(value="Preparing...")
        ttk.Label(dialog, textvariable=status_var,
                  style="Subtitle.TLabel").pack(pady=5)

        progress = ttk.Progressbar(dialog, length=400, mode="determinate")
        progress.pack(pady=20)

        def update_progress(downloaded, total):
            if total > 0:
                pct = int((downloaded / total) * 100)
                progress["value"] = pct
                mb = downloaded / (1024 * 1024)
                total_mb = total / (1024 * 1024)
                status_var.set(f"{mb:.1f} MB / {total_mb:.1f} MB ({pct}%)")

        def update_status(msg):
            status_var.set(msg)

        def download_thread():
            result = core.download_chromium(
                progress_cb=update_progress,
                status_cb=update_status
            )
            self.chrome_path = result
            dialog.after(100, dialog.destroy)
            if result:
                messagebox.showinfo("Success", "Chromium downloaded successfully!")
            else:
                messagebox.showerror("Error", "Failed to download Chromium.")

        threading.Thread(target=download_thread, daemon=True).start()

    # ═════════════════════════════════════════════════════════════════════════
    # STYLING
    # ═════════════════════════════════════════════════════════════════════════

    def _apply_style(self):
        style = ttk.Style(self)
        style.theme_use("clam")

        # Base
        style.configure(".", background=BG, foreground=FG, fieldbackground=BG_INPUT,
                        borderwidth=0, focuscolor=BG)
        style.configure("TFrame", background=BG)
        style.configure("Sidebar.TFrame", background=BG_SIDEBAR)
        style.configure("Card.TFrame", background=BG_CARD)

        # Labels
        style.configure("TLabel", background=BG, foreground=FG, font=("Segoe UI", 10))
        style.configure("Sidebar.TLabel", background=BG_SIDEBAR, foreground=FG)
        style.configure("Title.TLabel", background=BG, foreground=FG,
                        font=("Segoe UI", 20, "bold"))
        style.configure("Subtitle.TLabel", background=BG, foreground=FG_DIM,
                        font=("Segoe UI", 10))
        style.configure("CardTitle.TLabel", background=BG_CARD, foreground=FG,
                        font=("Segoe UI", 11, "bold"))
        style.configure("CardInfo.TLabel", background=BG_CARD, foreground=FG_DIM,
                        font=("Segoe UI", 9))

        # Buttons
        style.configure("Accent.TButton", background=ACCENT, foreground=BG,
                        font=("Segoe UI", 10, "bold"), padding=(16, 10))
        style.map("Accent.TButton",
                  background=[("active", ACCENT2), ("disabled", FG_MUTED)])

        style.configure("Success.TButton", background=SUCCESS, foreground=BG,
                        font=("Segoe UI", 10, "bold"), padding=(16, 10))
        style.map("Success.TButton", background=[("active", "#2ea043")])

        style.configure("Danger.TButton", background=DANGER, foreground=BG,
                        font=("Segoe UI", 10, "bold"), padding=(16, 10))
        style.map("Danger.TButton", background=[("active", "#da3633")])

        style.configure("Ghost.TButton", background=BG_CARD, foreground=FG,
                        font=("Segoe UI", 10), padding=(12, 8))
        style.map("Ghost.TButton", background=[("active", BG_HOVER)])

        style.configure("Sidebar.TButton", background=BG_SIDEBAR, foreground=FG,
                        font=("Segoe UI", 10), padding=(12, 10), anchor="w")
        style.map("Sidebar.TButton", background=[("active", BG_HOVER)])

        # Inputs
        style.configure("TEntry", fieldbackground=BG_INPUT, foreground=FG,
                        insertcolor=FG, padding=8)
        style.configure("TCombobox", fieldbackground=BG_INPUT, foreground=FG,
                        padding=8)

        # Treeview
        style.configure("Treeview", background=BG_CARD, foreground=FG,
                        fieldbackground=BG_CARD, rowheight=36,
                        font=("Segoe UI", 10))
        style.configure("Treeview.Heading", background=BG_INPUT, foreground=ACCENT,
                        font=("Segoe UI", 9, "bold"))
        style.map("Treeview", background=[("selected", ACCENT)],
                  foreground=[("selected", BG)])

        # Notebook (tabs)
        style.configure("TNotebook", background=BG, borderwidth=0)
        style.configure("TNotebook.Tab", background=BG_INPUT, foreground=FG_DIM,
                        padding=(16, 8), font=("Segoe UI", 10))
        style.map("TNotebook.Tab",
                  background=[("selected", BG_CARD)],
                  foreground=[("selected", FG)])

        # Labelframe
        style.configure("TLabelframe", background=BG_CARD, foreground=FG,
                        borderwidth=1, relief="solid")
        style.configure("TLabelframe.Label", background=BG_CARD, foreground=ACCENT,
                        font=("Segoe UI", 10, "bold"))

    # ═════════════════════════════════════════════════════════════════════════
    # LAYOUT
    # ═════════════════════════════════════════════════════════════════════════

    def _build_layout(self):
        # Sidebar
        sidebar = ttk.Frame(self, style="Sidebar.TFrame", width=240)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        # Logo
        logo_frame = ttk.Frame(sidebar, style="Sidebar.TFrame")
        logo_frame.pack(fill="x", pady=(24, 20))
        ttk.Label(logo_frame, text="🌐", font=("Segoe UI", 32),
                  background=BG_SIDEBAR).pack()
        ttk.Label(logo_frame, text="SimpleBrowser", style="Sidebar.TLabel",
                  font=("Segoe UI", 16, "bold")).pack(pady=(8, 0))
        ttk.Label(logo_frame, text="v2.0", style="Sidebar.TLabel",
                  font=("Segoe UI", 9), foreground=FG_DIM).pack()

        ttk.Separator(sidebar, orient="horizontal").pack(fill="x", padx=12, pady=8)

        # Navigation
        self.btn_profiles = ttk.Button(sidebar, text="  📋  Profiles", style="Sidebar.TButton",
                                       command=self._show_profiles)
        self.btn_profiles.pack(fill="x", padx=10, pady=3)

        self.btn_extensions = ttk.Button(sidebar, text="  🧩  Extensions", style="Sidebar.TButton",
                                         command=self._show_extensions)
        self.btn_extensions.pack(fill="x", padx=10, pady=3)

        self.btn_settings = ttk.Button(sidebar, text="  ⚙️  Settings", style="Sidebar.TButton",
                                       command=self._show_settings)
        self.btn_settings.pack(fill="x", padx=10, pady=3)

        # Chrome status
        status_frame = ttk.Frame(sidebar, style="Sidebar.TFrame")
        status_frame.pack(side="bottom", fill="x", padx=12, pady=20)

        if self.chrome_path:
            ttk.Label(status_frame, text="● Chromium Ready",
                      background=BG_SIDEBAR, foreground=SUCCESS,
                      font=("Segoe UI", 9, "bold")).pack(anchor="w")
            ttk.Label(status_frame, text=os.path.basename(self.chrome_path),
                      background=BG_SIDEBAR, foreground=FG_DIM,
                      font=("Segoe UI", 8)).pack(anchor="w")
        else:
            ttk.Label(status_frame, text="● Chromium Missing",
                      background=BG_SIDEBAR, foreground=DANGER,
                      font=("Segoe UI", 9, "bold")).pack(anchor="w")
            ttk.Button(status_frame, text="Download Now", style="Ghost.TButton",
                       command=self._download_chromium).pack(anchor="w", pady=(4, 0))

        # Main content
        self.main = ttk.Frame(self)
        self.main.pack(side="right", fill="both", expand=True, padx=24, pady=20)

        self._show_profiles()

    # ═════════════════════════════════════════════════════════════════════════
    # PROFILES VIEW
    # ═════════════════════════════════════════════════════════════════════════

    def _show_profiles(self):
        self._clear_main()

        # Header
        header = ttk.Frame(self.main)
        header.pack(fill="x", pady=(0, 16))

        ttk.Label(header, text="Browser Profiles", style="Title.TLabel").pack(side="left")

        running_count = sum(1 for p in self.profiles
                           if self.running_procs.get(p["id"]) and
                           self.running_procs[p["id"]].poll() is None)
        ttk.Label(header, text=f"{len(self.profiles)} profiles · {running_count} running",
                  style="Subtitle.TLabel").pack(side="left", padx=20)

        ttk.Button(header, text="➕  New Profile", style="Accent.TButton",
                   command=self._new_profile).pack(side="right")

        # Profile list
        cols = ("name", "proxy", "resolution", "platform", "status", "last_used")
        self.tree = ttk.Treeview(self.main, columns=cols, show="headings", selectmode="browse")

        widths = {"name": 220, "proxy": 200, "resolution": 120,
                  "platform": 140, "status": 100, "last_used": 160}
        titles = {"name": "Profile Name", "proxy": "Proxy", "resolution": "Resolution",
                  "platform": "Platform", "status": "Status", "last_used": "Last Used"}

        for c in cols:
            self.tree.heading(c, text=titles[c])
            self.tree.column(c, width=widths[c], anchor="w")

        scrollbar = ttk.Scrollbar(self.main, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.tree.bind("<Double-1>", lambda e: self._open_selected())

        # Action bar
        actions = ttk.Frame(self.main)
        actions.pack(fill="x", pady=(12, 0))

        ttk.Button(actions, text="▶  Open", style="Success.TButton",
                   command=self._open_selected).pack(side="left", padx=(0, 6))
        ttk.Button(actions, text="✎  Edit", style="Ghost.TButton",
                   command=self._edit_selected).pack(side="left", padx=3)
        ttk.Button(actions, text="⧉  Duplicate", style="Ghost.TButton",
                   command=self._duplicate_selected).pack(side="left", padx=3)
        ttk.Button(actions, text="■  Stop", style="Ghost.TButton",
                   command=self._stop_selected).pack(side="left", padx=3)
        ttk.Button(actions, text="🗑  Delete", style="Danger.TButton",
                   command=self._delete_selected).pack(side="right")

        self._render_profile_list()

    def _render_profile_list(self):
        if not hasattr(self, "tree"):
            return
        self.tree.delete(*self.tree.get_children())

        for p in self.profiles:
            proc = self.running_procs.get(p["id"])
            alive = proc is not None and proc.poll() is None

            status = "● Running" if alive else "○ Stopped"
            proxy = "None"
            if p.get("proxy_type") in ("http", "socks5") and p.get("proxy_host"):
                proxy = f"{p['proxy_type'].upper()} {p['proxy_host']}:{p.get('proxy_port','')}"

            ua = p.get("user_agent", "")
            if "Windows" in ua: plat = "Windows"
            elif "Macintosh" in ua: plat = "macOS"
            elif "Linux" in ua: plat = "Linux"
            else: plat = "—"

            last = (p.get("last_used") or "—")[:16].replace("T", " ")

            name_display = f"{p['name']}"
            self.tree.insert("", "end", iid=p["id"], values=(
                name_display, proxy, p.get("resolution", "—"), plat, status, last
            ))

    def _clear_main(self):
        for w in self.main.winfo_children():
            w.destroy()

    # ═════════════════════════════════════════════════════════════════════════
    # PROFILE CRUD
    # ═════════════════════════════════════════════════════════════════════════

    def _new_profile(self):
        self._open_profile_editor(None)

    def _edit_selected(self):
        sel = self.tree.selection()
        if not sel: return
        pid = sel[0]
        profile = next((p for p in self.profiles if p["id"] == pid), None)
        if profile:
            self._open_profile_editor(profile)

    def _duplicate_selected(self):
        sel = self.tree.selection()
        if not sel: return
        pid = sel[0]
        original = next((p for p in self.profiles if p["id"] == pid), None)
        if not original: return

        dup = original.copy()
        dup["id"] = str(uuid.uuid4())[:8]
        dup["name"] = original["name"] + " (copy)"
        dup["created_at"] = datetime.utcnow().isoformat()
        dup["last_used"] = None

        src = DATA_DIR / f"p_{original['id']}"
        dst = DATA_DIR / f"p_{dup['id']}"
        if src.exists():
            shutil.copytree(src, dst, ignore_dangling_symlinks=True)

        self.profiles.append(dup)
        core.save_profiles(self.profiles)
        self._render_profile_list()

    def _delete_selected(self):
        sel = self.tree.selection()
        if not sel: return
        pid = sel[0]
        profile = next((p for p in self.profiles if p["id"] == pid), None)
        if not profile: return

        proc = self.running_procs.get(pid)
        if proc and proc.poll() is None:
            proc.terminate()
            self.running_procs.pop(pid, None)

        if not messagebox.askyesno("Delete Profile",
                                   f"Delete '{profile['name']}' and all its data?"):
            return

        data_dir = DATA_DIR / f"p_{pid}"
        if data_dir.exists():
            shutil.rmtree(data_dir, ignore_errors=True)

        self.profiles = [p for p in self.profiles if p["id"] != pid]
        core.save_profiles(self.profiles)
        self._render_profile_list()

    def _open_selected(self):
        sel = self.tree.selection()
        if not sel: return
        pid = sel[0]
        profile = next((p for p in self.profiles if p["id"] == pid), None)
        if not profile: return

        proc = self.running_procs.get(pid)
        if proc and proc.poll() is None:
            messagebox.showinfo("Profile", f"'{profile['name']}' is already running.")
            return

        if not self.chrome_path:
            messagebox.showerror("Error", "Chromium not available. Download it from Settings.")
            return

        proc = core.launch_profile(profile, self.chrome_path)
        if proc:
            self.running_procs[pid] = proc
            profile["last_used"] = datetime.utcnow().isoformat()
            core.save_profiles(self.profiles)
            self._render_profile_list()

    def _stop_selected(self):
        sel = self.tree.selection()
        if not sel: return
        pid = sel[0]
        proc = self.running_procs.get(pid)
        if proc and proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                proc.kill()
            self.running_procs.pop(pid, None)
            self._render_profile_list()

    def _poll_running(self):
        changed = False
        for pid, proc in list(self.running_procs.items()):
            if proc.poll() is not None:
                self.running_procs.pop(pid, None)
                changed = True
        if changed and hasattr(self, "tree"):
            self._render_profile_list()
        self.after(2000, self._poll_running)

    # ═════════════════════════════════════════════════════════════════════════
    # PROFILE EDITOR
    # ═════════════════════════════════════════════════════════════════════════

    def _open_profile_editor(self, profile: dict | None):
        is_new = profile is None
        p = profile.copy() if profile else core.new_profile()

        win = tk.Toplevel(self)
        win.title("New Profile" if is_new else f"Edit: {p['name']}")
        win.configure(bg=BG)
        win.geometry("900x750")
        win.transient(self)
        win.grab_set()

        # Scrollable frame
        canvas = tk.Canvas(win, bg=BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(win, orient="vertical", command=canvas.yview)
        scroll_frame = ttk.Frame(canvas)

        scroll_frame.bind("<Configure>",
                         lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True, padx=20, pady=10)
        scrollbar.pack(side="right", fill="y")

        # Bind mouse wheel
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        # Notebook (tabs)
        notebook = ttk.Notebook(scroll_frame)
        notebook.pack(fill="both", expand=True, pady=(0, 16))

        # ── Tab 1: General ──
        tab_general = ttk.Frame(notebook, padding=16)
        notebook.add(tab_general, text="General")

        ttk.Label(tab_general, text="Profile Information", style="Title.TLabel").pack(anchor="w", pady=(0, 12))

        frm = ttk.LabelFrame(tab_general, text="Basic Info", padding=12)
        frm.pack(fill="x", pady=(0, 12))

        v_name = tk.StringVar(value=p["name"])
        ttk.Label(frm, text="Profile Name:").grid(row=0, column=0, sticky="w", padx=8, pady=6)
        ttk.Entry(frm, textvariable=v_name, width=50).grid(row=0, column=1, sticky="ew", padx=8, pady=6)

        v_id = tk.StringVar(value=p["id"])
        ttk.Label(frm, text="Profile ID:").grid(row=1, column=0, sticky="w", padx=8, pady=6)
        ttk.Label(frm, textvariable=v_id, foreground=FG_DIM).grid(row=1, column=1, sticky="w", padx=8, pady=6)

        frm.columnconfigure(1, weight=1)

        v_notes = tk.StringVar(value=p.get("notes", ""))
        frm2 = ttk.LabelFrame(tab_general, text="Notes", padding=12)
        frm2.pack(fill="x")
        ttk.Entry(frm2, textvariable=v_notes, width=80).pack(fill="x")

        # ── Tab 2: Proxy ──
        tab_proxy = ttk.Frame(notebook, padding=16)
        notebook.add(tab_proxy, text="Proxy")

        ttk.Label(tab_proxy, text="Proxy Configuration", style="Title.TLabel").pack(anchor="w", pady=(0, 12))

        frm_proxy = ttk.LabelFrame(tab_proxy, text="Proxy Settings", padding=12)
        frm_proxy.pack(fill="x", pady=(0, 12))

        v_ptype = tk.StringVar(value=p["proxy_type"])
        ttk.Label(frm_proxy, text="Proxy Type:").grid(row=0, column=0, sticky="w", padx=8, pady=6)
        ttk.Combobox(frm_proxy, textvariable=v_ptype, state="readonly",
                     values=["none", "http", "socks5"], width=16).grid(row=0, column=1, sticky="w", padx=8, pady=6)

        v_phost = tk.StringVar(value=p["proxy_host"])
        v_pport = tk.StringVar(value=p["proxy_port"])
        v_puser = tk.StringVar(value=p["proxy_user"])
        v_ppass = tk.StringVar(value=p["proxy_pass"])

        ttk.Label(frm_proxy, text="Host:").grid(row=1, column=0, sticky="w", padx=8, pady=6)
        ttk.Entry(frm_proxy, textvariable=v_phost, width=40).grid(row=1, column=1, sticky="ew", padx=8, pady=6)

        ttk.Label(frm_proxy, text="Port:").grid(row=2, column=0, sticky="w", padx=8, pady=6)
        ttk.Entry(frm_proxy, textvariable=v_pport, width=12).grid(row=2, column=1, sticky="w", padx=8, pady=6)

        ttk.Label(frm_proxy, text="Username:").grid(row=3, column=0, sticky="w", padx=8, pady=6)
        ttk.Entry(frm_proxy, textvariable=v_puser, width=40).grid(row=3, column=1, sticky="ew", padx=8, pady=6)

        ttk.Label(frm_proxy, text="Password:").grid(row=4, column=0, sticky="w", padx=8, pady=6)
        ttk.Entry(frm_proxy, textvariable=v_ppass, width=40, show="•").grid(row=4, column=1, sticky="ew", padx=8, pady=6)

        frm_proxy.columnconfigure(1, weight=1)

        # Validate button
        btn_frame = ttk.Frame(tab_proxy)
        btn_frame.pack(fill="x", pady=8)

        def validate_proxy():
            result = core.validate_proxy(
                v_ptype.get(), v_phost.get(), v_pport.get(),
                v_puser.get(), v_ppass.get()
            )
            if result["success"]:
                info = (f"✓ Proxy Valid\n\n"
                       f"IP: {result['ip']}\n"
                       f"Country: {result['country']}\n"
                       f"Region: {result['region']}\n"
                       f"City: {result['city']}\n"
                       f"Timezone: {result['timezone']}\n"
                       f"ISP: {result['isp']}\n"
                       f"Latency: {result['latency_ms']}ms")
                messagebox.showinfo("Proxy Validation", info)
            else:
                messagebox.showerror("Proxy Validation", f"✗ Proxy Failed\n\n{result['error']}")

        ttk.Button(btn_frame, text="✓  Validate Proxy", style="Success.TButton",
                   command=validate_proxy).pack(side="left", padx=(0, 8))

        def auto_match():
            result = core.validate_proxy(
                v_ptype.get(), v_phost.get(), v_pport.get(),
                v_puser.get(), v_ppass.get()
            )
            if result["success"]:
                matched = core.auto_match_fingerprint(result)
                v_ua.set(matched["user_agent"])
                v_tz.set(matched["timezone"])
                v_lang.set(matched["language"])
                messagebox.showinfo("Auto-Match", f"✓ Matched to {matched['country']}\n\n"
                                                  f"Timezone: {matched['timezone']}\n"
                                                  f"Language: {matched['language']}")
            else:
                messagebox.showerror("Auto-Match", f"Cannot match - proxy validation failed:\n{result['error']}")

        ttk.Button(btn_frame, text="🎯  Auto-Match Fingerprint", style="Accent.TButton",
                   command=auto_match).pack(side="left")

        # ── Tab 3: Fingerprint ──
        tab_fp = ttk.Frame(notebook, padding=16)
        notebook.add(tab_fp, text="Fingerprint")

        ttk.Label(tab_fp, text="Browser Fingerprint", style="Title.TLabel").pack(anchor="w", pady=(0, 12))

        frm_fp = ttk.LabelFrame(tab_fp, text="User Agent & Platform", padding=12)
        frm_fp.pack(fill="x", pady=(0, 12))

        v_ua = tk.StringVar(value=p["user_agent"])
        ttk.Label(frm_fp, text="User Agent:").grid(row=0, column=0, sticky="w", padx=8, pady=6)
        ttk.Entry(frm_fp, textvariable=v_ua, width=80).grid(row=0, column=1, columnspan=2, sticky="ew", padx=8, pady=6)

        def randomize_ua():
            import random
            chrome_ver = random.randint(125, 131)
            templates = [
                f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome_ver}.0.0.0 Safari/537.36",
                f"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome_ver}.0.0.0 Safari/537.36",
                f"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome_ver}.0.0.0 Safari/537.36",
            ]
            v_ua.set(random.choice(templates))

        ttk.Button(frm_fp, text="🎲 Randomize", style="Ghost.TButton",
                   command=randomize_ua).grid(row=1, column=1, sticky="w", padx=8, pady=4)

        frm_fp.columnconfigure(1, weight=1)

        frm_fp2 = ttk.LabelFrame(tab_fp, text="Screen & Locale", padding=12)
        frm_fp2.pack(fill="x", pady=(0, 12))

        v_res = tk.StringVar(value=p["resolution"])
        ttk.Label(frm_fp2, text="Resolution:").grid(row=0, column=0, sticky="w", padx=8, pady=6)
        ttk.Combobox(frm_fp2, textvariable=v_res, width=16,
                     values=["1920x1080", "1366x768", "1536x864", "1440x900",
                             "2560x1440", "1280x720", "3840x2160"]).grid(row=0, column=1, sticky="w", padx=8, pady=6)

        v_tz = tk.StringVar(value=p["timezone"])
        ttk.Label(frm_fp2, text="Timezone:").grid(row=1, column=0, sticky="w", padx=8, pady=6)
        tz_values = [c["tz"] for c in core.COUNTRIES]
        ttk.Combobox(frm_fp2, textvariable=v_tz, width=28, values=tz_values).grid(row=1, column=1, sticky="w", padx=8, pady=6)

        v_lang = tk.StringVar(value=p["language"])
        ttk.Label(frm_fp2, text="Language:").grid(row=2, column=0, sticky="w", padx=8, pady=6)
        lang_values = [c["lang"] for c in core.COUNTRIES]
        ttk.Combobox(frm_fp2, textvariable=v_lang, width=16, values=lang_values).grid(row=2, column=1, sticky="w", padx=8, pady=6)

        v_webrtc = tk.StringVar(value=p.get("webrtc", "disabled"))
        ttk.Label(frm_fp2, text="WebRTC:").grid(row=3, column=0, sticky="w", padx=8, pady=6)
        ttk.Combobox(frm_fp2, textvariable=v_webrtc, state="readonly", width=16,
                     values=["disabled", "enabled"]).grid(row=3, column=1, sticky="w", padx=8, pady=6)

        frm_fp2.columnconfigure(1, weight=1)

        # ── Tab 4: Advanced Spoofing ──
        tab_adv = ttk.Frame(notebook, padding=16)
        notebook.add(tab_adv, text="Advanced Spoofing")

        ttk.Label(tab_adv, text="Anti-Detection Settings", style="Title.TLabel").pack(anchor="w", pady=(0, 12))

        # Canvas
        frm_canvas = ttk.LabelFrame(tab_adv, text="Canvas Fingerprint", padding=12)
        frm_canvas.pack(fill="x", pady=(0, 10))

        v_canvas = tk.StringVar(value=p.get("canvas_spoof", "noise"))
        ttk.Radiobutton(frm_canvas, text="Add Noise (Recommended)", variable=v_canvas, value="noise").pack(anchor="w", pady=2)
        ttk.Radiobutton(frm_canvas, text="Disabled", variable=v_canvas, value="off").pack(anchor="w", pady=2)

        # WebGL
        frm_webgl = ttk.LabelFrame(tab_adv, text="WebGL Fingerprint", padding=12)
        frm_webgl.pack(fill="x", pady=(0, 10))

        v_webgl = tk.StringVar(value=p.get("webgl_spoof", "custom"))
        ttk.Radiobutton(frm_webgl, text="Custom Vendor/Renderer (Recommended)", variable=v_webgl, value="custom").pack(anchor="w", pady=2)
        ttk.Radiobutton(frm_webgl, text="Disabled", variable=v_webgl, value="off").pack(anchor="w", pady=2)

        v_wv = tk.StringVar(value=p.get("webgl_vendor", ""))
        v_wr = tk.StringVar(value=p.get("webgl_renderer", ""))
        ttk.Label(frm_webgl, text="Vendor:").grid(row=2, column=0, sticky="w", padx=8, pady=6)
        ttk.Entry(frm_webgl, textvariable=v_wv, width=60).grid(row=2, column=1, sticky="ew", padx=8, pady=6)
        ttk.Label(frm_webgl, text="Renderer:").grid(row=3, column=0, sticky="w", padx=8, pady=6)
        ttk.Entry(frm_webgl, textvariable=v_wr, width=60).grid(row=3, column=1, sticky="ew", padx=8, pady=6)

        frm_webgl.columnconfigure(1, weight=1)

        # Audio
        frm_audio = ttk.LabelFrame(tab_adv, text="Audio Fingerprint", padding=12)
        frm_audio.pack(fill="x", pady=(0, 10))

        v_audio = tk.StringVar(value=p.get("audio_spoof", "noise"))
        ttk.Radiobutton(frm_audio, text="Add Noise (Recommended)", variable=v_audio, value="noise").pack(anchor="w", pady=2)
        ttk.Radiobutton(frm_audio, text="Disabled", variable=v_audio, value="off").pack(anchor="w", pady=2)

        # Client Rects
        frm_rects = ttk.LabelFrame(tab_adv, text="Client Rects Fingerprint", padding=12)
        frm_rects.pack(fill="x", pady=(0, 10))

        v_rects = tk.StringVar(value=p.get("client_rects_spoof", "noise"))
        ttk.Radiobutton(frm_rects, text="Add Noise (Recommended)", variable=v_rects, value="noise").pack(anchor="w", pady=2)
        ttk.Radiobutton(frm_rects, text="Disabled", variable=v_rects, value="off").pack(anchor="w", pady=2)

        # Hardware
        frm_hw = ttk.LabelFrame(tab_adv, text="Hardware Properties", padding=12)
        frm_hw.pack(fill="x", pady=(0, 10))

        v_hc = tk.StringVar(value=str(p.get("hardware_concurrency", 8)))
        v_dm = tk.StringVar(value=str(p.get("device_memory", 8)))

        ttk.Label(frm_hw, text="CPU Cores:").grid(row=0, column=0, sticky="w", padx=8, pady=6)
        ttk.Combobox(frm_hw, textvariable=v_hc, width=12,
                     values=["2", "4", "6", "8", "12", "16", "24", "32"]).grid(row=0, column=1, sticky="w", padx=8, pady=6)

        ttk.Label(frm_hw, text="Memory (GB):").grid(row=1, column=0, sticky="w", padx=8, pady=6)
        ttk.Combobox(frm_hw, textvariable=v_dm, width=12,
                     values=["2", "4", "8", "16", "32", "64"]).grid(row=1, column=1, sticky="w", padx=8, pady=6)

        frm_hw.columnconfigure(1, weight=1)

        # ── Tab 5: Cookies ──
        tab_cookies = ttk.Frame(notebook, padding=16)
        notebook.add(tab_cookies, text="Cookies")

        ttk.Label(tab_cookies, text="Cookie Management", style="Title.TLabel").pack(anchor="w", pady=(0, 12))

        frm_cookies = ttk.LabelFrame(tab_cookies, text="Import / Export", padding=12)
        frm_cookies.pack(fill="x")

        def export_cookies():
            path = filedialog.asksaveasfilename(
                title="Export Cookies",
                defaultextension=".json",
                filetypes=[("JSON files", "*.json")]
            )
            if path:
                if core.export_cookies(p["id"], path):
                    messagebox.showinfo("Export", "Cookies exported successfully!")
                else:
                    messagebox.showerror("Export", "Failed to export cookies. Profile may not have been used yet.")

        def import_cookies():
            path = filedialog.askopenfilename(
                title="Import Cookies",
                filetypes=[("JSON files", "*.json")]
            )
            if path:
                if core.import_cookies(p["id"], path):
                    messagebox.showinfo("Import", "Cookies imported successfully!")
                else:
                    messagebox.showerror("Import", "Failed to import cookies.")

        ttk.Button(frm_cookies, text="📤  Export Cookies", style="Ghost.TButton",
                   command=export_cookies).pack(side="left", padx=(0, 8), pady=8)
        ttk.Button(frm_cookies, text="📥  Import Cookies", style="Ghost.TButton",
                   command=import_cookies).pack(side="left", pady=8)

        # ── Save / Cancel buttons (always visible at bottom) ──
        btn_bar = ttk.Frame(win)
        btn_bar.pack(fill="x", padx=20, pady=(0, 20))

        def save():
            updated = {
                "name": v_name.get().strip() or "Unnamed",
                "proxy_type": v_ptype.get(),
                "proxy_host": v_phost.get().strip(),
                "proxy_port": v_pport.get().strip(),
                "proxy_user": v_puser.get().strip(),
                "proxy_pass": v_ppass.get().strip(),
                "user_agent": v_ua.get().strip(),
                "resolution": v_res.get(),
                "timezone": v_tz.get(),
                "language": v_lang.get(),
                "webrtc": v_webrtc.get(),
                "canvas_spoof": v_canvas.get(),
                "webgl_spoof": v_webgl.get(),
                "webgl_vendor": v_wv.get().strip(),
                "webgl_renderer": v_wr.get().strip(),
                "audio_spoof": v_audio.get(),
                "client_rects_spoof": v_rects.get(),
                "hardware_concurrency": int(v_hc.get()),
                "device_memory": int(v_dm.get()),
                "notes": v_notes.get(),
            }
            if is_new:
                p.update(updated)
                self.profiles.append(p)
            else:
                for i, prof in enumerate(self.profiles):
                    if prof["id"] == p["id"]:
                        self.profiles[i].update(updated)
                        break
            core.save_profiles(self.profiles)
            self._render_profile_list()
            win.destroy()

        ttk.Button(btn_bar, text="💾  Save Profile", style="Success.TButton",
                   command=save).pack(side="right", padx=(8, 0))
        ttk.Button(btn_bar, text="Cancel", style="Ghost.TButton",
                   command=win.destroy).pack(side="right")

    # ═════════════════════════════════════════════════════════════════════════
    # EXTENSIONS VIEW
    # ═════════════════════════════════════════════════════════════════════════

    def _show_extensions(self):
        self._clear_main()

        ttk.Label(self.main, text="Extension Manager", style="Title.TLabel").pack(anchor="w", pady=(0, 16))

        # Built-in extension
        frm_builtin = ttk.LabelFrame(self.main, text="Built-in Extensions", padding=12)
        frm_builtin.pack(fill="x", pady=(0, 12))

        ttk.Label(frm_builtin, text="🛡️  Fingerprint Shield v2.0",
                  font=("Segoe UI", 11, "bold")).pack(anchor="w")
        ttk.Label(frm_builtin, text="Anti-detect fingerprint protection (Canvas, WebGL, Audio, ClientRects)",
                  foreground=FG_DIM).pack(anchor="w", pady=(2, 0))
        ttk.Label(frm_builtin, text="Status: ✓ Active", foreground=SUCCESS,
                  font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(4, 0))

        # User extensions
        frm_user = ttk.LabelFrame(self.main, text="User Extensions", padding=12)
        frm_user.pack(fill="x", pady=(0, 12))

        exts = core.list_installed_extensions()
        if exts:
            for ext in exts:
                ext_item = ttk.Frame(frm_user)
                ext_item.pack(fill="x", pady=6)
                ttk.Label(ext_item, text=f"🧩  {ext['name']} v{ext['version']}",
                          font=("Segoe UI", 10, "bold")).pack(side="left")
                ttk.Button(ext_item, text="Remove", style="Danger.TButton",
                           command=lambda eid=ext["id"]: self._remove_extension(eid)).pack(side="right")
        else:
            ttk.Label(frm_user, text="No user extensions installed",
                      foreground=FG_DIM).pack(anchor="w")

        # Install buttons
        btn_frame = ttk.Frame(self.main)
        btn_frame.pack(fill="x", pady=8)

        def install_crx():
            path = filedialog.askopenfilename(
                title="Install Extension (.crx)",
                filetypes=[("Chrome Extension", "*.crx")]
            )
            if path:
                result = core.install_extension_from_crx(path)
                if result:
                    messagebox.showinfo("Installed", f"Extension '{result['name']}' installed!")
                    self._show_extensions()
                else:
                    messagebox.showerror("Error", "Failed to install extension.")

        def install_folder():
            path = filedialog.askdirectory(title="Select Extension Folder")
            if path:
                result = core.install_extension_from_folder(path)
                if result:
                    messagebox.showinfo("Installed", f"Extension '{result['name']}' installed!")
                    self._show_extensions()
                else:
                    messagebox.showerror("Error", "Failed to install extension.")

        ttk.Button(btn_frame, text="📦  Install from .crx", style="Accent.TButton",
                   command=install_crx).pack(side="left", padx=(0, 8))
        ttk.Button(btn_frame, text="📁  Install from Folder", style="Ghost.TButton",
                   command=install_folder).pack(side="left")

    def _remove_extension(self, ext_id):
        if messagebox.askyesno("Remove Extension", "Remove this extension?"):
            if core.uninstall_extension(ext_id):
                self._show_extensions()

    # ═════════════════════════════════════════════════════════════════════════
    # SETTINGS VIEW
    # ═════════════════════════════════════════════════════════════════════════

    def _show_settings(self):
        self._clear_main()

        ttk.Label(self.main, text="Settings", style="Title.TLabel").pack(anchor="w", pady=(0, 16))

        # Chromium
        frm_chrome = ttk.LabelFrame(self.main, text="Chromium Browser", padding=12)
        frm_chrome.pack(fill="x", pady=(0, 12))

        if self.chrome_path:
            ttk.Label(frm_chrome, text="✓ Chromium detected",
                      foreground=SUCCESS, font=("Segoe UI", 10, "bold")).pack(anchor="w")
            ttk.Label(frm_chrome, text=self.chrome_path,
                      foreground=FG_DIM, font=("Segoe UI", 9)).pack(anchor="w", pady=(4, 0))
        else:
            ttk.Label(frm_chrome, text="✗ Chromium not found",
                      foreground=DANGER, font=("Segoe UI", 10, "bold")).pack(anchor="w")
            ttk.Button(frm_chrome, text="Download Chrome for Testing", style="Accent.TButton",
                       command=self._download_chromium).pack(anchor="w", pady=(8, 0))

        # Data
        frm_data = ttk.LabelFrame(self.main, text="Data Storage", padding=12)
        frm_data.pack(fill="x", pady=(0, 12))
        ttk.Label(frm_data, text=f"Profiles stored in:\n{DATA_DIR}",
                  font=("Segoe UI", 9)).pack(anchor="w")

        # About
        frm_about = ttk.LabelFrame(self.main, text="About", padding=12)
        frm_about.pack(fill="x")
        about_text = (
            "SimpleBrowser 2.0 — Advanced Anti-Detect Browser Manager\n\n"
            "Features:\n"
            "• Multi-profile management with isolated browser instances\n"
            "• Advanced fingerprint spoofing (Canvas, WebGL, Audio, ClientRects)\n"
            "• Proxy validation and auto-matching\n"
            "• Cookie import/export\n"
            "• Extension manager\n"
            "• Built-in Chromium downloader\n\n"
            "Inspired by AdsPower and Dolphin Anty"
        )
        ttk.Label(frm_about, text=about_text, justify="left").pack(anchor="w")

# ═══════════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    app = App()
    app.mainloop()
