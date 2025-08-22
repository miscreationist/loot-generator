import streamlit as st
import random
import re

# Shared penalties & locker table
penalties_table = [
    "A creature in the fog has found you and killed you. When you wake back up you have a -2 penalty for 1d12 matches and are unable to scavenge until the negative penalty is gone, or it is the next day",
    "You were injured and will take a day to recover. There is a -1 penalty for 1d6 matches",
    "If you were carrying something scavenged earlier, you lose it. If you had nothing, you lost nothing.",
    "You were chased until you reached your campfire, but any time you try to scavenge again you feel something following you until you reach your campfire. You are unable to scavenge until the next day"
]

locker_table = [
    "There is a feral rat that bites you badly enough to injure your hand, no more scavenging today",
    "A small pair of shoes",
    "1d2 brand new parts [+1 to your next trial]",
    "There are just bloodied body parts in there. Ew."
]

# Maps dictionary
maps = {
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
        ]
    },
    "Dvarka Darkwood - Nostromo": {
        "small_items": [
            "1d2 bundle of wires/cables",
            "1d4 Metal scraps",
            "Key card [if you don't use it, you lose it. But if you do use it!! You get either a med kit or a toolbox +1 to your next trial!]",
            "Vial of android goop — yes, from the one on the table, you were curious!",
            "A bundle of dried long grass — could be a fire starter. And ough, it smells good, too! Alien heather!",
            "1d2 Computer components? These have to have a use...",
            "Cat treats? Is there a cat around here?",
            "A fossil of some sort of creature. Kinda looks like the one that is in the med bay on the big ship",
            "Drinking bird toy. There is no cup for it to drink from, but he does have a fancy top hat"
        ],
        "medium_items": [
            "Old vent cover, but it looks like it could be used over a campfire to cook something on",
            "Portable light! Seems to have a limited power source, though [1d10 uses]",
            "Utility belt from the astronaut suit",
            "Head lamp from the astronaut helmet — 1d10 uses",
            "1d6 Large, blue plants. Can have different effects! 1d4 to figure out what this bundle is",
            "Yellow tarp, very worn, but can be used as ground cover",
            "Canister of fuel, 1/4 of the way full",
            "Locked locker. DC 15 to break it open. If you do, roll on locker table"
        ],
        "large_items": [
            "Utility box that contains 1d8 + 2 amount of medkits and toolboxes [+1 to each trial you bring those to]",
            "Metal plates with atmospheric entry burns, smells faintly of ozone",
            "Metal door, definitely busted, but still sturdy looking",
            "Computer monitor, though it does look rather busted up. Maybe with some extra components you may be able to fix it; could double as a TV monitor [1d6 +2 amount of components to fix as well as a rolling 1d20 with a DC 15 to fix it properly]"
        ]
    }
}

def roll_dice(text):
    """Replace 1dX or NdX dice rolls with actual numbers."""
    dice_match = re.findall(r'(\d+)d(\d+)', text)
    for match in dice_match:
        num, sides = int(match[0]), int(match[1])
        total = sum(random.randint(1, sides) for _ in range(num))
        text = text.replace(f"{num}d{sides}", str(total), 1)
    return text

def roll_item(item):
    """Roll item, replace choose options with a random pick (in parentheses)."""
    item = roll_dice(item)
    choose_match = re.search(r"\[choose: (.+?)\]", item)
    if choose_match:
        options = choose_match.group(1).split(", ")
        choice = random.choice(options)
        item = re.sub(r"\[choose: .+?\]", f"({choice.capitalize()})", item)
        if item.lower().startswith("poster"):
            item = "Poster " + item[len("Poster "):]
        elif item.lower().startswith("school text books"):
            item = "School Text Book " + item[len("School Text Books "):]
    return item

def roll_penalty():
    penalty_text = random.choice(penalties_table)
    penalty_text = roll_dice(penalty_text) 
    return penalty_text

def roll_locker():
    result = random.choice(locker_table)
    return roll_item(result)

st.title("Scavenging")

map_choices = ["Random Map"] + list(maps.keys())
map_name = st.selectbox("Choose a map", map_choices)

