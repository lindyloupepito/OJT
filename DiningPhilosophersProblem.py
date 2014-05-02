import threading
import time
import logging
import sys

class Philosopher(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
		self.ID = None
		self.right_fork = None
		self.left_fork = None
		self.delay = 0
		self.parent_list = []
		self.fork_list = []
		self.alive = True

	def run(self):
		while self.alive:
			self.__think()
			self.__eat()

	def __acquire_forks(self):
		successfully_acquired = False
		if not self.left_fork.locked():
			self.left_fork.acquire()
			logging.info("Philosopher %d acquires left fork(%d)" % (self.ID, self.fork_list.index(self.left_fork)+1))
			if not self.right_fork.locked():
				self.right_fork.acquire()
				logging.info("Philosopher %d acquires right fork(%d)" % (self.ID, self.fork_list.index(self.right_fork)+1))
				successfully_acquired = True
			else:
				self.left_fork.release()
				logging.info("Philosopher %d releases left fork(%d)" % (self.ID, self.fork_list.index(self.left_fork)+1))
		return successfully_acquired

	def __eat(self):
		if self.__acquire_forks():
			print("Philosopher %d is eating" % self.ID)
			logging.info("Philosopher %d starts eating" % self.ID)
			time.sleep(self.delay)
			print("Philosopher %d has finished eating" % self.ID)
			logging.info("Philosopher %d has finished eating" % self.ID)
			self.__release_forks()
			self.__remove_self()
			self.alive = False

	def __think(self):
		logging.info("Philosopher " + str(self.ID) + " is thinking")
		# time.sleep(1)

	def __release_forks(self):
		self.left_fork.release()
		logging.info("Philosopher %d releases left fork(%d)" % (self.ID, self.fork_list.index(self.left_fork)+1))
		self.right_fork.release()
		logging.info("Philosopher %d releases right fork(%d)" % (self.ID, self.fork_list.index(self.right_fork)+1))

	def __remove_self(self):
		self.parent_list.remove(self)

class DiningPhilosopher():
	def __init__(self, num_of_philosophers, delay):
		self.forks = [threading.Lock() for x in range(num_of_philosophers)]
		self.philosophers = []
		for i in range(num_of_philosophers):
			philosopher = Philosopher()
			philosopher.ID = i+1
			philosopher.left_fork = self.forks[i%num_of_philosophers]
			philosopher.right_fork = self.forks[(i+1)%num_of_philosophers]
			philosopher.delay = delay
			philosopher.fork_list = self.forks
			self.philosophers.append(philosopher)

		for philosopher in self.philosophers:
			philosopher.parent_list = self.philosophers

	def start_eating(self):
		logging.basicConfig(filename="data.log", level=logging.INFO, format='%(message)s')
		for i in range(len(self.philosophers)):
			self.philosophers[i].start()

dp = DiningPhilosopher(6, 1)
dp.start_eating()
