# Task 4 - File and Exception Forensics: The Library Log

Run: `python library.py` (output.txt, files in demo/).

Note: my copy of the assignment PDF ends at the opening paragraph of Task 4, so this task is built from the scenario only (the log kept only the last day's books, and one day stopped with an error without any message being saved).
The numbered questions of Task 4 were not in the PDF.

## Hypotheses and evidence (simulated week of 7 days; on day 4 one return slip is damaged)

| Hypothesis | Evidence |
|---|---|
| H1: the program opens the log with mode `"w"`, which empties the file every time it is opened | In the original program the file had 2, 2, 2, 1, 2, 1 and 3 lines after the days 1 to 7: it never grows. After the week it contains only day 7. |
| H2: the error left no message because nothing writes it anywhere | Day 4 crashed with `AttributeError` (the damaged slip `None` has no `upper()`); the exception only goes to the console of the run, and there is no `try/except` or log file, so a scheduled run leaves nothing to read. |
| H3: a crash can leave a partly written file | On day 4 only "COMPILERS" was written before the crash (the file had 1 line); the day's other books were lost, and the next day replaced it anyway. |

## Repair (`add_returns_fixed`)
- mode `"a"` (append): the log keeps every day; after the week it has 14 lines against 3 in the original.
- `with open(...)` closes and flushes the file even after an error.
- the damaged record is caught with `except AttributeError`, written to `error.log` with the date, the record number and the full traceback through the `logging` module, and the program goes on with the next book.

The log after each day (original vs repaired) is in output.txt; the error report is in demo/error.log.
