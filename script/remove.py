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
from follow import loginTwitter
from follow import getAccountsFromList

dotenv_path = join(dirname(__file__), 'config', '.env')
load_dotenv(dotenv_path)

USER_NAME = os.environ.get("USER_NAME")
PASSWORD = os.environ.get("PASSWORD")
REMOVE_IGNORE_LISTS = os.environ.get("REMOVE_IGNORE_LISTS")
TOTAL_REMOVE_LIMIT = 30
remove_ignore_lists = REMOVE_IGNORE_LISTS.split(',')

remain_remove_count = TOTAL_REMOVE_LIMIT

def removeKataomoi(browser: webdriver, safe_accounts):
    global remain_remove_count
    """
    片思いったーにログインする
    :param browser: webdriver
    """

    # 片思いったーにアクセス
    browser.get('http://kataomoi.net/redirect.php')
    sleep(1)

    url = browser.current_url
    is_confirm = url.startswith("https://api.twitter.com/oauth/authorize?oauth_token")

    if is_confirm:
        submit_btn = browser.find_element_by_id("allow")
        submit_btn.click()
        sleep(1)
    else:
        # ログイン情報の入力
        username_or_email = browser.find_element_by_xpath("//*[@id='username_or_email']")
        username_or_email.send_keys(USER_NAME)
        password = browser.find_element_by_xpath("//*[@id='password']")
        password.send_keys(PASSWORD)
        # ログイン
        password.submit()
        sleep(1)

    browser.get('http://kataomoi.net/find_one_way.php')
    sleep(1)

    trs = browser.find_elements_by_tag_name("tr")

    # 古い順位に並び替え
    reversed_trs = reversed(trs)

    print('▼フォロー解除中…▼')
    for tr in reversed_trs:
        if remain_remove_count <= 0:
            break
        tds = tr.find_elements_by_tag_name("td")
        if len(tds) > 1 and not(tds[1].find_element_by_tag_name("a").text in safe_accounts):
            print(tds[1].find_element_by_tag_name("a").text)
            tr.find_elements_by_tag_name("span")[0].click()
            remain_remove_count = remain_remove_count - 1
            sleep(0.5)

if __name__ == '__main__':
    try:
        #browser = webdriver.Firefox()  # 普通のFilefoxを制御する場合
        #browser = webdriver.Chrome()   # 普通のChromeを制御する場合

        # HEADLESSブラウザに接続
        browser = webdriver.Remote(
            command_executor='http://selenium-hub:4444/wd/hub',
            desired_capabilities=DesiredCapabilities.CHROME)

        # リストの中のアカウントはremoveしない
        loginTwitter(browser)
        safe_accounts = []
        for remove_ignore_list in remove_ignore_lists:
            ignore_list = getAccountsFromList(browser, remove_ignore_list)
            safe_accounts.extend(ignore_list)
        # 片思いったーにログイン
        print('▼以下のアカウントはフォロー解除されません▼')
        print(safe_accounts)
        removeKataomoi(browser, safe_accounts)

    finally:
        # 終了
        browser.close()
        browser.quit()

