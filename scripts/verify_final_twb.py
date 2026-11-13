import subprocess
import time
import json
import os
import sys

TARGET = r"C:\Users\HP\Desktop\Customer 360 and Marketing Attribution Platform\exports\tableau\Customer360_Analytics.twb"
EXE = r"C:\Program Files\Tableau\Tableau Public 2026.3\bin\Tabpublic.exe"
LOG_FILE = os.path.expanduser(r"~\Documents\My Tableau Repository\Logs\log_1.txt")

print(f"Launching Tableau Public with target workbook:\n{TARGET}")
p = subprocess.Popen([EXE, os.path.abspath(TARGET)])
pid = p.pid
print(f"Process started with PID: {pid}. Waiting 12 seconds for workbook load...")
time.sleep(12)
p.kill()
print("Process terminated. Parsing log_1.txt...")

fatal_error = False
extract_warning = False
dom_ok = False
filter_warnings = []
rendered_dashboards = set()

log_dir = os.path.expanduser(r"~\Documents\My Tableau Repository\Logs")
for log_file in os.listdir(log_dir):
    if not log_file.endswith('.txt'):
        continue
    log_path = os.path.join(log_dir, log_file)
    with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            try:
                d = json.loads(line)
                if d.get('pid') == pid:
                    k = d.get('k')
                    if 'show-detailed-error-dialog' in line:
                        msg = d.get('v', {}).get('args', '')
                        if 'must use extracts' in msg:
                            extract_warning = True
                        elif 'Errors occurred while trying to load' in msg:
                            fatal_error = True
                            print(f"  [FATAL ERROR]: {msg}")
                    if 'Error parsing filter' in line:
                        filter_warnings.append(d.get('v', ''))
                    if k == 'end-workbook-dom-loader.load-workbook-dom':
                        rk = d.get('a', {}).get('rk')
                        print(f"  [DOM LOADER]: {rk}")
                        if rk == 'ok':
                            dom_ok = True
                    if k == 'get-dashboard-current-layout':
                        dash = d.get('v', {}).get('dash')
                        if dash:
                            rendered_dashboards.add(dash)
            except:
                pass

print("\n" + "="*50)
print("FINAL TABLEAU PUBLIC VERIFICATION SUMMARY:")
print("="*50)
print(f"DOM Loader Status : {'OK (Workbook DOM loaded successfully)' if dom_ok else 'FAILED'}")
print(f"Fatal Errors      : {'None (Zero errors)' if not fatal_error else 'FATAL LOAD ERROR DETECTED'}")
print(f"Filter Warnings   : {len(filter_warnings)} ({filter_warnings})")
print(f"Extract Notice    : {'Present (Expected for live CSVs in Tableau Public)' if extract_warning else 'None'}")
print(f"Dashboards Loaded : {list(rendered_dashboards)}")

if dom_ok and not fatal_error and len(filter_warnings) == 0:
    print("\n>>> OVERALL RESULT: VERIFIED SUCCESS! Zero errors and zero filter warnings.")
    sys.exit(0)
else:
    print("\n>>> OVERALL RESULT: VERIFICATION FAILED.")
    sys.exit(1)

