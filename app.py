import streamlit as st
import json
import random
import re

# Load JSON
with open("maps_loot.json") as f:
    maps_data = json.load(f)

st.title("Loot Generator")

# Choose map
map_name = st.selectbox("Choose a map", list(maps_data.keys()))
map_data = maps_data[map_name]

# Roll D20
if st.button("Roll d20"):
    roll = random.randint(1, 20)
    st.write(f"You rolled: {roll} on {map_name}")

    # Find the range
    for key, outcome in map_data["rolls"].items():
        match_range = re.findall(r'\d+', key)
        if len(match_range) == 2:
            low, high = int(match_range[0]), int(match_range[1])
        else:
            low = high = int(match_range[0])
        if low <= roll <= high:
            result = outcome
            break

    st.write(result)

    # Loot handling
    loot_obtained = []

    def roll_item(item):
        # Handle dX
        dice_match = re.match(r"1d(\d+)", item)
        if dice_match:
            num = random.randint(1, int(dice_match.group(1)))
            item = f"{num} {item.split(' ', 1)[1]}"
        # Handle choose
        choose_match = re.search(r"\[choose: (.+?)\]", item)
        if choose_match:
            options = choose_match.group(1).split(", ")
            choice = random.choice(options)
            item = re.sub(r"\[choose: .+?\]", choice, item)
        return item

    if "small" in result.lower():
        loot_obtained.append(roll_item(random.choice(map_data["small_items"])))
    if "medium" in result.lower():
        loot_obtained.append(roll_item(random.choice(map_data["medium_items"])))
    if "large" in result.lower():
        loot_obtained.append(roll_item(random.choice(map_data["large_items"])))

    # Check for locked locker
    for i, litem in enumerate(loot_obtained):
        if "Locked locker" in litem:
            st.write("You found a locked locker! DC 15 to open.")
            check = random.randint(1, 20)
            st.write(f"You rolled: {check} for the locker check")
            if check >= 15:
                loot_obtained[i] = "Success! Inside you find: " + roll_item(random.choice(map_data["locker_table"]))
            else:
                loot_obtained[i] = "Failed to open locker."

    if "Mission fail" in result:
        penalty = random.choice(map_data["penalties_table"])
        st.write(f"Penalty applied: {penalty}")

    if loot_obtained:
        st.write("You obtained:")
        for l in loot_obtained:
            st.write(f"- {l}")
