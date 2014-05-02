from bs4 import BeautifulSoup
from collections import OrderedDict
import requests
import json
import threading
import cProfile
import logging

class Queue():
	def __init__(self):
		self.lst = []

	def enqueue(self, element):
		self.lst.append(element)

	def dequeue(self):
		to_return = None
		if len(self.lst) > 0:
			first = self.lst[0]
			self.lst.remove(self.lst[0])
			to_return = first
		else:
			to_return = "Queue is empty"
		return to_return

class WebScraper():
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
		keyword_queue = Queue()
		workers = []

		for i in range(len(keywords)):
			keyword = Keyword(keywords[i])
			keyword_queue.enqueue(keyword)
			worker = Worker()
			worker.url = url
			worker.ID = i
			worker.keyword_queue = keyword_queue
			worker.proxies = self.proxies
			workers.append(worker)
		
		print "Program running..."
		logging.basicConfig(filename="results.json", level=logging.INFO, format='%(message)s')
		for worker in workers:
			worker.start()

class Keyword():
	def __init__(self, ID):
		self.ID = ID
		self.lock = threading.Lock()

class Worker(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
		self.ID = None
		self.keyword = None
		self.proxies = None
		self.url = None
		self.search_type = "jobs"
		self.search_category = ""
		self.not_finished = True
		self.keyword_queue = None

	def run(self):
		k = self.keyword_queue.dequeue()
		while self.not_finished:
			if k.lock:
				k.lock.acquire()
				self.keyword = k
				self.scrape()
				k.lock.release()

	def scrape(self):
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
					d['keyword'] = self.keyword.ID
					d['job_title'] = job_title
					d['location'] = location
					d['company'] = company
					d['short_description'] = short_description
					self.__write_data(d)
					job_entries += 1
				page += 1
			else:
				not_last_page = False
				self.not_finished = False
		print job_entries, "entries found for the keyword", self.keyword.ID

	def __write_data(self, dictionary):
		toWrite = json.dumps(dictionary, indent=4)
		logging.info(toWrite + "\n")
		# print toWrite + "\n"

	def __send_request(self, page):
		self.url += str(self.search_type) + "/search/"
		payload = {'q': self.keyword.ID, 'searchType': self.search_type, 'searchCategory': self.search_category, 'page': page}
		return requests.get(self.url, params = payload)


search = WebScraper()
keywords = ["java", "php", "python", "ruby", "rails"]
url = "http://mynimo.com/"
search.search(keywords, url)
