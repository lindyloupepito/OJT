import threading
import time
import random
import logging

customer_min_interval = 2
customer_max_interval = 5
min_service_time = 5
max_service_time = 10
min_waiting_time = 5
max_waiting_time = 15

class Queue:
	def __init__(self):
		self.lst = []

	def enqueue(self, element):
		self.lst.append(element)

	def dequeue(self):
		to_return = None
		if not self.is_empty():
			first = self.lst[0]
			del self.lst[0]
			to_return = first
		else:
			to_return = "Queue is empty."
		return to_return

	def is_empty(self):
		return True if len(self.lst) == 0 else False

class CustomerQueue(Queue):
	def __init__(self):
		Queue.__init__(self)

	def remove(self, element):
		self.lst.remove(element)

class Customer(threading.Thread):
	def __init__(self, name):
		threading.Thread.__init__(self)
		self.name = name
		self.service_time = random.randrange(min_service_time, max_service_time)
		self.delay = random.randrange(customer_min_interval, customer_max_interval)
		self.shop = None
		self.is_last = False
		self.served = False
		self.leave = False

	def run(self):
		time.sleep(self.delay)
		logging.info("%s arrives at the barber shop." % self.name)
		printed = False
		while True:
			vacant = self.shop.seats.acquire(False)
			if vacant:
				logging.info("%s acquires a seat." % self.name)
				self.shop.waiting_customers.enqueue(self)
				break
			else:
				if not printed:
					logging.info("Waiting lounge is full. %s waits for a vacant seat." % self.name)
					printed = True
		self.__wait()
		
	def __wait(self):
		time_to_leave = 0
		printed = False
		if not self.is_last:
			if random.randrange(0, 100) < 50:
				self.leave = True
				waiting_time = random.randrange(min_waiting_time, max_waiting_time)
				time_to_leave = int(time.time() + waiting_time)

		while not self.served:
			if not printed:
				logging.info("%s is waiting for his turn." % self.name)
				printed = True

			if self.leave:
				if int(time.time()) == time_to_leave:
					try:
						self.shop.waiting_customers.remove(self)
						logging.info("%s cannot wait and leaves the shop." % self.name)
						self.shop.seats.release()
						self.served = True
					except:
						self.served = True

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
					customer.served = True
					self.__service_customer(customer)
					if customer.is_last:
						stop = True
			if stop:
				break
		logging.info("The barber shop closes.")
		print "Simulation done. See 'barber.log' in your folder to track events."

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
	def __init__(self, customers, num_of_seats):
		logging.basicConfig(filename="barber.log", level=logging.INFO, format="%(message)s")
		self.seats = threading.Semaphore(num_of_seats)
		self.waiting_customers = CustomerQueue()

		print "Simulating..."
		barber = Barber(self)
		barber.start()
		self.customers = customers
		for customer in self.customers:
			customer.shop = self
			customer.start()

num_of_customers = 10
num_of_seats = 5
customers = []
for i in range(num_of_customers):
	name = "Customer " + str(i+1)
	customers.append(Customer(name))

customers[len(customers)-1].delay = ((min_service_time + max_service_time)/ 2) * num_of_customers
customers[len(customers)-1].is_last = True
bs = Barbershop(customers, num_of_seats)
