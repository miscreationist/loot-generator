import streamlit as st
import random
import re

# --- Map Data ---
maps_data = {
    "Midwich Elementary School": {
        "small_items": [
            "1d4 pieces of chalk",
            "Poster [choose: star, sunflower, monkey]",
            "1d4 stack of music paper",
            "Pens/Pencils",
            "1d8 thumb tacks",
            "1d4 Medkit [+1 to your next trial]",
            "1d6 Metallic star stickers"
        ],
        "medium_items": [
            "Globe, out of date",
            "School text books [choose: biology, history, english]",
            "Projector, requires power",
            "Desk chair",
            "Mop and bucket",
            "Tray",
            "Duffle bag with 1d4 shirts",
            "Locked locker. DC 15 to break it open. If you do, roll on locker table",
            "VHS tapes. Looks to be kids movies",
            "Wall clock"
        ],
        "large_items": [
            "1d4 + 2 Teachers chairs",
            "Desk",
            "Media/Book cart, but it is upstairs, you need help carrying it down the stairs, lest the denizens of the realm hear you",
            "Bench"
        ],
        "penalties_table": [
            {"desc": "A creature in the fog has found you and killed you. When you wake back up you have a -2 penalty for 1d12 matches and are unable to scavenge until the negative penalty is gone, or it is the next day.", "penalty": "-2", "matches": "1d12"},
            {"desc": "You were injured and will take a day to recover. There is a -1 penalty for 1d6 matches.", "penalty": "-1", "matches": "1d6"},
            {"desc": "If you were carrying something scavenged earlier, you lose it [but if you had nothing, you lost nothing].", "penalty": "0", "matches": "0"},
            {"desc": "You were chased until you reached your campfire, but any time you try to scavenge again you feel something following you until you reach your campfire. You are unable to scavenge until the next day.", "penalty": "0", "matches": "0"}
        ],
        "locker_table": [
            "There is a feral rat that bites you badly enough to injure your hand, no more scavenging today",
            "A small pair of shoes",
            "1d2 brand new parts [+1 to your next trial]",
            "There are just bloodied body parts in there. Ew."
        ]
    }
}

# --- Helpers ---
def roll_dice(text):
    dice_match = re.findall(r'(\d+)d(\d+)', text)
    for match in dice_match:
        num, sides = int(match[0]), int(match[1])
        total = sum(random.randint(1, sides) for _ in range(num))
        text = text.replace(f"{num}d{sides}", str(total), 1)
    return text

def roll_item(item):
    item = roll_dice(item)
    choose_match = re.search(r"\[choose: (.+?)\]", item)
    if choose_match:
        options = choose_match.group(1).split(", ")
        choice = random.choice(options)
        item = re.sub(r"\[choose: .+?\]", f"({choice})", item)
    return item

def roll_penalty(map_data):
    penalty_entry = random.choice(map_data["penalties_table"])
    if penalty_entry["matches"] != "0":
        matches = roll_dice(penalty_entry["matches"])
        return f"{penalty_entry['desc']} Penalty: {penalty_entry['penalty']} for {matches} matches."
    else:
        return penalty_entry["desc"]

def roll_locker(map_data):
    result = random.choice(map_data["locker_table"])
    return roll_item(result)

# --- Streamlit UI ---
st.title("Scavenging")

map_name = st.selectbox("Choose a map:", list(maps_data.keys()))
map_data = maps_data[map_name]

st.write("Roll a D20 to Scavenge!")

roll_button = st.button("Roll d20")

if roll_button:
    d20 = random.randint(1, 20)
    st.write(f"You rolled: {d20}")

    loot_obtained = None
    loot_options = []

    # --- Determine outcome ---
    if 1 <= d20 <= 7:
        st.write("**Mission fail!** You run into one of the realm's denizens and are attacked!")
        penalty = roll_penalty(map_data)
        st.write(penalty)
    elif 8 <= d20 <= 10:
        st.write("**Unsuccessful mission.** You find nothing.")
    elif 11 <= d20 <= 13:
        bloodpoints = roll_dice("1d30")
        st.write(f"You found a memory fragment! Add {bloodpoints} bloodpoints.")
    elif 14 <= d20 <= 15:
        st.write("**Mission success!** You found a small item!")
        loot_obtained = [roll_item(random.choice(map_data["small_items"]))]
    elif 16 <= d20 <= 17:
        st.write("**Mission success!** You found 2 small items OR 1 medium item!")
        option1 = [roll_item(random.choice(map_data["small_items"])),
                   roll_item(random.choice(map_data["small_items"]))]
        option2 = [roll_item(random.choice(map_data["medium_items"]))]
        loot_options = [option1, option2]
    elif 18 <= d20 <= 19:
        st.write("**Mission success!** You found 1 large item OR 2 medium items!")
        option1 = [roll_item(random.choice(map_data["large_items"]))]
        option2 = [roll_item(random.choice(map_data["medium_items"])),
                   roll_item(random.choice(map_data["medium_items"]))]
        loot_options = [option1, option2]
    elif d20 == 20:
        st.write("**YO! You got a nice li’l haul there!** 5 small items + 1 large item.")
        loot_obtained = [roll_item(random.choice(map_data["small_items"])) for _ in range(5)]
        loot_obtained.append(roll_item(random.choice(map_data["large_items"])))

    # --- Special locker handling ---
    if loot_obtained:
        for i, item in enumerate(loot_obtained):
            if "Locked locker" in item:
                st.write(f"You found a locked locker! DC 15 to open.")
                locker_roll = random.randint(1, 20)
                st.write(f"You rolled {locker_roll} for the locker check.")
                if locker_roll >= 15:
                    st.write("Success! Inside you find:")
                    locker_items = roll_locker(map_data)
                    st.write(f"- {locker_items}")
                else:
                    st.write("Failed to open the locker.")

    # --- Display loot ---
    if loot_options:
        st.write("You obtained (choose one option):")
        for idx, option in enumerate(loot_options, 1):
            st.write(f"Option {idx}: {', '.join(option)}")

    if loot_obtained:
        st.write("You obtained:")
        for item in loot_obtained:
            if "Locked locker" not in item:
                st.write(f"- {item}")
