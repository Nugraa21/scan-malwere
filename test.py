# scan.py
"""
Ludang's Cyber Malware Scanner v2.5
By: Ludang Prasetyo Nugroho (nugra.online)
-----------------------------------------
- Menampilkan info hardware lengkap (CPU, RAM, GPU, Disk, Network)
- Mode Scan (Quick, Full, Custom)
- Animasi Cyber UI
- Simulasi deteksi malware & folder mencurigakan
- Opsi karantina / hapus / lewati
"""

import os
import sys
import time
import platform
import shutil
import subprocess
import socket
import random
import psutil
from datetime import datetime
from threading import Thread, Event
from itertools import cycle
from colorama import Fore, Style, init

try:
    from send2trash import send2trash
    HAS_TRASH = True
except:
    HAS_TRASH = False

init(autoreset=True)


# =======================
# SYSTEM INFORMATION
# =======================
def get_system_info():
    info = {}
    try:
        info["OS"] = f"{platform.system()} {platform.release()}"
        info["Python"] = platform.python_version()
        info["CPU"] = platform.processor() or "Unknown"
        info["Cores"] = psutil.cpu_count(logical=True)
        info["RAM Total"] = f"{psutil.virtual_memory().total / (1024 ** 3):.2f} GB"
        info["RAM Used"] = f"{psutil.virtual_memory().used / (1024 ** 3):.2f} GB"
        info["Disk Total"] = f"{psutil.disk_usage('/').total / (1024 ** 3):.2f} GB"
        info["Disk Used"] = f"{psutil.disk_usage('/').used / (1024 ** 3):.2f} GB"
        info["CPU Usage"] = f"{psutil.cpu_percent(interval=0.5)}%"
        info["Uptime"] = f"{round(time.time() - psutil.boot_time()) // 3600} hrs"
        info["Processes"] = len(psutil.pids())
        info["Hostname"] = socket.gethostname()
        info["IP"] = socket.gethostbyname(socket.gethostname())

        # GPU info (Windows)
        try:
            gpu_cmd = subprocess.run(["wmic", "path", "win32_VideoController", "get", "name"],
                                     capture_output=True, text=True)
            lines = [l.strip() for l in gpu_cmd.stdout.splitlines() if l.strip()]
            if len(lines) > 1:
                info["GPU"] = lines[1]
        except:
            info["GPU"] = "N/A"

    except Exception as e:
        info["Error"] = str(e)
    return info


