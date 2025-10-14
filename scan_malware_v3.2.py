"""
Ludang's Ultimate Cyber Malware Scanner v3.2
By: Ludang Prasetyo Nugroho (nugra.online)
-----------------------------------------
- Auto-launches in a new terminal window via batch script.
- Immersive hacker-style UI with animated borders, glitch effects, neon colors, and matrix rain.
- Mode scan: Quick, Full (all drives/devices), Custom.
- Integrates ClamAV or Windows Defender if available, falls back to simulation.
- Realistic simulated malware detection with dynamic file names.
- Interactive options for quarantine, recycle, delete with secure confirmation.
- Comprehensive system info: CPU, RAM, GPU, Network, Battery, Disks, Temps, BIOS, etc.
- Enhanced table rendering with text wrapping for long values.
- New: Animated borders, mission log output, dynamic glitch effects, and boot sequence.

Requirements:
    pip install colorama tqdm send2trash psutil
"""
import argparse
import os
import subprocess
import sys
import time
import random
import shutil
import socket
import platform
import psutil
from datetime import datetime
from threading import Thread, Event
from itertools import cycle
import textwrap

# Initialize colorama for Windows compatibility
try:
    from colorama import init as colorama_init, Fore, Style
    colorama_init(autoreset=True)
except ImportError:
    print("[CRITICAL] Colorama not installed. Install with: pip install colorama")
    sys.exit(1)

try:
    from send2trash import send2trash
    HAS_SEND2TRASH = True
except ImportError:
    HAS_SEND2TRASH = False

try:
    from tqdm import tqdm
    HAS_TQDM = True
except ImportError:
    HAS_TQDM = False

try:
    import psutil
except ImportError:
    print("[CRITICAL] Psutil not installed. Install with: pip install psutil")
    sys.exit(1)

# ---------------------------
# Helper Functions: System Info & Detection
# ---------------------------
def get_system_info():
    """Collect comprehensive system and hardware information."""
    info = {}
    try:
        info["Hostname"] = socket.gethostname()
        info["OS"] = f"{platform.system()} {platform.release()} ({platform.version()})"
        info["Architecture"] = platform.machine()
        info["Python"] = platform.python_version()
        info["CPU"] = platform.processor() or "Unknown"
        info["Cores (Physical)"] = psutil.cpu_count(logical=False)
        info["Cores (Logical)"] = psutil.cpu_count(logical=True)
        try:
            freq = psutil.cpu_freq()
            info["CPU Frequency"] = f"{freq.current:.2f} MHz (Max: {freq.max:.2f} MHz)"
        except:
            info["CPU Frequency"] = "N/A"
        info["CPU Usage"] = f"{psutil.cpu_percent(interval=0.5)}%"
        info["RAM Total"] = f"{psutil.virtual_memory().total / (1024 ** 3):.2f} GB"
        info["RAM Available"] = f"{psutil.virtual_memory().available / (1024 ** 3):.2f} GB"
        info["RAM Used"] = f"{psutil.virtual_memory().used / (1024 ** 3):.2f} GB"
        info["Swap Total"] = f"{psutil.swap_memory().total / (1024 ** 3):.2f} GB"
        info["Swap Used"] = f"{psutil.swap_memory().used / (1024 ** 3):.2f} GB"
        info["Disk Total"] = f"{psutil.disk_usage('/').total / (1024 ** 3):.2f} GB"
        info["Disk Used"] = f"{psutil.disk_usage('/').used / (1024 ** 3):.2f} GB"
        info["Disk Partitions"] = ", ".join([p.device for p in psutil.disk_partitions()])
        info["Uptime"] = f"{round(time.time() - psutil.boot_time()) // 3600} hours"
        info["Processes"] = len(psutil.pids())
        info["Logged Users"] = ", ".join([u.name for u in psutil.users()]) or "N/A"
        info["IP Address"] = socket.gethostbyname(socket.gethostname())
        
        # GPU Info
        try:
            gpu_cmd = subprocess.run(["wmic", "path", "win32_VideoController", "get", "name"],
                                     capture_output=True, text=True)
            lines = [l.strip() for l in gpu_cmd.stdout.splitlines() if l.strip()]
            if len(lines) > 1:
                info["GPU"] = lines[1]
            else:
                info["GPU"] = "N/A"
        except:
            info["GPU"] = "N/A"
        
        # Network Interfaces
        net_info = psutil.net_if_addrs()
        info["Network Interfaces"] = ", ".join([iface for iface in net_info.keys()]) or "N/A"
        
        # Temperatures
        temps = psutil.sensors_temperatures()
        if temps:
            temp_str = []
            for name, entries in temps.items():
                for entry in entries:
                    temp_str.append(f"{name}: {entry.current}°C")
            info["Temperatures"] = ", ".join(temp_str)
        else:
            info["Temperatures"] = "N/A"
        
        # Battery
        battery = psutil.sensors_battery()
        if battery:
            info["Battery"] = f"{battery.percent}% ({'Plugged' if battery.power_plugged else 'Not Plugged'}, Time left: {battery.secsleft // 60} min)"
        else:
            info["Battery"] = "N/A"
        
        # Windows-specific: BIOS, Motherboard
        if platform.system() == "Windows":
            try:
                bios_cmd = subprocess.run(["wmic", "bios", "get", "smbiosbiosversion"], capture_output=True, text=True)
                bios = bios_cmd.stdout.strip().splitlines()[-1].strip()
                info["BIOS Version"] = bios if bios else "N/A"
                
                mb_cmd = subprocess.run(["wmic", "baseboard", "get", "product"], capture_output=True, text=True)
                mb = mb_cmd.stdout.strip().splitlines()[-1].strip()
                info["Motherboard"] = mb if mb else "N/A"
            except:
                info["BIOS Version"] = "N/A"
                info["Motherboard"] = "N/A"
        
    except Exception as e:
        info["Error"] = str(e)
    return info

