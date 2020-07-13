import pandas as pd
from MJCS_Scraper import *
import datetime
from progress.bar import ShadyBar


start_time = datetime.datetime.now()
print("Started @ {}".format(start_time))
#Load DF of cases and select the case numbers (500 samples)
cases_df = pd.read_csv("casesearch-results.csv", header = None)
cases = cases_df[0]

#Create Scraper
scraper = MJCS_Scraper()
#Accept Disclaimer to be able to submit requests
scraper.accept_disclaimer()

#Test Case
scraper.search_case_id("10149U")

#Load DF of cases and select the case numbers (500 samples)
cases_df = pd.read_csv("casesearch-results.csv", header = None)
cases = cases_df.iloc[0:100, 0]

#Iterate cases and submit POST requests
results = {}
bar = ShadyBar('Scraping', max=len(cases)) #Create Progress Bar
for case_id in cases:
	results[case_id] = scraper.search_case_id(case_id)
	bar.next()
bar.finish()

print(results)

run_time = datetime.datetime.now() - start_time

print("{} records searched in {}".format(len(results), run_time))

scraper.close()