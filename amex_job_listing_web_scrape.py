# install the requirements
# pip install -r "C:\Users\Jacob Shughrue\Dropbox\Coding\Python\amex_job_listing_web_scrape\requirements.txt"
import pandas as pd
import numpy as np
import os.path
from selenium import webdriver
import time
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import chromedriver_autoinstaller as chromedriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementClickInterceptedException

# Configure Selenium webdriver settings
path = str(chromedriver.install())
s = Service(path)
options = Options()
options.headless = False  # option to run without visibly opening the browser

# get the program start time - so the total execution time can be measured
st = time.time()

# set position search term and location
position_search_term = 'Data%20Science'  # 'Data%20Science' # where %20 is a space " " in an encoded URL
position_location = 'new%20york'

# set site address
url = 'https://aexp.eightfold.ai/careers?' + 'query=' + position_search_term + '&location=' + position_location

# open url in browser - allows Selenium to interact with the webpage
driver = webdriver.Chrome(service=s, options=options)
driver.get(url)
driver.set_window_position(1300, 0, windowHandle='current')  # maximize window right
time.sleep(2)  # wait 2 seconds for web page to load

# initialize
total_count = 0


def scroll_down():
    """" function to scroll down 25 times """
    # set the "page down" counts to be 0 for each loop
    repeat_count = 0

    # the number of times to send the "page down" button
    repeat = 25
    global total_count

    for i in range(repeat):
        # select sidebar on the left as scrolling section
        scroll = driver.find_element(By.CSS_SELECTOR, value=".card.position-card")

        # scroll down and wait .4 seconds for the page to load
        scroll.send_keys(Keys.PAGE_DOWN)
        time.sleep(.4)

        # Keep track of how many "page down" key presses have been sent
        repeat_count += 1
        total_count += 1
        print(f"Number of page down sends this loop: " + str(repeat_count),
              f"Number of page down sends total: " + str(total_count))


def scroll_down_some_more():
    """ function to click the "show more postings" button when needed """
    # call a function to scroll down 25 times
    scroll_down()

    # locate the 'more job postings' button which appears after ~25 "page down" sends
    more_postings = driver.find_element(By.CSS_SELECTOR, value=".btn.btn-sm.btn-secondary.show-more-positions")

    # click the 'more postings' button to load more content
    more_postings.click()

    print("Continuing with newly loaded content...")


# while statement to scroll all the way to bottom of the page to load all possible relevant positions
while 1 == 1:
    try:
        scroll_down_some_more()

    # when the "more postings" button is not available, you are at the bottom of the page
    except NoSuchElementException:
        print('Scrolling finished')
        break

# get the html labels for all position cards on the page
section = driver.find_elements(By.CSS_SELECTOR, value=".card.position-card")

# initialize
jobs_available_list = []

# iterate through all position cards to get a list of all open job titles
for position in section:
    # get the english text of each web element
    title = position.find_element(By.CSS_SELECTOR, value=r".position-title.line-clamp.line-clamp-2").text

    # append the current job title to the list of all job titles
    jobs_available_list.append(title)

# create a new df with our job titles stored
df_job_titles = pd.DataFrame(jobs_available_list)

# go to top of page - allows us to scroll down as we scrape for more data
print('sending-to-top-of-age')
driver.execute_script("scrollBy(0,-5000);")  # scroll to top of page
time.sleep(2)

# drop the last 9 rows of junk data
df_job_titles = df_job_titles.iloc[:-9, :]

# get the total number of job postings
job_titles_length = len(df_job_titles.index)

# initialize
description_list = []


def find_n_click():
    """ function to click on every job posting and scrape the job description """
    # scroll to current element, give the page time to load, then click on the element
    driver.execute_script("arguments[0].scrollIntoView({'block':'center','inline':'center'})", current_card)
    time.sleep(1)
    current_card.click()
    time.sleep(1)

    # grab the english text of the current job description
    description = driver.find_element(By.CSS_SELECTOR, value=r".position-job-description").text

    # append the current job description to the list of all job descriptions
    description_list.append(description)


# initialize
bullet_list = []

