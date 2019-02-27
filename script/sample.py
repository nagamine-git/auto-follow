#!/usr/local/bin/python3
from selenium import webdriver
#from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from time import sleep
import datetime
import os
from os.path import join, dirname
from dotenv import load_dotenv
import random
from tqdm import tqdm

dotenv_path = join(dirname(__file__), 'config', '.env')
load_dotenv(dotenv_path)

USER_NAME = os.environ.get("USER_NAME")
PASSWORD = os.environ.get("PASSWORD")
LIST_NAME = 'media'
TOTAL_FOLLOW_LIMIT = 30
ACCOUNT_FOLLOW_LIMIT = 5

remain_follow_count = TOTAL_FOLLOW_LIMIT

def loginTwitter(browser: webdriver):
    """
    Twitterにログインする
    :param browser: webdriver
    """
    # スクリーンショットのファイル名用に日付を取得
    dt = datetime.datetime.today()
    dtstr = dt.strftime("%Y%m%d%H%M%S")

    # twitterにアクセス
    browser.get('https://twitter.com/login')
    sleep(1)

   # ログイン情報の入力
    username_or_email = browser.find_element_by_xpath("//*[@id='page-container']/div/div[1]/form/fieldset/div[1]/input")
    username_or_email.send_keys(USER_NAME)
    password = browser.find_element_by_xpath("//*[@id='page-container']/div/div[1]/form/fieldset/div[2]/input")
    password.send_keys(PASSWORD)
    # ログイン
    password.submit()
    sleep(1)

def getAccountsFromList(browser: webdriver):
    """
    Twitterでリストのフォロワーを抽出する
    :param browser: webdriver
    """
    # スクリーンショットのファイル名用に日付を取得
    dt = datetime.datetime.today()
    dtstr = dt.strftime("%Y%m%d%H%M%S")

    # リストにアクセスする
    browser.get('https://twitter.com/'+ USER_NAME +'/lists/'+ LIST_NAME +'/members')
    browser.save_screenshot('images/' + dtstr + '.png')

    accounts = browser.find_elements_by_class_name("js-actionable-user")
    account_list = []
    for account in accounts:
        account_list.append(account.get_attribute('data-screen-name'))
    return account_list

def getNotFollowingAccounts(browser: webdriver, account):
    global remain_follow_count
    """
    Twitterでアカウントのフォロワーをフォローする
    :param browser: webdriver
    """
    # スクリーンショットのファイル名用に日付を取得
    dt = datetime.datetime.today()
    dtstr = dt.strftime("%Y%m%d%H%M%S")

    # リストにアクセスする
    browser.get('https://twitter.com/'+ account + '/followers')
    grid = browser.find_element_by_class_name("GridTimeline")
    profile_cards = grid.find_elements_by_class_name("js-actionable-user")
    limit = ACCOUNT_FOLLOW_LIMIT
    for profile_card in profile_cards:
        if remain_follow_count > 0:
            is_follow = profile_card.find_elements_by_class_name("not-following")# ない
            description = profile_card.find_element_by_class_name("ProfileCard-bio")
            description_text = description.text
            follow_btn = profile_card.find_elements_by_class_name("follow-text")
            if len(description_text) > 20 and is_follow != [] and follow_btn != [] :
                follow_btn[0].click()
                sleep(1)
                remain_follow_count = remain_follow_count - 1
        else:
            break

if __name__ == '__main__':
    try:
        #browser = webdriver.Firefox()  # 普通のFilefoxを制御する場合
        #browser = webdriver.Chrome()   # 普通のChromeを制御する場合

        # HEADLESSブラウザに接続
        browser = webdriver.Remote(
            command_executor='http://selenium-hub:4444/wd/hub',
            desired_capabilities=DesiredCapabilities.CHROME)

        # Twitterにログイン
        loginTwitter(browser)
        # Twitterで自動フォローする
        accounts = getAccountsFromList(browser)
        random.shuffle(accounts)
        for account in tqdm(accounts):
            if account != None:
                getNotFollowingAccounts(browser, account)

    finally:
        # 終了
        browser.close()
        browser.quit()

