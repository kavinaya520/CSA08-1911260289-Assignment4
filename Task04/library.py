"""Task 4: file and exception forensics - why the library log kept only the last day and an error left no message.
(Built from the scenario text only; the numbered questions of Task 4 are not in the PDF I was given.)"""
import json
import logging
import traceback
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEMO = HERE / "demo"

WEEK = {1: ["Python Basics", "Data Structures"], 2: ["Algorithms", "Networks"], 3: ["Databases", "Operating Systems"],
        4: ["Compilers", None, "Graph Theory"],            # the record None (a damaged return slip) will cause the error
        5: ["Statistics", "Linear Algebra"], 6: ["Machine Learning"], 7: ["Digital Logic", "Calculus", "Physics"]}


def add_returns_buggy(path, day, books):
    """THE ORIGINAL PROGRAM'S STYLE: mode 'w' empties the file when it is opened; no error handling; no close()."""
    f = open(path, "w")
    for title in books:
        f.write(f"day {day}: {title.upper()}\n")           # title.upper() fails for a damaged record (None)
    f.close()


def add_returns_fixed(path, day, books, log):
    """Repair: mode 'a' appends; with statement; the bad record is logged with its traceback and skipped."""
    with open(path, "a", encoding="utf-8") as f:
        for index, title in enumerate(books):
            try:
                f.write(f"day {day}: {title.upper()}\n")
            except AttributeError:
                log.error("day %s record %s is damaged: %r\n%s", day, index, title, traceback.format_exc())


def size_lines(path):
    p = Path(path)
    return (p.stat().st_size, len(p.read_text().splitlines())) if p.exists() else (0, 0)


if __name__ == "__main__":
    DEMO.mkdir(exist_ok=True)
    for name in ("library_buggy.txt", "library_fixed.txt", "error.log"):
        (DEMO / name).unlink(missing_ok=True)
    logger = logging.getLogger("library")
    logger.setLevel(logging.ERROR)
    handler = logging.FileHandler(DEMO / "error.log", mode="a", encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    logger.addHandler(handler)

    print("Evidence: the log file after each day of the week")
    print(f"{'day':>3} | {'original (mode w)':<46} | {'repaired (mode a)':<22}")
    rows = []
    for day, books in WEEK.items():
        outcome = "ok"
        try:
            add_returns_buggy(DEMO / "library_buggy.txt", day, books)
        except Exception as err:
            outcome = f"CRASH {type(err).__name__}, not logged"
        add_returns_fixed(DEMO / "library_fixed.txt", day, books, logger)
        b, f = size_lines(DEMO / "library_buggy.txt"), size_lines(DEMO / "library_fixed.txt")
        print(f"{day:>3} | {outcome + ', file: ' + str(b[1]) + ' lines':<46} | {str(f[1]) + ' lines, ' + str(f[0]) + ' bytes':<22}")
        rows.append({"day": day, "buggy": outcome, "buggy_lines": b[1], "fixed_lines": f[1]})
    print("\nContents of library_buggy.txt after the week:")
    print("  " + (DEMO / "library_buggy.txt").read_text().replace("\n", "\n  ").rstrip())
    print("\nContents of error.log (repaired program):")
    print("  " + (DEMO / "error.log").read_text().strip().replace("\n", "\n  "))
    print("\nlines in library_fixed.txt:", size_lines(DEMO / "library_fixed.txt")[1])
    json.dump({"rows": rows, "fixed_lines": size_lines(DEMO / "library_fixed.txt")[1], "buggy_lines": size_lines(DEMO / "library_buggy.txt")[1]},
              open("results.json", "w"), indent=1)
