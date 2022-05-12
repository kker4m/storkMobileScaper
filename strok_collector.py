from abc import ABC, abstractmethod
from bs4 import BeautifulSoup
from typing import List
import time
from plan import Plan
from selenium import webdriver
from selenium.webdriver.common.by import By
import os
import warnings
import itertools
import json
from tqdm import tqdm
from collector import Collector
from colorama import Fore

class StorkCollector(Collector):

    def __init__(self, url):
        self.url = url

    # This function converts the elements found with the BeautifulSoup library to XPATH format,
    # allowing them to interact with Selenium easily.

    def xpath_soup(self, element):
        components = []
        child = element if element.name else element.parent
        for parent in child.parents:
            previous = itertools.islice(parent.children, 0, parent.contents.index(child))
            xpath_tag = child.name
            xpath_index = sum(1 for i in previous if i.name == xpath_tag) + 1
            components.append(xpath_tag if xpath_index == 1 else '%s[%d]' % (xpath_tag, xpath_index))
            child = parent
        components.reverse()
        return '/%s' % '/'.join(components)

    def collect(self) -> List[Plan]:
        # Last list  will be returned as a json or a list
        last = []
        # We get the HTML of the website using the selenium library to find the information we are looking for.
        # I prefer the use selenium because of the hidden elements couldn't find via requests library.

        # Get the current path of where the script is running so we can easily find the location of chromedriver.exe

        current_path = os.getcwd()

        # Set some options before create the driver to avoid bot protection

        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36 OPR/79.0.4143.73")
        warnings.filterwarnings("ignore", category=FutureWarning)
        warnings.filterwarnings("ignore", category=DeprecationWarning)

        # Add "chromedriver.exe" to the executable path which created two steps ago, and put the options in to webdriver

        browser = webdriver.Chrome(executable_path=current_path + "\\chromedriver.exe", options=options)

        # Gave Information To The Client

        print(Fore.YELLOW + "[+] Extraction Started, Please Wait..")


        # Get the url which is gaven by user

        browser.get(self.url)
        time.sleep(2)

        # We find countries buttons by their places to click on the buttons one by one to show the countries.

        elements = browser.find_elements(By.XPATH,
                                         "//div[@data-v-5e4a239e and @class = 'flex-push ts-small ts-quiet ts-pointer hide-xs button button-small button-flat-nohover']")

        # We make the hidden elements scrapable by clicking the buttons.

        for element in elements:
            element.click()

            # Scroll down with JavaScript will made the element clickable

            browser.execute_script("window.scrollTo(0, (window.pageYOffset)+350);")

            time.sleep(1)

        # Take the page source with countries are appearing using BeautifulSoup to take the data from site

        soup = BeautifulSoup(browser.page_source, 'lxml')

        # Take all the regional plans and we are gonna take the data for each of them

        regional_plans = soup.find('div', attrs={'id': 'region'})
        regional_plans = regional_plans.find_all('div', attrs={'class': 'block-md'})

        # Work for each region in a for loop
        with tqdm(total=(20), unit=' page', desc='Pages are extracting, please wait.') as bar:
            for region in regional_plans:

                # Take the country list with an for loop

                countries = [i.text for i in (region.find_all('span', attrs={'class': 'ts-bold'}))]


                last.append(countries)

                # Take the icon url of region or country

                image_div = region.find('div', attrs={'class': 'panel-head'})
                image = image_div.find_all('img')
                icon_url = [("https://storkmobile.com" + i.get('src')) for i in image][0]



                last.append(icon_url)

                # Take the each plan links

                plans = (region.find_all('div', attrs={'class': 'plans-row'}))[1:]

                # Get into each plan to get data
                # Used tqdm to make it look more understandable and productive

                for plan in plans:
                    plan_data = []
                    # Get the size_mb, duration_days and price from the texts

                    texts = [i.text for i in plan.find_all('span')]

                    size_mb = int((texts[0]).replace('GB', '')) * 1000

                    plan_data.append(size_mb)

                    duration_days = int(texts[1].replace('days', ''))

                    plan_data.append(duration_days)

                    currency_symbol = str(texts[-1])[0]

                    if currency_symbol=='$':
                        currency = 'Dollar'
                    elif currency_symbol=='€':
                        currency='Euro'
                    elif currency_symbol=='£':
                        currency="Pound"
                    else:
                        currency=None

                    plan_data.append(currency)

                    price = float(texts[-1].replace('$', '').replace(',', '.'))


                    plan_data.append(price)

                    # Get the operator_url from a link

                    operator_url = plan.find('a', attrs={'class': 'button button-small'})
                    operator_url = ("https://storkmobile.com" + operator_url.get('href'))
                    plan_data.append(operator_url)

                    # Get to operator url for more information and scrape that too

                    browser.get(operator_url)
                    time.sleep(1)

                    # Take page source of operator url

                    soup = BeautifulSoup(browser.page_source, 'lxml')

                    # Get the region name of the plan

                    temp_name = soup.find('div', attrs={'class': 'icon-text-group flex-grow'})
                    temp_name = (temp_name.find('span',attrs={'id':'coverage'})).text

                    # With the special characters causing problems, it made more sense to take the name from different pages and combine it.
                    # Texts contains default duration days and size GB which is name of the plan, so i used them

                    name = temp_name +' '+str(texts[0])+' / '+str(texts[1])
                    plan_data.append(name)

                    time.sleep(1)

                    # Return as a json or a list all the data who recieved

                    bar.update(1)
                    last.append(plan_data)

        browser.close()
        jsonStr = json.dumps(last)
        return jsonStr


result = StorkCollector('https://storkmobile.com/plans/')
print(result.collect())