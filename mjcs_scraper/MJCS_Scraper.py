from seleniumrequests import Chrome
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options
from chromedriver_py import binary_path
import requests

class MJCS_Scraper:
	def __init__(self, headless = True):
		chrome_options = Options()  
		
		if headless:
			chrome_options.add_argument("--headless")

		self.driver = Chrome(chrome_options = chrome_options, executable_path = binary_path)
		self.url = "http://casesearch.courts.state.md.us/casesearch/inquiryByCaseNum.jis"
		self.disclaimer_accepted = False
		self.session = requests.session()

		self.location_codes = {
			"District Court" : "DC",
			"Allegany County" : "01",
			"Anne Arrundel County" : "02",
			"Baltimore City" : "24",
			"Baltimore County" : "03",
			"Calvert County" : "04",
			"Caroline County" : "05",
			"Carroll County" : "06",
			"Cecil County" : "07",
			"Charles County" : "08",
			"Dorchester County" : "09",
			"Frederick County" : "10",
			"Garrett County" : "11",
			"Harford" : "12",
			"Howard County" : "13",
			"Kent County" : "14",
			"Montgomery County" : "15",
			"Prince George's County" : "16",
			"Queen Anne's County" : "17",
			"Saint Mary's County" : "18",
			"Somerset County" : "19",
			"Talbot County" : "20",
			"Washington County" : "21",
			"Wicomico County" : "22",
			"Worcester County" : "23"
		}

	#Accepts disclaimer and passes cookie to the Requests Session
	def accept_disclaimer(self):
		#Request home page
		self.driver.get(self.url)
		#Check the disclaimer box and submit
		disclaimer = self.driver.find_element_by_name("disclaimer")
		disclaimer.click()
		accept_disclaimer = self.driver.find_element_by_name("action")
		accept_disclaimer.click()

		#Set Cookies with Accepted Disclaimer
		request_cookies_browser = self.driver.get_cookies()
		c = [self.session.cookies.set(c['name'], c['value']) for c in request_cookies_browser]

		#Set indicator that the disclaimer has been accepted
		self.disclaimer_accepted = True

	#Takes Case ID and submits a POST Request
	#Returns True if the case was found and False if not
	def search_case_id(self, case_id):
		if not self.disclaimer_accepted:
			self.accept_disclaimer()
		case_field = self.driver.find_element_by_name("caseId")
		case_field.send_keys(case_id)
		submit_case = self.driver.find_element_by_xpath("//*[@name='action' and @value='Get Case']")
		submit_case.click()

		response = self.driver.page_source

		#Return to Search
		self.driver.get("http://casesearch.courts.state.md.us/casesearch/goBackLink.jis")
		
		results = parse_response(response)

		return results

	def seach_case_id_post(self, case_id, location_code):
		if not self.disclaimer_accepted:
			self.accept_disclaimer()
		#Define POST Request
		searchRequest = {
			"locationCode": location_code,
			"caseId" : case_id,
			"action" : "Get Case"
		}
		#Send Request
		response = self.session.post(self.url, searchRequest)

		if response.status_code == 200:
			results = parse_response(response.text)
		else:
			results = False
		return results
		
	def search_all_locations(self, case_id):
		if not self.disclaimer_accepted:
			self.accept_disclaimer()
		
		#Iterate through locations and search for case_id
		for key, value in self.location_codes.items():
			result = self.seach_case_id_post(case_id, value)

			if result:
				return {"found" : result, "location" : key}

			#Case not found
			return {"found" : False, "location" : "None"}

	def close(self):
		self.driver.close()
#Takes response and returns whether or not the case was found
def parse_response(response):
	#Parse Response
	soup = BeautifulSoup(response, "lxml")

	page_title = soup.title.string
	if "Case Information" in page_title:
		case_found = True
	else:
		case_found = False

	return case_found