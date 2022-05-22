import time
import json
from os import path
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.service import Service


def install_addon(driver, path, temporary=None):
    payload = {
        "path": path
    }
    if temporary:
        payload["temporary"] = temporary

    _ = driver.execute("INSTALL_ADDON", payload)["value"]

    return


# create object for tracking URLs and cookie results
def create_tracking_dict(url_file):
    # list of URLs
    with open(url_file, 'r') as file:
        urls = file.read().splitlines()

    tracking_dict = {url: [] for url in urls}

    return tracking_dict


# write to output file
def save_tracking_dict(data, file_out):
    with open(file_out, 'w') as out:
        json.dump(data, out, indent=4)


# Read cookies
def get_cookies(driver, link, position):
    try:
        # call website
        driver.get(link)
        # sleep for 3 seconds for page loading & ConsentOMatic
        time.sleep(3)

        # read cookies
        my_cookies = driver.get_cookies()


    except WebDriverException:
        print('Error: WebDriverException')
        my_cookies = []

    # print the currently viewed page to console
    print(f"{position}) {driver.title} - {driver.current_url}")

    return my_cookies


# store dict to file
def write_output(tracking_dict):
    timeString = time.strftime("%Y-%m-%d_%H-%M-%S")
    save_tracking_dict(tracking_dict, f"cookies_{timeString}.json")

    cookies_per_page = {url: len(cookies)
                        for url, cookies in tracking_dict.items()}
    total_cookies = sum(cookies_per_page.values())
    print(f"Timestamp: {timeString}")
    print(f"Total Cookies: {total_cookies}")


def process_pages(driver):
    # load dict with URLs and empty lists for cookie storage
    tracking_dict = create_tracking_dict('top_100_links.txt')

    # iterate over url and cookie_storage, append new cookies
    for url, cookie_storage in tracking_dict.items():
        pos = list(tracking_dict).index(url) + 1
        cookie_storage.extend(get_cookies(driver, url, pos))

    return tracking_dict


def setup_chrome():
    from selenium.webdriver.chrome.options import Options

    chrome_options = webdriver.ChromeOptions()

    # start Chrome in incognito mode
    #chrome_options.add_argument('--incognito')

    ser = Service(path.join(path.abspath(path.curdir), 'chromedriver.exe'))

    addon_dir = path.join(path.abspath(path.curdir), 'addons\Chrome')

    # Install Extension PrivacyBadger
    chrome_options.add_extension(path.join(addon_dir, 'privacy_badger-chrome.crx'))

    # Install Extension CookieBlock
    #chrome_options.add_extension(path.join(addon_dir, 'CookieBlock.crx'))

    # Install Extension ConsentOMatic
    chrome_options.add_extension(path.join(addon_dir, 'Consent-O-Matic-1.0.2.crx'))

    chrome = webdriver.Chrome(service=ser,options=chrome_options)

    return chrome


def setup_firefox():
    from selenium.webdriver.firefox.options import Options

    # start Firefox in private mode
    #firefox_options = Options()
    #firefox_options.add_argument("-private")
    #firefox = webdriver.Firefox(options=firefox_options)

    firefox = webdriver.Firefox()

    addon_dir = path.join(path.abspath(path.curdir), 'addons\Firefox')

    # Install Extension PrivacyBadger
    install_addon(firefox, path.join(addon_dir, 'privacy_badger-2021.11.23.1-an+fx.xpi'), temporary=True)

    # Install Extension CookieBlock
    #install_addon(firefox, path.join(addon_dir, 'cookieblock-1.0.0.xpi'), temporary=True)

    # Install Extension ConsentOMatic
    install_addon(firefox, path.join(addon_dir, 'consent_o_matic-1.0.0-an+fx.xpi'),
                  temporary=True)

    return firefox


if __name__ == '__main__':
    # Initial load of the browser (Chrome or Firefox)

    #driver = setup_firefox()
    driver = setup_chrome()

    # go to first tab for ConsentOMatic to work
    driver.switch_to.window(driver.current_window_handle)

    # run main processing function
    tracking_dict = process_pages(driver)

    # write dictionary to JSON output
    write_output(tracking_dict)

    # cleanup
    driver.quit()
