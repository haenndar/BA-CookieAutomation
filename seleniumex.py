import time
import json
from os import path
from selenium import webdriver


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
    # call website
    driver.get(link)

    # sleep for 3 seconds for page loading & cookie consent
    time.sleep(3)

    # read cookies
    my_cookies = driver.get_cookies()

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
    tracking_dict = create_tracking_dict('cookiebot_links.txt')

    # iterate over url and cookie_storage, append new cookies
    for url, cookie_storage in tracking_dict.items():
        pos = list(tracking_dict).index(url) + 1
        cookie_storage.extend(get_cookies(driver, url, pos))

    write_output(tracking_dict)


if __name__ == '__main__':
    # Initial load of the browser
    driver = webdriver.Firefox()
    driver.delete_all_cookies()

    addon_dir = path.join(path.abspath(path.curdir), 'addons')

    # Install Extension PrivacyBadger
    install_addon(driver, path.join(addon_dir, 'privacy_badger-2021.11.23.1-an+fx.xpi'),
                  temporary=True)

    # Install Extension ConsentOMatic
    install_addon(driver, path.join(addon_dir, 'consent_o_matic-1.0.0-an+fx.xpi'),
                  temporary=True)

    # go to first tab
    driver.switch_to.window(driver.current_window_handle)

    # run main processing function
    process_pages(driver)

    # cleanup
    driver.quit()
