from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import _find_element, presence_of_element_located
import time
import pandas as pd

driver = webdriver.Chrome()
user_data = open("userdata.txt", "r")
user_content = user_data.read().splitlines()
user_name = user_content[0]
user_password = user_content[1]
user_data.close()


def stat_exist(div):
    try:
        time_played = WebDriverWait(driver, 10).until(
            lambda x: x.find_elements_by_class_name(div)
        )
        time_played = time_played[-1]
        time_played = time_played.get_attribute("innerHTML").strip()
        return time_played
    except:
        return "-1"


driver.get(
    "https://account.xbox.com/en-us/Profile?xr=socialtwistnav&activetab=main:mainTab2")

email = WebDriverWait(driver, 10).until(
    lambda x: x.find_element_by_id("i0116")
)
email.send_keys(user_name)
submit_email = driver.find_element_by_id("idSIButton9")
submit_email.click()
password = WebDriverWait(driver, 10).until(
    lambda x: x.find_element_by_id("i0118")
)
password.send_keys(user_password)
time.sleep(0.5)
password = WebDriverWait(driver, 10).until(
    lambda x: x.find_element_by_id("i0118")
)
password.submit()
list_of_games = WebDriverWait(driver, 10).until(
    lambda x: x.find_element_by_id("gamesList")
)
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

df = pd.DataFrame(columns=['Game_Name', 'Minutes_Played'])

for url, name in zip(time_played_urls[:5], game_names[:5]):
    driver.get(url)
    time_played = stat_exist("statdata")
    df = df.append(
        {"Game_Name": name, "Minutes_Played": time_played}, ignore_index=True)
    print(time_played, name)
print(df)
