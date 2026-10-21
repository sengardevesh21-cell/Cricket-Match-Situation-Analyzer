"""
app.py - Flask Application for Cricket Match Situation Analyzer
Routes, form validation, analysis orchestration, and preset management.

BCA (Data Science) Project
"""

import json
from flask import Flask, render_template, request, redirect, url_for
from match_analysis import (
    validate_match_inputs,
    calculate_current_run_rate,
    calculate_required_runs,
    calculate_remaining_balls,
    calculate_required_run_rate,
    calculate_projected_score,
    compare_linear_pace,
    calculate_pressure_assessment,
    plan_next_overs,
    compare_batting_strategies,
)
from player_analysis import analyze_batters, analyze_bowlers

app = Flask(__name__)

# Sample Pre-configured Match Scenarios
PRESETS = {
    "t20_chase": {
        "title": "T20 Tight Chase (India vs Australia Scenario)",
        "match_format": "T20",
        "innings_type": "chase",
        "custom_total_overs": 20,
        "balls_per_over": 6,
        "target_score": 175,
        "current_score": 124,
        "wickets_lost": 4,
        "completed_overs": 14,
        "balls_in_over": 3,
        "horizon_overs": 3,
        "batters": [
            {"name": "Virat Kohli", "runs": 54, "balls": 38, "fours": 5, "sixes": 2, "is_out": False},
            {"name": "Suryakumar Yadav", "runs": 32, "balls": 18, "fours": 3, "sixes": 2, "is_out": True},
            {"name": "Hardik Pandya", "runs": 18, "balls": 10, "fours": 1, "sixes": 1, "is_out": False},
            {"name": "Rohit Sharma", "runs": 15, "balls": 12, "fours": 2, "sixes": 0, "is_out": True},
        ],
        "bowlers": [
            {"name": "Pat Cummins", "overs": 3, "balls": 3, "runs_conceded": 24, "wickets": 2, "dot_balls": 11},
            {"name": "Mitchell Starc", "overs": 3, "balls": 0, "runs_conceded": 28, "wickets": 1, "dot_balls": 7},
            {"name": "Adam Zampa", "overs": 4, "balls": 0, "runs_conceded": 32, "wickets": 1, "dot_balls": 9},
            {"name": "Josh Hazlewood", "overs": 4, "balls": 0, "runs_conceded": 36, "wickets": 0, "dot_balls": 8},
        ],
    },
    "odi_chase": {
        "title": "ODI Steady Chase (Middle Overs Building)",
        "match_format": "ODI",
        "innings_type": "chase",
        "custom_total_overs": 50,
        "balls_per_over": 6,
        "target_score": 280,
        "current_score": 168,
        "wickets_lost": 3,
        "completed_overs": 32,
        "balls_in_over": 0,
        "horizon_overs": 5,
        "batters": [
            {"name": "KL Rahul", "runs": 62, "balls": 74, "fours": 6, "sixes": 1, "is_out": False},
            {"name": "Shreyas Iyer", "runs": 48, "balls": 52, "fours": 4, "sixes": 1, "is_out": True},
            {"name": "Shubman Gill", "runs": 34, "balls": 40, "fours": 4, "sixes": 0, "is_out": True},
        ],
        "bowlers": [
            {"name": "Matt Henry", "overs": 8, "balls": 0, "runs_conceded": 42, "wickets": 2, "dot_balls": 25},
            {"name": "Trent Boult", "overs": 7, "balls": 0, "runs_conceded": 38, "wickets": 1, "dot_balls": 22},
            {"name": "Mitchell Santner", "overs": 8, "balls": 0, "runs_conceded": 35, "wickets": 0, "dot_balls": 26},
            {"name": "Lockie Ferguson", "overs": 9, "balls": 0, "runs_conceded": 51, "wickets": 0, "dot_balls": 20},
        ],
    },
    "first_innings": {
        "title": "T20 First Innings (Setting a Defendable Total)",
        "match_format": "T20",
        "innings_type": "first_innings",
        "custom_total_overs": 20,
        "balls_per_over": 6,
        "target_score": 0,
        "current_score": 112,
        "wickets_lost": 2,
        "completed_overs": 13,
        "balls_in_over": 2,
        "horizon_overs": 3,
        "batters": [
            {"name": "Yashasvi Jaiswal", "runs": 58, "balls": 36, "fours": 7, "sixes": 3, "is_out": True},
            {"name": "Sanju Samson", "runs": 35, "balls": 24, "fours": 3, "sixes": 2, "is_out": False},
            {"name": "Rinku Singh", "runs": 14, "balls": 8, "fours": 1, "sixes": 1, "is_out": False},
        ],
        "bowlers": [
            {"name": "Shaheen Afridi", "overs": 3, "balls": 0, "runs_conceded": 26, "wickets": 1, "dot_balls": 8},
            {"name": "Haris Rauf", "overs": 3, "balls": 2, "runs_conceded": 34, "wickets": 1, "dot_balls": 7},
            {"name": "Naseem Shah", "overs": 3, "balls": 0, "runs_conceded": 24, "wickets": 0, "dot_balls": 9},
            {"name": "Shadab Khan", "overs": 4, "balls": 0, "runs_conceded": 28, "wickets": 0, "dot_balls": 11},
        ],
    },
}