# click on each position and extract the job description along with the bulleted points
for line in range(job_titles_length):
    try:
        # specified the position number that will be scraped on each iteration
        card_xpath = "//div[@data-test-id='position-card-" + str(line) + "']"
        current_card = driver.find_element(By.XPATH, value=card_xpath)

        # scrape the job description
        find_n_click()

        # scrape bulleted details from each posting
        # use a dictionary to store the iteration number so the bullet can be linked to its posting
        for i in driver.find_elements(By.CSS_SELECTOR, value=r"#pcs-body-container ul"):
            bullet_data = str(i.text)
            bullet_dict = {
                line: bullet_data
            }
            bullet_list.append(bullet_dict)

    except ElementClickInterceptedException:
        print('Failed to find item')
        continue
    except NoSuchElementException:
        description_list.append('Error: job description missing')
        print("Description details no longer present")
        continue

# create a new df with our job descriptions stored
df_descriptions = pd.DataFrame(description_list)

# take the list of dictionaries, stack them vertically by posting number/occurrence, and group them together by posting
df_bullets = pd.DataFrame(bullet_list).stack().groupby(level=-1).agg(list)

# combine our three separate tables into one cohesive df
df = pd.concat([df_job_titles, df_descriptions, df_bullets], axis=1)
df.columns = ['title', 'description', 'bullets']


def split_string(new_column, source_column, split_word, which_half):
    """ Split the strings of a column then take either the 1st slice or the 2nd slice based on your input (0 or 1) """
    df[new_column] = df[source_column].str.split(split_word).str[which_half]


def col_trimmer(new_column, source_column, front_trim, back_trim):
    """ trim the first x number of characters from the front of a column & x number of characters from the back """
    df[new_column] = df[source_column].str[front_trim:].str[:-back_trim]


# parse the job description for the salary info string
split_string('salary_range', 'description', 'Salary Range: ', 1)
split_string('salary_range', 'salary_range', 'benefits', 0)

# remove 2 extraneous character from the end of the string
col_trimmer('salary_range', 'salary_range', 0, 2)

# drop rows in nonstandard format
df['salary_range'] = df['salary_range'].str.split()
df = df[~df.salary_range.str.contains('hourly', regex=False, na=False)]
df = df[~df.salary_range.str.contains('-', regex=False, na=False)]
df['salary_range'] = df['salary_range'].str.join(" ")

# parse the salary range string
split_string('max_salary', 'salary_range', 'annually', 0)
split_string('max_salary', 'max_salary', 'to', 1)
# remove 2 character from the front and 4 from the back end of the string
col_trimmer('max_salary', 'max_salary', 2, 4)
# convert to an integer
df['max_salary'] = df['max_salary'].str.replace(',', '').replace(np.nan, 0).astype(int)

# parse the salary range string
split_string('min_salary', 'salary_range', 'annually', 0)
split_string('min_salary', 'min_salary', 'to', 0)
# remove 1 character off the front and 4 off of the back
col_trimmer('min_salary', 'min_salary', 1, 4)
# convert to an integer
df['min_salary'] = df['min_salary'].str.replace(',', '').replace(np.nan, 0).astype(int)

# calculate a salary midpoint
df['salary_midpoint'] = (((df['max_salary'] - df['min_salary']) / 2) + df['min_salary']).astype(int)

# create a list of key-words that are of interest
search_words = {'data', 'finance', 'financial' 'dashboard', 'dashboards', 'bi', 'powerbi'
    , 'tableau', 'analysis',
                'analyze', 'analytical', 'analytics', 'deploying', 'trend', 'science', 'scientist', 'decision', 'ai',
                'ml', 'aiml', 'learning', 'sql', 'python', 'python/r', 'predictive', 'modeling'}  # case sensitive

# count the number of keyword occurrences in the description
df['all_key_words'] = df['description'].str.lower().str.split().apply(set(search_words).intersection)
df['key_word_count'] = df['all_key_words'].str.len()

# order the df so the most relevant jobs, based on the key word count, are at the top of the table
df = df.sort_values(by=['key_word_count', 'salary_midpoint'], ascending=[False, False])

# convert list to a string
df['bullets'] = df['bullets'].astype(str)

# clean rows of extra backslashes and brackets
df['bullets'] = df['bullets'].replace('\\\\n', ' \n', regex=True).str[2:].str[:-2]

# drop description column as the bullets column contains the vital information
df = df.drop('description', axis=1)

# write the df to a csv
export_path = r'C:\Users\Jacob Shughrue\Dropbox\Coding\Python\amex_job_listing_web_scrape'
file_name = 'export_current_job_postings.csv'
df.to_csv(os.path.join(export_path, file_name), encoding='utf-8-sig')

# quit the Selenium instance
driver.close()

# calculate how long this code ran for and print the result
elapsed_time = time.time() - st
print('Program Finished - Execution Time:', time.strftime("%M:%S", time.gmtime(elapsed_time)))
