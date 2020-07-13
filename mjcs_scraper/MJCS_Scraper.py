from seleniumrequests import Chrome
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options
from chromedriver_py import binary_path

class MJCS_Scraper:
	def __init__(self):
		chrome_options = Options()  
		chrome_options.add_argument("--headless")

		self.driver = Chrome(chrome_options = chrome_options, executable_path = binary_path)
		self.url = "http://casesearch.courts.state.md.us/casesearch/inquiryByCaseNum.jis"
		self.disclaimer_accepted = False

	def accept_disclaimer(self):
		#Request home page
		self.driver.get(self.url)
		#Check the disclaimer box and submit
		disclaimer = self.driver.find_element_by_name("disclaimer")
		disclaimer.click()
		accept_disclaimer = self.driver.find_element_by_name("action")
		accept_disclaimer.click()

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
		# #Define POST Request
		# searchRequest = {
		# 	"locationCode": "DC",
		# 	"caseId" : case_id,
		# 	"action" : "Get Case"
		# }
		# #Send Request
		# response = self.driver.request("post", self.url, searchRequest)
		response = self.driver.page_source

		#Return to Search
		self.driver.get("http://casesearch.courts.state.md.us/casesearch/goBackLink.jis")
		
		results = parse_response(response)

		return results

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