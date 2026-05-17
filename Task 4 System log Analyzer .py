#Sysyem LOG Analyzer and report generator
#Features : Load | Analyze | Search | Filter | Report |
          # Chart (matplotlib) | PDF Export | Live Monitor
import re, os, csv, sys, time, threading
from datetime import datetime
from collections import defaultdict

#Optional libraries
try:    import matplotlib.pyplot as plt;      HAS_PLT = True
except: HAS_PLT = False

try:    from fpdf import FPDF;                HAS_PDF = True
except: HAS_PDF = False

#Colors
R="\033[91m"; Y="\033[93m"; G="\033[92m"; C="\033[96m"
B="\033[1m";  D="\033[2m";  E="\033[0m"

def red(t):  return f"{R}{t}{E}"
def yel(t):  return f"{Y}{t}{E}"
def grn(t):  return f"{G}{t}{E}"
def cyn(t):  return f"{C}{t}{E}"
def bld(t):  return f"{B}{t}{E}"
def dim(t):  return f"{D}{t}{E}"

#  Global state
log_entries  = []
current_file = None
monitor_stop = threading.Event()

# Regex (compiled once)
TS_PAT  = re.compile(r'(\d{4}-\d{2}-\d{2}[\sT]\d{2}:\d{2}:\d{2})')
LVL_PAT = re.compile(r'\b(ERROR|WARNING|WARN|INFO|DEBUG|CRITICAL)\b', re.I)

CMAP = {"ERROR":red,"CRITICAL":red,"WARNING":yel,"INFO":grn,"DEBUG":cyn}
HEX  = {"ERROR":"#ff4d4d","CRITICAL":"#cc0000","WARNING":"#ffcc00",
         "INFO":"#33cc66","DEBUG":"#33ccff","UNKNOWN":"#888888"}

#  HELPER: parse one raw line into a dict

def _parse(raw, lineno):
    m   = LVL_PAT.search(raw)
    lvl = m.group(1).upper() if m else "UNKNOWN"
    if lvl == "WARN": lvl = "WARNING"
    tm  = TS_PAT.search(raw)
    return {"lineno":lineno, "raw":raw, "level":lvl,
            "timestamp": tm.group(0) if tm else None}

#  1. LOAD LOG FILE
def load_log_file():
    global log_entries, current_file
    path = input(cyn("\n  Log file path (.txt/.log): ")).strip()
    if not path:                                    print(red("✗ No path given.")); return
    if not os.path.exists(path):                   print(red(f"✗ Not found: {path}")); return
    if os.path.splitext(path)[1] not in(".txt",".log"):
                                                   print(red("✗ Only .txt/.log allowed.")); return
    if os.path.getsize(path) == 0:                 print(red("✗ File is empty.")); return

    try:
        with open(path, encoding='utf-8', errors='replace') as f:
            log_entries = [_parse(l.rstrip('\n'), i)
                           for i, l in enumerate(f, 1) if l.strip()]
    except PermissionError:   print(red("✗ Permission denied.")); return
    except Exception as ex:   print(red(f"✗ Error: {ex}")); return

    current_file = path
    print(grn(f"\n  ✔ {len(log_entries)} entries loaded from '{os.path.basename(path)}'"))


#  2. ANALYZE LOGS

def analyze_logs():
    if not _check(): return
    counts, samples = defaultdict(int), defaultdict(list)
    for e in log_entries:
        counts[e["level"]] += 1
        if e["timestamp"] and len(samples[e["level"]]) < 2:
            samples[e["level"]].append(e["timestamp"])

    total = sum(counts.values())
    print(bld("\n  ┌─── Analysis ─────────────────────────────────┐"))
    print(f"  │  Total : {bld(str(total))}  |  File : {dim(os.path.basename(current_file))}")
    print("  │")
    for lvl in ["ERROR","CRITICAL","WARNING","INFO","DEBUG","UNKNOWN"]:
        if lvl in counts:
            bar = "█" * min(counts[lvl], 35)
            pct = counts[lvl] / total * 100
            print(f"  │  {CMAP.get(lvl,dim)(f'{lvl:<10}')} {bar:<35} {counts[lvl]:>4} ({pct:.0f}%)")
    print("  └──────────────────────────────────────────────┘")
    print(bld("\n  Sample timestamps:"))
    for lvl, ts in samples.items():
        print(f"{CMAP.get(lvl,dim)(lvl)}: {', '.join(ts)}")

