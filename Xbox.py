from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import _find_element, _find_elements, presence_of_element_located
import time
import pandas as pd

driver = webdriver.Chrome()


def return_game_stats(div: str) -> WebDriverWait:
    return WebDriverWait(driver, 10).until(
        lambda x: x.find_elements_by_class_name(div)
    )


def stat_exist_time(game_stats: list) -> str:
    try:
        time_played = game_stats[-1]
        time_played = time_played.get_attribute("innerHTML").strip()
        return time_played
    except:
        return "0"


def get_gamerscore(game_stats: list) -> list:
    try:
        gamer_score = game_stats[0]
        gamer_score = gamer_score.get_attribute(
            "innerHTML").replace(" ", "").replace(",", "").strip().split("/")
        return gamer_score
    except:
        return [0, 0]


def wait_for_id(id: str, time=10) -> WebDriverWait:
    return WebDriverWait(driver, time).until(
        lambda x: x.find_element_by_id(id)
    )


driver.get(
    "https://account.xbox.com/en-us/Profile?xr=socialtwistnav&activetab=main:mainTab2")

list_of_games = wait_for_id("gamesList", 180)
games = list_of_games.find_elements_by_tag_name("li")

time_played_urls = []
game_names = []

for game in games:
    game_wrapper = game.find_element_by_class_name(
        "recentProgressLinkWrapper")
    url = game_wrapper.get_attribute("href")
    time_played_urls.append(url)
    game_name = game_wrapper.get_attribute("aria-label")
    game_names.append(game_name)

df = pd.DataFrame(columns=['Game_Name', 'Minutes_Played',
                  "GamerScore_Earned", "GamerScore_Possible"])

for url, name in zip(time_played_urls[0:5], game_names[:5]):
    driver.get(url)
    game_stats = return_game_stats("statdata")
    time_played = stat_exist_time(game_stats)
    gamer_score_earned, gamer_score_max = get_gamerscore(game_stats)
    df = df.append(
        {
            "Game_Name": name,
            "Minutes_Played": time_played,
            "GamerScore_Earned": gamer_score_earned,
            "GamerScore_Possible": gamer_score_max
        }, ignore_index=True)
    print(time_played, name, gamer_score_earned, gamer_score_max)

df[["Minutes_Played", "GamerScore_Earned", "GamerScore_Possible"]] = df[[
    "Minutes_Played", "GamerScore_Earned", "GamerScore_Possible"]].astype(int)
print(df)
print(df.info())
time.sleep(300)
