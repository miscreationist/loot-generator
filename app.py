import streamlit as st
import random

st.set_page_config(page_title="Scavenging")
st.title("Scavenging")

# --- Dice Rolling Functions ---
def roll_dice(dice_str):
    num, die = map(int, dice_str.lower().split("d"))
    return sum(random.randint(1, die) for _ in range(num))

# --- Roll Penalty ---
def roll_penalty(penalty_table):
    roll = random.randint(1, len(penalty_table))
    penalty = penalty_table[roll - 1]
    # Calculate dice if present
    if "1d12" in penalty or "1d6" in penalty:
        for part in ["1d12", "1d6"]:
            if part in penalty:
                matches = roll_dice(part)
                penalty = penalty.replace(part, str(matches))
                return penalty, int(penalty.split(" ")[-2]), matches
    return penalty, 0, 0

# --- Roll Loot Table ---
def roll_loot_table(table, count):
    items = []
    for _ in range(count):
        choice = random.choice(table)
        # Handle /choose
        if isinstance(choice, str) and "[/choose" in choice:
            options = choice.split("[/choose ")[1].split("]")[0].split(", ")
            choice = choice.split("[/choose")[0].strip() + "(" + random.choice(options) + ")"
        items.append(choice)
    return items

# --- Example Map Data ---
maps = {
    "Midwich Elementary School": {
        "rolls": [
            (1, 7, "Mission fail! You run into one of the realm's denizens, be it a killer or a creature of the Fog, and are attacked! Roll on the penalties table."),
            (8, 10, "Unsuccessful mission. You find nothing."),
            (11, 13, "You found a memory fragment! Add 1d30 bloodpoints."),
            (14, 15, "Mission success! You found a small item! Roll on the small loot table."),
            (16, 17, "Mission success! You found 2 small items or 1 medium item. Roll on the appropriate loot table."),
            (18, 19, "Mission success! You found 1 large item or 2 medium items. Roll on the appropriate loot table."),
            (20, 20, "YO! You got a nice li’l haul there! You have found 5 small items and one large one. Hope you have a bag with you, and a second person. You will need help carrying all of it back.")
        ],
        "penalties": [
            "A creature in the fog has found you and killed you. When you wake back up you have a -2 penalty for 1d12 matches and are unable to scavenge until the negative penalty is gone, or it is the next day.",
            "You were injured and will take a day to recover. There is a -1 penalty for 1d6 matches.",
            "If you were carrying something scavenged earlier, you lose it [but if you had nothing, you lost nothing].",
            "You were chased until you reached your campfire, but any time you try to scavenge again you feel something following you until you reach your campfire. You are unable to scavenge until the next day."
        ],
        "small": [
            "1d4 pieces of chalk",
            "Poster [/choose star, sunflower, monkey]",
            "1d4 stack of music paper",
            "Pens/Pencils",
            "1d8 thumb tacks",
            "1d4 Medkit [+1 to your next trial]",
            "1d6 Metallic star stickers"
        ],
        "medium": [
            "Globe, out of date",
            "School text books [/choose biology, history, english]",
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
        "locker_table": [
            "D4: 1 There is a feral rat that bites you badly enough to injure your hand, no more scavenging today",
            "2 A small pair of shoes",
            "3 1d2 brand new parts [+1 to your next trial]",
            "4 There are just bloodied body parts in there. Ew."
        ]
    }
}

# --- Session State for Penalties ---
if "penalty" not in st.session_state:
    st.session_state["penalty"] = 0

# --- Map Selection ---
selected_map = st.selectbox("Choose a map:", list(maps.keys()))

# --- Roll Button ---
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
    else:
        st.write(outcome)  # Always show the descriptive message first

        # Penalties
        if "Mission fail" in outcome:
            penalty_text, val, matches = roll_penalty(map_data["penalties"])
            st.session_state["penalty"] += val
            st.write(penalty_text)

        # Memory fragment
        elif "memory fragment" in outcome:
            bloodpoints = roll_dice("1d30")
            st.write(outcome.replace("1d30", str(bloodpoints)))

        # Loot handling
        elif "Mission success" in outcome or "YO! You got a nice li’l haul" in outcome:
            # Small items only
            if "small item" in outcome and "2 small items or 1 medium item" not in outcome:
                small_items = roll_loot_table(map_data["small"], 1)
                st.write("You obtained:")
                for item in small_items:
                    st.write("-", item)

            # 2 small or 1 medium
            elif "2 small items or 1 medium item" in outcome:
                small_items = roll_loot_table(map_data["small"], 2)
                medium_item = roll_loot_table(map_data["medium"], 1)[0]
                st.write("You obtained (choose one):")
                st.write("Option 1: 2 small items")
                for item in small_items:
                    st.write("-", item)
                st.write("Option 2: 1 medium item")
                st.write("-", medium_item)

            # 1 large or 2 medium
            elif "1 large item or 2 medium items" in outcome:
                large_item = roll_loot_table(map_data["large"], 1)[0]
                medium_items = roll_loot_table(map_data["medium"], 2)
                st.write("You obtained (choose one):")
                st.write("Option 1: 1 large item")
                st.write("-", large_item)
                st.write("Option 2: 2 medium items")
                for i, item in enumerate(medium_items, start=1):
                    st.write(f"{i}.", item)

            # Big haul
            elif "5 small items and one large" in outcome:
                small_items = roll_loot_table(map_data["small"], 5)
                large_item = roll_loot_table(map_data["large"], 1)[0]
                st.write("You obtained:")
                st.write("Small items:")
                for item in small_items:
                    st.write("-", item)
                st.write("Large item:")
                st.write("-", large_item)

        # Handle locker separately if chosen
        for idx, item in enumerate(map_data.get("medium", [])):
            if "Locked locker" in item:
                locker_roll = random.randint(1, 20)
                st.write(f"You rolled: {locker_roll} for the locker check")
                locker_result = random.choice(map_data["locker_table"])
                st.write("Inside you find:", locker_result)


