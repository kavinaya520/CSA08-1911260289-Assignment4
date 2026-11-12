"""Task 3 Complete the Code (TODO 1 and TODO 2 done)."""
import os
import tempfile


class InvalidRecord(Exception):
    """Raised when a line of the attendance file is not in the expected format."""


def parse_line(line):
    """'192311001,2026-10-08,P' -> ('192311001', '2026-10-08', 'P')"""
    parts = line.strip().split(",")
    # TODO 1 (completed): raise InvalidRecord if there are not exactly 3 fields or the status is not P or A
    if len(parts) != 3:
        raise InvalidRecord(f"expected 3 fields, found {len(parts)}")
    fields = tuple(p.strip() for p in parts)
    if fields[2] not in ("P", "A"):
        raise InvalidRecord(f"invalid status {fields[2]!r}")
    return fields


def summarise(path):
    present, absent, errors = 0, 0, []
    # TODO 2 (completed): with statement, parse each line inside try/except InvalidRecord,
    # count P and A, record (line number, message) for bad lines
    try:
        with open(path, encoding="utf-8") as f:
            for number, line in enumerate(f, 1):
                if not line.strip():
                    continue
                try:
                    _regno, _date, status = parse_line(line)
                except InvalidRecord as err:
                    errors.append((number, str(err)))
                else:
                    if status == "P":
                        present += 1
                    else:
                        absent += 1
    except FileNotFoundError:                       # the changed file name asked in the task
        errors.append((0, f"file not found: {path}"))
    return present, absent, errors


data = ("192311001, 2026-10-08, P\n192311002, 2026-10-08, A\n"
        "192311003, 2026-10-08\n192311004, 2026-10-08, L\n")
with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False, encoding="utf-8") as tmp:
    tmp.write(data)
print(summarise(tmp.name))
os.remove(tmp.name)

print(summarise("no_such_file.csv"))                # a file name that does not exist is handled inside summarise()