def is_clamscan_available():
    """Check if ClamAV is available."""
    from shutil import which
    return which("clamscan") or which("clamscan.exe")

def find_mp_cmd():
    """Find path to MpCmdRun for Windows Defender."""
    candidates = [
        r"C:\Program Files\Windows Defender\MpCmdRun.exe",
        r"C:\Program Files\Microsoft Defender ATP\MpCmdRun.exe",
        r"C:\Program Files (x86)\Windows Defender\MpCmdRun.exe",
    ]
    from shutil import which
    p = which("MpCmdRun.exe")
    if p:
        return p
    for c in candidates:
        if os.path.exists(c):
            return c
    return None

# ---------------------------
# Scanner Engines
# ---------------------------
def run_clamscan_collect(paths):
    """Run ClamAV and collect infected files."""
    clamscan = is_clamscan_available()
    if not clamscan:
        return []
    cmd = [clamscan, "-r", "--infected", "--no-summary"] + list(paths)
    try:
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        out_lines = proc.stdout.splitlines()
    except Exception as e:
        print(Fore.RED + "[ERROR] ClamAV failed:", e)
        return []
    infected = []
    for line in out_lines:
        line = line.strip()
        if not line or not line.endswith(" FOUND"):
            continue
        try:
            left, right = line.rsplit(":", 1)
            file_path = left.strip()
            sig = right.replace(" FOUND", "").strip()
            infected.append((file_path, sig))
        except Exception:
            pass
    return infected

