"""Task 2: monthly attendance from daily biometric files - one pass over every file, counts in a dictionary."""
import csv
import sys
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

HERE = Path(__file__).resolve().parent


def parse(line):
    """'192311001,2026-10-01,P' -> (regno, date, status); ValueError for a damaged line."""
    parts = [p.strip() for p in line.split(",")]
    if len(parts) != 3:
        raise ValueError(f"expected 3 fields, found {len(parts)}")
    if parts[2] not in ("P", "A"):
        raise ValueError(f"invalid status {parts[2]!r}")
    return tuple(parts)


def process_month(folder, trace=False):
    """Read every daily file once. Returns (counts, damaged) where counts[regno] = [present, absent]."""
    counts, damaged = {}, []
    for path in sorted(Path(folder).glob("*.txt")):             # all daily files of the month, in order
        with open(path, "r", encoding="utf-8") as f:            # r: read only, utf-8: fixed encoding
            for number, line in enumerate(f, 1):                # iteration: one line at a time
                line = line.strip()
                if not line:
                    continue
                try:
                    regno, date, status = parse(line)
                except ValueError as err:
                    damaged.append((path.name, number, str(err), line))
                    if trace:
                        print(f"  {path.name} line {number}: {line!r:30} -> DAMAGED ({err})")
                    continue
                counts.setdefault(regno, [0, 0])[0 if status == "P" else 1] += 1
                if trace:
                    print(f"  {path.name} line {number}: {line!r:30} -> counts[{regno}] = {counts[regno]}")
    return counts, damaged


def percent(present, absent):
    """Attendance percentage with 2 decimals (half up)."""
    total = present + absent
    return (Decimal(present) * 100 / total).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP) if total else Decimal("0.00")


def write_reports(counts, damaged, out_dir):
    """Write the three output files (mode w: a new run replaces the old reports)."""
    out = Path(out_dir)
    out.mkdir(exist_ok=True)
    with open(out / "attendance_report.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["regno", "present", "total", "percent"])
        for regno in sorted(counts):
            p, a = counts[regno]
            writer.writerow([regno, p, p + a, percent(p, a)])
    low = [(r, percent(*counts[r])) for r in sorted(counts) if percent(*counts[r]) < 75]
    with open(out / "below75.txt", "w", encoding="utf-8") as f:
        for regno, pc in low:
            f.write(f"{regno} {pc}\n")
    with open(out / "damaged.log", "w", encoding="utf-8") as f:
        for name, number, reason, text in damaged:
            f.write(f"{name}:{number}: {reason}: {text}\n")
    return low


if __name__ == "__main__":
    if "--trace" in sys.argv:
        print("Trace of one small file with a damaged line (data/trace)")
        counts, damaged = process_month(HERE / "data" / "trace", trace=True)
        print("  final counts:", counts, "| damaged:", len(damaged))
    else:
        counts, damaged = process_month(HERE / "data" / "2026-10")
        low = write_reports(counts, damaged, HERE / "out")
        print("Attendance report (out/attendance_report.csv)")
        for regno in sorted(counts):
            p, a = counts[regno]
            print(f"  {regno}: present {p} of {p + a} = {percent(p, a)}%")
        print("Below 75% (out/below75.txt):", [f"{r} {pc}" for r, pc in low])
        print("Damaged lines (out/damaged.log):")
        for name, number, reason, text in damaged:
            print(f"  {name} line {number}: {reason}: {text!r}")