def parse_and_analyze(form_data):
    """
    Extract form parameters, execute validation, run calculations,
    and package everything for Jinja2 template rendering.
    """
    try:
        match_format = form_data.get("match_format", "T20")
        innings_type = form_data.get("innings_type", "chase")
        current_score = int(form_data.get("current_score", 0))
        wickets_lost = int(form_data.get("wickets_lost", 0))
        completed_overs = int(form_data.get("completed_overs", 0))
        balls_in_over = int(form_data.get("balls_in_over", 0))
        balls_per_over = int(form_data.get("balls_per_over", 6))
        horizon_overs = int(form_data.get("horizon_overs", 3))

        target_score_str = form_data.get("target_score", "").strip()
        target_score = int(target_score_str) if target_score_str else None

        custom_overs_str = form_data.get("custom_total_overs", "").strip()
        custom_total_overs = int(custom_overs_str) if custom_overs_str else None

    except ValueError as ve:
        return None, f"Invalid number input: Please ensure numeric fields contain valid whole numbers. ({ve})"

    # Validate inputs
    is_valid, err_msg, cleaned = validate_match_inputs(
        match_format=match_format,
        innings_type=innings_type,
        current_score=current_score,
        wickets_lost=wickets_lost,
        completed_overs=completed_overs,
        balls_in_over=balls_in_over,
        target_score=target_score,
        custom_total_overs=custom_total_overs,
        balls_per_over=balls_per_over,
    )

    if not is_valid:
        return None, err_msg

    # Core Calculations
    completed_balls = cleaned["completed_legal_balls"]
    total_balls = cleaned["total_legal_balls"]
    rem_balls = calculate_remaining_balls(total_balls, completed_balls)
    crr = calculate_current_run_rate(current_score, completed_balls, balls_per_over)
    projected_score = calculate_projected_score(current_score, crr, rem_balls, balls_per_over)

    # Chase specific calculations
    if innings_type == "chase" and target_score is not None:
        req_runs = calculate_required_runs(current_score, target_score)
        rrr = calculate_required_run_rate(req_runs, rem_balls, balls_per_over)
        runs_per_ball = round(req_runs / rem_balls, 2) if rem_balls > 0 else 0.0
        pace_analysis = compare_linear_pace(
            current_score, target_score, completed_balls, total_balls
        )
        is_chase_complete = current_score >= target_score
        is_impossible = (rem_balls == 0 or wickets_lost >= 10) and not is_chase_complete
    else:
        req_runs = 0
        rrr = None
        runs_per_ball = None
        pace_analysis = None
        is_chase_complete = False
        is_impossible = (rem_balls == 0 or wickets_lost >= 10)

    # Pressure Assessment
    pressure = calculate_pressure_assessment(
        innings_type=innings_type,
        current_score=current_score,
        wickets_lost=wickets_lost,
        completed_legal_balls=completed_balls,
        total_legal_balls=total_balls,
        target_score=target_score,
        balls_per_over=balls_per_over,
    )

    # Next-Overs Planning
    planning = plan_next_overs(
        innings_type=innings_type,
        current_score=current_score,
        wickets_lost=wickets_lost,
        remaining_balls=rem_balls,
        target_score=target_score,
        current_run_rate=crr,
        horizon_overs=horizon_overs,
        balls_per_over=balls_per_over,
    )

    # Strategy Comparison
    strategies = compare_batting_strategies(
        innings_type=innings_type,
        current_score=current_score,
        wickets_lost=wickets_lost,
        remaining_balls=rem_balls,
        current_run_rate=crr,
        target_score=target_score,
        horizon_overs=horizon_overs,
        balls_per_over=balls_per_over,
    )

    # Parse Batter Data from Form
    batters_dict = {}
    batter_names = form_data.getlist("batter_name[]")
    batter_runs = form_data.getlist("batter_runs[]")
    batter_balls = form_data.getlist("batter_balls[]")
    batter_fours = form_data.getlist("batter_fours[]")
    batter_sixes = form_data.getlist("batter_sixes[]")
    batter_out = form_data.getlist("batter_out[]")

    for i in range(len(batter_names)):
        name = batter_names[i].strip()
        if name:
            try:
                runs = int(batter_runs[i]) if i < len(batter_runs) and batter_runs[i] != "" else 0
                b_balls = int(batter_balls[i]) if i < len(batter_balls) and batter_balls[i] != "" else 0
                fours = int(batter_fours[i]) if i < len(batter_fours) and batter_fours[i] != "" else 0
                sixes = int(batter_sixes[i]) if i < len(batter_sixes) and batter_sixes[i] != "" else 0
                out_val = str(batter_out[i]).lower() in ["1", "true", "yes", "out"] if i < len(batter_out) else False

                batters_dict[name] = {
                    "runs": runs,
                    "balls": b_balls,
                    "fours": fours,
                    "sixes": sixes,
                    "is_out": out_val,
                }
            except (ValueError, IndexError):
                continue

    # Parse Bowler Data from Form
    bowlers_dict = {}
    bowler_names = form_data.getlist("bowler_name[]")
    bowler_overs = form_data.getlist("bowler_overs[]")
    bowler_balls = form_data.getlist("bowler_balls[]")
    bowler_runs = form_data.getlist("bowler_runs[]")
    bowler_wickets = form_data.getlist("bowler_wickets[]")
    bowler_dots = form_data.getlist("bowler_dots[]")

    for i in range(len(bowler_names)):
        name = bowler_names[i].strip()
        if name:
            try:
                overs = int(bowler_overs[i]) if i < len(bowler_overs) and bowler_overs[i] != "" else 0
                b_balls = int(bowler_balls[i]) if i < len(bowler_balls) and bowler_balls[i] != "" else 0
                runs = int(bowler_runs[i]) if i < len(bowler_runs) and bowler_runs[i] != "" else 0
                wickets = int(bowler_wickets[i]) if i < len(bowler_wickets) and bowler_wickets[i] != "" else 0
                dots = int(bowler_dots[i]) if i < len(bowler_dots) and bowler_dots[i] != "" else 0

                bowlers_dict[name] = {
                    "overs": overs,
                    "balls": b_balls,
                    "runs_conceded": runs,
                    "wickets": wickets,
                    "dot_balls": dots,
                }
            except (ValueError, IndexError):
                continue

    # Batter & Bowler analysis
    ranked_batters = analyze_batters(batters_dict, match_crr=crr, match_rrr=rrr, balls_per_over=balls_per_over)
    ranked_bowlers = analyze_bowlers(bowlers_dict, match_crr=crr, balls_per_over=balls_per_over)

    # Format overs representation e.g. "14.3"
    overs_display = f"{cleaned['completed_overs']}.{cleaned['balls_in_over']}"
    total_overs_display = f"{cleaned['total_overs']}.0"

    raw_batters = [
        {"name": k, **v} for k, v in batters_dict.items()
    ]
    raw_bowlers = [
        {"name": k, **v} for k, v in bowlers_dict.items()
    ]

    results = {
        "params": cleaned,
        "display": {
            "overs": overs_display,
            "total_overs": total_overs_display,
            "completed_balls": completed_balls,
            "total_balls": total_balls,
            "remaining_balls": rem_balls,
            "crr": crr,
            "projected_score": projected_score,
            "req_runs": req_runs,
            "rrr": rrr,
            "runs_per_ball": runs_per_ball,
            "is_chase_complete": is_chase_complete,
            "is_impossible": is_impossible,
        },
        "pace_analysis": pace_analysis,
        "pressure": pressure,
        "planning": planning,
        "strategies": strategies,
        "ranked_batters": ranked_batters,
        "ranked_bowlers": ranked_bowlers,
        "raw_batters": raw_batters,
        "raw_bowlers": raw_bowlers,
    }

    return results, None


