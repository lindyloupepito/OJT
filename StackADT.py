class Stack(object):
    def __init__(self):
        self.lst = []

    def push(self, element):
        self.lst.append(element)

    def pop(self):
        if len(self.lst) > 0:
            self.lst = self.lst[0:len(self.lst)-1]
            print "Pop: %r" % self.lst[len(self.lst)-1]
            return self.lst[len(self.lst)-1]
        else:
            print "Stack is empty."
            return False

    def top(self):
        if len(self.lst) > 0:
            print "Top: %r" % self.lst[len(self.lst)-1]
            return self.lst[len(self.lst)-1]
        else:
            print "Stack is empty."
            return False

stack = Stack()
stack.push(4)
stack.push("String")
stack.top()
stack.pop()
print stack.lst
