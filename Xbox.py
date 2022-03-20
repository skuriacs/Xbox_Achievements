from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
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
    try: 
        return WebDriverWait(driver, 20).until(
            lambda x: x.find_elements(by= By.CLASS_NAME, value = div)
        )
    except Exception as e:
        print("Webdriver probably timed out, no stats found for game")
        return []

# Tries to get html element that has the minutes played for the game


def stat_exist_time(game_stats: list) -> int:
    try:
        for game_stat_box in game_stats:
            if  game_stat_box.find_element(by = By.CLASS_NAME, value= "statlabel").get_attribute("innerHTML") == "Minutes Played":
                time_played_stat = game_stat_box.find_element(by = By.CLASS_NAME, value= "statdata")
                time_played = time_played_stat.get_attribute(
                    "innerHTML").strip().replace(",", "")
                return int(time_played)
        return "0"
    except Exception as e:
        print(e)
        return 0

# Returns a list of the GamerScore a player has earned and the max possible amount for a game


def get_gamerscore(game_stats: list) -> list:
    if len(game_stats) < 2:
        return [0, 0]

    for game_stat_box in game_stats:
        try:
            if  game_stat_box.find_element(by = By.CLASS_NAME, value= "statlabel").get_attribute("innerHTML") == "Gamerscore":
                game_score_stat = game_stat_box.find_element(by = By.CLASS_NAME, value= "statdata")
                gamer_score = game_score_stat.get_attribute(
                "innerHTML").replace(" ", "").replace(",", "").strip().split("/")
                return gamer_score
        except Exception as e:
            print(e)
            return [0,0]

    return [0, 0]

# Gets the number of achievements a player has earned


def get_achievement_num(game_stats: list) -> int:
    try:
        for game_stat_box in game_stats:
            if  game_stat_box.find_element(by = By.CLASS_NAME, value= "statlabel").get_attribute("innerHTML") == "Achievements":
                achieve_stat = game_stat_box.find_element(by = By.CLASS_NAME, value= "statdata")
                num_achieve_stats = int(achieve_stat.get_attribute("innerHTML"))
                return num_achieve_stats if num_achieve_stats else 0
    except Exception as e:
        print(e)
        return 0

# Waits for a HTML element with the same id to show up on the page


def wait_for_id(id: str, time=10) -> WebDriverWait:
    return WebDriverWait(driver, time).until(
        lambda x: x.find_elements(by = By.ID, value = id)
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

games = list_of_games[0].find_elements(by = By.TAG_NAME , value = "li")
game_urls = []
game_names = []

# Goes through the game list and appends each href link to game_urls, and appends the name of the game as well
for game in games:
    game_wrapper = game.find_element(by = By.CLASS_NAME,
        value = "recentProgressLinkWrapper")
    url = game_wrapper.get_attribute("href")
    game_urls.append(url)
    game_name = game_wrapper.get_attribute("aria-label")
    game_names.append(game_name)

# Pandas dataframe for storing the info
"""
For each url page, try to get the time played in minutes, gamer score, and number of achievements for each game, then append it to the df
"""
total_games = len(game_names)
game_stats_all = []
for url, name, current_game_num in zip(game_urls, game_names, range(1,total_games)):
    driver.get(url)
    print("Getting info for : {:<70}{:<4} out of {:<4}".format(
        name, current_game_num, total_games))
    game_stats = return_game_stats("stattile")
    if len(game_stats) == 0:
        game_stats.append([name,0,0,0,0])
        continue
    time_played = stat_exist_time(game_stats)
    gamer_score_earned, gamer_score_max = get_gamerscore(game_stats)
    num_of_achievements = get_achievement_num(game_stats)
    game_stats_all.append([name,time_played,gamer_score_earned,gamer_score_max,num_of_achievements])



# Some new update caused some numbers to be "---", these lines should replace those values with 0 (11/16/21)
def replaceDashes(element):
    if element == "---":
        element = "0"
    return element

df : pd.DataFrame = pd.DataFrame(game_stats_all, columns= ['Game_Name', 'Minutes_Played',
                  "GamerScore_Earned", "GamerScore_Possible", "Number_of_Achievements"])


df = df.fillna(value = 0)

df[["Minutes_Played", "GamerScore_Earned", "GamerScore_Possible", "Number_of_Achievements"]] = df[[
    "Minutes_Played", "GamerScore_Earned", "GamerScore_Possible", "Number_of_Achievements"]].applymap(replaceDashes)
# Converts some columns to int type
df[["Minutes_Played", "GamerScore_Earned", "GamerScore_Possible", "Number_of_Achievements"]] = df[[
    "Minutes_Played", "GamerScore_Earned", "GamerScore_Possible", "Number_of_Achievements"]].astype(int)

# Asking the user if they want to include games with 0 minutes played
choice = input(
    "Do you want to include games with 0 minutes played in your csv? (Y/N)")
choice = choice.upper().strip()
if choice.capitalize().strip() == 'N':
    zero_minutes_filter = df["Minutes_Played"] != 0
    df = df[zero_minutes_filter]

# Creating csv file and quiting
print("Dumping data into XboxStats.csv")
df.to_csv(cwd + r"\XboxStats.csv", index=False)
print("Finished! Closing your browser now :) ")
driver.quit()