@app.route("/", methods=["GET", "POST"])
def index():
    error_message = None
    results = None
    form_values = {}
    batters_list = []
    bowlers_list = []

    if request.method == "POST":
        form_values = request.form
        results, error_message = parse_and_analyze(request.form)
        if results:
            batters_list = results.get("raw_batters", [])
            bowlers_list = results.get("raw_bowlers", [])
        else:
            # Reconstruct player lists from request.form so input is preserved on error
            b_names = request.form.getlist("batter_name[]")
            b_runs = request.form.getlist("batter_runs[]")
            b_balls = request.form.getlist("batter_balls[]")
            b_fours = request.form.getlist("batter_fours[]")
            b_sixes = request.form.getlist("batter_sixes[]")
            b_outs = request.form.getlist("batter_out[]")
            for i in range(len(b_names)):
                batters_list.append({
                    "name": b_names[i],
                    "runs": b_runs[i] if i < len(b_runs) else 0,
                    "balls": b_balls[i] if i < len(b_balls) else 0,
                    "fours": b_fours[i] if i < len(b_fours) else 0,
                    "sixes": b_sixes[i] if i < len(b_sixes) else 0,
                    "is_out": b_outs[i] in ["1", "true", "True"] if i < len(b_outs) else False,
                })

            bw_names = request.form.getlist("bowler_name[]")
            bw_overs = request.form.getlist("bowler_overs[]")
            bw_balls = request.form.getlist("bowler_balls[]")
            bw_runs = request.form.getlist("bowler_runs[]")
            bw_wkts = request.form.getlist("bowler_wickets[]")
            bw_dots = request.form.getlist("bowler_dots[]")
            for j in range(len(bw_names)):
                bowlers_list.append({
                    "name": bw_names[j],
                    "overs": bw_overs[j] if j < len(bw_overs) else 0,
                    "balls": bw_balls[j] if j < len(bw_balls) else 0,
                    "runs_conceded": bw_runs[j] if j < len(bw_runs) else 0,
                    "wickets": bw_wkts[j] if j < len(bw_wkts) else 0,
                    "dot_balls": bw_dots[j] if j < len(bw_dots) else 0,
                })
    else:
        # Check if a preset is requested via query parameter
        preset_key = request.args.get("preset", "t20_chase")
        from werkzeug.datastructures import MultiDict

        if preset_key == "blank":
            form_values = MultiDict({
                "match_format": "T20",
                "innings_type": "chase",
                "current_score": "0",
                "wickets_lost": "0",
                "completed_overs": "0",
                "balls_in_over": "0",
                "target_score": "150",
                "custom_total_overs": "20",
                "balls_per_over": "6",
                "horizon_overs": "3",
            })
            batters_list = [
                {"name": "Batter 1", "runs": 0, "balls": 0, "fours": 0, "sixes": 0, "is_out": False}
            ]
            bowlers_list = [
                {"name": "Bowler 1", "overs": 0, "balls": 0, "runs_conceded": 0, "wickets": 0, "dot_balls": 0}
            ]
            results = None
        elif preset_key in PRESETS:
            preset = PRESETS[preset_key]
            mock_form = {
                "match_format": preset["match_format"],
                "innings_type": preset["innings_type"],
                "current_score": str(preset["current_score"]),
                "wickets_lost": str(preset["wickets_lost"]),
                "completed_overs": str(preset["completed_overs"]),
                "balls_in_over": str(preset["balls_in_over"]),
                "target_score": str(preset["target_score"]),
                "custom_total_overs": str(preset["custom_total_overs"]),
                "balls_per_over": str(preset["balls_per_over"]),
                "horizon_overs": str(preset["horizon_overs"]),
            }
            md = MultiDict(mock_form)
            for b in preset["batters"]:
                md.add("batter_name[]", b["name"])
                md.add("batter_runs[]", str(b["runs"]))
                md.add("batter_balls[]", str(b["balls"]))
                md.add("batter_fours[]", str(b["fours"]))
                md.add("batter_sixes[]", str(b["sixes"]))
                md.add("batter_out[]", "1" if b["is_out"] else "0")

            for bw in preset["bowlers"]:
                md.add("bowler_name[]", bw["name"])
                md.add("bowler_overs[]", str(bw["overs"]))
                md.add("bowler_balls[]", str(bw["balls"]))
                md.add("bowler_runs[]", str(bw["runs_conceded"]))
                md.add("bowler_wickets[]", str(bw["wickets"]))
                md.add("bowler_dots[]", str(bw["dot_balls"]))

            form_values = md
            results, error_message = parse_and_analyze(md)
            if results:
                batters_list = results.get("raw_batters", [])
                bowlers_list = results.get("raw_bowlers", [])

    return render_template(
        "index.html",
        results=results,
        error_message=error_message,
        form=form_values,
        batters_list=batters_list,
        bowlers_list=bowlers_list,
        presets=PRESETS,
        current_preset=request.args.get("preset", "t20_chase"),
    )


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
