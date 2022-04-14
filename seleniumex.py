import time
import json
from selenium import webdriver

pageCount = 0
cookieCount = 0

def install_addon(self, path, temporary=None):
    payload = {"path": path}
    if temporary:
        payload["temporary"] = temporary
    return self.execute("INSTALL_ADDON", payload)["value"]

def save_cookies(driver, link, filename):
    global pageCount
    global cookieCount

    #call website
    driver.get(link)
    
    # sleep for 2 seconds to allow storing cookies
    time.sleep(2)

    # read cookies
    myCookies = driver.get_cookies()
    data = myCookies
    
    # increase counters
    pageCount = pageCount + 1
    cookieCount = cookieCount + len(myCookies)

    # print the currently viewed page 
    print(str(pageCount) + ') ' + driver.title + ' - ' + driver.current_url)
    print(str(len(myCookies)) + ' Cookies stored\n')

    # append cookies to current json
    with open(filename, 'r') as json_file:
        try:
            data = json.load(json_file)
            temp = data
            data.append(myCookies)
        except json.JSONDecodeError:
            pass

    # write cookies to output file
    with open(filename, 'w') as fp:
        json.dump(data, fp, indent=4)

#####################################################################################################

# Initial load of the browser
driver = webdriver.Firefox()
driver.delete_all_cookies()

# create json file for output
timestr = time.strftime("%Y-%m-%d_%H-%M-%S")
filename = 'cookies_' + timestr + '.json'
open(filename, 'w')

# Install Extension PrivacyBadger
driver.install_addon('privacy_badger-2021.11.23.1-an+fx.xpi', temporary=True)

# Call pages and save Cookies as JSON file
with open('cookiebot_links.txt') as links:
    for link in links:
        save_cookies(driver, link, filename)

print('Total Cookies: ' + str(cookieCount))

driver.quit()
