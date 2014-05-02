class Soldier(object):
	def __init__(self):
		self.ID = None
		self.next = None

class CircularLinkedList(object):
	def __init__(self):
		self.head = None
		self.tail = None
		self.size = 0

	def add(self, ID):
		newSoldier = Soldier()
		newSoldier.ID = ID

		if self.head == None:
			self.head = newSoldier
			self.tail = newSoldier
		
		self.tail.next = newSoldier
		newSoldier.next = self.head
		self.tail = newSoldier
		self.size += 1

	def remove(self, ID):
		newSoldier = self.head

		if self.size == 1 and self.head.ID == ID:
			newSoldier = self.head
			self.head = None
			self.tail = None
			self.size = 0
		else:
			while newSoldier:
				if self.head.ID == ID:
					self.head = self.head.next
					self.tail.next = self.head
					self.size -= 1
					break
				else:
					if newSoldier.next.ID == ID:
						if self.tail.ID == newSoldier.next.ID:
							self.tail = newSoldier

						afternext = newSoldier.next.next
						newSoldier.next = afternext
						self.size -= 1
						break
					else:
						newSoldier = newSoldier.next
		return newSoldier

def JosephusProblem(numSoldier, step):
	if numSoldier == 0 or step == 0:
		result(numSoldier, step, None)
		pass
	else:
		ll = CircularLinkedList()
		for i in range(numSoldier):
			ll.add(i+1)

		newSoldier = ll.head
		counter = 1
		while ll.size > 1:
			if counter == step:
				newSoldier = ll.remove(newSoldier.ID)
				counter = 1
			else:
				counter += 1

			newSoldier = newSoldier.next
		result(numSoldier, step, ll.head.ID)
		return ll.head.ID


def result(numSoldier, step, survivor):
	print "SOLDIERS: ", numSoldier
	print "STEPS: ", step
	if survivor:
		print "Soldier %d survives" % survivor
	else:
		print "Invalid parameters passed."
	print ""


JosephusProblem(40,7)
JosephusProblem(41,3)
JosephusProblem(5,2)
JosephusProblem(6,3)
JosephusProblem(6,2)
JosephusProblem(2,1)
JosephusProblem(0,0)
JosephusProblem(500,3)
JosephusProblem(20,3)
JosephusProblem(31,4)
JosephusProblem(20,5)
JosephusProblem(41,3)
