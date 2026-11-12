"""Task 2 alternative: re-read all files for every student  vs  read every file once and accumulate."""
import json
import shutil
import tempfile
import time
from pathlib import Path


def make_files(folder, students, files):
    """files daily files with one line per student (every 5th student absent on odd days)."""
    for d in range(files):
        with open(Path(folder) / f"day{d:02d}.txt", "w", encoding="utf-8") as f:
            for s in range(students):
                f.write(f"{192300000 + s},2026-10-{d + 1:02d},{'A' if (s % 5 == 0 and d % 2) else 'P'}\n")


def once(folder):
    """Read every file once, accumulate counts in a dictionary: O(f x l)."""
    counts, reads = {}, 0
    for p in sorted(Path(folder).glob("*.txt")):
        with open(p, encoding="utf-8") as f:
            for line in f:
                reads += 1
                regno, _date, status = line.strip().split(",")
                c = counts.setdefault(regno, [0, 0])
                c[0 if status == "P" else 1] += 1
    return counts, reads


def per_student(folder, regnos):
    """Re-read all files for each student: O(s x f x l)."""
    counts, reads = {}, 0
    for regno in regnos:
        present = absent = 0
        for p in sorted(Path(folder).glob("*.txt")):
            with open(p, encoding="utf-8") as f:
                for line in f:
                    reads += 1
                    r, _date, status = line.strip().split(",")
                    if r == regno:
                        if status == "P":
                            present += 1
                        else:
                            absent += 1
        counts[regno] = [present, absent]
    return counts, reads


if __name__ == "__main__":
    print("30 daily files, s students (one line per student per file, l = s)")
    print(f"{'s':>5} | {'once: line reads':>16} | {'once (s)':>9} | {'per student: reads':>18} | {'per student (s)':>15} | same")
    rows = []
    for s in (50, 100, 200):
        folder = tempfile.mkdtemp()
        make_files(folder, s, 30)
        regnos = [str(192300000 + i) for i in range(s)]
        t0 = time.perf_counter(); c1, r1 = once(folder); t1 = time.perf_counter() - t0
        t0 = time.perf_counter(); c2, r2 = per_student(folder, regnos); t2 = time.perf_counter() - t0
        print(f"{s:>5} | {r1:>16,} | {t1:>9.4f} | {r2:>18,} | {t2:>15.4f} | {c1 == c2}")
        rows.append({"s": s, "once_reads": r1, "once_s": round(t1, 4), "per_reads": r2, "per_s": round(t2, 4), "same": c1 == c2})
        shutil.rmtree(folder)
    json.dump({"rows": rows}, open("results.json", "w"), indent=1)
