# Task 1 - Review and Repair a File-Processing Script

Run: `python mess_totals.py` (output.txt, raw numbers in results.json; input sample: mess_oct.txt). The original script's logic is kept in `original_script_total()` (only the hard-coded path became a parameter so that it can be run).

## 1.1 Diagnosis: at least eight weaknesses

| # | Weakness of the original script | What can go wrong in the hostel office |
|---|---|---|
| 1 | File name is hard-coded (`C:\Users\Office\Desktop\mess_oct.txt`) | Works only on one computer and one month; November needs the code to be edited; a different user name breaks it. |
| 2 | `open()` without `with` / `close()` | The file stays open if an error happens, so it can stay locked or lose data; many open files exhaust handles. |
| 3 | `f.read()` loads the whole file | 50,000 lines are all held in memory at once (about 5.5 MB measured, against 22 KB when reading line by line). |
| 4 | Bare `except: pass` | Every error is hidden, including a typing error in the code, a Ctrl-C and a damaged line; nobody knows that anything failed. |
| 5 | `int(parts[2])` for amounts | An amount such as 1250.50 fails and is swallowed: the paise are lost and whole bills disappear. On the sample file 3,351.25 rupees were silently lost. |
| 6 | `report = report + ...` in a loop | Strings are immutable, so every `+` copies the growing text: 1.15 s for 50,000 lines against 0.007 s with a list and `join()`. |
| 7 | The last empty line of the file | `split('\n')` gives an empty last item; the script only survives because `except: pass` hides the IndexError it causes. |
| 8 | No record of rejected lines | A student whose bill was dropped is never discovered; the office cannot correct the file. |
| 9 | Name and amount are not stripped or validated | ' 950 ' or 'abc' or a missing field are handled differently by accident, with no message. |

## 1.2 Repaired script (`mess_totals.py`, function `mess_total`)
Reads one line at a time inside `with open(filename, encoding="utf-8")`, skips blank lines, strips the fields, checks that there are 3 fields, converts the amount with `Decimal` (keeps the paise) and catches only `InvalidOperation`.
A rejected line is saved with its line number and the reason; the report is built as a list. The file name is a parameter (`python mess_totals.py other_file.txt`), and a missing file raises `FileNotFoundError` with a clear message.

Result on mess_oct.txt (7 lines): original total 2750 (lost 1250.50 and 2100.75 silently); repaired total 6101.25 with 2 rejected lines (line 3: amount 'abc' is not a number; line 4: expected 3 fields, found 2); the blank line 6 is skipped.

## 1.3 Defence (74 words, limit 100)
My version is safer for 50,000 lines because it reads one line at a time, so memory stays small, and closes the file automatically with a with statement. It keeps the paise by using Decimal, catches only the expected errors, and records every rejected line with its line number, so no bill disappears silently. The file name is a parameter, so it works on any file, and a missing file raises a clear FileNotFoundError.

## Alternative concept: f.read() or f.readlines() against iterating the file (50,000 lines, 1.5 MB)

| Method | Time (s) | Peak memory (KB) |
|---|---|---|
| f.read() | 0.019 | 5,496 |
| f.readlines() | 0.0175 | 4,001 |
| iteration | 0.0159 | 22 |

All three give the same total. Time is O(n) in every case; memory is O(file size) for `read()` and `readlines()` and O(longest line) for iteration. Building the 50,000-line report with repeated `+` took 1.1477 s against 0.0068 s with a list and `join()`.
