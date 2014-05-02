import threading
import time
import random
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
			to_return = "Queue is empty."
		return to_return

	def is_empty(self):
		return True if len(self.lst) <= 0 else False

class Customer():
	def __init__(self, name):
		self.name = name
		self.is_last = False
		self.service_time = random.randrange(min_service_time, max_service_time)
		rand = random.randrange(0, 100)
		if rand <= 50:
			self.leave = True
			self.waiting_time = random.randrange(min_waiting_time, max_waiting_time)
		else:
			self.leave = False

class Barber():
	def __init__(self):
		self.is_sleeping = False

	def service_customer(self, customer):
		logging.info("%s is having a haircut for %d seconds." % (customer.name, customer.service_time))
		time.sleep(customer.service_time)
		logging.info("%s is done and leaves the shop." % customer.name)

	def sleep(self):
		self.is_sleeping = True
		logging.info("The barber is sleeping -.-")

	def wake_up(self):
		self.is_sleeping = False
		logging.info("The barber wakes up O.O")

class Barbershop():
	def __init__(self, num_of_seats):
		self.seats = threading.Semaphore(num_of_seats)
		self.barber = Barber()
		self.waiting_customers = Queue()
		#the next two variables are just for printing purposes only
		self.num_of_seats = num_of_seats
		self.counter = 0

		self.working_thread = threading.Thread(target=self.start_work)
		self.working_thread.start()

	def start_work(self):
		logging.info("The barber shop opens.")
		stop = False
		while True:
			if self.waiting_customers.is_empty():
				if not self.barber.is_sleeping:
					self.barber.sleep()
			else:
				self.barber.wake_up()
				while not self.waiting_customers.is_empty():
					customer = self.waiting_customers.dequeue()
					self.seats.release()
					self.counter -= 1
					self.barber.service_customer(customer)
					if customer.is_last:
						stop = True
						break
			if stop:
				break
		logging.info("The barber shop closes.")

	def enter_shop(self, customer):
		logging.info("%s arrives at the barber shop." % customer.name)
		if self.counter == self.num_of_seats:
			logging.info("Waiting lounge is full. %s waits for a vacant seat." % customer.name)
		self.seats.acquire()
		self.counter += 1
		logging.info("%s acquires a seat." % customer.name)
		self.waiting_customers.enqueue(customer)
		if customer.leave:
			time.sleep(customer.waiting_time)
			try:
				self.waiting_customers.lst.remove(customer)
				logging.info("%s cannot wait and leaves the shop." % customer.name)
				self.seats.release()
				self.counter -= 1
			except:
				pass

number_of_customers = 15
number_of_seats = 3
customer_min_interval = 3
customer_max_interval = 5
min_service_time = 3
max_service_time = 15
min_waiting_time = 5
max_waiting_time = 15

customers = []
for i in range(number_of_customers):
	customers.append(Customer("Customer " + str(i+1)))
customers[len(customers)-1].is_last = True
customers[len(customers)-1].leave = False	#forces the last customer not to leave so that the loop in start_work will be stopped

print "Process running..."
logging.basicConfig(filename="barber.log", level=logging.INFO, format="%(message)s")
bs = Barbershop(number_of_seats)
for customer in customers:
	bs.enter_shop(customer)
	time.sleep(random.randrange(customer_min_interval, customer_max_interval)) 		#time interval for the next customer to enter the barber shop
