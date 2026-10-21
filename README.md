# Cricket Match Situation Analyzer

**A Practical Match Situation and Scenario Analysis Web Application**  
*Developed for BCA (Data Science) Academic Curriculum & Python Demonstration*

---

## 1. Project Overview

The **Cricket Match Situation Analyzer** is a locally runnable, beginner-friendly web application designed to evaluate live cricket innings dynamics, specifically focusing on chase situations and 1st innings target setting.

Rather than relying on ungrounded predictions or black-box machine learning models, this application uses **transparent mathematical formulas, weighted heuristic scoring, and scenario forecasting** to answer practical match questions:
* *What is the current run rate (CRR) and required run rate (RRR)?*
* *How many legal deliveries remain, and what is the required rate per ball?*
* *Is the batting team ahead of or behind the linear target pace?*
* *How much should the team target over the next 2, 3, or 5 overs?*
* *How do remaining wickets influence tactical risk?*
* *Which batter and bowler have contributed most effectively?*
* *What are the projected outcomes under Conservative, Balanced, and Aggressive batting strategies?*

Every calculation is fully explained on-screen with step-by-step arithmetic to ensure complete educational clarity.

---

## 2. Core Python Programming Concepts Demonstrated

This project is structured specifically to showcase foundational and intermediate Python concepts:
1. **Modular Functions with Type Hints & Docstrings:** Pure calculation functions in `match_analysis.py` and `player_analysis.py`, kept separate from Flask routes and UI.
2. **Nested Dictionaries & Lists:** Complex player data structures storing runs, deliveries, boundaries, wickets, dot balls, and statuses.
3. **Loops & Iteration:** Iterating over dictionaries to calculate strike rates, economy rates, and weighted aggregate scores.
4. **Multi-Key Sorting:** Ranking batters and bowlers dynamically using Python's `sorted()` with custom lambda keys.
5. **Robust Conditional Statements & Edge Case Handling:** Handling 0 balls bowled (division-by-zero prevention), target reached, all-out innings termination, and mathematically impossible chases.
6. **Server-Side Input Validation:** Validating whole numbers, overs vs. balls limits (0–5 balls per over), wicket bounds (0–10), and target scores while preserving user inputs on error.
7. **Weighted Multi-Factor Heuristics:**
   - **Pressure Assessment (0–100):** 30% RRR Demand + 25% CRR/RRR Gap + 20% Ball Depletion + 25% Wickets Lost.
   - **Batter Impact Score (0–100):** 35% Volume + 35% Strike Rate vs Benchmark + 20% Boundary % + 10% Not-Out Bonus.
   - **Bowler Impact Score (0–100):** 40% Wickets Taken + 35% Economy Control + 25% Dot Ball %.
8. **Automated Unit Testing:** Full test suite in `tests/` using Python's standard `unittest` framework.

---

## 3. Technology Stack

* **Language:** Python 3 (standard libraries: `typing`, `math`, `unittest`, `json`)
* **Backend Framework:** Flask 3.x (WSGI routes, Jinja2 templating, form parsing)
* **Frontend:** Semantic HTML5, Custom Responsive CSS3 (Scoreboard theme, no external CDN dependencies), Vanilla JavaScript for dynamic table rows
* **Storage:** In-memory nested Python dictionaries and lists (no SQL server, cloud account, or API keys required)
* **Launcher:** Windows Batch Script (`run.bat`)

---

## 4. Project Directory Structure

```
Devesh Sengar/
│
├── app.py                      # Flask web application, routing, and preset handling
├── match_analysis.py           # Core match mathematics, validation, pacing, and planning
├── player_analysis.py          # Nested dictionary player models, ranking, and impact scores
├── requirements.txt            # Minimal Python dependencies (Flask)
├── run.bat                     # 1-Click Windows batch launcher
├── README.md                   # Complete academic documentation and viva guide
│
├── templates/
│   ├── base.html               # Base HTML layout and document head
│   └── index.html              # Main dashboard with all 12 project sections
│
├── static/
│   ├── css/
│   │   └── style.css           # Restrained cricket-scoreboard-inspired styling
│   └── js/
│       └── app.js              # Dynamic player row additions and form triggers
│
└── tests/
    ├── __init__.py
    ├── test_calculations.py    # Unit tests for match math, edge cases, and heuristics
    └── test_app.py             # Integration tests for Flask routes, GET/POST, and templates
```

---

## 5. How to Run the Application

### Option A: 1-Click Windows Batch Launcher (Recommended)
Double-click `run.bat` in the project root folder.  
The script will automatically:
1. Verify Python is installed.
2. Create a virtual environment (`.venv`) if not present.
3. Install dependencies from `requirements.txt`.
4. Open your default web browser to `http://127.0.0.1:5000/`.
5. Launch the local Flask server.

### Option B: Manual Command Line Execution
Open PowerShell or Command Prompt in the project directory:

```powershell
# 1. Create virtual environment
python -m venv .venv

# 2. Activate virtual environment (Windows PowerShell)
.\.venv\Scripts\Activate.ps1
# Or on Command Prompt:
# .\.venv\Scripts\activate.bat

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the web server
python app.py
```
Then navigate to `http://127.0.0.1:5000/` in any browser.

