# Task 2 - Monthly Attendance from Daily Biometric Files

Run: `python attendance.py` (output.txt and the files in out/), `python attendance.py --trace` (output_trace.txt) and `python experiments.py` (output_experiments.txt). Input sample: data/2026-10 (4 daily files, 5 students, 2 damaged lines).

## 2.1 Data model
- Input line: `regno,date,status` with status `P` or `A`, one file per day (`2026-10-01.txt`, ...).
- In memory: dictionary `counts[regno] = [present, absent]` (O(1) update, one entry per student) and a list `damaged` of (file, line number, reason, text).
- Output files: `attendance_report.csv` (regno, present, total, percent), `below75.txt` (students under 75%), `damaged.log` (one line per damaged record).

## 2.2 File operations and why

| Step | Operation | Reason |
|---|---|---|
| list the daily files | `Path(folder).glob("*.txt")`, `sorted()` | every day of the month, in date order |
| read a daily file | `open(path, "r", encoding="utf-8")` in a `with` statement | read only, fixed encoding, closed automatically |
| go through the lines | `for number, line in enumerate(f, 1)` | one line at a time, line numbers for the damaged log |
| write the reports | `open(..., "w", newline="")` | mode `w`: a new run replaces the old reports (mode `a` would repeat the lines when the program is run twice); `newline=""` is needed by the csv module |

## 2.3 Pseudocode
    BEGIN
      counts = empty dictionary; damaged = empty list
      FOR EACH daily file IN the month folder, sorted by name
        OPEN the file for reading
        FOR EACH line, with its line number
          IF the line is blank THEN skip it
          split the line into regno, date, status
          IF there are not 3 fields OR status is not P or A THEN
            add (file, line number, reason, line) to damaged
          ELSE
            add 1 to the present or the absent count of regno
        CLOSE the file
      FOR EACH regno IN counts: percent = present / (present + absent) * 100
      WRITE attendance_report.csv, below75.txt (percent < 75), damaged.log
    END

## 2.4 Trace of one small file (data/trace/2026-10-08.txt, one damaged line)

| Line | Text | Action | counts afterwards |
|---|---|---|---|
| 1 | 192311001,2026-10-08,P | counted as present | {192311001: [1, 0]} |
| 2 | 192311002,2026-10-08,Q | damaged: invalid status 'Q' | {192311001: [1, 0]} |
| 3 | 192311001,2026-10-08,A | counted as absent | {192311001: [1, 1]} |

## Result for October (sample data)
192311001 100.00%, 192311002 75.00%, 192311003 33.33%, 192311004 100.00%, 192311005 50.00%. Below 75%: 192311003 and 192311005 (192311002 has exactly 75.00%, so it is not below). The damaged log lists 2026-10-02.txt line 4 (invalid status 'X') and 2026-10-03.txt line 3 (expected 3 fields, found 1); the blank last line of 2026-10-04.txt is skipped.

## Alternative concept: read all files once, or re-read all files for every student

| Students s | Line reads: once | Time once (s) | Line reads: per student | Time per student (s) | Same result |
|---|---|---|---|---|---|
| 50 | 1,500 | 0.001 | 75,000 | 0.0307 | True |
| 100 | 3,000 | 0.0015 | 300,000 | 0.086 | True |
| 200 | 6,000 | 0.0022 | 1,200,000 | 0.3411 | True |

Reading every file once is O(f x l) time and O(s) space (the dictionary). Re-reading for each student is O(s x f x l): s times more line reads (200 times more at s = 200) and much slower, although it needs no dictionary (O(1) extra space). Both give the same counts (checked).
