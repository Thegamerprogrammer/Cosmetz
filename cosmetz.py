#!/usr/bin/env python3
"""Cosmetz - Interactive Windows optimizer with safety scouting."""

from __future__ import annotations

import ctypes
import json
import os
import platform
import re
import socket
import subprocess
import sys
import time
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

APP_NAME = "Cosmetz"
APP_VERSION = "3.5"
LOG_FILE = Path(__file__).with_name("Cosmetz.log")

try:
    from rich.console import Console
    from rich.live import Live
    from rich.panel import Panel
    from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
    from rich.table import Table
    from rich.text import Text
except Exception:  # noqa: BLE001
    Console = None
    Live = None
    Panel = None
    Progress = None
    Table = None
    Text = None

try:
    import psutil
except Exception:  # noqa: BLE001
    psutil = None

WINDOWS_DOCS: Dict[str, str] = {
    "powercfg": "https://learn.microsoft.com/windows-hardware/design/device-experiences/powercfg-command-line-options",
    "bcdedit": "https://learn.microsoft.com/windows-hardware/drivers/devtest/bcdedit--set",
    "netsh": "https://learn.microsoft.com/windows-server/networking/technologies/netsh/netsh-contexts",
    "dism": "https://learn.microsoft.com/windows-hardware/manufacture/desktop/dism-reference--deployment-image-servicing-and-management",
    "sfc": "https://support.microsoft.com/windows/use-the-system-file-checker-tool-to-repair-missing-or-corrupted-system-files",
    "mma": "https://learn.microsoft.com/powershell/module/mmagent/enable-mmagent",
}


@dataclass
class HardwareProfile:
    cpu_name: str
    gpu_name: str
    ram_gb: float
    cpu_cores: int
    tier: str


@dataclass
class SystemProfile:
    manufacturer: str
    model: str
    architecture: str
    os_caption: str
    os_build: str
    is_laptop: bool


@dataclass
class Preferences:
    dry_run: bool
    mode: str  # aggressive / balanced / peaceful
    allow_registry: bool
    allow_bcd: bool
    allow_service_changes: bool
    allow_network_resets: bool
    allow_storage_tuning: bool
    allow_visual_tuning: bool
    allow_memory_tuning: bool
    step_confirmations: bool
    internet_guard: bool


@dataclass
class Step:
    description: str
    command: List[str]
    category: str
    risk: str = "low"
    docs_key: str = ""
    fallback: Optional[List[str]] = None
    fallback_desc: str = ""


