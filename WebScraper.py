from bs4 import BeautifulSoup
from collections import OrderedDict
from splinter import Browser
import requests, json, multiprocessing, logging, time

logging.basicConfig(filename="extracted_data.json", level=logging.WARNING, format='%(message)s')
requests_log = logging.getLogger("requests")

proxies = [
	"--proxy=23.27.197.200:24801",
	"--proxy=23.27.197.201:24801",
	"--proxy=23.27.197.202:24801",
	"--proxy=23.27.197.203:24801",
	"--proxy=23.27.197.204:24801",
	"--proxy=23.27.197.205:24801",
	"--proxy-type=http",
]

class WebScraper:
	def search(self, keywords, url, search_type = "jobs", search_category = ""):
		keyword = multiprocessing.Queue()
		for key in keywords:
			keyword.put(key)
		keyword.put(None) #poison pill to end each worker
		extracted_data = multiprocessing.Queue()
		logger = Logger(extracted_data)

		workers = []
		for i in range(multiprocessing.cpu_count()):
			worker = Worker(url, i, search_category, search_type, keyword, logger)
			workers.append(worker)

		print "Scraping..."
		for worker in workers:
			worker.start()

		logger.start()

		for worker in workers:
			worker.join()

		logger.extracted_data.put(None) #poison pill to end the writer

class Worker(multiprocessing.Process):
	def __init__(self, url, id, search_category, search_type, keywords, logger):
		multiprocessing.Process.__init__(self)
		self.ID = id
		self.keyword = None
		self.url = url
		self.search_type = search_type
		self.search_category = search_category
		self.keyword_queue = keywords
		self.logger = logger
		self.job_entries = 0

	def run(self):
		while True:
			keyword = self.keyword_queue.get()
			if keyword is None:
				self.keyword_queue.put(keyword)
				break
			else:
				self.keyword = keyword
				browser = Browser('phantomjs', service_args=proxies)
				with browser:
					browser.visit(self.url)
					browser.fill('q', self.keyword)
					browser.find_by_name('gosearch').click()
					self.job_entries = 0
					while True:
						nxt = browser.find_by_css('li.next')
						if len(nxt) > 0:
							self.__scrape(browser.html.encode('utf-8'))
							browser.find_by_css('li.next > a').first.click()
						else:
							self.__scrape(browser.html.encode('utf-8'))
							break
					print "Worker %d - %d entries found for the keyword '%s'" % (self.ID, self.job_entries, self.keyword)

	def __scrape(self, text):
		job_entries = 0
		soup = BeautifulSoup(text)
		content = soup.findAll('tr', attrs = {'class' : 'searchExcerpt'})
		job = soup.findAll('tr', attrs = {'class' : 'aJobS'})
		for i in range(len(job)):
			job_title = job[i].find(attrs = 'jobTitleLink').text.encode("utf-8").strip()
			try:
				location = job[i].find(attrs = "address").text.strip() + ", "
				location += job[i].find(attrs = "address").previous_element.previous_element.strip()
			except:
				location = job[i].findAll('td')[1].text.encode("utf-8").strip()

			company = job[i].findAll('td')[2].text.encode("utf-8").strip()
			try:
				short_description = content[i].find(attrs = 'searchContent').text.encode("utf-8").strip()
			except:
				short_description = None

			short_description = " ".join(short_description.split())
			d = OrderedDict()
			d['keyword'] = self.keyword
			d['job_title'] = job_title
			d['location'] = location
			d['company'] = company
			d['short_description'] = short_description
			self.logger.extracted_data.put(d)
			self.job_entries += 1

class Logger(multiprocessing.Process):
	def __init__(self, extracted_data):
		multiprocessing.Process.__init__(self)
		self.extracted_data = extracted_data

	def run(self):
		while True:
			if not self.extracted_data.empty():
				to_write = self.extracted_data.get()
				if to_write is None:
					break
				to_write = json.dumps(to_write, indent=4)
				logging.warning(to_write)
			else:
				time.sleep(2)

if __name__ == "__main__":
	search = WebScraper()
	keywords = ['python', 'php', 'java', 'ruby', 'ada']
	url = "http://cebu.mynimo.com/"
	search.search(keywords, url)
