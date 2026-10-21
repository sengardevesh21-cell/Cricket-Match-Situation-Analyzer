"""
match_analysis.py - Cricket Match Situation Analyzer
Core mathematical calculations, pace comparisons, pressure scoring, and planning.

Developed for BCA (Data Science) curriculum demonstration:
Demonstrating functions, conditional logic, input validation, and weighted scoring.
"""

from typing import Dict, Any, Tuple, Optional


def validate_match_inputs(
    match_format: str,
    innings_type: str,
    current_score: int,
    wickets_lost: int,
    completed_overs: int,
    balls_in_over: int,
    target_score: Optional[int] = None,
    custom_total_overs: Optional[int] = None,
    balls_per_over: int = 6,
) -> Tuple[bool, Optional[str], Dict[str, Any]]:
    """
    Validate all match input fields strictly and return cleaned parameters.

    Returns:
        (is_valid: bool, error_message: Optional[str], cleaned_data: dict)
    """
    if balls_per_over <= 0:
        return False, "Balls per over must be a positive integer (standard is 6).", {}

    if balls_in_over < 0 or balls_in_over >= balls_per_over:
        return (
            False,
            f"Balls completed in current over must be between 0 and {balls_per_over - 1}.",
            {},
        )

    if current_score < 0:
        return False, "Current innings score cannot be negative.", {}

    if wickets_lost < 0 or wickets_lost > 10:
        return False, "Wickets lost must be between 0 and 10.", {}

    if completed_overs < 0:
        return False, "Completed overs cannot be negative.", {}

    # Determine total overs based on format
    format_clean = match_format.upper().strip()
    if format_clean == "T20":
        total_overs = 20
    elif format_clean == "ODI":
        total_overs = 50
    elif format_clean == "CUSTOM":
        if custom_total_overs is None or custom_total_overs <= 0:
            return False, "For Custom match format, total overs must be greater than zero.", {}
        total_overs = int(custom_total_overs)
    else:
        return False, f"Unsupported match format: '{match_format}'. Choose T20, ODI, or Custom.", {}

    total_legal_balls = total_overs * balls_per_over
    completed_legal_balls = (completed_overs * balls_per_over) + balls_in_over

    if completed_legal_balls > total_legal_balls:
        return (
            False,
            f"Completed balls ({completed_legal_balls}) cannot exceed total innings balls ({total_legal_balls} balls / {total_overs} overs).",
            {},
        )

    innings_type_clean = innings_type.lower().strip()
    if innings_type_clean not in ["chase", "first_innings"]:
        return False, "Innings type must be either 'chase' or 'first_innings'.", {}

    if innings_type_clean == "chase":
        if target_score is None:
            return False, "A target score is required for chase analysis.", {}
        if target_score <= 0:
            return False, "Target score must be greater than zero.", {}

    cleaned_data = {
        "match_format": format_clean,
        "innings_type": innings_type_clean,
        "total_overs": total_overs,
        "balls_per_over": balls_per_over,
        "current_score": current_score,
        "wickets_lost": wickets_lost,
        "completed_overs": completed_overs,
        "balls_in_over": balls_in_over,
        "completed_legal_balls": completed_legal_balls,
        "total_legal_balls": total_legal_balls,
        "target_score": target_score if innings_type_clean == "chase" else None,
    }
    return True, None, cleaned_data


def calculate_current_run_rate(
    current_score: int, completed_legal_balls: int, balls_per_over: int = 6
) -> Optional[float]:
    """
    Calculate current run rate based on actual completed legal deliveries.
    Formula: Current Run Rate = (Current Score * Balls Per Over) / Completed Legal Balls
    Returns None if no legal balls have been bowled yet.
    """
    if completed_legal_balls <= 0:
        return None
    return round((current_score * balls_per_over) / completed_legal_balls, 2)


def calculate_required_runs(current_score: int, target_score: int) -> int:
    """
    Calculate runs needed to achieve target.
    Formula: Required Runs = Target Score - Current Score
    Returns 0 if target is already met or exceeded.
    """
    return max(0, target_score - current_score)


