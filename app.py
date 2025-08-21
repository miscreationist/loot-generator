import random
import streamlit as st

# --- Data ---

maps = {
    "Midwich Elementary School": {
        "rolls": [
            (1, 7, "Mission fail! You run into one of the realm's denizens, be it a killer or a creature of the Fog, and are attacked! Roll on the penalties table"),
            (8, 10, "Unsuccessful mission. You find nothing"),
            (11, 13, "You found a memory fragment! Add 1d30 bloodpoints"),
            (14, 15, "Mission success! You found a small item! Roll on the small loot table"),
            (16, 17, "Mission success! You found 2 small items or 1 medium item. Roll on the appropriate loot table"),
            (18, 19, "Mission success! You found 1 large item or 2 medium items. Roll on the appropriate loot table"),
            (20, 20, "YO! You got a nice li’l haul there! You have found 5 small items and 1 large one. Hope you have a bag with you, and a second person. You will need help carrying all of it back.")
        ],
        "small": [
            "1d4 pieces of chalk",
            "Poster ({})".format(random.choice(["star", "sunflower", "monkey"])),
            "1d4 stack of music paper",
            "Pens/Pencils",
            "1d8 thumb tacks",
            "1d4 Medkit [+1 to your next trial]",
            "1d6 Metallic star stickers"
        ],
        "medium": [
            "Globe, out of date",
            "School text books [{}]".format(random.choice(["biology", "history", "english"])),
            "Projector, requires power",
            "Desk chair",
            "Mop and bucket",
            "Tray",
            "Duffle bag with 1d4 shirts",
            "Locked locker. DC 15 to break it open. If you do choose 1d4 on table below",
            "VHS tapes. Looks to be kids movies",
            "Wall clock"
        ],
        "large": [
            "1d4 + 2 Teachers chairs",
            "Desk",
            "Media/Book cart, but it is upstairs, you need help carrying it down the stairs, lest the denizens of the realm hear you",
            "Bench"
        ],
        "penalties": [
            "A creature in the fog has found you and killed you. When you wake back up you have a -2 penalty for 1d12 matches and are unable to scavenge until the negative penalty is gone, or it is the next day",
            "You were injured and will take a day to recover. There is a -1 penalty for 1d6 matches",
            "If you were carrying something scavenged earlier, you lose it [but if you had nothing, you lost nothing]",
            "You were chased until you reached your campfire, but any time you try to scavenge again you feel something following you until you reach your campfire. You are unable to scavenge until the next day"
        ]
    }
}

# --- Helper Functions ---

def roll_dice(dice_str):
    """Roll dice in XdY format, e.g. 1d4"""
    if "d" in dice_str:
        num, die = map(int, dice_str.lower().split("d"))
        return sum(random.randint(1, die) for _ in range(num))
    else:
        return int(dice_str)

def roll_penalty(penalty_table):
    import re
    penalty_text = random.choice(penalty_table)
    match = re.search(r'(-?\d+) penalty for (\d+d\d+) matches', penalty_text)
    if match:
        penalty_value = int(match.group(1))
        dice_str = match.group(2)
        num_matches = roll_dice(dice_str)
        penalty_text = re.sub(r'(-?\d+) penalty for (\d+d\d+) matches',
                              f"{penalty_value} penalty for {num_matches} matches",
                              penalty_text)
        return penalty_text, penalty_value, num_matches
    else:
        return penalty_text, 0, 0

def roll_loot_table(table, count=1):
    items = []
    for _ in range(count):
        choice = random.choice(table)
        items.append(choice)
    return items

# --- Streamlit UI ---

st.title("Scavenging")

selected_map = st.selectbox("Choose a map", list(maps.keys()))

if "penalty" not in st.session_state:
    st.session_state["penalty"] = 0

if st.button("Roll a D20 to Scavenge!"):
    roll = random.randint(1, 20)
    st.write(f"You rolled: {roll} on {selected_map}")
    map_data = maps[selected_map]

    # Find roll result
    outcome = None
    for low, high, text in map_data["rolls"]:
        if low <= roll <= high:
            outcome = text
            break

    if outcome is None:
        st.write("No outcome found for this roll.")
    elif "Mission fail" in outcome:
        penalty_text, val, matches = roll_penalty(map_data["penalties"])
        st.session_state["penalty"] += val
        st.write(penalty_text)
    elif "memory fragment" in outcome:
        bloodpoints = roll_dice("1d30")
        st.write(outcome.replace("1d30", str(bloodpoints)))
    elif "Mission success" in outcome:
        st.write(outcome)
        # Handle loot
        if "small item" in outcome:
            small_count = 1
            items = roll_loot_table(map_data["small"], small_count)
            st.write("You obtained:")
            for i in items:
                st.write("-", i)
        elif "2 small items or 1 medium item" in outcome:
            small_items = roll_loot_table(map_data["small"], 2)
            medium_item = roll_loot_table(map_data["medium"], 1)[0]
            st.write("You obtained (choose one):")
            st.write("- 2 small items:", small_items)
            st.write("- 1 medium item:", medium_item)
        elif "1 large item or 2 medium items" in outcome:
            large_item = roll_loot_table(map_data["large"], 1)[0]
            medium_items = roll_loot_table(map_data["medium"], 2)
            st.write("You obtained (choose one):")
            st.write("- 1 large item:", large_item)
            st.write("- 2 medium items:", medium_items)
        elif "5 small items and 1 large one" in outcome:
            small_items = roll_loot_table(map_data["small"], 5)
            large_item = roll_loot_table(map_data["large"], 1)[0]
            st.write("You obtained:")
            st.write("- Small items:", small_items)
            st.write("- Large item:", large_item)
