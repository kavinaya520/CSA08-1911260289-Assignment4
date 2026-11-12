"""Task 1: mess-bill totals - the original script (logic kept) and the repaired design."""
import json
import os
import sys
import tempfile
import time
import tracemalloc
from decimal import Decimal, InvalidOperation


def original_script_total(path):
    """The office script, with only the hard-coded path replaced by a parameter so that it can be run here."""
    f = open(path)
    data = f.read()
    total = 0
    report = ""
    for line in data.split("\n"):
        try:
            parts = line.split(",")
            total = total + int(parts[2])
            report = report + parts[1] + " " + parts[2] + "\n"
        except:
            pass
    return report, total


def mess_total(filename):
    """Repaired design. Returns (total as Decimal, report lines, rejected [(line number, text, reason)])."""
    total = Decimal("0")
    report, rejected = [], []
    with open(filename, encoding="utf-8") as f:           # closed automatically, even after an error
        for number, line in enumerate(f, 1):                # one line in memory at a time
            line = line.strip()
            if not line:
                continue                                    # blank line (for example the last one): not an error
            parts = [p.strip() for p in line.split(",")]
            if len(parts) != 3:
                rejected.append((number, line, f"expected 3 fields, found {len(parts)}"))
                continue
            try:
                amount = Decimal(parts[2])                  # exact, keeps the paise
            except InvalidOperation:
                rejected.append((number, line, f"amount {parts[2]!r} is not a number"))
                continue
            total += amount
            report.append(f"{parts[1]} {amount}")
    return total, report, rejected


DEFENCE = ("My version is safer for 50,000 lines because it reads one line at a time, so memory stays small, and closes the file "
           "automatically with a with statement. It keeps the paise by using Decimal, catches only the expected errors, and "
           "records every rejected line with its line number, so no bill disappears silently. The file name is a parameter, "
           "so it works on any file, and a missing file raises a clear FileNotFoundError.")

if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "mess_oct.txt")
    print("Original script on mess_oct.txt")
    rep, tot = original_script_total(path)
    print(rep + f"Total {tot}")
    print("Repaired script on mess_oct.txt")
    total, report, rejected = mess_total(path)
    print("\n".join(report))
    print("Total", total)
    print("Rejected lines:")
    for number, text, reason in rejected:
        print(f"  line {number}: {text!r} -> {reason}")
    print(f"\nThe original silently lost {total - tot} rupees (1250.50 and 2100.75 failed int() and were swallowed by 'except: pass')")
    print("Defence word count:", len(DEFENCE.split()), "(limit 100)")
    assert len(DEFENCE.split()) <= 100
    try:
        mess_total("no_such_file.txt")
    except FileNotFoundError as err:
        print("Missing file ->", type(err).__name__ + ":", err)

    print("\nAlternative: f.read() / f.readlines() against iterating the file, 50,000 lines")
    tmp = os.path.join(tempfile.gettempdir(), "mess_50000.txt")
    with open(tmp, "w", encoding="utf-8") as f:
        for i in range(50_000):
            f.write(f"{192300000 + i},Student {i},{1000 + i % 900}.{i % 100:02d}\n")
    size = os.path.getsize(tmp)

    def via_read():
        with open(tmp, encoding="utf-8") as f:
            return sum(Decimal(l.split(",")[2]) for l in f.read().split("\n") if l)

    def via_readlines():
        with open(tmp, encoding="utf-8") as f:
            return sum(Decimal(l.split(",")[2]) for l in f.readlines())

    def via_iteration():
        with open(tmp, encoding="utf-8") as f:
            return sum(Decimal(l.split(",")[2]) for l in f)

    rows, answers = [], set()
    print(f"  file size {size:,} bytes")
    print(f"  {'method':<16} {'time (s)':>9} {'peak memory (KB)':>17}")
    for name, func in (("f.read()", via_read), ("f.readlines()", via_readlines), ("iteration", via_iteration)):
        start = time.perf_counter(); answers.add(func()); t = time.perf_counter() - start
        tracemalloc.start(); func(); peak = tracemalloc.get_traced_memory()[1] / 1024; tracemalloc.stop()
        print(f"  {name:<16} {t:>9.4f} {peak:>17,.0f}")
        rows.append({"method": name, "time": round(t, 4), "peak_kb": round(peak)})
    print("  all three give the same total:", len(answers) == 1)

    start = time.perf_counter(); text = ""
    for i in range(50_000):
        text = text + f"Student {i} 1000.00\n"
    t_plus = time.perf_counter() - start
    start = time.perf_counter(); "".join(f"Student {i} 1000.00\n" for i in range(50_000)); t_join = time.perf_counter() - start
    print(f"  building the 50,000-line report: repeated + {t_plus:.4f} s | list/join {t_join:.4f} s")
    os.remove(tmp)
    json.dump({"lost": str(total - tot), "total": str(total), "rejected": len(rejected), "size": size, "rows": rows,
               "t_plus": round(t_plus, 4), "t_join": round(t_join, 4), "defence_words": len(DEFENCE.split())}, open("results.json", "w"), indent=1)
