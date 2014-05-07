from bs4 import BeautifulSoup
from collections import OrderedDict
import requests
import json
import multiprocessing
import logging
import time
logging.basicConfig(filename="extracted_data.json", level=logging.WARNING, format='%(message)s')
requests_log = logging.getLogger("requests")

class WebScraper:
	def __init__(self):
		self.proxies = {
			"http": "http://23.27.197.200:24801",
			"http": "http://23.27.197.201:24801",
			"http": "http://23.27.197.202:24801",
			"http": "http://23.27.197.203:24801",
			"http": "http://23.27.197.204:24801",
			"http": "http://23.27.197.205:24801"
		}

	def search(self, keywords, url, search_type = "jobs", search_category = ""):
		keyword = multiprocessing.Queue()
		for key in keywords:
			keyword.put(key)
		keyword.put(None) #poison pill to end each worker
		extracted_data = multiprocessing.Queue()
		logger = Logger(extracted_data)

		workers = []
		for i in range(multiprocessing.cpu_count()):
			worker = Worker(url, i, search_category, search_type, keyword, self.proxies, logger)
			workers.append(worker)

		for worker in workers:
			worker.start()

		logger.start()

		for worker in workers:
			worker.join()

		logger.extracted_data.put(None) #poison pill to end the writer

class Worker(multiprocessing.Process):
	def __init__(self, url, id, search_category, search_type, keywords, proxies, logger):
		multiprocessing.Process.__init__(self)
		self.ID = id
		self.keyword = None
		self.proxies = proxies
		self.url = url
		self.search_type = search_type
		self.search_category = search_category
		self.keyword_queue = keywords
		self.logger = logger

	def run(self):
		while True:
			keyword = self.keyword_queue.get()
			if keyword is None:
				self.keyword_queue.put(keyword)
				break
			else:
				self.keyword = keyword
				self.__scrape()

	def __scrape(self):
		page = 1
		job_entries = 0
		not_last_page = True
		while not_last_page:
			r = self.__send_request(page)
			soup = BeautifulSoup(r.text)
			no_result = soup.findAll(attrs = "no_entries")
			if len(no_result) == 0:
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
					job_entries += 1
				page += 1
			else:
				not_last_page = False
		print "Worker %d - %d entries found for the keyword '%s'" % (self.ID, job_entries, self.keyword)

	def __send_request(self, page):
		self.url += str(self.search_type) + "/search/"
		payload = {'q': self.keyword, 'searchType': self.search_type, 'searchCategory': self.search_category, 'page': page}
		return requests.get(self.url, params = payload, proxies = self.proxies)

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
	keywords = ['python', 'php', 'developer', 'java', 'ruby', 'rail']
	url = "http://mynimo.com/"
	search.search(keywords, url)
