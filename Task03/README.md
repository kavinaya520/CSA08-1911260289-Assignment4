# Task 3 - Failure Analysis and Exception Handling

Run: `python complete_code.py` (the Complete the Code program, output.txt) and `python handling.py` (output_experiments.txt, results.json).

## Complete the Code
TODO 1: `parse_line` raises `InvalidRecord` when there are not exactly 3 fields (`expected 3 fields, found N`) or the status is not P or A (`invalid status 'L'`).
TODO 2: `summarise` uses a `with` statement and a `try/except InvalidRecord` for every line, counts P and A, and records (line number, message).
Output: `(1, 1, [(3, 'expected 3 fields, found 2'), (4, "invalid status 'L'")])` - equal to the expected output. With a file name that does not exist `summarise` returns `(0, 0, [(0, 'file not found: no_such_file.csv')])`.

## 3.1 Failure table (each failure is triggered in handling.py)

| Failure | Expected exception | Observed here | Where it is handled |
|---|---|---|---|
| missing folder | FileNotFoundError | FileNotFoundError | process_month: reported once, the month is skipped |
| missing file | FileNotFoundError | FileNotFoundError | process_file raises ProcessingError from the cause |
| permission denied | PermissionError | no exception | process_file raises ProcessingError |
| wrong encoding (UTF-16) | UnicodeDecodeError | UnicodeDecodeError | process_file raises ProcessingError |
| damaged line: 2 fields | InvalidRecord | InvalidRecord | process_file: the line is recorded, processing goes on |
| damaged line: bad date | InvalidRecord | InvalidRecord | process_file: the line is recorded, processing goes on |
| damaged line: no [2] | IndexError | IndexError | avoided: parse_line checks the number of fields first |
| non-number text | ValueError | ValueError | caught and reported (Task 1) |
| empty file | none (0 lines) | no exception | no exception: process_file prints a warning in the else clause |

"Permission denied" showed no exception here because the programs ran with administrator rights (and on Windows `chmod` does not block reading); with a normal user it raises `PermissionError`. An empty file is not an error: it simply gives no records, so the program must check for it.

## 3.2 Custom exception
`InvalidRecord` (a damaged line) is raised in `parse_line` and handled in `process_file`, which records the line and goes on. `ProcessingError` (the whole file cannot be used) is raised in `process_file` and handled by the caller.
Using `raise InvalidRecord(...) from err` keeps the original error: for the date 2026-13-45 the original `ValueError` is available as `err.__cause__`.

## 3.3 Complete try statement (`process_file`)
- `try`: open the file and process the lines.
- `except FileNotFoundError / PermissionError / UnicodeDecodeError`: only the expected errors, each turned into a `ProcessingError` with `from`.
- `else`: runs only when no exception happened (here: warns about an empty file and returns the result).
- `finally`: always runs, so the file is closed with or without an error.

## 3.4 Misuse experiment: `except Exception: pass`
On a file with 2 P and 1 A the correct code gives (present 2, absent 1). The misused version with the typing error `presnt += 1` gives (0, 1) and NO message: `presnt += 1` raises `UnboundLocalError` (a NameError, an Exception) for every present student, `except Exception` catches it and `pass` throws it away.
With only `except InvalidRecord` the same typing error is shown immediately: `UnboundLocalError: cannot access local variable 'presnt'`. Rule: catch the narrowest exception that you can handle, never `pass` silently.

## Alternative concept: look before you leap (LBYL) or easier to ask forgiveness (EAFP)
`lbyl` checks with `if` statements; `eafp` calls the parser and catches `InvalidRecord`. Time per line for 100,000 lines:

| Bad lines | EAFP: try/except (us per line) | LBYL: if checks (us per line) |
|---|---|---|
| 0% | 0.13 | 0.104 |
| 1% | 0.126 | 0.1 |
| 10% | 0.149 | 0.104 |
| 50% | 0.271 | 0.108 |

Both are O(n). Raising and catching an exception costs more than an `if` check, so EAFP is only slightly slower (about 25%) when bad lines are rare and clearly slower when many lines are bad (50% bad: about 2.5 times). EAFP is shorter and avoids repeating the checks, and it is the natural style for failures that cannot be checked in advance (a file that disappears, a permission error).
