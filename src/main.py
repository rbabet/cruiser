import json
import os
import random

# === Constants ===
rep_schemes = {
    8: {"light": [3], "medium": [3, 4], "heavy": [3, 4, 5]},
    9: {"light": [3], "medium": [3, 5], "heavy": [3, 5, 6]},
    10: {"light": [3], "medium": [3, 5], "heavy": [3, 5, 7]},
    11: {"light": [4], "medium": [4, 6], "heavy": [4, 6, 7]},
    12: {"light": [4], "medium": [4, 6], "heavy": [4, 6, 8]}
}

volume_map = {
    1: {"total": 60, "heavy": 25, "medium": 20, "light": 15},
    2: {"total": 88, "heavy": 37, "medium": 29, "light": 22},
    3: {"total": 88, "heavy": 37, "medium": 29, "light": 22},
    4: {"total": 112, "heavy": 47, "medium": 37, "light": 28},
    5: {"total": 112, "heavy": 47, "medium": 37, "light": 28},
    6: {"total": 140, "heavy": 59, "medium": 46, "light": 35}
}

session_structure = {
    "A": [("hinge", "medium"), ("push", "medium"), ("squat", "light"), ("pull", "light")],
    "B": [("squat", "heavy"), ("pull", "heavy"), ("hinge", "light"), ("push", "light")],
    "C": [("hinge", "heavy"), ("push", "heavy"), ("squat", "medium"), ("pull", "medium")]
}

# === Utility Functions ===
def build_ladder(scheme, nl):
    reps, total, i = [], 0, 0
    while total < nl:
        r = scheme[i % len(scheme)]
        if total + r > nl:
            r = nl - total
        reps.append(r)
        total += r
        i += 1
    return reps

def load_or_create_rms(drills, filename="rms.json"):
    if os.path.exists(filename):
        with open(filename, "r") as f:
            saved = json.load(f)
        print("Stored RMs:")
        for d, v in saved.items(): print(f"  {d}: {v}")
        choice = input("Use these? ([y]/n): ").strip().lower()
        if choice == 'y' or choice == '': return saved
        elif choice in ('n'): os.remove(filename)
    rms = {}
    print("Enter RM (8–12) for each drill:")
    for drill in drills:
        while True:
            try:
                val = int(input(f"{drill}: "))
                if 8 <= val <= 12:
                    rms[drill] = val
                    break
                else: print("Must be 8–12.")
            except: print("Invalid.")
    with open(filename, "w") as f:
        json.dump(rms, f)
    return rms

def load_prev_nl(filename="nl.json"):
    if os.path.exists(filename):
        with open(filename) as f:
            return json.load(f)
    else:
        return {}

def save_week_nl(week_nl, filename="nl.json"):
    with open(filename, "w") as f:
        json.dump(week_nl, f)

def reroll_nls(drills, last_nls, max_attempts=20):
    attempt = 0
    while attempt < max_attempts:
        rolls = {}
        week_nl = {}
        for drill in drills:
            for _ in range(10):  # up to 10 retries per drill
                roll = random.randint(1, 6)
                nl_total = volume_map[roll]["total"]
                if last_nls.get(drill) != nl_total:
                    rolls[drill] = roll
                    week_nl[drill] = nl_total
                    break
            else:
                break  # couldn't find a unique roll for this drill
        if len(rolls) == len(drills):
            return rolls, week_nl
        attempt += 1
    raise ValueError("Failed to generate unique weekly NLs per drill.")

def print_pair(label, drills, ladders, nl_map):
    print(f"\n{label} (alternate between drills):")
    for d in drills:
        reps = ladders[d]
        line = f"{d:<6} " + " ".join(f"{r:>3}" for r in reps)
        print(line)
    for d in drills:
        print(f"NL for {d}: {nl_map[d]}")

# === Main Execution ===
def generate_week():
    drill_list = ["squat", "pull", "hinge", "push"]
    rms = load_or_create_rms(drill_list)
    last_nl = load_prev_nl()
    rolls, week_nl_totals = reroll_nls(drill_list, last_nl)
    save_week_nl(week_nl_totals)

    weekly_nl = {d: 0 for d in drill_list}

    for session, block in session_structure.items():
        print(f"\n\nSession {session}")
        tier_groups = {}

        for drill, tier in block:
            tier_groups.setdefault(tier, []).append(drill)

        for tier, drills in tier_groups.items():
            nl_map, ladders = {}, {}
            for drill in drills:
                rm = rms[drill]
                scheme = rep_schemes[rm][tier]
                nl = volume_map[rolls[drill]][tier]
                nl_map[drill] = nl
                weekly_nl[drill] += nl
                ladders[drill] = build_ladder(scheme, nl)
            print_pair(tier, drills, ladders, nl_map)

    print("\nTotal NL for the week:")
    for drill in drill_list:
        print(f"  {drill:<6}: {weekly_nl[drill]}")

if __name__ == "__main__":
    generate_week()
