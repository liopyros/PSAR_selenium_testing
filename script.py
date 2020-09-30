from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from datetime import datetime
from csv import writer
import time

# This script navigates Google Chrome through "chromedriver.exe"
# Find your version of Chrome by navigating to Settings > Help > About
# Download the chromedriver compatible for your Chrome version from
# https://chromedriver.chromium.org/ 
PATH = "PATH_TO_YOUR_CHROMEDRIVER"

# Open Chrome
driver = webdriver.Chrome(PATH)

# Go to TradingView
driver.get("https://www.tradingview.com/#signin")

# Choose to sign in by email
email = driver.find_element_by_class_name("i-clearfix")
email.click()

# Input credentials and sign in
username = driver.find_element_by_name("username")
username.send_keys("YOUR_USERNAME")
password = driver.find_element_by_name("password")
password.send_keys("YOUR_PASSWORD")
time.sleep(3)
sign_in = driver.find_element_by_xpath("//span[@class='tv-button__loader']").click()
time.sleep(3)

# Navigate to the charts tab of TradingView
charts = driver.find_element_by_xpath("//li[@class='tv-mainmenu__item tv-mainmenu__item--chart']").click()

# With the PSAR strategy already open on your chart, navigate to the symbol you want to test (ex. NVDA)
# Input that symbol into the terminal so that the resulting spreadsheet can be appropriately named
# (ensure that your chart is on the 1 minute time frame; the PSAR strategy works best here, from my experience)
# 
# Find the PSAR strategy here: https://www.tradingview.com/script/7Oy9YylB-PSAR-Strategy-No-Overnight-Holds/
symbol = input("What ticker is being tested? ")

# Open the PSAR strategy's input settings
settings = driver.find_element_by_xpath("//div[@class='icon-button js-backtesting-open-format-dialog apply-common-tooltip']").click()
time.sleep(1)

# There are 3 settings labeled "start" "increment" and "maximum" - extract their locations
start_input = driver.find_element_by_xpath("//div[@class='content-jw-2aYgg']//div[2]//div//div//div//div//div//input")
increment_input = driver.find_element_by_xpath("//div[@class='content-jw-2aYgg']//div[4]//div//div//div//div//div//input")
maximum_input = driver.find_element_by_xpath("//div[@class='content-jw-2aYgg']//div[6]//div//div//div//div//div//input")
time.sleep(1)

# Set "start" to 0 (personal preference - doesn't seem to affect the outcome nearly as much as "increment")
start_input.send_keys(Keys.CONTROL, "a")
start_input.send_keys("0")
time.sleep(1)

# Set "maximum" to 1 (personal preference - doesn't seem to affect the outcome nearly as much as "increment")
maximum_input.send_keys(Keys.CONTROL, "a")
maximum_input.send_keys("1")
time.sleep(1)

# Begin with an "increment" value of 0.001. Increase this number by 0.0002 every iteration
# until the stopping criterion is reached (1000 closed trades in the backtested period of ~30 days)
increment_value = 0.001
increment_delta = 0.0002
stopping_value = 0
stopping_criterion = 1000
my_list = []

today = str(datetime.today().strftime('%Y-%m-%d'))

# Create and/or open the csv file for writing
with open(f'data_{symbol}_{today}.csv', 'a', newline='') as f:
    csv_writer = writer(f)
    while stopping_value < stopping_criterion:
        increment_input.send_keys(Keys.CONTROL, "a")
        increment_input.send_keys(Keys.DELETE)
        time.sleep(0.5)
        increment_input.send_keys(str(increment_value))
        maximum_input.send_keys(Keys.CONTROL, "a")
        time.sleep(1.5)

        # Collect the profit_factor, profit, total_closed_trades, and percent_profitable fields
        # only if the strategy settings yield net positive profits (given by a profit_factor greater than 1)
        profit_factor = driver.find_element_by_xpath("//div[@class='report-data']//div[4]//strong").text
        if float(profit_factor) > 1:
            profit = driver.find_element_by_xpath("//div[@class='report-data']//div//strong").text
            total_closed_trades = driver.find_element_by_xpath("//div[@class='report-data']//div[2]//strong").text
            percent_profitable = driver.find_element_by_xpath("//div[@class='report-data']//div[3]//strong").text
            
            my_list = [profit[2:], total_closed_trades, percent_profitable[:-2], profit_factor, increment_value]
            csv_writer.writerow(my_list)
            
            increment_value += increment_delta
            increment_value = round(increment_value, 4)
            stopping_value = int(total_closed_trades)
        else:
            total_closed_trades = 0
            increment_value += increment_delta
            increment_value = round(increment_value, 4)