#  3. SEARCH LOGS
def search_logs():
    if not _check(): return
    kw = input(cyn("  Keyword: ")).strip()
    if not kw: print(red("  ✗ Empty.")); return
    res = [e for e in log_entries if re.search(re.escape(kw), e["raw"], re.I)]
    print(bld(f"\n  '{kw}' → {len(res)} match(es)\n"))
    _show(res[:50])
    if len(res) > 50: print(dim(f"  ...+{len(res)-50} more"))

#  4. FILTER LOGS

def filter_logs():
    if not _check(): return
    print(bld("\n  1. By Level   2. By Date   3. Back"))
    c = input(cyn("  Choice: ")).strip()
    if c == "1":
        lvl = input(cyn("  Level (ERROR/WARNING/INFO/DEBUG/CRITICAL): ")).upper().strip()
        if lvl == "WARN": lvl = "WARNING"
        res, label = [e for e in log_entries if e["level"]==lvl], f"Level={lvl}"
    elif c == "2":
        dt  = input(cyn("  Date (e.g. 2024-01-15): ")).strip()
        res, label = [e for e in log_entries if e["timestamp"] and dt in e["timestamp"]], f"Date={dt}"
    else: return
    print(bld(f"\n  {label} → {len(res)} result(s)\n"))
    _show(res[:50])
    if len(res) > 50: print(dim(f"  ...+{len(res)-50} more"))

#  5. GENERATE REPORT  (TXT / CSV)

def generate_report():
    if not _check(): return
    counts = defaultdict(int)
    for e in log_entries: counts[e["level"]] += 1
    total = len(log_entries)
    now   = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    lines = ["="*52,"  SYSTEM LOG ANALYSIS REPORT",
             f"  Generated : {now}",
             f"  File      : {current_file or 'N/A'}","="*52,"",
             "SUMMARY","-"*30,
             f"  Total Entries  : {total}",
             f"  Total Errors   : {counts['ERROR']+counts['CRITICAL']}",
             f"  Total Warnings : {counts['WARNING']}",
             f"  Total Info     : {counts['INFO']}",
             "","LEVEL BREAKDOWN","-"*30,
    ] + [f"  {l:<12}: {c:>4}  ({c/total*100:.0f}%)" for l,c in sorted(counts.items())] + [
             "","TOP ERRORS (first 8)","-"*30,
    ] + [f"  [L{e['lineno']}] {e['raw'][:85]}"
         for e in log_entries if e["level"] in ("ERROR","CRITICAL")][:8] + [
             "","="*52,"  End of Report","="*52]

    print(bld("\n  ── Report Preview ─────────────────────────────"))
    for l in lines: print(f"  {l}")

    if input(cyn("\n  Save? [y/n]: ")).lower() != 'y': return
    fmt = input(cyn("  [1] TXT   [2] CSV: ")).strip()
    ts  = datetime.now().strftime('%Y%m%d_%H%M%S')

    if fmt == "1":
        fn = (input(cyn(f"  Filename (default report_{ts}.txt): ")).strip() or f"report_{ts}") + ".txt"
        fn = fn.replace(".txt.txt",".txt")
        try: open(fn,'w').write('\n'.join(lines)); print(grn(f"  ✔ Saved: {fn}"))
        except Exception as ex: print(red(f"  ✗ {ex}"))

    elif fmt == "2":
        fn = (input(cyn(f"  Filename (default report_{ts}.csv): ")).strip() or f"report_{ts}") + ".csv"
        fn = fn.replace(".csv.csv",".csv")
        try:
            with open(fn,'w',newline='') as f:
                w = csv.writer(f)
                w.writerow(["Generated",now]); w.writerow(["File",current_file])
                w.writerow([]); w.writerow(["Level","Count","%"])
                for l,c in sorted(counts.items()): w.writerow([l,c,f"{c/total*100:.0f}%"])
            print(grn(f"  ✔ Saved: {fn}"))
        except Exception as ex: print(red(f"  ✗ {ex}"))

#  6. VISUAL CHART  (Bonus - matplotlib)

