"""
player_analysis.py - Batter and Bowler Impact Analysis
Uses nested dictionaries, iteration loops, conditional logic, and transparent weighted scoring.

Designed for BCA (Data Science) students to showcase practical data structures and metrics.
"""

from typing import Dict, Any, List, Optional


def analyze_batters(
    batters_data: Dict[str, Dict[str, Any]],
    match_crr: Optional[float] = None,
    match_rrr: Optional[float] = None,
    balls_per_over: int = 6,
) -> List[Dict[str, Any]]:
    """
    Process nested dictionary of batters, compute cricket metrics,
    apply weighted impact scoring, and return sorted rankings.

    Input dictionary structure:
    {
        "Batter Name": {
            "runs": int,
            "balls": int,
            "fours": int,
            "sixes": int,
            "is_out": bool
        }
    }
    """
    # Benchmark strike rate based on match context
    # If chasing, match required SR = (RRR / balls_per_over) * 100
    if match_rrr and match_rrr > 0:
        benchmark_sr = max(100.0, (match_rrr / balls_per_over) * 100.0)
    elif match_crr and match_crr > 0:
        benchmark_sr = max(100.0, (match_crr / balls_per_over) * 100.0)
    else:
        benchmark_sr = 125.0

    ranked_batters = []

    for name, stats in batters_data.items():
        # Validate individual stats
        runs = max(0, int(stats.get("runs", 0)))
        balls = max(0, int(stats.get("balls", 0)))
        fours = max(0, int(stats.get("fours", 0)))
        sixes = max(0, int(stats.get("sixes", 0)))
        is_out = bool(stats.get("is_out", False))

        # Boundary calculations
        boundary_runs = (fours * 4) + (sixes * 6)
        # Cap boundary runs if user input entered more boundary runs than total runs
        if boundary_runs > runs:
            boundary_runs = runs

        # Strike Rate
        if balls > 0:
            strike_rate = round((runs / balls) * 100.0, 2)
        else:
            strike_rate = 0.0

        # Boundary Percentage
        boundary_pct = round((boundary_runs / runs) * 100.0, 1) if runs > 0 else 0.0
        singles_and_twos = max(0, runs - boundary_runs)

        # Weighted Batter Impact Score (0 to 100 scale)
        # 1. Volume Score (35%): 50 runs represents a strong baseline benchmark
        volume_score = min(100.0, (runs / 50.0) * 100.0)

        # 2. Strike Rate Score (35%): relative to required/match benchmark SR
        sr_ratio = strike_rate / benchmark_sr if benchmark_sr > 0 else 1.0
        sr_score = min(100.0, max(0.0, sr_ratio * 50.0))

        # 3. Boundary Impact (20%): reward power hitting
        boundary_score = min(100.0, boundary_pct)

        # 4. Wicket Conservation / Not-Out Bonus (10%)
        not_out_bonus = 10.0 if not is_out and balls > 0 else 0.0

        # Combined Impact Score
        impact_score = round(
            (0.35 * volume_score)
            + (0.35 * sr_score)
            + (0.20 * boundary_score)
            + not_out_bonus,
            1,
        )
        impact_score = min(100.0, max(0.0, impact_score))

        # Qualitative classification
        if strike_rate >= 150.0 and boundary_pct >= 50.0:
            role_tag = "Aggressor"
        elif not is_out and balls >= 25:
            role_tag = "Anchor"
        elif strike_rate < 100.0 and balls >= 15:
            role_tag = "Struggling / Defensive"
        else:
            role_tag = "Rotator / Contributor"

        ranked_batters.append({
            "name": name.strip(),
            "runs": runs,
            "balls": balls,
            "fours": fours,
            "sixes": sixes,
            "is_out": is_out,
            "status": "Out" if is_out else "Not Out",
            "strike_rate": strike_rate,
            "boundary_runs": boundary_runs,
            "boundary_pct": boundary_pct,
            "singles_and_twos": singles_and_twos,
            "impact_score": impact_score,
            "role_tag": role_tag,
        })

    # Sort batters descending by impact score using standard Python sorted()
    ranked_batters.sort(key=lambda b: (b["impact_score"], b["runs"], b["strike_rate"]), reverse=True)

    # Assign ranks and explanations
    for rank, batter in enumerate(ranked_batters, start=1):
        batter["rank"] = rank
        if rank == 1:
            batter["explanation"] = (
                f"Rank 1: Top impact ({batter['impact_score']} pts). Scored {batter['runs']} "
                f"off {batter['balls']} balls (SR: {batter['strike_rate']}) with {batter['boundary_pct']}% "
                f"runs in boundaries ({batter['status']})."
            )
        else:
            batter["explanation"] = (
                f"Rank {rank}: Impact {batter['impact_score']} pts. "
                f"{batter['runs']} runs (SR: {batter['strike_rate']}, {batter['status']})."
            )

    return ranked_batters


