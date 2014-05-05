import threading
import time
import random
import logging

class Queue:
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

	def remove(self, element):
		self.lst.remove(element)

class Customer(threading.Thread):
	def __init__(self, name, barbershop):
		threading.Thread.__init__(self)
		self.name = name
		self.is_last = False
		self.shop = barbershop
		self.served = False
		self.tracker = False
		self.service_time = random.randrange(self.shop.min_service_time, self.shop.max_service_time)
		rand = random.randrange(0, 100)
		if rand < 50:
			self.leave = True
			self.waiting_time = random.randrange(self.shop.min_waiting_time, self.shop.max_waiting_time)
		else:
			self.leave = False

	def run(self):
		self.__enter_shop()
		while not self.served:
			self.__wait()

	def __enter_shop(self):
		time.sleep(random.randrange(self.shop.customer_min_interval, self.shop.customer_max_interval))
		logging.info("%s arrives at the barber shop." % self.name)
		self.shop.customers_arrived += 1
		if self.shop.customers_arrived == self.shop.num_of_customers:
			self.is_last = True
			self.leave = False #forces the last customer not to leave so that the loop 'start work' will end
		if self.shop.counter == self.shop.num_of_seats:
			logging.info("Waiting lounge is full. %s waits for a vacant seat." % self.name)
		self.shop.seats.acquire()
		self.shop.counter += 1
		logging.info("%s acquires a seat." % self.name)
		self.shop.waiting_customers.enqueue(self)

	def __wait(self):
		if self.leave:
			time.sleep(self.waiting_time)
			try:
				self.shop.waiting_customers.remove(self)
				logging.info("%s cannot wait and leaves the shop." % self.name)
				self.seats.release()
				self.shop.counter -= 1
			except:
				pass
		else:
			if not self.tracker:
				logging.info("%s is waiting for his turn." % self.name)
				self.tracker = True

class Barber(threading.Thread):
	def __init__(self, barbershop):
		threading.Thread.__init__(self)
		self.is_sleeping = False
		self.shop = barbershop

	def run(self):
		logging.info("The barber shop opens.")
		stop = False
		while True:
			if self.shop.waiting_customers.is_empty():
				if not self.is_sleeping:
					self.__sleep()
			else:
				self.__wake_up()
				while not self.shop.waiting_customers.is_empty():
					customer = self.shop.waiting_customers.dequeue()
					self.shop.seats.release()
					self.shop.counter -= 1
					self.__service_customer(customer)
					customer.served = True
					logging.info(customer.served, customer.served)
					if customer.is_last:
						stop = True
						break
			if stop:
				break
		logging.info("The barber shop closes.")

	def __service_customer(self, customer):
		logging.info("%s is having a haircut for %d seconds." % (customer.name, customer.service_time))
		time.sleep(customer.service_time)
		logging.info("%s is done and leaves the shop." % customer.name)

	def __sleep(self):
		self.is_sleeping = True
		logging.info("The barber is sleeping -.-")

	def __wake_up(self):
		self.is_sleeping = False
		logging.info("The barber wakes up O.O")

class Barbershop:
	def __init__(self):
		logging.basicConfig(filename="barber.log", level=logging.INFO, format="%(message)s")

		self.num_of_seats = 3
		self.customer_min_interval = 5
		self.customer_max_interval = 15
		self.min_service_time = 3
		self.max_service_time = 15
		self.min_waiting_time = 5
		self.max_waiting_time = 10
		self.num_of_customers = 5

		self.customers_arrived = 0
		self.counter = 0
		self.seats = threading.Semaphore(self.num_of_seats)
		self.waiting_customers = Queue()

		customers = []
		for i in range(self.num_of_customers):
			name = "Customer " + str(i+1)
			customers.append(Customer(name, self))

		print "Processing..."
		barber = Barber(self)
		barber.start()

		for customer in customers:
			customer.start()

bs = Barbershop()