def visual_chart():
    if not _check(): return
    if not HAS_PLT: print(red("  ✗ Run: pip install matplotlib")); return

    counts = defaultdict(int)
    for e in log_entries: counts[e["level"]] += 1
    lvls = list(counts.keys()); vals = [counts[l] for l in lvls]
    cols = [HEX.get(l,"#aaa") for l in lvls]

    fig, (ax1,ax2) = plt.subplots(1,2,figsize=(11,5))
    fig.patch.set_facecolor("#1a1a2e")
    for ax in (ax1,ax2): ax.set_facecolor("#16213e")

    bars = ax1.bar(lvls, vals, color=cols, edgecolor="#ffffff22")
    ax1.set_title("Log Level Distribution", color="white")
    ax1.tick_params(colors="white"); ax1.set_ylabel("Count",color="#aaa")
    [ax1.text(b.get_x()+b.get_width()/2, b.get_height()+.1,
              str(v), ha='center', color='white') for b,v in zip(bars,vals)]

    ax2.pie(vals, labels=lvls, colors=cols, autopct='%1.0f%%',
            textprops={'color':'white'}, wedgeprops={'edgecolor':'#1a1a2e'})
    ax2.set_title("Share (%)", color="white")

    fn = f"chart_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    plt.tight_layout()
    plt.savefig(fn, dpi=130, bbox_inches='tight', facecolor=fig.get_facecolor())
    print(grn(f"\n  ✔ Chart saved: {fn}"))
    plt.show()

#  7. EXPORT PDF  (Bonus - fpdf2)
def export_pdf():
    if not _check(): return
    if not HAS_PDF: print(red("  ✗ Run: pip install fpdf2")); return

    counts = defaultdict(int)
    for e in log_entries: counts[e["level"]] += 1
    total = len(log_entries)
    now   = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    fn    = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

    pdf = FPDF(); pdf.add_page()
    pdf.set_font("Helvetica","B",16)
    pdf.cell(0,10,"System Log Analysis Report",ln=True,align="C")
    pdf.set_font("Helvetica",size=10)
    pdf.cell(0,7,f"Generated: {now}  |  File: {os.path.basename(current_file or 'N/A')}",ln=True,align="C")
    pdf.ln(5)

    pdf.set_font("Helvetica","B",12); pdf.cell(0,8,"Summary",ln=True)
    pdf.set_font("Helvetica",size=10)
    for label,val in [("Total Entries",total),
                      ("Errors",counts['ERROR']+counts['CRITICAL']),
                      ("Warnings",counts['WARNING']),("Info",counts['INFO'])]:
        pdf.cell(60,7,label); pdf.cell(0,7,str(val),ln=True)
    pdf.ln(3)

    pdf.set_font("Helvetica","B",12); pdf.cell(0,8,"Level Breakdown",ln=True)
    pdf.set_font("Helvetica",size=10)
    for lvl,cnt in sorted(counts.items()):
        pdf.cell(50,7,lvl); pdf.cell(30,7,str(cnt)); pdf.cell(0,7,f"{cnt/total*100:.0f}%",ln=True)
    pdf.ln(3)

    pdf.set_font("Helvetica","B",12); pdf.cell(0,8,"Top Errors",ln=True)
    pdf.set_font("Helvetica",size=9)
    for e in [x for x in log_entries if x["level"] in ("ERROR","CRITICAL")][:8]:
        txt = f"[L{e['lineno']}] {e['raw'][:40]}"
        pdf.cell(0, 6, txt[:60], ln=True)

    pdf.output(fn)
    print(grn(f"\n  ✔ PDF saved: {fn}"))

#  8. REAL-TIME MONITOR  (Bonus - tail style)
def monitor_logs():
    path = input(cyn("  File to monitor (.txt/.log): ")).strip()
    if not os.path.exists(path): print(red("  ✗ File not found.")); return

    print(grn(f"  ✔ Monitoring '{path}' — press Enter to stop\n"))
    monitor_stop.clear()

    def _tail():
        with open(path, encoding='utf-8', errors='replace') as f:
            f.seek(0, 2)                    # jump to end
            while not monitor_stop.is_set():
                line = f.readline()
                if not line: time.sleep(0.4); continue
                line = line.rstrip('\n')
                if not line.strip(): continue
                e  = _parse(line, "NEW")
                fn = CMAP.get(e["level"], dim)
                ts = f"[{e['timestamp']}] " if e["timestamp"] else ""
                lvl_tag = f"[{e['level']}]"
                print(f"  {fn(lvl_tag)} {ts}{line[:105]}")

    threading.Thread(target=_tail, daemon=True).start()
    input()                                 # wait for Enter
    monitor_stop.set()
    print(dim("  ■ Monitor stopped."))