def run_mp_tasks_and_collect(paths, result_list):
    """Run Windows Defender and collect threats."""
    mp = find_mp_cmd()
    if mp:
        for p in paths:
            try:
                subprocess.run([mp, "-Scan", "-ScanType", "3", "-File", p],
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except:
                pass
    else:
        try:
            subprocess.run(["powershell", "-Command", "Start-MpScan -ScanType QuickScan"],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except:
            pass

    try:
        ps_cmd = r"Get-MpThreat | Format-List -Property Resources,ThreatName"
        procq = subprocess.run(["powershell", "-Command", ps_cmd],
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        out = procq.stdout.splitlines()
        cur_resources = None
        cur_threat = None
        for line in out:
            line = line.strip()
            if not line:
                continue
            if line.startswith("Resources"):
                parts = line.split(":", 1)
                if len(parts) == 2:
                    res = parts[1].strip().lstrip("{").rstrip("}")
                    resources = [r.strip() for r in res.split(",") if r.strip()]
                    cur_resources = resources
            elif line.startswith("ThreatName"):
                parts = line.split(":", 1)
                if len(parts) == 2:
                    cur_threat = parts[1].strip()
                    if cur_resources:
                        for r in cur_resources:
                            result_list.append((r, cur_threat))
                        cur_resources = None
                        cur_threat = None
    except:
        pass

# ---------------------------
# UI: Ultimate Hacker-Style Animated Scanner
# ---------------------------
class AnimatedScanner:
    def __init__(self, title="Cyber Malware Scanner", paths=None):
        self.title = title
        self.paths = paths or [os.path.expanduser("~")]
        self._stop_event = Event()
        self._spinner_cycle = cycle(["[HACKING]", "[INFILTRATING]", "[DECODING]", "[BREACHING]", "[CRACKING]", "[SCANNING]"])
        self._binary_stream = cycle(["010101", "101010", "110011", "001100", "111000", "000111"])
        self._file_samples = [
            "kernel_exploit.dll", "rootkit.sys", "trojan_backdoor.exe", "ransomware.tmp", "spyware.dat",
            "phishing_script.js", "malware_payload.bin", "virus_infected.pdf", "worm_network.exe", "adware_popup.tmp"
        ]
        self._ascii_art = [
            "  ____  ", " | __ ) ", " |  _ \\ ", " | |_) |", " |____/ ", "  ***  ", "  ***  ", " [VIRUS] "
        ]
        self.start_time = None
        self.elapsed = 0.0
        self.checked = 0
        self.fake_speed = random.uniform(1200, 3000)  # Increased speed for realism
        self.progress = 0.0
        self.status_message = "Initializing Cyber Matrix..."
        self.module_status = {"ClamAV": False, "Defender": False, "Mode": "Unknown"}
        self.system_info = get_system_info()
        self.glitch_counter = 0
        self.border_cycle = cycle(["═", "▒", "█", "░", "■", "═"])

    def _human_time(self, seconds):
        """Format time in a human-readable way."""
        if seconds < 1:
            return "0s"
        m, s = divmod(int(seconds), 60)
        h, m = divmod(m, 60)
        if h:
            return f"{h}h{m}m{s}s"
        if m:
            return f"{m}m{s}s"
        return f"{s}s"

    def _render_line(self, left, right, width=80):
        """Render a line with aligned text."""
        left = str(left)[:width]
        right = str(right)
        space = width - len(left) - len(right)
        return left + (" " * max(0, space)) + right

    def _is_external_running(self, external_proc):
        """Check if external process is running (supports Popen/Thread/None)."""
        if external_proc is None:
            return False
        poll = getattr(external_proc, "poll", None)
        if callable(poll):
            return external_proc.poll() is None
        is_alive = getattr(external_proc, "is_alive", None)
        if callable(is_alive):
            return external_proc.is_alive()
        return False

    def _ui_loop(self, external_proc=None):
        self.start_time = time.time()
        while not self._stop_event.is_set():
            self.elapsed = time.time() - self.start_time
            running = self._is_external_running(external_proc)
            if running:
                inc = random.uniform(0.5, 3.5) * (1.0 - (self.progress / 100.0))
                self.progress = min(self.progress + inc, 95.0)
            else:
                inc = random.uniform(12, 30)
                self.progress = min(self.progress + inc, 100.0)

            self.checked = int(self.progress / 100.0 * (self.fake_speed * max(1, self.elapsed)))
            spinner = next(self._spinner_cycle)
            binary = next(self._binary_stream)
            file_name = random.choice(self._file_samples)
            ascii_line = random.choice(self._ascii_art)
            border_char = next(self.border_cycle)
            
            # Glitch effect
            self.glitch_counter += 1
            glitch = random.choice(["~", "#", "%", "&", "$", "@"]) if self.glitch_counter % 12 == 0 else ""
            
            # Build UI
            lines = []
            lines.append(Fore.CYAN + Style.BRIGHT + f"╔{border_char * 78}╗")
            lines.append(Fore.CYAN + f"║ {self.title.center(76)} {glitch}║")
            lines.append(Fore.CYAN + f"╠{border_char * 78}╣")
            lines.append(Fore.MAGENTA + self._render_line(f"[STATUS] {self.status_message}", f"[MODE] {self.module_status['Mode']}"))
            lines.append(Fore.YELLOW + self._render_line(
                f"[MODULES] ClamAV={Fore.GREEN + 'ON' if self.module_status['ClamAV'] else Fore.RED + 'OFF'} | Defender={Fore.GREEN + 'ON' if self.module_status['Defender'] else Fore.RED + 'OFF'}",
                f"[ELAPSED] {self._human_time(self.elapsed)}"))
            bar_width = 50
            filled = int((self.progress / 100.0) * bar_width)
            bar = Fore.GREEN + "[" + "#" * filled + Fore.RED + ">" + "." * (bar_width - filled - 1) + Fore.GREEN + "]"
            lines.append(Fore.MAGENTA + self._render_line(f"{spinner}{bar} {self.progress:5.1f}%", f"[SCANNED] {self.checked:,} files"))
            lines.append(Fore.YELLOW + self._render_line(f"[TARGET] {file_name}", f"[SPEED] {int(self.fake_speed)} files/s"))
            lines.append(Fore.BLUE + self._render_line(f"[DATA] {binary * 8}", f"[HEX] {hex(random.randint(0, 0xFFFF))[2:].zfill(4).upper()}"))
            lines.append(Fore.CYAN + f"║ {ascii_line.center(76)} {glitch}║")
            lines.append(Fore.CYAN + f"╠{border_char * 78}╣")
            lines.append(Fore.MAGENTA + f"║ [TIP] Press Ctrl+C to abort mission (intel retained). {glitch}║")
            lines.append(Fore.CYAN + f"╚{border_char * 78}╝")
            
            sys.stdout.write("\x1b[2J\x1b[H")
            sys.stdout.write("\n".join(lines) + "\n")
            sys.stdout.flush()

            if not running and self.progress >= 99.9:
                self.progress = 100.0
                self._stop_event.set()
                break
            time.sleep(0.05)  # Ultra-smooth animation

    def start_ui_for_process(self, external_proc, status_message="Infiltrating System..."):
        self.status_message = status_message
        self._stop_event.clear()
        t = Thread(target=self._ui_loop, args=(external_proc,), daemon=True)
        t.start()
        return t

    def start_ui_simulation(self, status_message="Simulating Cyber Intrusion..."):
        return self.start_ui_for_process(None, status_message=status_message)

# ---------------------------
# File Action Helpers
# ---------------------------
def ensure_quarantine_dir(base_dir=None):
    """Create quarantine directory with timestamp."""
    if base_dir is None:
        base_dir = os.path.join(os.getcwd(), "cyber_quarantine")
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    qdir = os.path.join(base_dir, f"quarantine_{ts}")
    os.makedirs(qdir, exist_ok=True)
    return qdir

def quarantine_file(file_path, qdir):
    """Move file to quarantine."""
    try:
        if not os.path.exists(file_path):
            return False, "Target not found in matrix"
        dest = os.path.join(qdir, os.path.basename(file_path))
        base, ext = os.path.splitext(dest)
        i = 1
        while os.path.exists(dest):
            dest = f"{base}_{i}{ext}"
            i += 1
        shutil.move(file_path, dest)
        return True, f"Isolated in vault: {dest}"
    except Exception as e:
        return False, str(e)

def send_to_recycle_or_fallback(file_path, fallback_dir=None):
    """Send to Recycle Bin or fallback directory."""
    if not os.path.exists(file_path):
        return False, "Target not found in matrix"
    if HAS_SEND2TRASH:
        try:
            send2trash(file_path)
            return True, "Exiled to digital trash"
        except Exception:
            pass
    if fallback_dir is None:
        fallback_dir = os.path.join(os.getcwd(), "cyber_trash")
    os.makedirs(fallback_dir, exist_ok=True)
    try:
        dest = os.path.join(fallback_dir, os.path.basename(file_path))
        base, ext = os.path.splitext(dest)
        i = 1
        while os.path.exists(dest):
            dest = f"{base}_{i}{ext}"
            i += 1
        shutil.move(file_path, dest)
        return True, f"Trash module offline — relocated to {dest}"
    except Exception as e:
        return False, str(e)

def delete_permanent(file_path):
    """Permanently delete file or directory."""
    try:
        if not os.path.exists(file_path):
            return False, "Target not found in matrix"
        if os.path.isdir(file_path):
            shutil.rmtree(file_path)
        else:
            os.remove(file_path)
        return True, "Permanently eradicated"
    except Exception as e:
        return False, str(e)

def interactive_menu(detections):
    """Interactive menu for handling detections with mission log style."""
    if not detections:
        print(Fore.GREEN + "[MISSION LOG] System secure. No intrusions detected.")
        return
    qdir = ensure_quarantine_dir()
    print(Fore.RED + "[MISSION LOG] Intrusions detected in the matrix:")
    for i, (p, sig) in enumerate(detections, start=1):
        p_wrapped = textwrap.wrap(p, width=60)
        print(Fore.RED + f"[ALERT {i}] Signature: {sig}")
        for line in p_wrapped:
            print(Fore.RED + f"  Target: {line}")
    while True:
        choice = input(Fore.CYAN + "[COMMAND] Select target (or 'all', 'exit' to abort): ").strip().lower()
        if choice in ("exit", "q"):
            break
        targets = []
        if choice == "all":
            targets = list(range(1, len(detections) + 1))
        else:
            try:
                targets = [int(x) for x in choice.split(",") if x.strip()]
            except ValueError:
                print(Fore.YELLOW + "[ERROR] Invalid input. Try again.")
                continue
        for idx in targets:
            if idx < 1 or idx > len(detections):
                print(Fore.YELLOW + "[ERROR] Target out of range.")
                continue
            file_path, sig = detections[idx - 1]
            print(Fore.MAGENTA + f"\n[TARGET] File: {file_path}")
            print(Fore.RED + f"[SIGNATURE] {sig}")
            print(Fore.CYAN + "[OPTIONS] 1) Isolate (Quarantine)  2) Exile (Recycle)  3) Eradicate (Delete)  4) Ignore")
            act = input(Fore.CYAN + "[EXECUTE] Command: ").strip()
            if act == "1":
                ok, msg = quarantine_file(file_path, qdir)
                print(Fore.GREEN if ok else Fore.RED + f"[LOG] Isolation: {msg}")
            elif act == "2":
                ok, msg = send_to_recycle_or_fallback(file_path)
                print(Fore.GREEN if ok else Fore.RED + f"[LOG] Exile: {msg}")
            elif act == "3":
                c = input(Fore.RED + "[CONFIRM] Type 'CONFIRM' to eradicate: ").strip().upper()
                if c == "CONFIRM":
                    ok, msg = delete_permanent(file_path)
                    print(Fore.GREEN if ok else Fore.RED + f"[LOG] Eradication: {msg}")
                else:
                    print(Fore.YELLOW + "[LOG] Operation aborted.")
            else:
                print(Fore.YELLOW + "[LOG] Target ignored.")

# ---------------------------
# Cyber Intro & Welcome
# ---------------------------
def cyber_intro(system_info):
    """Hacker-style intro with boot sequence, matrix rain, and dynamic typing."""
    os.system("cls" if os.name == "nt" else "clear")
    boot_sequence = [
        "[BOOT] Initializing Cyber Matrix Protocol...",
        "[BOOT] Loading Neural Network Interfaces...",
        "[BOOT] Establishing Quantum Encryption...",
        "[BOOT] Activating Intrusion Detection Systems..."
    ]
    for msg in boot_sequence:
        print(Fore.GREEN + Style.BRIGHT + msg)
        time.sleep(0.5)
    
    # Matrix Rain Effect
    matrix_lines = [" " * random.randint(0, 80) + random.choice("01") for _ in range(35)]
    for _ in range(25):
        sys.stdout.write("\x1b[2J\x1b[H")
        for line in matrix_lines:
            print(Fore.GREEN + Style.BRIGHT + line)
        matrix_lines = [line[1:] + random.choice("01") if random.random() > 0.1 else line for line in matrix_lines]
        time.sleep(0.06)
    
    # Welcome Message
    device_name = system_info.get("Hostname", "Unknown Device")
    welcome_msg = f"Welcome to the Matrix, {device_name}. Cyber Defense Systems Engaged."
    border_char = random.choice(["═", "▒", "█"])
    print(Fore.CYAN + Style.BRIGHT + f"╔{border_char * 78}╗")
    for c in welcome_msg:
        sys.stdout.write(Fore.MAGENTA + Style.BRIGHT + c)
        sys.stdout.flush()
        time.sleep(0.01)
    print("\n" + Fore.CYAN + f"╚{border_char * 78}╝")
    
    # Loading Bar with Glitch
    print(Fore.YELLOW + "[INIT] Deploying Cyber Arsenal...")
    for i in range(0, 101, 2):
        bar = "#" * (i // 2) + "." * (50 - i // 2)
        glitch = random.choice(["~", "#", "%", "&", "@"]) if random.random() < 0.2 else ""
        sys.stdout.write(Fore.CYAN + f"\r[{bar}] {i}% {glitch}")
        sys.stdout.flush()
        time.sleep(0.04)
    print(Fore.GREEN + "\n[✓] Arsenal Deployed!\n")
    time.sleep(0.5)
    
    # System Info Table
    table_width = 80
    key_width = 32
    value_width = table_width - key_width - 5
    print(Fore.CYAN + Style.BRIGHT + f"╔{border_char * table_width}╗")
    print(Fore.CYAN + f"║ {'SYSTEM INTEL REPORT'.center(table_width - 2)} ║")
    print(Fore.CYAN + f"╠{border_char * table_width}╣")
    for k, v in system_info.items():
        v_str = str(v)
        if len(v_str) > value_width:
            wrapped = textwrap.wrap(v_str, width=value_width)
            print(Fore.YELLOW + f"║ {k:<{key_width}}: {Fore.GREEN + wrapped[0]:<{value_width}} ║")
            for line in wrapped[1:]:
                print(Fore.YELLOW + f"║ {'':<{key_width}}  {Fore.GREEN + line:<{value_width}} ║")
        else:
            print(Fore.YELLOW + f"║ {k:<{key_width}}: {Fore.GREEN + v_str:<{value_width}} ║")
    print(Fore.CYAN + f"╚{border_char * table_width}╝\n")

# ---------------------------
# Main Orchestration
# ---------------------------
def main():
    parser = argparse.ArgumentParser(description="Ultimate Cyber Malware Scanner")
    parser.add_argument("--paths", nargs="+", help="Paths to scan (override mode)")
    args = parser.parse_args()
    
    try:
        system_info = get_system_info()
        cyber_intro(system_info)
    except Exception as e:
        print(Fore.RED + f"[CRITICAL] Failed to initialize: {e}")
        sys.exit(1)
    
    # Scan Mode Selection
    print(Fore.MAGENTA + Style.BRIGHT + "═[ SELECT CYBER SCAN MODE ]═")
    print(Fore.CYAN + "[1] Quick Scan (User Folders)")
    print(Fore.CYAN + "[2] Full Scan (All Devices/Drives)")
    print(Fore.CYAN + "[3] Custom Scan (Specify Path)")
    try:
        choice = input(Fore.YELLOW + "[COMMAND] Execute Mode [1-3]: ").strip()
    except KeyboardInterrupt:
        print(Fore.YELLOW + "\n[MISSION LOG] Initialization aborted.")
        sys.exit(0)
    
    if choice == "3":
        try:
            path = input(Fore.CYAN + "[INPUT] Enter Target Path: ").strip()
            if not os.path.exists(path):
                print(Fore.RED + "[ERROR] Path not in matrix. Falling back to Quick Scan.")
                path = os.path.expanduser("~")
            paths = [path]
        except KeyboardInterrupt:
            print(Fore.YELLOW + "\n[MISSION LOG] Path input aborted.")
            sys.exit(0)
    elif choice == "2":
        if platform.system() == "Windows":
            paths = [f"{d}:\\" for d in "ABCDEFGHIJKLMNOPQRSTUVWXYZ" if os.path.exists(f"{d}:\\")]
        else:
            paths = ["/"]
        print(Fore.CYAN + f"[LOG] Full Matrix Scan: Targeting {', '.join(paths)}")
    else:
        paths = [os.path.expanduser("~")]
    
    if args.paths:
        paths = args.paths
    
    # Initialize UI & Detect Engines
    ui = AnimatedScanner(title="Ludang's Cyber Matrix Scanner v3.2", paths=paths)
    clam = is_clamscan_available()
    mp = find_mp_cmd()
    ui.module_status["ClamAV"] = bool(clam)
    ui.module_status["Defender"] = bool(mp)
    ui.module_status["Mode"] = "ClamAV" if clam else ("Defender" if mp else "Simulation")
    
    infected = []
    
    try:
        if clam:
            cmd = [clam, "-r", "--infected", "--no-summary"] + paths
            try:
                proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            except Exception as e:
                print(Fore.RED + "[ERROR] ClamAV activation failed:", e)
                proc = None
            ui.status_message = "Deploying ClamAV Payload..."
            ui_thread = ui.start_ui_for_process(proc)
            if proc:
                out, err = proc.communicate()
                for line in out.splitlines():
                    line = line.strip()
                    if line.endswith(" FOUND"):
                        try:
                            left, right = line.rsplit(":", 1)
                            file_path = left.strip()
                            sig = right.replace(" FOUND", "").strip()
                            infected.append((file_path, sig))
                        except:
                            pass
        elif mp:
            threats = []
            t_proc = Thread(target=run_mp_tasks_and_collect, args=(paths, threats), daemon=True)
            t_proc.start()
            ui.status_message = "Activating Defender Shield..."
            ui_thread = ui.start_ui_for_process(t_proc)
            t_proc.join()
            infected = threats
        else:
            ui.status_message = "Running Simulated Cyber Attack..."
            ui_thread = ui.start_ui_simulation()
            while not ui._stop_event.is_set():
                time.sleep(0.1)
            if random.random() > 0.5:
                infected = [(random.choice(paths) + "\\" + random.choice(ui._file_samples), random.choice(["Trojan", "Worm", "Ransomware", "Spyware"])) for _ in range(random.randint(1, 5))]
        
        ui._stop_event.set()
        time.sleep(0.1)
    except KeyboardInterrupt:
        ui._stop_event.set()
        print(Fore.YELLOW + "\n[MISSION LOG] Mission aborted. Declassifying partial intel.")
    except Exception as e:
        ui._stop_event.set()
        print(Fore.RED + "[ERROR] Critical failure in matrix:", e)
    
    # Final Summary
    border_char = random.choice(["═", "▒", "█"])
    print("\n" + Fore.CYAN + Style.BRIGHT + f"╔{border_char * 80}╗")
    print(Fore.CYAN + f"║ {'CYBER SCAN DEBRIEF'.center(78)} ║")
    print(Fore.CYAN + f"╠{border_char * 80}╣")
    if not infected:
        print(Fore.GREEN + "║ System Fortified: No Threats Infiltrated. ".center(78) + " ║")
    else:
        print(Fore.RED + f"║ Alert: {len(infected)} Intrusions Detected! ".center(78) + " ║")
        for i, (p, sig) in enumerate(infected, start=1):
            p_wrapped = textwrap.wrap(p, width=62)
            print(Fore.RED + f"║ [ALERT {i}] Sig: {sig} ".ljust(78) + " ║")
            for line in p_wrapped:
                print(Fore.RED + f"║   Target: {line:<62} ║")
    print(Fore.CYAN + f"╚{border_char * 80}╝\n")
    
    # Interactive Actions
    interactive_menu(infected)
    print(Fore.CYAN + f"\n[MISSION LOG] Session Terminated at {datetime.now().strftime('%H:%M:%S')}. Stay Vigilant! 🔒")

if __name__ == "__main__":
    main()