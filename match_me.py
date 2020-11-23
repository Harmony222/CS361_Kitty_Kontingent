from config import map_api_key
import requests
import json

# desired difficulty = feeling selection + fitness level
# difficulty_num = {
#     2: "green",
#     3: "greenBlue",
#     4: "blue",
#     5: "blueBlack",
#     6: "black",
#     7: "dblack"
# }
# def filter_trails(trails_list, feeling, fitness):
#     """
#     Filters trails based on feeling selection and fitness level.
#     Feelings are 1, 2, and 3 for "easy and chill", "match my fitness level"
#     and "challenge me!". Fitness levels are 1-4.
#     """
#     filtered_trails = []
#     filter_difficulty = difficulty_num[int(feeling) + int(fitness)]

#     # filter trails - trail[3] is eg. "green"
#     for trail in trails_list:
#         if filter_difficulty == trail[3]:
#             filtered_trails.append(trail)
#     return filtered_trails

# int representation of trail difficulty for feeling + fitness
diff_dict = { "green": 0, "greenBlue": 1, "blue": 2, "blueBlack": 3, "black": 4, "dblack": 5}

def filter_trails(trails_list, feeling, fitness):
    """
    Filters trails based on feeling selection and fitness level.
    Feelings are 1, 2, and 3 for "easy and chill", "match my fitness level"
    and "challenge me!". Fitness levels are 1-4.
    """
    filtered_trails = []
    feel, fit = int(feeling), int(fitness)

    # filter trails - trail[3] is eg. "green"
    for trail in trails_list:
        if feel == 1:
            if fit > diff_dict[trail[3]]:
                filtered_trails.append(trail)
        elif feel == 2:
            if fit == diff_dict[trail[3]]:
                filtered_trails.append(trail)
        else:
            if fit < diff_dict[trail[3]]:
                filtered_trails.append(trail)

    return filtered_trails


def trail_locations(trails):
    """
    Returns a list of trails data for map trail markers.
    Data is formatted for the map javascript code.
    """
    locations = []
    for trail in trails:
        # 0:name, 1:latitude, 2:longitude, 3:summary, 4:length,
        # 5:rating, 6: difficulty, 7:location, 8:directions_url, 9:gear_url
        locations.append([trail[1], trail[10], trail[11], trail[12], trail[2],
                          trail[4], trail[3], trail[5], trail[13], trail[14]])

    return json.dumps(locations)

# imported directly to app.py to avoid additional function imports and calls
# def get_map_api_key():
#     return map_api_key

def calculate_fitness(days, hours, miles, intensity):
    """calculate the user's fitness level"""
    # first get the average number of hours of physical activity per week
    level = avg_hours = int(days) * int(hours) // 7
    intensity, miles = int(intensity), int(miles)
    # adjust level based off of the user's intensity when hiking
    if intensity > avg_hours and avg_hours <= 3:
        level += 1
    elif intensity < avg_hours and avg_hours >= 2:
        level -= 1
    # adjust level based off of the user's average length for a hike
    if miles > avg_hours and level <= 3:
        level += 1
    elif miles < avg_hours and level >= 2:
        level -= 1
    # ensure level is a value from 1-4
    if level <= 1:
        level = 1

    return level
