from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import time

# Set up headless mode (no browser window pops up)
options = Options()
options.headless = True

# Initialize the WebDriver
driver = webdriver.Firefox(options=options)

# URL to fetch
url = 'https://classic.warcraftlogs.com/zone/reports?zone=1038'

# Open the page
driver.get(url)

# Optional: wait for JavaScript to load
time.sleep(3)

# Get the page HTML
html = driver.page_source
with open('warcraft_logs_html.txt', 'w+') as f:
    f.write(html)

# Clean up
driver.quit()