st.write("Roll a D20 to Scavenge!")

roll_button = st.button("Roll D20")

if roll_button:
    if map_name == "Random Map":
        map_name = random.choice(list(maps.keys()))
        st.write(f" Randomly selected map: **{map_name}**")

    D20 = random.randint(1, 20)
    st.write(f"You rolled: {D20}")

    loot_obtained = []
    mission_message = ""

    if 1 <= D20 <= 7:
        mission_message = "Mission fail! You run into one of the realm's denizens and are attacked!"
        st.write(mission_message)
        penalty = roll_penalty()
        st.write(f"Penalty: {penalty}")

    elif 8 <= D20 <= 10:
        mission_message = "Unsuccessful mission. You find nothing."
        st.write(mission_message)

    elif 11 <= D20 <= 13:
        mission_message = "Mission success! You found a memory fragment!"
        st.write(mission_message)
        bloodpoints = roll_dice("1d30")
        st.write(f"Add {bloodpoints} bloodpoints.")

    elif 14 <= D20 <= 15:
        mission_message = "Mission success! You found a small item!"
        st.write(mission_message)
        loot_obtained.append(roll_item(random.choice(maps[map_name]["small_items"])))

    elif 16 <= D20 <= 17:
        mission_message = "Mission success! You found 2 small items OR 1 medium item."
        st.write(mission_message)

        option1 = [roll_item(random.choice(maps[map_name]["small_items"])) for _ in range(2)]
        option2 = [roll_item(random.choice(maps[map_name]["medium_items"]))]

        loot_obtained.append(("Option 1: 2 small items", option1))
        loot_obtained.append(("Option 2: 1 medium item", option2))

    elif 18 <= D20 <= 19:
        mission_message = "Mission success! You found 1 large item OR 2 medium items."
        st.write(mission_message)

        option1 = [roll_item(random.choice(maps[map_name]["large_items"]))]
        option2 = [roll_item(random.choice(maps[map_name]["medium_items"])) for _ in range(2)]

        loot_obtained.append(("Option 1: 1 large item", option1))
        loot_obtained.append(("Option 2: 2 medium items", option2))
        
    elif D20 == 20:
        mission_message = "YO! You got a nice li’l haul! 5 small items and 1 large item!"
        st.write(mission_message)
        loot_obtained.extend([("Main Loot", [roll_item(random.choice(maps[map_name]["small_items"])) for _ in range(5)] + [roll_item(random.choice(maps[map_name]["large_items"]))])])

    # Handle locked locker rolls
    for i, item_group in enumerate(loot_obtained):
        if isinstance(item_group, tuple):
            title, items = item_group
            new_items = []
            for item in items:
                if "Locked locker" in item:
                    locker_roll = random.randint(1, 20)
                    locker_text = f"Locked locker roll: {locker_roll} DC 15"
                    if locker_roll >= 15:
                        locker_items = roll_locker()
                        if isinstance(locker_items, list):
                            locker_text += " -> Success! Inside: " + ", ".join(locker_items)
                        else:
                            locker_text += " -> Success! Inside: " + locker_items
                    else:
                        locker_text += " -> Failed to open the locker."
                    new_items.append(locker_text)
                else:
                    new_items.append(item)
            loot_obtained[i] = (title, new_items)
        else:
            if "Locked locker" in item_group:
                locker_roll = random.randint(1, 20)
                locker_text = f"Locked locker roll: {locker_roll} DC 15"
                if locker_roll >= 15:
                    locker_items = roll_locker()
                    if isinstance(locker_items, list):
                        locker_text += " -> Success! Inside: " + ", ".join(locker_items)
                    else:
                        locker_text += " -> Success! Inside: " + locker_items
                else:
                    locker_text += " -> Failed to open the locker."
                loot_obtained[i] = locker_text

    if loot_obtained:
        st.write("You obtained:")
        for item_group in loot_obtained:
            if isinstance(item_group, tuple):
                title, items = item_group
                st.write(f"**{title}**")
                for idx, item in enumerate(items, start=1):
                    st.write(f"{idx}. {item}")
            else:
                st.write(f"- {item_group}")

