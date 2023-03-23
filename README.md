## Job_Listing_Web_Scrape

### Objective:
**Use the Selenium library in Python to web scrape [American Express' open job postings](https://aexp.eightfold.ai/careers?intlink=us-amex-career-en-us-home-findalljobs)**

### File Glossary
**1. export_current_job_postings.xlsx** - This document shows the final results of the processed data frame. [The file has been uploaded to Google Sheets here](https://docs.google.com/spreadsheets/d/1HljzjnqWC5c-imBxmA5Fb-VG9ZW3g45FBBAyX-RVwZo/edit?usp=sharing)

**2. amex_job_listing_web_scrape.py** - Python file that will open Google Chrome and scrape the the site and process the results

**3. requirementst.txt** - a list of packages needed for this project

### My Steps
**1.** At the begining of this project I tried to use the library Beautiful Soup to scrape Amex's job site but I realized that the page is loaded with dynamic JavaScript and additional html code is added as a user scrolls down the page... this sent me back to the drawing board.

**2.** After some research, I learned I could extract and parse the dynamic JavaScript code using Selenium which has the ability to launch a browser, appear as a human, and interact with a webpage. 

**3.** After getting up and running with Selenium my plan was simple:
- Load all web elements (e.g. all job postings) by scrolling to the bottom of the webpage through sending the "Page Down" key. 
- Due to the nature of the site, a posting needs to be individually clicked on in order to view it and load its corresponding JavaScript. Given this setup, I created a loop to click on every jop title, scrape the contents, and move on to the next posting.
- Another hurdle was, after about 20 "Page Down" sends, postings would stop loading and a button would appear saying "Load more positions", I created a loop to ensure that this was clicked if it was on the screen.

**4.** Now that data was flowing into a dataframe nicely, I was able to add additional features:
- Seeing that job descriptions can be lengthy and filled with standard HR verbiage, I created a column to extract only the bulleted attributes from the descripition, on these job postings bulleted lines list responsibilities, preferred expereince, and minimum qualifications.
- Once all data was loaded, I dropped any data that was in a nonstandard format and parsed the job description for the salary range, allowing me to calculate a salary midpoint.
- Finally, in order to quickly see positions of interest to me, I put together a list of search words (ex. {"data","analytics"}) - the program counts how many search words are in the job description and sorts the positions in a descending fashion, positions with the most number of hits will be at the top of the dataframe.

A video of the program running can be seen [here](https://www.youtube.com/watch?v=smIsr_H56MY&ab_channel=JacobShughrue)
