"""Task 3: failure table, custom exception, complete try statement with raise ... from, misuse experiment, LBYL vs EAFP."""
import json
import os
import tempfile
import timeit
from datetime import datetime
from pathlib import Path


class InvalidRecord(Exception):
    """A line of the attendance file is not in the expected format (raised in parse_line, handled in process_file)."""


class ProcessingError(Exception):
    """The whole file could not be processed (raised in process_file, handled by the caller)."""


def parse_line(line):
    """Return (regno, date, status) or raise InvalidRecord. The original ValueError is kept with 'from'."""
    parts = [p.strip() for p in line.split(",")]
    if len(parts) != 3:
        raise InvalidRecord(f"expected 3 fields, found {len(parts)}")
    try:
        datetime.strptime(parts[1], "%Y-%m-%d")
    except ValueError as err:
        raise InvalidRecord(f"bad date {parts[1]!r}") from err           # keeps the original cause
    if parts[2] not in ("P", "A"):
        raise InvalidRecord(f"invalid status {parts[2]!r}")
    return tuple(parts)


def process_file(path):
    """Complete try statement: try / except (specific) / else / finally."""
    present = absent = 0
    errors = []
    f = None
    try:
        f = open(path, encoding="utf-8")
        for number, line in enumerate(f, 1):
            if not line.strip():
                continue
            try:
                _r, _d, status = parse_line(line)
            except InvalidRecord as err:                                   # a bad line is recorded, processing goes on
                errors.append((number, str(err)))
                continue
            if status == "P":
                present += 1
            else:
                absent += 1
    except FileNotFoundError as err:
        raise ProcessingError(f"file not found: {path}") from err
    except PermissionError as err:
        raise ProcessingError(f"permission denied: {path}") from err
    except UnicodeDecodeError as err:
        raise ProcessingError(f"wrong encoding in {path}") from err
    else:
        if present + absent + len(errors) == 0:
            print("    (else clause) the file is empty - no records")
        return present, absent, errors
    finally:
        if f is not None:
            f.close()                                                      # always runs, with or without an error


def summarise_misuse(path):
    """MISUSE: except Exception: pass, and a typing error in a variable name (presnt)."""
    present, absent, errors = 0, 0, []
    with open(path, encoding="utf-8") as f:
        for number, line in enumerate(f, 1):
            try:
                _r, _d, status = parse_line(line)
                if status == "P":
                    presnt += 1                  # typing error: the name should be present
                else:
                    absent += 1
            except Exception:
                pass
    return present, absent, errors


def summarise_typo_specific(path):
    """The same typing error, but only InvalidRecord is caught."""
    present, absent = 0, 0
    with open(path, encoding="utf-8") as f:
        for line in f:
            try:
                _r, _d, status = parse_line(line)
            except InvalidRecord:
                continue
            if status == "P":
                presnt += 1
            else:
                absent += 1
    return present, absent


def parse_light(line):
    """Only the field-count and status checks (no date parsing), so that the two styles can be compared fairly."""
    parts = line.split(",")
    if len(parts) != 3 or parts[2].strip() not in ("P", "A"):
        raise InvalidRecord("bad line")
    return parts


def eafp(lines):
    """Easier to ask forgiveness: just call it and catch InvalidRecord."""
    bad = 0
    for line in lines:
        try:
            parse_light(line)
        except InvalidRecord:
            bad += 1
    return bad


def lbyl(lines):
    """Look before you leap: check with if statements first, no exception is raised."""
    bad = 0
    for line in lines:
        parts = line.split(",")
        if len(parts) != 3 or parts[2].strip() not in ("P", "A"):
            bad += 1
    return bad