def analyze_bowlers(
    bowlers_data: Dict[str, Dict[str, Any]],
    match_crr: Optional[float] = None,
    balls_per_over: int = 6,
) -> List[Dict[str, Any]]:
    """
    Process nested dictionary of bowlers, compute bowling metrics,
    apply weighted impact scoring, and return sorted rankings.

    Input dictionary structure:
    {
        "Bowler Name": {
            "overs": int,
            "balls": int,
            "runs_conceded": int,
            "wickets": int,
            "dot_balls": int
        }
    }
    """
    ranked_bowlers = []
    benchmark_economy = match_crr if match_crr and match_crr > 0 else 7.5

    for name, stats in bowlers_data.items():
        overs = max(0, int(stats.get("overs", 0)))
        balls = max(0, int(stats.get("balls", 0)))
        runs_conceded = max(0, int(stats.get("runs_conceded", 0)))
        wickets = max(0, min(10, int(stats.get("wickets", 0))))
        dot_balls = max(0, int(stats.get("dot_balls", 0)))

        legal_balls = (overs * balls_per_over) + balls
        if dot_balls > legal_balls:
            dot_balls = legal_balls

        # Cricket overs display string: e.g. "3.4"
        overs_display = f"{overs}.{balls}"

        # Economy Rate
        if legal_balls > 0:
            economy_rate = round((runs_conceded * balls_per_over) / legal_balls, 2)
            dot_ball_pct = round((dot_balls / legal_balls) * 100.0, 1)
        else:
            economy_rate = 0.0
            dot_ball_pct = 0.0

        # Bowling Strike Rate (balls per wicket)
        if wickets > 0:
            strike_rate = round(legal_balls / wickets, 1)
        else:
            strike_rate = None

        # Weighted Bowler Impact Score (0 to 100 scale)
        # 1. Wickets Component (40%): 4 wickets represents 100 pts
        wicket_score = min(100.0, wickets * 25.0)

        # 2. Economy Control Component (35%):
        # Economy of <= 4 is 100 pts, Economy >= 12 is 0 pts
        eco_score = max(0.0, min(100.0, (12.0 - economy_rate) * 12.5))

        # 3. Dot Ball Dominance Component (25%):
        dot_score = min(100.0, dot_ball_pct)

        # Combined Impact Score
        impact_score = round(
            (0.40 * wicket_score) + (0.35 * eco_score) + (0.25 * dot_score), 1
        )
        impact_score = min(100.0, max(0.0, impact_score))

        # Role tag
        if wickets >= 2:
            role_tag = "Strike Bowler (Wicket Taker)"
        elif economy_rate < benchmark_economy and dot_ball_pct >= 40.0:
            role_tag = "Miserly Container"
        elif economy_rate > benchmark_economy + 2.0:
            role_tag = "Expensive Spell"
        else:
            role_tag = "Support Bowler"

        ranked_bowlers.append({
            "name": name.strip(),
            "overs_display": overs_display,
            "overs": overs,
            "balls": balls,
            "legal_balls": legal_balls,
            "runs_conceded": runs_conceded,
            "wickets": wickets,
            "dot_balls": dot_balls,
            "economy_rate": economy_rate,
            "strike_rate": strike_rate if strike_rate is not None else "N/A",
            "dot_ball_pct": dot_ball_pct,
            "impact_score": impact_score,
            "role_tag": role_tag,
        })

    # Sort bowlers descending by impact score using sorted()
    ranked_bowlers.sort(
        key=lambda b: (b["impact_score"], b["wickets"], -b["economy_rate"]), reverse=True
    )

    # Assign ranks and explanations
    for rank, bowler in enumerate(ranked_bowlers, start=1):
        bowler["rank"] = rank
        if rank == 1:
            bowler["explanation"] = (
                f"Rank 1: Greatest bowling impact ({bowler['impact_score']} pts). "
                f"Took {bowler['wickets']} wkts in {bowler['overs_display']} ovs, conceding "
                f"{bowler['runs_conceded']} runs (Eco: {bowler['economy_rate']}) with "
                f"{bowler['dot_ball_pct']}% dot balls."
            )
        else:
            bowler["explanation"] = (
                f"Rank {rank}: Impact {bowler['impact_score']} pts. "
                f"{bowler['wickets']} wkts, Eco {bowler['economy_rate']}."
            )

    return ranked_bowlers