# =======================
# CYBER INTRO
# =======================
def cyber_intro():
    os.system("cls" if os.name == "nt" else "clear")
    print(Fore.CYAN + "=" * 70)
    title = "⚡ LUDANG'S CYBER MALWARE SCANNER ⚡"
    for c in title:
        sys.stdout.write(Fore.GREEN + Style.BRIGHT + c)
        sys.stdout.flush()
        time.sleep(0.03)
    print("\n" + Fore.CYAN + "=" * 70)
    print(Fore.YELLOW + "Initializing system modules...")
    for i in range(0, 101, 4):
        bar = "=" * (i // 4) + "-" * ((100 - i)//4)
        sys.stdout.write(Fore.CYAN + f"\r[{bar}] {i}%")
        sys.stdout.flush()
        time.sleep(0.05)
    print(Fore.GREEN + "\n[✓] Initialization complete!\n")
    time.sleep(0.5)


# =======================
# ANIMATED SCAN
# =======================
class AnimatedScanner:
    def __init__(self):
        self._stop = Event()
        self.spinner = cycle("⣾⣷⣯⣟⡿⢿⣻⣽")
        self.progress = 0

    def start(self):
        t = Thread(target=self._loop, daemon=True)
        t.start()
        return t

    def stop(self):
        self._stop.set()

    def _loop(self):
        files = ["system32.dll", "chrome_cache.dat", "kernel32.sys", "winupdate.tmp", "unknown.bin"]
        while not self._stop.is_set():
            spinner = next(self.spinner)
            fake = random.choice(files)
            self.progress = min(100, self.progress + random.uniform(0.5, 2.0))
            bar = "=" * int(self.progress // 2) + "-" * (50 - int(self.progress // 2))
            sys.stdout.write("\x1b[2J\x1b[H")
            print(Fore.CYAN + "=" * 70)
            print(Fore.MAGENTA + Style.BRIGHT + "SCANNING FOR MALWARE...".center(70))
            print(Fore.CYAN + "=" * 70)
            print(Fore.YELLOW + f"File: {fake}")
            print(Fore.CYAN + f"[{bar}] {self.progress:5.1f}% {spinner}")
            print(Fore.GREEN + f"Checked: {int(self.progress*120)} files | Time: {int(self.progress)}s")
            print(Fore.BLUE + "Analyzing: registry, memory, startup items...")
            time.sleep(0.1)
        print(Fore.GREEN + "\n[✓] Scan completed!\n")


# =======================
# THREAT MANAGEMENT
# =======================
def ensure_quarantine():
    qdir = os.path.join(os.getcwd(), "quarantine_" + datetime.now().strftime("%Y%m%d_%H%M%S"))
    os.makedirs(qdir, exist_ok=True)
    return qdir

def quarantine_file(file_path, qdir):
    try:
        if os.path.exists(file_path):
            shutil.move(file_path, os.path.join(qdir, os.path.basename(file_path)))
            print(Fore.GREEN + f"[+] Quarantined → {file_path}")
        else:
            print(Fore.YELLOW + f"File not found: {file_path}")
    except Exception as e:
        print(Fore.RED + f"Failed to quarantine: {e}")

def delete_file(file_path):
    try:
        if HAS_TRASH:
            send2trash(file_path)
        else:
            os.remove(file_path)
        print(Fore.GREEN + f"[✓] Deleted → {file_path}")
    except Exception as e:
        print(Fore.RED + f"Failed to delete: {e}")


# =======================
# MAIN
# =======================
def main():
    cyber_intro()
    info = get_system_info()

    print(Fore.CYAN + "📊 SYSTEM INFORMATION")
    print(Fore.CYAN + "-" * 70)
    for k, v in info.items():
        print(Fore.YELLOW + f"{k:<15}: " + Fore.GREEN + str(v))
    print(Fore.CYAN + "-" * 70)

    print(Fore.MAGENTA + "\n=== SCAN MODE SELECTION ===")
    print("1. Quick Scan (Documents, Downloads)")
    print("2. Full Scan (All drives)")
    print("3. Custom Scan (Choose folder)")
    choice = input(Fore.YELLOW + "Choose [1-3]: ").strip()

    if choice == "3":
        path = input(Fore.CYAN + "Enter path: ").strip()
        if not os.path.exists(path):
            print(Fore.RED + "Path not found. Using Quick Scan.")
            path = os.path.expanduser("~")
    elif choice == "2":
        path = "C:\\"
    else:
        path = os.path.expanduser("~")

    print(Fore.CYAN + f"\n[!] Scanning path: {path}")
    print(Fore.CYAN + "-" * 70)

    scan = AnimatedScanner()
    scan.start()
    time.sleep(random.randint(15, 25))
    scan.stop()
    time.sleep(1)

    # Fake detections
    detections = [
        (r"C:\Users\User\Downloads\virus_sample.exe", "Trojan:Win32/Agent"),
        (r"C:\Temp\suspicious.tmp", "Worm:Win64/AutoRun"),
        (r"C:\Windows\system32\driverX.tmp", "Backdoor:Win32/Cobalt")
    ] if random.random() > 0.4 else []

    suspicious = [
        "C:\\Users\\Public\\logs\\temp_config\\",
        "C:\\Temp\\hidden_folder\\",
        "C:\\Users\\User\\AppData\\Roaming\\unknown_app\\"
    ]

    print(Fore.CYAN + "\n🔎 SCAN RESULTS")
    print(Fore.CYAN + "-" * 70)
    if detections:
        for f, sig in detections:
            print(Fore.RED + f"[!] {sig} found in {f}")
    else:
        print(Fore.GREEN + "No malware detected. System clean ✅")

    print(Fore.CYAN + "\n⚠️  SUSPICIOUS FOLDERS DETECTED:")
    for s in suspicious:
        print(Fore.YELLOW + f"→ {s}")

    if detections:
        qdir = ensure_quarantine()
        for f, sig in detections:
            print(Fore.CYAN + f"\nFile: {f}")
            print(Fore.RED + f"Threat: {sig}")
            act = input("1) Quarantine  2) Delete  3) Skip > ").strip()
            if act == "1":
                quarantine_file(f, qdir)
            elif act == "2":
                delete_file(f)
            else:
                print("Skipped.")

    print(Fore.CYAN + "\n[✓] Scan session finished at", datetime.now().strftime("%H:%M:%S"))
    print(Fore.GREEN + "Stay protected, Ludang 🔒")


if __name__ == "__main__":
    main()