class CosmetzApp:
    def __init__(self) -> None:
        self.console = Console() if Console else None
        self.is_windows = platform.system().lower() == "windows"
        self.preferences: Optional[Preferences] = None
        self.last_benchmark_aborted: bool = False
        self.last_benchmark_peak_temp_c: Optional[float] = None

    def cprint(self, text: str) -> None:
        if self.console:
            self.console.print(text)
        else:
            print(text)

    def log(self, message: str) -> None:
        stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        prev = LOG_FILE.read_text(encoding="utf-8") if LOG_FILE.exists() else ""
        LOG_FILE.write_text(prev + f"[{stamp}] {message}\n", encoding="utf-8")

    def ask_yes_no(self, prompt: str, default: bool = True) -> bool:
        suffix = " [Y/n]: " if default else " [y/N]: "
        raw = input(prompt + suffix).strip().lower()
        if raw == "":
            return default
        return raw in {"y", "yes"}

    def animate_background(self, seconds: float = 1.6) -> None:
        if not (self.console and Live and Text):
            return
        frames = ["░▒▓", "▒▓░", "▓░▒"]
        start = time.time()
        with Live(refresh_per_second=8, console=self.console, transient=True) as live:
            i = 0
            while time.time() - start < seconds:
                bar = (frames[i % len(frames)] * 26)[:78]
                txt = Text(f"{bar}\n{APP_NAME} ambient UI animation ...\n{bar}", style="magenta")
                live.update(Panel(txt, border_style="bright_magenta"))
                time.sleep(0.12)
                i += 1

    def run(self) -> None:
        self.banner()
        if not self.is_windows:
            self.cprint("[bold red]Cosmetz is designed for Windows only.[/bold red]" if self.console else "Cosmetz is designed for Windows only.")
            return
        if not self.is_admin():
            self.elevate()
            return

        self.preferences = self.setup_wizard()
        hw = self.detect_hardware_profile()
        sp = self.detect_system_profile()
        self.show_profiles(hw, sp)

        while True:
            self.animate_background(1.2)
            choice = self.menu()
            if choice == "1":
                self.explain_plan()
            elif choice == "2":
                self.quick_optimize(hw, sp)
            elif choice == "3":
                self.gaming_boost(hw)
            elif choice == "4":
                self.ram_memory_suite()
            elif choice == "5":
                self.creative_boost(hw, sp)
            elif choice == "6":
                self.deep_repair()
            elif choice == "7":
                self.network_toolkit()
            elif choice == "8":
                self.driver_assistant(hw, sp)
            elif choice == "9":
                self.resource_analysis()
            elif choice == "10":
                self.github_discovery_massive()
            elif choice == "11":
                self.benchmark_suite(hw, sp)
            elif choice == "12":
                self.revert_defaults()
            elif choice == "13":
                self.preferences = self.setup_wizard()
            elif choice == "0":
                self.cprint("Thanks for using Cosmetz.")
                return
            else:
                self.cprint("Invalid option")

    def banner(self) -> None:
        t = f"{APP_NAME} {APP_VERSION} - Interactive Optimization Scout"
        if self.console and Panel:
            self.console.print(Panel.fit(f"[bold magenta]{t}[/bold magenta]\n[cyan]Animated UI + per-step controls + safety scouting[/cyan]", border_style="magenta"))
        else:
            print(t)

    @staticmethod
    def is_admin() -> bool:
        try:
            return ctypes.windll.shell32.IsUserAnAdmin() == 1
        except Exception:  # noqa: BLE001
            return False

    def elevate(self) -> None:
        self.cprint("Re-launching with administrator rights...")
        params = " ".join(f'"{a}"' for a in sys.argv)
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, params, None, 1)

    def setup_wizard(self) -> Preferences:
        self.cprint("\nSetup Wizard: choose safe + versatile behaviour")
        mode_in = input("Optimization mode [aggressive/balanced/peaceful] (default balanced): ").strip().lower()
        mode = mode_in if mode_in in {"aggressive", "balanced", "peaceful"} else "balanced"

        prefs = Preferences(
            dry_run=self.ask_yes_no("Preview mode (no changes)?", False),
            mode=mode,
            allow_registry=self.ask_yes_no("Allow Registry edits?", True),
            allow_bcd=self.ask_yes_no("Allow BCD edits?", False),
            allow_service_changes=self.ask_yes_no("Allow service changes?", True),
            allow_network_resets=self.ask_yes_no("Allow network resets?", True),
            allow_storage_tuning=self.ask_yes_no("Allow storage tuning?", True),
            allow_visual_tuning=self.ask_yes_no("Allow visual effects tuning?", False),
            allow_memory_tuning=self.ask_yes_no("Allow RAM/memory tuning?", True),
            step_confirmations=self.ask_yes_no("Interactive confirm on each medium/high step?", True),
            internet_guard=self.ask_yes_no("Run internet/document safety check before each step?", True),
        )
        self.log(f"Preferences: {prefs}")
        return prefs

    def menu(self) -> str:
        self.cprint(
            "\n1 Explain Plan\n2 Quick Optimize\n3 Gaming Boost\n4 RAM + Memory Suite\n5 Creative Workstation Boost\n"
            "6 Deep Repair\n7 Network Toolkit\n8 Driver + OEM Assistant\n9 Heavy App Analyzer\n10 Massive GitHub Scout\n"
            "11 Benchmark FPS Chart + Compare\n12 Revert Tweaks\n13 Re-run Setup\n0 Exit"
        )
        return input("Select option: ").strip()

    def run_cmd_capture(self, cmd: List[str]) -> tuple[int, str, str]:
        if self.preferences and self.preferences.dry_run:
            self.log(f"DRY-RUN (capture): {' '.join(cmd)}")
            return 0, "", ""
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
            self.log(f"CMD {' '.join(cmd)} => {proc.returncode}")
            if proc.stdout.strip():
                self.log(proc.stdout.strip()[:1000])
            if proc.stderr.strip():
                self.log(proc.stderr.strip()[:1000])
            return proc.returncode, proc.stdout, proc.stderr
        except Exception as exc:  # noqa: BLE001
            self.log(f"CMD ERROR {' '.join(cmd)}: {exc}")
            return 1, "", str(exc)

    def allowed_category(self, category: str) -> bool:
        p = self.preferences
        if not p:
            return True
        mapping = {
            "registry": p.allow_registry,
            "bcd": p.allow_bcd,
            "service": p.allow_service_changes,
            "network": p.allow_network_resets,
            "storage": p.allow_storage_tuning,
            "visual": p.allow_visual_tuning,
            "memory": p.allow_memory_tuning,
            "core": True,
        }
        return mapping.get(category, True)

    def internet_check(self, docs_key: str) -> tuple[bool, str]:
        # checks both general internet and docs reachability (if key provided)
        try:
            socket.create_connection(("1.1.1.1", 53), timeout=2).close()
        except OSError:
            return False, "No internet route"

        if docs_key and docs_key in WINDOWS_DOCS:
            try:
                req = urllib.request.Request(WINDOWS_DOCS[docs_key], method="HEAD", headers={"User-Agent": "Cosmetz"})
                with urllib.request.urlopen(req, timeout=5):
                    return True, f"Docs reachable: {docs_key}"
            except Exception:  # noqa: BLE001
                return False, f"Docs not reachable for {docs_key}"
        return True, "Internet reachable"

    def run_cmd(self, cmd: List[str]) -> int:
        if self.preferences and self.preferences.dry_run:
            self.log(f"DRY-RUN: {' '.join(cmd)}")
            return 0
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
            self.log(f"CMD {' '.join(cmd)} => {proc.returncode}")
            if proc.stdout.strip():
                self.log(proc.stdout.strip()[:1000])
            if proc.stderr.strip():
                self.log(proc.stderr.strip()[:1000])
            return proc.returncode
        except Exception as exc:  # noqa: BLE001
            self.log(f"CMD ERROR {' '.join(cmd)}: {exc}")
            return 1

    def step_menu(self, step: Step) -> str:
        self.cprint(f"\nStep: {step.description} | category={step.category} | risk={step.risk}")
        if step.docs_key in WINDOWS_DOCS:
            self.cprint(f"Docs: {WINDOWS_DOCS[step.docs_key]}")
        self.cprint("[r]un  [s]kip  [f]allback  [d]etails")
        ch = input("Action: ").strip().lower() or "r"
        return ch

    def execute_step(self, step: Step) -> None:
        # Category gate
        if not self.allowed_category(step.category):
            if step.fallback:
                self.log(f"Category disabled; fallback: {step.fallback_desc}")
                self.run_cmd(step.fallback)
            else:
                self.log(f"Skipped (category disabled): {step.description}")
            return

        # Internet safety scout
        if self.preferences and self.preferences.internet_guard:
            ok, msg = self.internet_check(step.docs_key)
            self.log(f"Internet guard for '{step.description}': {msg}")
            if not ok and step.risk in {"medium", "high"}:
                self.cprint(f"Safety guard blocked high-risk step due to connectivity/doc check: {msg}")
                if step.fallback:
                    self.run_cmd(step.fallback)
                return

        # Per-step interactive control
        action = "r"
        if self.preferences and self.preferences.step_confirmations:
            action = self.step_menu(step)

        if action == "s":
            self.log(f"User skipped: {step.description}")
            return
        if action == "f":
            if step.fallback:
                self.run_cmd(step.fallback)
            else:
                self.log(f"No fallback available: {step.description}")
            return
        if action == "d":
            self.cprint(f"Command: {' '.join(step.command)}")
            if step.fallback:
                self.cprint(f"Fallback: {' '.join(step.fallback)}")
            action = input("Run now? [y/N]: ").strip().lower()
            if action != "y":
                return

        self.run_cmd(step.command)

    def run_steps(self, title: str, steps: List[Step]) -> None:
        if self.console and Progress:
            with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), BarColumn(), TimeElapsedColumn(), console=self.console) as progress:
                task = progress.add_task(title, total=len(steps))
                for st in steps:
                    progress.update(task, description=st.description)
                    self.execute_step(st)
                    progress.advance(task)
        else:
            print(title)
            for st in steps:
                print("-", st.description)
                self.execute_step(st)

    def detect_hardware_profile(self) -> HardwareProfile:
        cpu_name, gpu_name = "Unknown CPU", "Unknown GPU"
        cores = os.cpu_count() or 4
        ram_gb = 8.0
        for cmd, key in [(["wmic", "cpu", "get", "name"], "cpu"), (["wmic", "path", "win32_videocontroller", "get", "name"], "gpu")]:
            try:
                out = subprocess.check_output(cmd, text=True, stderr=subprocess.DEVNULL)
                vals = [x.strip() for x in out.splitlines() if x.strip() and "Name" not in x]
                if vals:
                    if key == "cpu":
                        cpu_name = vals[0]
                    else:
                        gpu_name = vals[0]
            except Exception:  # noqa: BLE001
                pass
        if psutil:
            ram_gb = round(psutil.virtual_memory().total / (1024**3), 1)
        tier = "low-end"
        if ram_gb >= 32 and cores >= 12:
            tier = "high-end"
        elif ram_gb >= 16 and cores >= 8:
            tier = "mid-range"
        return HardwareProfile(cpu_name, gpu_name, ram_gb, cores, tier)

    def detect_system_profile(self) -> SystemProfile:
        manufacturer, model = "Unknown", "Unknown"
        os_caption, os_build = platform.platform(), platform.version()
        arch = platform.machine()
        chassis = ""

        try:
            out = subprocess.check_output(["wmic", "computersystem", "get", "manufacturer,model"], text=True, stderr=subprocess.DEVNULL)
            lines = [l.strip() for l in out.splitlines() if l.strip() and "Manufacturer" not in l]
            if lines:
                parts = lines[0].split(maxsplit=1)
                manufacturer = parts[0]
                model = parts[1] if len(parts) > 1 else "Unknown"
        except Exception:  # noqa: BLE001
            pass

        try:
            out = subprocess.check_output(["wmic", "os", "get", "caption,buildnumber"], text=True, stderr=subprocess.DEVNULL)
            lines = [l.strip() for l in out.splitlines() if l.strip() and "Caption" not in l]
            if lines:
                bits = lines[0].rsplit(" ", 1)
                if len(bits) == 2:
                    os_caption, os_build = bits[0], bits[1]
        except Exception:  # noqa: BLE001
            pass

        try:
            out = subprocess.check_output(["wmic", "systemenclosure", "get", "chassistypes"], text=True, stderr=subprocess.DEVNULL)
            lines = [l.strip() for l in out.splitlines() if l.strip() and "ChassisTypes" not in l]
            if lines:
                chassis = lines[0]
        except Exception:  # noqa: BLE001
            pass
        is_laptop = any(v in chassis for v in ["8", "9", "10", "14"])
        return SystemProfile(manufacturer, model, arch, os_caption, os_build, is_laptop)

    def show_profiles(self, hw: HardwareProfile, sp: SystemProfile) -> None:
        if self.console and Table:
            t = Table(title="Detected Platform")
            t.add_column("Field")
            t.add_column("Value")
            t.add_row("CPU", hw.cpu_name)
            t.add_row("GPU", hw.gpu_name)
            t.add_row("RAM", f"{hw.ram_gb} GB")
            t.add_row("Tier", hw.tier)
            t.add_row("Architecture", sp.architecture)
            t.add_row("Manufacturer", sp.manufacturer)
            t.add_row("Model", sp.model)
            t.add_row("OS", f"{sp.os_caption} ({sp.os_build})")
            t.add_row("Device", "Laptop" if sp.is_laptop else "Desktop")
            self.console.print(t)
        else:
            print(hw)
            print(sp)

    def explain_plan(self) -> None:
        self.cprint("\nEvery operation is step-interactive: run/skip/fallback/details.")
        self.cprint("Internet guard runs before each step and can block higher risk operations.")
        self.cprint("Modes: aggressive = deeper changes, peaceful = low-risk practical tuning.")
        self.cprint("Benchmark mode can capture baseline vs optimized score and generate an FPS chart.")
        self.cprint("Creative Workstation Boost targets content creation apps with stability-first tuning.")

    def create_restore_point(self) -> None:
        self.run_cmd(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", "Checkpoint-Computer -Description 'Cosmetz Restore Point' -RestorePointType 'MODIFY_SETTINGS'"])

    def mode_filter(self, steps: List[Step]) -> List[Step]:
        mode = self.preferences.mode if self.preferences else "balanced"
        if mode == "aggressive":
            return steps
        if mode == "peaceful":
            return [s for s in steps if s.risk == "low"]
        return [s for s in steps if s.risk in {"low", "medium"}]

    def quick_optimize(self, hw: HardwareProfile, sp: SystemProfile) -> None:
        self.create_restore_point()
        steps = [
            Step("Set high performance plan", ["powercfg", "/setactive", "scheme_min"], "core", "low", "powercfg"),
            Step("Enable memory compression", ["powershell", "-NoProfile", "-Command", "Enable-MMAgent -MemoryCompression"], "memory", "low", "mma"),
            Step("Set memoryusage=2", ["fsutil", "behavior", "set", "memoryusage", "2"], "memory", "medium"),
            Step("Apply disabledynamictick", ["bcdedit", "/set", "disabledynamictick", "yes"], "bcd", "medium", "bcdedit", ["powercfg", "/setacvalueindex", "scheme_current", "sub_processor", "PROCTHROTTLEMIN", "100"], "CPU min state 100%"),
            Step("Apply useplatformtick", ["bcdedit", "/set", "useplatformtick", "yes"], "bcd", "medium", "bcdedit", ["powercfg", "/setacvalueindex", "scheme_current", "sub_processor", "PROCTHROTTLEMAX", "100"], "CPU max state 100%"),
            Step("Flush DNS", ["ipconfig", "/flushdns"], "network", "low", "netsh"),
        ]
        if hw.tier == "low-end":
            steps.append(Step("Set VisualFX performance", ["reg", "add", r"HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects", "/v", "VisualFXSetting", "/t", "REG_DWORD", "/d", "2", "/f"], "visual", "medium"))
        if sp.is_laptop:
            steps.append(Step("Enable processor boost on AC", ["powercfg", "/setacvalueindex", "scheme_current", "sub_processor", "PERFBOOSTMODE", "2"], "core", "low", "powercfg"))
        self.run_steps("Quick Optimize", self.mode_filter(steps))

    def gaming_boost(self, hw: HardwareProfile) -> None:
        self.create_restore_point()
        steps = [
            Step("Disable GameDVR", ["reg", "add", r"HKCU\System\GameConfigStore", "/v", "GameDVR_Enabled", "/t", "REG_DWORD", "/d", "0", "/f"], "registry", "low"),
            Step("Disable game bar policy", ["reg", "add", r"HKLM\SOFTWARE\Policies\Microsoft\Windows\GameDVR", "/v", "AllowGameDVR", "/t", "REG_DWORD", "/d", "0", "/f"], "registry", "low"),
            Step("Set NetworkThrottlingIndex", ["reg", "add", r"HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile", "/v", "NetworkThrottlingIndex", "/t", "REG_DWORD", "/d", "4294967295", "/f"], "registry", "high", fallback=["netsh", "interface", "tcp", "set", "global", "rss=enabled"], fallback_desc="RSS only"),
            Step("Enable RSS", ["netsh", "interface", "tcp", "set", "global", "rss=enabled"], "network", "low", "netsh"),
            Step("Disable hibernation", ["powercfg", "/h", "off"], "storage", "medium", "powercfg", fallback=["powercfg", "/h", "on"], fallback_desc="Keep hibernation"),
        ]
        if "nvidia" in hw.gpu_name.lower() or "amd" in hw.gpu_name.lower() or "intel" in hw.gpu_name.lower():
            steps.append(Step("Enable HAGS", ["reg", "add", r"HKLM\SYSTEM\CurrentControlSet\Control\GraphicsDrivers", "/v", "HwSchMode", "/t", "REG_DWORD", "/d", "2", "/f"], "registry", "medium"))
        self.run_steps("Gaming Boost", self.mode_filter(steps))

    def ram_memory_suite(self) -> None:
        self.create_restore_point()
        steps = [
            Step("Enable MemoryCompression", ["powershell", "-NoProfile", "-Command", "Enable-MMAgent -MemoryCompression"], "memory", "low", "mma"),
            Step("Automatic managed pagefile", ["wmic", "computersystem", "where", "name='%computername%'", "set", "AutomaticManagedPagefile=True"], "memory", "medium"),
            Step("Set LargeSystemCache=1", ["reg", "add", r"HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management", "/v", "LargeSystemCache", "/t", "REG_DWORD", "/d", "1", "/f"], "registry", "high", fallback=["powershell", "-NoProfile", "-Command", "Write-Output 'Skip LargeSystemCache tweak'"], fallback_desc="Skip cache tweak"),
            Step("Trim process working sets", ["powershell", "-NoProfile", "-Command", "Get-Process | ForEach-Object { try { $_.MinWorkingSet = $_.MinWorkingSet } catch {} }"], "memory", "low"),
        ]
        self.run_steps("RAM + Memory Suite", self.mode_filter(steps))


    def creative_boost(self, hw: HardwareProfile, sp: SystemProfile) -> None:
        self.create_restore_point()
        steps = [
            Step("Set high performance power plan", ["powercfg", "/setactive", "scheme_min"], "core", "low", "powercfg"),
            Step("Enable memory compression", ["powershell", "-NoProfile", "-Command", "Enable-MMAgent -MemoryCompression"], "memory", "low", "mma"),
            Step("Ensure automatic managed pagefile", ["wmic", "computersystem", "where", "name='%computername%'", "set", "AutomaticManagedPagefile=True"], "memory", "medium"),
            Step("Enable NTFS long paths", ["reg", "add", r"HKLM\SYSTEM\CurrentControlSet\Control\FileSystem", "/v", "LongPathsEnabled", "/t", "REG_DWORD", "/d", "1", "/f"], "registry", "medium"),
            Step("Set visual effects to balanced quality", ["reg", "add", r"HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects", "/v", "VisualFXSetting", "/t", "REG_DWORD", "/d", "1", "/f"], "visual", "low"),
            Step("Flush DNS for cloud asset tools", ["ipconfig", "/flushdns"], "network", "low", "netsh"),
        ]
        if sp.is_laptop:
            steps.append(Step("Set active cooling policy on AC", ["powercfg", "/setacvalueindex", "scheme_current", "sub_processor", "SYSCOOLPOL", "1"], "core", "low", "powercfg"))
        if hw.tier == "high-end":
            steps.append(Step("Duplicate Ultimate Performance plan", ["powercfg", "-duplicatescheme", "e9a42b02-d5df-448d-aa00-03f14749eb61"], "core", "low", "powercfg"))
            steps.append(Step("Activate Ultimate Performance", ["powercfg", "/setactive", "e9a42b02-d5df-448d-aa00-03f14749eb61"], "core", "low", "powercfg"))

        self.run_steps("Creative Workstation Boost", self.mode_filter(steps))

    def deep_repair(self) -> None:
        self.create_restore_point()
        steps = [
            Step("DISM restore health", ["DISM", "/Online", "/Cleanup-Image", "/RestoreHealth"], "core", "low", "dism"),
            Step("SFC scan", ["sfc", "/scannow"], "core", "low", "sfc"),
            Step("Temp cleanup", ["powershell", "-NoProfile", "-Command", "Get-ChildItem $env:TEMP -Recurse -Force -ErrorAction SilentlyContinue | Remove-Item -Force -Recurse -ErrorAction SilentlyContinue"], "storage", "medium"),
            Step("Windows update cache cleanup", ["powershell", "-NoProfile", "-Command", "Stop-Service wuauserv,bits -Force -ErrorAction SilentlyContinue; Remove-Item $env:windir\\SoftwareDistribution\\Download\\* -Recurse -Force -ErrorAction SilentlyContinue; Start-Service bits,wuauserv -ErrorAction SilentlyContinue"], "storage", "medium"),
            Step("Defrag optimize", ["defrag", "/C", "/O"], "storage", "low"),
        ]
        self.run_steps("Deep Repair", self.mode_filter(steps))

    def network_toolkit(self) -> None:
        full = self.ask_yes_no("Run full network reset?", True)
        steps = [Step("Flush DNS", ["ipconfig", "/flushdns"], "network", "low", "netsh")]
        if full:
            steps += [
                Step("Release IP", ["ipconfig", "/release"], "network", "medium"),
                Step("Renew IP", ["ipconfig", "/renew"], "network", "medium"),
                Step("Reset IP stack", ["netsh", "int", "ip", "reset"], "network", "medium", "netsh"),
                Step("Reset winsock", ["netsh", "winsock", "reset"], "network", "medium", "netsh"),
            ]
        self.run_steps("Network Toolkit", self.mode_filter(steps))

    def driver_assistant(self, hw: HardwareProfile, sp: SystemProfile) -> None:
        hints = []
        g = hw.gpu_name.lower()
        m = sp.manufacturer.lower()
        if "nvidia" in g:
            hints.append(("GPU", "NVIDIA: install latest Game Ready via NVIDIA App/GeForce Experience"))
        elif "amd" in g or "radeon" in g:
            hints.append(("GPU", "AMD: install latest Adrenalin WHQL package"))
        elif "intel" in g:
            hints.append(("GPU", "Intel: use Intel Driver & Support Assistant"))
        if "dell" in m:
            hints.append(("OEM", "Use Dell Command Update / SupportAssist"))
        elif "hp" in m:
            hints.append(("OEM", "Use HP Support Assistant"))
        elif "lenovo" in m:
            hints.append(("OEM", "Use Lenovo Vantage"))
        elif "asus" in m:
            hints.append(("OEM", "Use MyASUS/Armoury Crate updates"))
        hints += [("Chipset", "Update chipset before GPU"), ("BIOS", "Keep BIOS stable/current")]

        if self.console and Table:
            t = Table(title="Driver + OEM Guidance")
            t.add_column("Area")
            t.add_column("Recommendation")
            for a, b in hints:
                t.add_row(a, b)
            self.console.print(t)
        else:
            print(hints)

    def resource_analysis(self) -> None:
        rows = []
        if psutil:
            for proc in psutil.process_iter(["name", "memory_info"]):
                try:
                    rows.append((proc.info["name"] or "unknown", f"{(proc.info['memory_info'].rss or 0)/(1024*1024):.1f} MB"))
                except Exception:  # noqa: BLE001
                    continue
            rows = sorted(rows, key=lambda x: float(x[1].split()[0]), reverse=True)[:15]

        dirs = self.scan_large_dirs()
        if self.console and Table:
            t1 = Table(title="Top RAM Processes")
            t1.add_column("Process")
            t1.add_column("RAM")
            for r in rows or [("psutil missing", "install psutil")]:
                t1.add_row(*r)
            self.console.print(t1)
            t2 = Table(title="Large User Folders")
            t2.add_column("Folder")
            t2.add_column("Size")
            for d in dirs:
                t2.add_row(*d)
            self.console.print(t2)
        self.cprint("Suggested fixes: disable heavy startup apps, remove unused launchers, move large game libraries.")

    def scan_large_dirs(self) -> List[tuple[str, str]]:
        user = Path(os.environ.get("USERPROFILE", "C:/Users"))
        targets = [user / "Downloads", user / "Desktop", user / "Documents", user / "AppData" / "Local" / "Temp"]
        out = []
        for path in targets:
            if not path.exists():
                continue
            total = 0
            for root, _, files in os.walk(path):
                for f in files:
                    p = Path(root) / f
                    try:
                        total += p.stat().st_size
                    except Exception:  # noqa: BLE001
                        pass
            out.append((str(path), f"{total/(1024**3):.2f} GB"))
        return sorted(out, key=lambda x: float(x[1].split()[0]), reverse=True)

    def github_discovery_massive(self) -> None:
        self.cprint("Scouting many GitHub repos across multiple query clusters...")
        queries = [
            "windows optimizer python", "windows tweak tool python", "pc optimization python",
            "windows gaming optimizer python", "windows debloat python", "system tuning python windows",
            "win11 optimizer python", "windows latency optimizer python",
        ]
        repos: Dict[str, tuple[str, str, str]] = {}
        for q in queries:
            for page in [1, 2, 3]:
                url = (
                    "https://api.github.com/search/repositories?q=" + urllib.parse.quote(q)
                    + f"&sort=stars&order=desc&per_page=30&page={page}"
                )
                try:
                    req = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json", "User-Agent": "Cosmetz"})
                    with urllib.request.urlopen(req, timeout=20) as resp:
                        data = json.loads(resp.read().decode("utf-8", errors="ignore"))
                    for it in data.get("items", []):
                        name = it.get("full_name", "")
                        if name:
                            repos[name] = (name, str(it.get("stargazers_count", 0)), it.get("html_url", ""))
                except Exception as exc:  # noqa: BLE001
                    self.log(f"GitHub query fail ({q},p{page}): {exc}")

        rows = sorted(repos.values(), key=lambda x: int(x[1]), reverse=True)[:80]
        if self.console and Table:
            t = Table(title="Top Aggregated Optimization Repositories")
            t.add_column("Repo")
            t.add_column("Stars")
            t.add_column("URL")
            for r in rows or [("No results", "0", "Check network/rate-limits")]:
                t.add_row(*r)
            self.console.print(t)
        else:
            print(rows)

    def optional_install_benchmark_tool(self, hw: HardwareProfile, sp: SystemProfile) -> None:  # noqa: ARG002
        want = self.ask_yes_no("Install external benchmark software (winget) with your permission?", default=False)
        if not want:
            return

        candidates = [
            "UL.Benchmark.3DMark",
            "Unigine.HeavenBenchmark",
            "PrimateLabs.Geekbench.6",
            "Maxon.CinebenchR23",
        ]
        if "nvidia" in hw.gpu_name.lower() or "amd" in hw.gpu_name.lower():
            candidates = ["UL.Benchmark.3DMark", "Unigine.HeavenBenchmark"] + candidates

        installed_any = False
        for pkg in candidates:
            self.cprint(f"Trying benchmark package: {pkg}")
            code = self.run_cmd([
                "winget", "install", "--id", pkg, "--silent", "--accept-package-agreements", "--accept-source-agreements"
            ])
            if code == 0:
                installed_any = True
                self.cprint(f"Installed benchmark package: {pkg}")
                break

        if not installed_any:
            self.cprint("Could not auto-install a benchmark app via winget. Using WinSAT built-in benchmark instead.")

    def get_max_temperature_c(self) -> Optional[float]:
        temps: List[float] = []

        # GPU temp via NVIDIA SMI (if available)
        try:
            code, out, _ = self.run_cmd_capture(["nvidia-smi", "--query-gpu=temperature.gpu", "--format=csv,noheader,nounits"])
            if code == 0:
                for line in out.splitlines():
                    line = line.strip()
                    if line and line.replace(".", "", 1).isdigit():
                        temps.append(float(line))
        except Exception:  # noqa: BLE001
            pass

        # CPU/board thermal zones (best effort)
        try:
            code, out, _ = self.run_cmd_capture([
                "powershell", "-NoProfile", "-Command",
                "Get-CimInstance -Namespace root/wmi -ClassName MSAcpi_ThermalZoneTemperature | Select-Object -ExpandProperty CurrentTemperature | ConvertTo-Json -Compress"
            ])
            if code == 0 and out.strip():
                raw = json.loads(out.strip())
                vals = raw if isinstance(raw, list) else [raw]
                for v in vals:
                    try:
                        c = (float(v) / 10.0) - 273.15
                        if c > 0:
                            temps.append(round(c, 1))
                    except Exception:  # noqa: BLE001
                        pass
        except Exception:  # noqa: BLE001
            pass

        return max(temps) if temps else None

    def run_winsat_with_temp_guard(self, cutoff_c: float = 90.0) -> bool:
        self.last_benchmark_aborted = False
        self.last_benchmark_peak_temp_c = None

        if self.preferences and self.preferences.dry_run:
            return True

        try:
            proc = subprocess.Popen(["winsat", "formal", "-restart", "clean"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        except Exception as exc:  # noqa: BLE001
            self.log(f"Failed to start winsat: {exc}")
            return False

        peak: Optional[float] = None
        while proc.poll() is None:
            t = self.get_max_temperature_c()
            if t is not None:
                peak = t if peak is None else max(peak, t)
                self.log(f"Benchmark temp check: {t:.1f}C")
                if t >= cutoff_c:
                    self.log(f"Benchmark aborted due to temperature cutoff {t:.1f}C >= {cutoff_c:.1f}C")
                    self.cprint(f"Temperature reached {t:.1f}°C. Stopping benchmark for safety.")
                    proc.terminate()
                    self.last_benchmark_aborted = True
                    break
            time.sleep(2.0)

        try:
            proc.wait(timeout=10)
        except Exception:  # noqa: BLE001
            proc.kill()

        self.last_benchmark_peak_temp_c = peak
        return not self.last_benchmark_aborted and proc.returncode == 0

    def collect_winsat_scores(self) -> Dict[str, float]:
        # Use built-in Windows assessment for a reproducible before/after metric.
        ok = self.run_winsat_with_temp_guard(cutoff_c=90.0)
        if not ok:
            return {"CPUScore": 0.0, "D3DScore": 0.0, "DiskScore": 0.0, "GraphicsScore": 0.0, "MemoryScore": 0.0}
        code, stdout, _ = self.run_cmd_capture([
            "powershell", "-NoProfile", "-Command",
            "Get-CimInstance Win32_WinSAT | Select-Object CPUScore,D3DScore,DiskScore,GraphicsScore,MemoryScore | ConvertTo-Json -Compress"
        ])
        if code != 0:
            return {"CPUScore": 0.0, "D3DScore": 0.0, "DiskScore": 0.0, "GraphicsScore": 0.0, "MemoryScore": 0.0}
        try:
            data = json.loads(stdout.strip() or "{}")
            return {
                "CPUScore": float(data.get("CPUScore", 0.0) or 0.0),
                "D3DScore": float(data.get("D3DScore", 0.0) or 0.0),
                "DiskScore": float(data.get("DiskScore", 0.0) or 0.0),
                "GraphicsScore": float(data.get("GraphicsScore", 0.0) or 0.0),
                "MemoryScore": float(data.get("MemoryScore", 0.0) or 0.0),
            }
        except Exception:  # noqa: BLE001
            # Fallback parser for raw output
            vals: Dict[str, float] = {"CPUScore": 0.0, "D3DScore": 0.0, "DiskScore": 0.0, "GraphicsScore": 0.0, "MemoryScore": 0.0}
            for key in vals:
                m = re.search(rf'"?{key}"?\s*[:=]\s*([0-9]+(?:\.[0-9]+)?)', stdout)
                if m:
                    vals[key] = float(m.group(1))
            return vals

    @staticmethod
    def estimated_fps(scores: Dict[str, float]) -> float:
        graphics = max(scores.get("D3DScore", 0.0), scores.get("GraphicsScore", 0.0))
        return round(graphics * 18.0, 1)

    def fps_chart(self, before_fps: float, after_fps: float) -> None:
        inc = after_fps - before_fps
        pct = (inc / before_fps * 100.0) if before_fps > 0 else 0.0
        max_fps = max(before_fps, after_fps, 1.0)
        b_len = int((before_fps / max_fps) * 40)
        a_len = int((after_fps / max_fps) * 40)
        b_bar = "█" * b_len
        a_bar = "█" * a_len

        if self.console and Table:
            t = Table(title="Estimated FPS Comparison (Before vs Optimized)")
            t.add_column("Phase")
            t.add_column("Estimated FPS")
            t.add_column("Chart")
            t.add_row("Before", f"{before_fps:.1f}", b_bar)
            t.add_row("After", f"{after_fps:.1f}", a_bar)
            t.add_row("Delta", f"{inc:+.1f} ({pct:+.2f}%)", "")
            self.console.print(t)
        else:
            print(f"Before: {before_fps:.1f} |{b_bar}")
            print(f"After : {after_fps:.1f} |{a_bar}")
            print(f"Delta : {inc:+.1f} FPS ({pct:+.2f}%)")

    def benchmark_suite(self, hw: HardwareProfile, sp: SystemProfile) -> None:
        if self.preferences and self.preferences.dry_run:
            self.cprint("Benchmarking is disabled in preview mode. Disable dry-run in setup to execute benchmarks.")
            return

        self.optional_install_benchmark_tool(hw, sp)
        self.cprint("Running baseline benchmark (WinSAT)...")
        before = self.collect_winsat_scores()
        before_fps = self.estimated_fps(before)

        self.cprint("Baseline captured. Apply optimization pack before second benchmark?")
        if self.ask_yes_no("Run Quick + Gaming + RAM optimization pack now?", default=True):
            self.quick_optimize(hw, sp)
            self.gaming_boost(hw)
            self.ram_memory_suite()

        self.cprint("Running post-optimization benchmark (WinSAT)...")
        after = self.collect_winsat_scores()
        after_fps = self.estimated_fps(after)

        if self.last_benchmark_peak_temp_c is not None:
            self.cprint(f"Benchmark peak observed temperature: {self.last_benchmark_peak_temp_c:.1f}°C")
        if self.last_benchmark_aborted:
            self.cprint("Benchmark was cut off for thermal safety at/above 90°C. Results may be incomplete.")

        self.fps_chart(before_fps, after_fps)
        self.log(f"Benchmark before={before} after={after} before_fps={before_fps} after_fps={after_fps} peak_temp={self.last_benchmark_peak_temp_c} aborted={self.last_benchmark_aborted}")

    def revert_defaults(self) -> None:
        steps = [
            Step("Set balanced plan", ["powercfg", "/setactive", "scheme_balanced"], "core", "low", "powercfg"),
            Step("Enable GameDVR", ["reg", "add", r"HKCU\System\GameConfigStore", "/v", "GameDVR_Enabled", "/t", "REG_DWORD", "/d", "1", "/f"], "registry", "low"),
            Step("Delete disabledynamictick", ["bcdedit", "/deletevalue", "disabledynamictick"], "bcd", "medium", "bcdedit"),
            Step("Delete useplatformtick", ["bcdedit", "/deletevalue", "useplatformtick"], "bcd", "medium", "bcdedit"),
            Step("Enable SysMain auto", ["sc", "config", "SysMain", "start=", "auto"], "service", "low"),
        ]
        self.run_steps("Revert Tweaks", steps)


if __name__ == "__main__":
    CosmetzApp().run()