def calculate_remaining_balls(total_legal_balls: int, completed_legal_balls: int) -> int:
    """
    Calculate legal balls remaining in the innings.
    Formula: Remaining Balls = Total Available Legal Balls - Completed Legal Balls
    """
    return max(0, total_legal_balls - completed_legal_balls)


def calculate_required_run_rate(
    required_runs: int, remaining_balls: int, balls_per_over: int = 6
) -> Optional[float]:
    """
    Calculate required run rate per 6-ball over.
    Formula: Required Run Rate = (Required Runs * Balls Per Over) / Remaining Balls
    Returns None if remaining_balls is 0.
    """
    if remaining_balls <= 0:
        return None
    return round((required_runs * balls_per_over) / remaining_balls, 2)


def calculate_projected_score(
    current_score: int,
    current_run_rate: Optional[float],
    remaining_balls: int,
    balls_per_over: int = 6,
) -> int:
    """
    Project final innings score based on continuing at current run rate.
    Formula: Projected Score = Current Score + (Current Run Rate * Remaining Overs)
    """
    if current_run_rate is None or remaining_balls <= 0:
        return current_score
    remaining_overs = remaining_balls / balls_per_over
    projected_additional = current_run_rate * remaining_overs
    return int(round(current_score + projected_additional))


def compare_linear_pace(
    current_score: int,
    target_score: int,
    completed_legal_balls: int,
    total_legal_balls: int,
    tolerance: float = 1.5,
) -> Dict[str, Any]:
    """
    Compare current score with simple linear target pace.
    Expected Score = Target Score * (Completed Legal Balls / Total Available Legal Balls)
    """
    if total_legal_balls <= 0:
        return {
            "expected_score": 0.0,
            "difference": 0.0,
            "status": "Innings start",
            "explanation": "No overs scheduled.",
        }

    expected_score = round((target_score * completed_legal_balls) / total_legal_balls, 2)
    difference = round(current_score - expected_score, 2)

    if completed_legal_balls == 0:
        status = "Innings Start"
        explanation = "Innings has just begun. Linear pace benchmark will update after first over."
    elif difference > tolerance:
        status = "Ahead of linear pace"
        explanation = (
            f"The batting team is {abs(difference):.1f} runs ahead of the simple linear target pace "
            f"({current_score} vs {expected_score:.1f} benchmark)."
        )
    elif difference < -tolerance:
        status = "Behind linear pace"
        explanation = (
            f"The batting team is {abs(difference):.1f} runs behind the simple linear target pace "
            f"({current_score} vs {expected_score:.1f} benchmark)."
        )
    else:
        status = "Approximately on pace"
        explanation = (
            f"The batting team is on pace with the linear benchmark "
            f"(Score: {current_score}, Benchmark: {expected_score:.1f})."
        )

    return {
        "expected_score": expected_score,
        "difference": difference,
        "status": status,
        "explanation": explanation,
    }