---

## 6. How to Run Automated Unit Tests

To run all 24 unit and integration tests:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests
```

Expected output:
```text
........................
----------------------------------------------------------------------
Ran 24 tests in 0.14s

OK
```

---

## 7. Mathematical Formulations & Algorithms

### A. Completed Legal Deliveries
Cricket overs are not decimal values. `14.3` overs indicates 14 full overs and 3 additional balls:
$$\text{Completed Balls} = (\text{Completed Overs} \times \text{Balls Per Over}) + \text{Balls in Current Over}$$

### B. Current Run Rate (CRR)
$$\text{CRR} = \frac{\text{Current Score} \times \text{Balls Per Over}}{\text{Completed Legal Deliveries}}$$

### C. Required Run Rate (RRR)
$$\text{Required Runs} = \max(0, \text{Target Score} - \text{Current Score})$$
$$\text{Remaining Balls} = \text{Total Legal Balls} - \text{Completed Legal Deliveries}$$
$$\text{RRR} = \frac{\text{Required Runs} \times \text{Balls Per Over}}{\text{Remaining Balls}}$$

### D. Linear Pace Benchmark
Calculates the expected score based on proportional ball completion:
$$\text{Expected Score} = \frac{\text{Target Score} \times \text{Completed Legal Deliveries}}{\text{Total Available Deliveries}}$$
$$\text{Difference} = \text{Current Score} - \text{Expected Score}$$
* Tolerance band: $\pm 1.5$ runs.
* $> +1.5$: *Ahead of simple linear pace*
* $< -1.5$: *Behind simple linear pace*
* $[-1.5, +1.5]$: *Approximately on pace*

*(Note: Stated clearly as a linear baseline for students, distinguishing it from Duckworth-Lewis-Stern resource percentages).*

### E. Pressure Assessment Heuristic (0–100 Scale)
Combines four normalized components:
1. **$C_1$ (30%):** Required Run Rate relative to format baseline.
2. **$C_2$ (25%):** Scoring Rate Gap ($\text{RRR} - \text{CRR}$).
3. **$C_3$ (20%):** Ball Depletion ($\frac{\text{Completed Deliveries}}{\text{Total Deliveries}} \times 100$).
4. **$C_4$ (25%):** Wicket Loss ($\frac{\text{Wickets Lost}}{10} \times 100$).

$$\text{Pressure Score} = \min(100, \max(0, 0.30 C_1 + 0.25 C_2 + 0.20 C_3 + 0.25 C_4))$$

**Bands:**
* `0–24`: Low pressure (Batting side in command)
* `25–49`: Moderate pressure (Even contest)
* `50–74`: High pressure (Fielding side holds advantage)
* `75–100`: Very high pressure (Extreme jeopardy / wickets depleted)

### F. Next-Overs Planning Formula
For user-selected horizon $H$ overs:
$$\text{Planning Balls} = \min(H \times \text{Balls Per Over}, \text{Remaining Balls})$$
$$\text{Target Runs in Horizon} = \text{round}\left( \frac{\text{Required Runs} \times \text{Planning Balls}}{\text{Remaining Balls}} \right)$$

### G. Batting Strategy Comparison
* **Conservative ($0.85\times$ base rate):** Reduces wicket risk; prioritizes consolidation.
* **Balanced ($1.00\times$ base rate):** Matches current/required benchmark rate.
* **Aggressive ($1.20\times$ base rate):** Attempts high boundary frequency; elevated dismissal risk.

---

## 8. College Viva Preparation: Common Questions & Answers

**Q1: Why represent overs and balls separately instead of using a floating-point number like 14.3?**  
*Answer:* In standard cricket notation, 14.3 overs represents 14 completed overs and 3 balls (87 legal balls). If treated as a decimal float, 14.3 would represent $14 + \frac{3}{10} = 14.3$ overs ($85.8$ balls), which introduces arithmetic inaccuracies. Representing them separately guarantees exact integer delivery tracking.

**Q2: How does the application avoid division-by-zero errors?**  
*Answer:* Defensive guards check if `completed_legal_balls <= 0` or `remaining_balls <= 0` before division. If balls are zero, functions return `None` or sensible fallbacks (e.g. "Not available yet" or 0.0), ensuring the web application never crashes.

**Q3: How are nested dictionaries utilized in this project?**  
*Answer:* In `player_analysis.py`, players are stored in a nested dictionary where each player's name is the primary key mapping to an inner dictionary of statistics (`runs`, `balls`, `fours`, `sixes`, `is_out`). This enables $O(1)$ key lookup and clean iteration to compute derived metrics like strike rates and weighted impact rankings.

**Q4: Is the pressure score or strategy comparison an AI machine learning model?**  
*Answer:* No. In keeping with sound scientific reporting, it is a transparent, rule-based weighted heuristic. It combines objective match variables (rates, wickets, deliveries) into bounded scores rather than claiming predictive infallibility.

---

## 9. Academic Declaration
This project was designed and implemented for practical academic demonstration in the **BCA (Data Science)** curriculum, illustrating software architecture, algorithm design, defensive programming, and user-centric web development in Python.
