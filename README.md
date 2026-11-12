# Python Programming - Assignment 4 (CO4)

File handling and exception handling.

- Name: Kavinaya A
- Register number: 1911260289
- Python version: 3.12
- Libraries: standard library only (see requirements.txt)
- GitHub: https://github.com/kavinaya520/CSA08-1911260289-Assignment4.git

## How to run
Run each program from inside its folder. Saved output: output*.txt (and the .png images of them); raw counts and timings: results.json. Timings depend on the computer, counts do not.

| Task | Folder | Commands | Result note |
|---|---|---|---|
| 1 | Task01 | `cd Task01` then `python mess_totals.py` | Original script lost 3351.25 rupees silently; repaired total 6101.25 with 2 rejected lines reported |
| 2 | Task02 | `python attendance.py`, `python attendance.py --trace`, `python experiments.py` | 5 students, 2 below 75%, 2 damaged lines logged; reading once is s times fewer line reads |
| 3 | Task03 | `python complete_code.py`, `python handling.py` | Expected output matched; `except Exception: pass` hides a typing error and gives a wrong count |
| 4 | Task04 | `python library.py` | Mode "w" kept only day 7 (3 lines); repaired program keeps all 14 lines and logs the error |

Each task folder has a README.md with the diagnosis, design, measurements and the alternative-concept analysis.