if __name__ == "__main__":
    tmp = Path(tempfile.mkdtemp())
    print("Failure table (each failure is triggered here)")
    results = []

    def attempt(name, expected, action):
        try:
            action()
            observed = "no exception"
        except Exception as err:
            observed = type(err).__name__
        print(f"  {name:<26} expected {expected:<22} observed {observed}")
        results.append({"failure": name, "expected": expected, "observed": observed})

    attempt("missing folder", "FileNotFoundError", lambda: list(os.scandir(tmp / "no_folder")))
    attempt("missing file", "FileNotFoundError", lambda: open(tmp / "none.txt"))
    locked = tmp / "locked.txt"
    locked.write_text("192311001,2026-10-08,P\n")
    os.chmod(locked, 0)
    attempt("permission denied", "PermissionError", lambda: open(locked).read())
    os.chmod(locked, 0o644)
    bad_bytes = tmp / "bad_encoding.txt"
    bad_bytes.write_bytes("192311001,2026-10-08,P\n".encode("utf-16"))
    attempt("wrong encoding (UTF-16)", "UnicodeDecodeError", lambda: open(bad_bytes, encoding="utf-8").read())
    attempt("damaged line: 2 fields", "InvalidRecord", lambda: parse_line("192311001,2026-10-08"))
    attempt("damaged line: bad date", "InvalidRecord", lambda: parse_line("192311001,2026-13-45,P"))
    attempt("damaged line: no [2]", "IndexError", lambda: "192311001,2026-10-08".split(",")[2])
    attempt("non-number text", "ValueError", lambda: int("abc"))
    empty = tmp / "empty.txt"
    empty.write_text("")
    attempt("empty file", "none (0 lines)", lambda: open(empty).read())
    print("  note: a file may stay readable when the program runs with administrator rights; on Windows chmod 0 does not block reading.")

    print("\nCustom exception: raised in parse_line, handled in process_file")
    try:
        parse_line("192311001,2026-13-45,P")
    except InvalidRecord as err:
        print("  InvalidRecord:", err, "| original cause kept with 'from':", repr(err.__cause__))

    print("\nComplete try statement (try / except / else / finally)")
    good = tmp / "good.txt"
    good.write_text("192311001,2026-10-08,P\n192311002,2026-10-08,A\n192311003,2026-10-08\n192311004,2026-10-08,L\n")
    print("  good file :", process_file(good))
    print("  empty file:", process_file(empty))
    for name, path in (("missing file", tmp / "none.txt"), ("wrong encoding", bad_bytes)):
        try:
            process_file(path)
        except ProcessingError as err:
            print(f"  {name:<14}: ProcessingError: {err} | caused by {type(err.__cause__).__name__}")

    print("\nMisuse experiment on a file with 2 P and 1 A")
    three = tmp / "three.txt"
    three.write_text("192311001,2026-10-08,P\n192311002,2026-10-08,A\n192311003,2026-10-08,P\n")
    correct = process_file(three)
    misuse = summarise_misuse(three)
    print("  correct result                       :", correct[:2])
    print("  with 'except Exception: pass' + typo :", misuse[:2], "<- WRONG, and no error message at all")
    try:
        summarise_typo_specific(three)
    except NameError as err:
        print("  with specific except + same typo    :", type(err).__name__ + ":", err)
    print("  The typing error raises UnboundLocalError (a NameError, an Exception). 'except Exception' catches every error, including")
    print("  programming mistakes, and 'pass' throws it away, so the program continues and reports zero present students.")

    print("\nLook before you leap vs easier to ask forgiveness (time per line, microseconds, 100,000 lines)")
    print(f"  {'bad lines':>9} | {'EAFP (try/except)':>17} | {'LBYL (if checks)':>16}")
    good_line, bad_line = "192311001,2026-10-08,P", "192311001,2026-10-08"
    rows = []
    for share in (0.0, 0.01, 0.10, 0.50):
        n = 100_000
        lines = [bad_line if (i % 100) < share * 100 else good_line for i in range(n)]
        assert eafp(lines) == lbyl(lines)
        t_e = min(timeit.repeat(lambda: eafp(lines), number=1, repeat=3)) / n * 1e6
        t_l = min(timeit.repeat(lambda: lbyl(lines), number=1, repeat=3)) / n * 1e6
        print(f"  {share * 100:>8.0f}% | {t_e:>17.3f} | {t_l:>16.3f}")
        rows.append({"bad": share, "eafp_us": round(t_e, 3), "lbyl_us": round(t_l, 3)})
    json.dump({"failures": results, "rows": rows, "correct": list(correct[:2]), "misuse": list(misuse[:2])}, open("results.json", "w"), indent=1)
