import json, os, random

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
        choice = input("Use these? (y/n or r to reset): ").strip().lower()
        if choice == 'y': return saved
        elif choice == 'r': os.remove(filename)
        elif choice == 'n': os.remove(filename)
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

def load_rolls(filename="rolls.json"):
    return json.load(open(filename)) if os.path.exists(filename) else None

def save_rolls(rolls, filename="rolls.json"):
    with open(filename, "w") as f:
        json.dump(rolls, f)

def roll_new_week(drills, last_rolls=None):
    rolls = {}
    for drill in drills:
        while True:
            roll = random.randint(1, 6)
            if not last_rolls or roll != last_rolls.get(drill):
                rolls[drill] = roll
                break
    return rolls

# === Main Execution ===
def generate_week():
    drill_list = ["squat", "pull", "hinge", "push"]
    rms = load_or_create_rms(drill_list)
    last_rolls = load_rolls()
    rolls = roll_new_week(drill_list, last_rolls)
    save_rolls(rolls)

    volume_targets = {d: volume_map[rolls[d]] for d in drill_list}

    for session, block in session_structure.items():
        print(f"\nSession {session}")
        rows = {}
        for drill, tier in block:
            rm = rms[drill]
            scheme = rep_schemes[rm][tier]
            nl = volume_targets[drill][tier]
            ladder = build_ladder(scheme, nl)
            rows[drill] = ladder
        for drill, sets in rows.items():
            print(f"{drill:<6}", end='')
            for s in sets: print(f"{s:>4}", end='')
            print()

if __name__ == "__main__":
    generate_week()

