from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
import os
import pandas as pd
import sys
import time

# Asking the user for what browser they want to use
driver = None
print("Please enter a number for the browser you want to use")
print("1 Google Chrome")
print("2 FireFox")
choice = input("Please enter your selection here: ").strip()
try:
    if choice == "1":
        driver = webdriver.Chrome()
    elif choice == "2":
        driver = webdriver.Firefox()
    else:
        print("Invalid input! Please type in 1 or 2.")
        time.sleep(10)
        sys.exit()
except Exception as e:
    print(e)
    print("Do you have the correct driver for Selenium? Please refer to github for help.")
    time.sleep(10)
    sys.exit()
cwd = os.getcwd()

# Returns game_stats which holds the listing of all games on the xbox site


def return_game_stats(div: str) -> WebDriverWait:
    return WebDriverWait(driver, 10).until(
        lambda x: x.find_elements_by_class_name(div)
    )

# Tries to get html element that has the minutes played for the game


def stat_exist_time(game_stats: list) -> str:
    try:
        time_played = game_stats[-1]
        time_played = time_played.get_attribute(
            "innerHTML").strip().replace(",", "")
        if "%" in time_played:
            time_played = game_stats[-2]
            time_played = time_played.get_attribute(
                "innerHTML").strip().replace(",", "")
        return time_played
    except Exception as e:
        print(e)
        return "0"

# Returns a list of the GamerScore a player has earned and the max possible amount for a game


def get_gamerscore(game_stats: list) -> list:
    try:
        gamer_score = game_stats[0]
        gamer_score = gamer_score.get_attribute(
            "innerHTML").replace(" ", "").replace(",", "").strip().split("/")
        return gamer_score
    except Exception as e:
        print(e)
        return [0, 0]

# Gets the number of achievements a player has earned


def get_achievement_num(game_stats: list) -> int:
    try:
        achievements = game_stats[1]
        achievements = achievements.get_attribute("innerHTML").strip()
        return int(achievements)
    except Exception as e:
        print(e)
        return 0

# Waits for a HTML element with the same id to show up on the page


def wait_for_id(id: str, time=10) -> WebDriverWait:
    return WebDriverWait(driver, time).until(
        lambda x: x.find_element_by_id(id)
    )


# User logging in
driver.get(
    "https://account.xbox.com/en-us/Profile?xr=socialtwistnav&activetab=main:mainTab2")

try:
    list_of_games = wait_for_id("gamesList", 300)
except Exception as e:
    print(e)
    print("Could not read game list in the allocated time (300 secs). Did you login in that time?")
    time.sleep(5)
    driver.quit()
    sys.exit()

games = list_of_games.find_elements_by_tag_name("li")
game_urls = []
game_names = []

# Goes through the game list and appends each href link to game_urls, and appends the name of the game as well
for game in games:
    game_wrapper = game.find_element_by_class_name(
        "recentProgressLinkWrapper")
    url = game_wrapper.get_attribute("href")
    game_urls.append(url)
    game_name = game_wrapper.get_attribute("aria-label")
    game_names.append(game_name)

# Pandas dataframe for storing the info
df = pd.DataFrame(columns=['Game_Name', 'Minutes_Played',
                  "GamerScore_Earned", "GamerScore_Possible", "Number_of_Achievements"])

"""
For each url page, try to get the time played in minutes, gamer score, and number of achievements for each game, then append it to the df
"""
current_game = 1
total_games = len(game_names)
for url, name in zip(game_urls, game_names):
    driver.get(url)
    print("Getting info for : {:<70}{:<4} out of {:<4}".format(
        name, current_game, total_games))
    current_game += 1
    game_stats = return_game_stats("statdata")
    time_played = stat_exist_time(game_stats)
    gamer_score_earned, gamer_score_max = get_gamerscore(game_stats)
    num_of_achievements = get_achievement_num(game_stats)
    df = df.append(
        {
            "Game_Name": name,
            "Minutes_Played": time_played,
            "GamerScore_Earned": gamer_score_earned,
            "GamerScore_Possible": gamer_score_max,
            "Number_of_Achievements": num_of_achievements
        }, ignore_index=True)


# Some new update caused some numbers to be "---", these lines should replace those values with 0 (11/16/21)
def replaceDashes(element):
    if element == "---":
        element = "0"
    return element


df[["Minutes_Played", "GamerScore_Earned", "GamerScore_Possible", "Number_of_Achievements"]] = df[[
    "Minutes_Played", "GamerScore_Earned", "GamerScore_Possible", "Number_of_Achievements"]].applymap(replaceDashes)
# Converts some columns to int type
df[["Minutes_Played", "GamerScore_Earned", "GamerScore_Possible", "Number_of_Achievements"]] = df[[
    "Minutes_Played", "GamerScore_Earned", "GamerScore_Possible", "Number_of_Achievements"]].astype(int)

# Asking the user if they want to include games with 0 minutes played
choice = input(
    "Do you want to include games with 0 minutes played in your csv? (Y/N)")
choice = choice.upper().strip()
if choice == 'N':
    zero_minutes_filter = df["Minutes_Played"] != 0
    df = df[zero_minutes_filter]

# Creating csv file and quiting
print("Dumping data into XboxStats.csv")
df.to_csv(cwd + r"\XboxStats.csv", index=False)
print("Finished! Closing your browser now :) ")
driver.quit()