#  HELPERS

def _check():
    if not log_entries:
        print(yel("  ⚠ Load a log file first (Option 1)."))
        return False
    return True

def _show(entries):
    for e in entries:
        fn = CMAP.get(e["level"], dim)
        ts = f"[{e['timestamp']}] " if e["timestamp"] else ""
        lvl_tag = f"[{e['level']:<8}]"
        print(f"  {dim(str(e['lineno']).rjust(4))}  {fn(lvl_tag)} {ts}{e['raw'][:105]}")

def _sample_log():
    if os.path.exists("sample_logs.log"): return
    logs = [
        "2024-01-15 08:00:01 INFO  App started successfully",
        "2024-01-15 08:01:05 INFO  DB connected at localhost:5432",
        "2024-01-15 08:02:14 WARNING  Memory usage high: 78%",
        "2024-01-15 08:03:30 ERROR  Config file not found: /etc/app/config.yaml",
        "2024-01-15 08:05:20 DEBUG  Cache hit ratio: 94.3%",
        "2024-01-15 08:06:45 WARNING  Slow query detected: 3.4s",
        "2024-01-15 08:07:10 ERROR  API timeout: payments.service.io",
        "2024-01-15 08:09:55 CRITICAL  Disk usage 98% on /dev/sda1",
        "2024-01-15 08:10:30 ERROR  NullPointerException in thread-3",
        "2024-01-15 08:12:15 WARNING  SSL certificate expires in 7 days",
        "2024-01-15 08:14:00 ERROR  Invalid login from 203.0.113.42",
        "2024-01-15 08:18:00 INFO  Health check passed",
        "2024-01-15 08:19:22 ERROR  DB connection lost",
        "2024-01-15 08:20:05 INFO  DB reconnected successfully",
        "2024-01-15 08:23:00 INFO  Shutdown complete",
    ]
    open("sample_logs.log","w").write('\n'.join(logs))
    print(dim("  ℹ  sample_logs.log created — use it to test!\n"))

#  BANNER + MENU

def _banner():
    print(f"""\n{C}{B}
  ╔══════════════════════════════════════════════════════╗
  ║      🐍 System Log Analyzer & Report Generator       ║
  ║           HK— Task 4                                 ║
  ╚══════════════════════════════════════════════════════╝
{E}{D}  Maryam!! | Python Internship 2026(HK){E}""")

def _menu():
    fs = grn(f"● {os.path.basename(current_file)}") if current_file else red("○ No file loaded")
    es = dim(f"({len(log_entries)} entries)") if log_entries else ""
    print(f"""
  {fs} {es}
  {bld("─"*44)}
  {cyn("1.")} Load Log File        {cyn("5.")} Generate Report
  {cyn("2.")} Analyze Logs         {cyn("6.")} Visual Chart  📊
  {cyn("3.")} Search Logs          {cyn("7.")} Export PDF    📄
  {cyn("4.")} Filter Logs          {cyn("8.")} Live Monitor  👁
  {red("9.")} Exit
  {bld("─"*44)}""")
#  MAIN

def main():
    _banner()
    _sample_log()
    actions = {
        "1": load_log_file, "2": analyze_logs,  "3": search_logs,
        "4": filter_logs,   "5": generate_report,"6": visual_chart,
        "7": export_pdf,    "8": monitor_logs,
    }
    while True:
        _menu()
        c = input(cyn("  → Option: ")).strip()
        if c == "9":   print(grn("\n  Goodbye! Stay sharp 🚀\n")); sys.exit()
        elif c in actions: actions[c]()
        else: print(red("  ✗ Enter 1–9"))
        input(dim("\n  [Enter to continue...]"))

if __name__ == "__main__":
    main()