def calculate_pressure_assessment(
    innings_type: str,
    current_score: int,
    wickets_lost: int,
    completed_legal_balls: int,
    total_legal_balls: int,
    target_score: Optional[int] = None,
    balls_per_over: int = 6,
    reference_run_rate: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Calculate transparent 0-100 pressure score with documented weighted components.

    For Chase:
    - Component 1 (30%): Required Run Rate relative to reference rate.
    - Component 2 (25%): Difference between RRR and CRR (scoring gap pressure).
    - Component 3 (20%): Percentage of available balls exhausted.
    - Component 4 (25%): Wickets lost proportion (wickets / 10).

    For First Innings:
    - Component 1 (30%): Scoring rate relative to standard par benchmark.
    - Component 2 (30%): Wickets lost proportion.
    - Component 3 (20%): Ball consumption rate.
    - Component 4 (20%): Acceleration requirement in final overs.
    """
    remaining_balls = max(0, total_legal_balls - completed_legal_balls)
    crr = calculate_current_run_rate(current_score, completed_legal_balls, balls_per_over) or 6.0

    if innings_type == "chase" and target_score is not None:
        # Check instant decisive conditions
        if current_score >= target_score:
            return {
                "score": 0,
                "band": "Low pressure",
                "summary": "Target achieved. Match won with zero pressure remaining.",
                "components": {
                    "rrr_pressure": 0.0,
                    "gap_pressure": 0.0,
                    "balls_pressure": 0.0,
                    "wickets_pressure": 0.0,
                },
            }

        if wickets_lost >= 10:
            return {
                "score": 100,
                "band": "Very high pressure",
                "summary": "All 10 wickets lost. Innings has terminated.",
                "components": {
                    "rrr_pressure": 100.0,
                    "gap_pressure": 100.0,
                    "balls_pressure": 100.0,
                    "wickets_pressure": 100.0,
                },
            }

        if remaining_balls == 0:
            return {
                "score": 100,
                "band": "Very high pressure",
                "summary": "All legal balls completed without reaching target.",
                "components": {
                    "rrr_pressure": 100.0,
                    "gap_pressure": 100.0,
                    "balls_pressure": 100.0,
                    "wickets_pressure": round((wickets_lost / 10) * 100, 1),
                },
            }

        required_runs = target_score - current_score
        rrr = (required_runs * balls_per_over) / remaining_balls

        # Reference rate fallback: starting required run rate
        if reference_run_rate is None or reference_run_rate <= 0:
            reference_run_rate = (target_score * balls_per_over) / total_legal_balls

        # 1. RRR pressure (30%): RRR vs Reference rate
        # RRR of 6 = ~35, RRR of 9 = ~60, RRR of 15+ = 100
        rrr_ratio = rrr / max(reference_run_rate, 4.0)
        c1 = min(100.0, max(0.0, (rrr_ratio - 0.5) * 80.0))

        # 2. Rate gap pressure (25%): RRR - CRR
        gap = rrr - crr
        if gap <= -2.0:
            c2 = 10.0
        elif gap <= 0:
            c2 = 30.0 + (gap * 10.0)
        else:
            c2 = min(100.0, 45.0 + (gap * 12.0))

        # 3. Ball consumption pressure (20%)
        # Pressure increases as innings nears conclusion
        balls_used_pct = (completed_legal_balls / total_legal_balls) * 100.0
        c3 = balls_used_pct

        # 4. Wickets lost pressure (25%)
        # Progressive penalty as batting depth diminishes
        c4 = (wickets_lost / 10.0) * 100.0

        # Weighted aggregate
        raw_score = (0.30 * c1) + (0.25 * c2) + (0.20 * c3) + (0.25 * c4)
        total_score = int(round(min(100.0, max(0.0, raw_score))))

    else:
        # First innings pressure heuristic
        par_rr = reference_run_rate if reference_run_rate else 8.0
        # CRR compared to format par
        crr_ratio = crr / par_rr
        # Lower CRR means higher pressure to accelerate
        c1 = min(100.0, max(0.0, (1.3 - crr_ratio) * 80.0))
        # Wickets lost
        c2 = (wickets_lost / 10.0) * 100.0
        # Balls used
        c3 = (completed_legal_balls / total_legal_balls) * 100.0
        # Wickets remaining vs overs remaining tension
        overs_left = remaining_balls / balls_per_over
        wickets_left = 10 - wickets_lost
        c4 = min(100.0, max(0.0, ((10 - wickets_left) / 10.0) * 100.0))

        raw_score = (0.30 * c1) + (0.30 * c2) + (0.20 * c3) + (0.20 * c4)
        total_score = int(round(min(100.0, max(0.0, raw_score))))
        c1, c2, c3, c4 = round(c1, 1), round(c2, 1), round(c3, 1), round(c4, 1)

    # Pressure bands
    if total_score < 25:
        band = "Low pressure"
        summary = "Batting side is in comfortable control of scoring pace and wicket conservation."
    elif total_score < 50:
        band = "Moderate pressure"
        summary = "Match situation is balanced; steady execution required without panic."
    elif total_score < 75:
        band = "High pressure"
        summary = "Demanding required rate or falling wickets creating tangible fielding-side advantage."
    else:
        band = "Very high pressure"
        summary = "Extreme match tension; immediate boundary-hitting or partnership rescue essential."

    return {
        "score": total_score,
        "band": band,
        "summary": summary,
        "components": {
            "rrr_pressure": round(c1, 1),
            "gap_pressure": round(c2, 1),
            "balls_pressure": round(c3, 1),
            "wickets_pressure": round(c4, 1),
        },
    }


def plan_next_overs(
    innings_type: str,
    current_score: int,
    wickets_lost: int,
    remaining_balls: int,
    target_score: Optional[int] = None,
    current_run_rate: Optional[float] = None,
    horizon_overs: int = 3,
    balls_per_over: int = 6,
) -> Dict[str, Any]:
    """
    Plan scoring requirements for the upcoming 2, 3, or 5 overs.
    Formula:
      Planning Period Balls = min(Horizon Overs * Balls Per Over, Remaining Balls)
      Expected Runs Needed = Required Runs * (Planning Period Balls / Remaining Balls)
    """
    if wickets_lost >= 10:
        return {
            "possible": False,
            "message": "All wickets lost. Innings has ended; no future overs can be planned.",
            "planning_overs": 0,
            "planning_balls": 0,
            "expected_runs": 0,
            "runs_per_over": 0.0,
            "runs_remaining_after": 0,
            "balls_remaining_after": 0,
        }

    if remaining_balls <= 0:
        return {
            "possible": False,
            "message": "No balls remaining in the innings. Chase or innings concluded.",
            "planning_overs": 0,
            "planning_balls": 0,
            "expected_runs": 0,
            "runs_per_over": 0.0,
            "runs_remaining_after": 0,
            "balls_remaining_after": 0,
        }

    horizon_balls = horizon_overs * balls_per_over
    planning_balls = min(horizon_balls, remaining_balls)
    actual_planning_overs = round(planning_balls / balls_per_over, 1)

    if innings_type == "chase" and target_score is not None:
        required_runs = max(0, target_score - current_score)
        if required_runs == 0:
            return {
                "possible": True,
                "message": "Target has already been reached. No further runs needed.",
                "planning_overs": actual_planning_overs,
                "planning_balls": planning_balls,
                "expected_runs": 0,
                "runs_per_over": 0.0,
                "runs_remaining_after": 0,
                "balls_remaining_after": max(0, remaining_balls - planning_balls),
            }

        # Linear distribution of remaining required runs across remaining balls
        expected_runs = int(round((required_runs * planning_balls) / remaining_balls))
        runs_per_over = round(expected_runs / (planning_balls / balls_per_over), 2)
        runs_remaining_after = max(0, required_runs - expected_runs)
        balls_remaining_after = remaining_balls - planning_balls

        message = (
            f"To stay near the current required pace, aim for approximately {expected_runs} runs "
            f"over the next {actual_planning_overs} overs ({runs_per_over} RPO). "
            f"This leaves {runs_remaining_after} runs needed from the final {balls_remaining_after} balls."
        )

        return {
            "possible": True,
            "message": message,
            "planning_overs": actual_planning_overs,
            "planning_balls": planning_balls,
            "expected_runs": expected_runs,
            "runs_per_over": runs_per_over,
            "runs_remaining_after": runs_remaining_after,
            "balls_remaining_after": balls_remaining_after,
        }
    else:
        # First innings: project based on current run rate
        base_rr = current_run_rate if current_run_rate and current_run_rate > 0 else 7.5
        expected_runs = int(round(base_rr * (planning_balls / balls_per_over)))
        runs_per_over = base_rr
        balls_remaining_after = remaining_balls - planning_balls
        projected_after = current_score + expected_runs

        message = (
            f"At the current scoring tempo, expect roughly {expected_runs} runs over the next "
            f"{actual_planning_overs} overs ({runs_per_over:.2f} RPO), taking the total to ~{projected_after} "
            f"with {balls_remaining_after} balls remaining."
        )

        return {
            "possible": True,
            "message": message,
            "planning_overs": actual_planning_overs,
            "planning_balls": planning_balls,
            "expected_runs": expected_runs,
            "runs_per_over": runs_per_over,
            "runs_remaining_after": 0,
            "balls_remaining_after": balls_remaining_after,
        }


def compare_batting_strategies(
    innings_type: str,
    current_score: int,
    wickets_lost: int,
    remaining_balls: int,
    current_run_rate: Optional[float],
    target_score: Optional[int] = None,
    horizon_overs: int = 3,
    balls_per_over: int = 6,
) -> Dict[str, Any]:
    """
    Compare Conservative (0.85x), Balanced (1.00x), and Aggressive (1.20x) strategies.
    Evaluates scoring rate, horizon yield, projected final score, and rule-based wicket risk.
    """
    # Base rate determination
    if innings_type == "chase" and target_score is not None:
        required_runs = max(0, target_score - current_score)
        if remaining_balls > 0:
            rrr = (required_runs * balls_per_over) / remaining_balls
        else:
            rrr = 0.0
        base_rate = rrr if rrr > 0 else (current_run_rate or 6.0)
    else:
        base_rate = current_run_rate if current_run_rate and current_run_rate > 0 else 7.0
        rrr = 0.0

    planning_balls = min(horizon_overs * balls_per_over, remaining_balls)
    planning_overs = planning_balls / balls_per_over if balls_per_over > 0 else 0
    remaining_overs = remaining_balls / balls_per_over if balls_per_over > 0 else 0

    strategies_config = [
        {
            "name": "Conservative",
            "multiplier": 0.85,
            "desc": "Prioritizes wicket conservation, strike rotation, and lower-risk shots.",
        },
        {
            "name": "Balanced",
            "multiplier": 1.00,
            "desc": "Matches required/current benchmark with calculated boundary pursuit.",
        },
        {
            "name": "Aggressive",
            "multiplier": 1.20,
            "desc": "Intentional attacking approach with higher boundary rate and lofted strokes.",
        },
    ]

    results = []
    for cfg in strategies_config:
        planned_rate = round(base_rate * cfg["multiplier"], 2)
        horizon_runs = int(round(planned_rate * planning_overs))
        projected_innings_score = current_score + int(round(planned_rate * remaining_overs))

        if innings_type == "chase" and target_score is not None:
            remaining_gap = max(0, target_score - projected_innings_score)
            meets_pace = planned_rate >= rrr
        else:
            remaining_gap = 0
            meets_pace = True

        # Rule-based Wicket Risk Heuristic
        # Conservative: Low when <= 6 wickets down, Medium when 7+
        # Balanced: Low when <= 3, Medium when 4-6, High when 7+
        # Aggressive: Medium when <= 3, High when 4-6, Critical/Very High when 7+
        if cfg["name"] == "Conservative":
            risk = "Low Risk" if wickets_lost <= 6 else "Medium Risk"
        elif cfg["name"] == "Balanced":
            if wickets_lost <= 3:
                risk = "Low-Medium Risk"
            elif wickets_lost <= 6:
                risk = "Medium Risk"
            else:
                risk = "High Risk"
        else:  # Aggressive
            if wickets_lost <= 3:
                risk = "Medium Risk"
            elif wickets_lost <= 6:
                risk = "High Risk"
            else:
                risk = "Very High Risk"

        # Practical college commentary
        if innings_type == "chase" and target_score is not None:
            if cfg["name"] == "Conservative":
                if meets_pace:
                    analysis = "Effective choice: keeps wickets in hand while still reaching target."
                else:
                    analysis = (
                        f"Leaves a deficit of ~{remaining_gap} runs; may push pressure to the final overs."
                    )
            elif cfg["name"] == "Balanced":
                analysis = "Keeps required pace steady and reduces sudden volatility."
            else:
                if wickets_lost >= 7:
                    analysis = "High jeopardy: severe risk of getting bowled out before reaching target."
                else:
                    analysis = "Creates a buffer early to alleviate death-over pressure."
        else:
            if cfg["name"] == "Conservative":
                analysis = "Consolidates innings; ideal after a cluster of early wickets."
            elif cfg["name"] == "Balanced":
                analysis = "Maintains optimal run flow without excessive batting risks."
            else:
                analysis = "Maximizes total score potential if substantial batting depth remains."

        results.append({
            "name": cfg["name"],
            "multiplier": cfg["multiplier"],
            "planned_rate": planned_rate,
            "horizon_runs": horizon_runs,
            "projected_score": projected_innings_score,
            "remaining_gap": remaining_gap,
            "meets_pace": meets_pace,
            "risk": risk,
            "description": cfg["desc"],
            "analysis": analysis,
        })

    return {
        "base_rate": round(base_rate, 2),
        "horizon_overs": round(planning_overs, 1),
        "strategies": results,
    }
