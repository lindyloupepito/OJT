def SieveOfEratosthenes(x):
	lst = [x for x in range(2, x+1) if x > 1]

	size = len(lst)
	for i in lst:
		if i != "x":
			index = 0
			for j in lst:
				if j != "x" and j != i and j % i == 0:
					lst[index] = "x"
				index += 1

	while "x" in lst:
		lst.remove("x")

	return lst

print SieveOfEratosthenes(30)
