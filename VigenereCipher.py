import cProfile

class VigenereCipher():
	def __init__(self, alphabet):
		self.alphabet = alphabet
		self.valid_alphabet = True
		string = ""
		for i in self.alphabet:
			if i in string:
				self.valid_alphabet = False
				break
			else:
				string += i

	def encrypt(self, message, key):
		if self.valid_alphabet:
			cipher_text = ""
			
			for i in message:
				if i not in self.alphabet:
					cipher_text = "Invalid message"

			if cipher_text == "":
				for i in key:
					if i not in self.alphabet:
						cipher_text = "Invalid key"

				string = ""
				for i in key:
					if i in string:
						cipher_text = "Invalid key"
						break
					else:
						string += i

				if cipher_text == "":
					mixed_alphabet = self.mix_alphabet(key)
					table = self.create_table(mixed_alphabet)
					newKey = self.generateKey(message, key)

					for i in range(len(message)):
						pos = self.alphabet.index(message[i])
						cipher_text += table[newKey[i]][pos]
		else:
			cipher_text = "Invalid alphabet"
		return cipher_text

	def decrypt(self, message, key):
		if self.valid_alphabet:
			cipher_text = ""
			
			for i in message:
				if i not in self.alphabet:
					print i
					cipher_text = "Invalid message"

			string = ""
			for i in key:
				if i in string:
					cipher_text = "Invalid key"
					break
				else:
					string += i

			if cipher_text == "":
				lst = [x for x in key if x not in self.alphabet]
				if len(lst) > 0:
					cipher_text = "Invalid key"

				if cipher_text == "":
					mixed_alphabet = self.mix_alphabet(key)
					table = self.create_table(mixed_alphabet)
					newKey = self.generateKey(message, key)

					for i in range(len(message)):
						pos = table[newKey[i]].index(message[i])
						cipher_text += self.alphabet[pos]
		else:
			cipher_text = "Invalid alphabet"
		return cipher_text

	def mix_alphabet(self, key):
		for i in self.alphabet:
			if i not in key:
				key += i

		lst = []
		counter = 0
		string = ""
		for i in key:
			string += i
			counter += 1
			if counter == 5:
				lst.append(string)
				counter = 0
				string = ""

		if string != "":
			lst.append(string)

		mixed = ""
		counter = 0
		index = 0
		alpha_size = len(self.alphabet)
		len_size = 0

		while True:
			try:
				mixed += lst[counter][index]
				counter += 1
				if counter == len_size:
					index += 1
					counter = 0
			except IndexError:
				counter = 0
				index += 1
				if len(mixed) == alpha_size:
					break
		return mixed

	def create_table(self, mixed_alphabet):
		d = {}
		size = len(self.alphabet)
		for i in range(len(mixed_alphabet)):
			k = self.alphabet[i]
			d[k] = ""
			index = i
			d_size = 0
			while d_size < size:
				if index >= size:
					index -= size
				d[k] += (mixed_alphabet[index])
				index += 1
				d_size += 1
		return d

	def generateKey(self, message, key):
		newKey = ""
		counter = 0
		size = len(key)
		for i in range(len(message)):
			newKey += key[counter]
			counter += 1
			if counter == size:
				counter = 0
		return newKey


message = "now is the time for all good men to come to the aid of their fellow man "
password = "excalibur"
v = VigenereCipher("abcdefghijklmnopqrstuvwxyz1234567890 ")
cProfile.run("encrypted = v.encrypt(message,password)")
cProfile.run("decrypted = v.decrypt(encrypted,password)")

print encrypted
print decrypted
