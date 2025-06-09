from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import re

# Initialize the WebDriver
driver = webdriver.Firefox()

# URL to fetch
url_base = 'https://classic.warcraftlogs.com/zone/reports?zone=1038&page='

for i in range(1,5):
    print('working on page ' + str(i))
    url = str(url_base) + str(i)
    driver.get(url)
    html = driver.page_source
    fight_codes = re.findall(r'<a href="/reports/(.*?)">', html)
    with open('warcraft_logs_html.txt', 'w+') as f:
        for code in fight_codes:
            f.write(code + '\n')

# Clean up
driver.quit()
