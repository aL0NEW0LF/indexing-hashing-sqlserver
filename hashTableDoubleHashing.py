# Node data structure - essentially a LinkedList node
class Node:
    def __init__(self, key, value):
        self.key = key
        self.value = value

    def __str__(self):
        return "<Node: (%s, %s)>" % (self.key, self.value)

    def __repr__(self):
        return str(self)


# Hash table with separate chaining
class HashTableDH:
    # Initialize hash table
    def __init__(self, INITIAL_CAPACITY = 50):
        self.capacity = INITIAL_CAPACITY
        self.size = 0
        self.buckets = [None] * self.capacity

    # Generate a hash for a given key
    # Input:  key - string
    # Output: Index from 0 to self.capacity
    def hash1(self, key):
        hashsum = 0
        # For each character in the key
        for index, c in enumerate(key):
            # Add (index + length of key) ^ (current char code)
            hashsum += (index + len(key)) ** ord(c)
            # Perform modulus to keep hashsum in range [0, self.capacity - 1]
            hashsum = hashsum % self.capacity
        return hashsum

    def hash2(self, key):
        hashsum = 0
        # For each character in the key
        for index, c in enumerate(key):
            # Add (index + length of key) ^ (current char code)
            hashsum += (index + len(key)) ** ord(c)
            # Perform modulus to keep hashsum in range [0, self.capacity - 1]
            hashsum = 1 + hashsum % (self.capacity - 2)
        return hashsum

    # Insert a key,value pair to the hashtable
    # Input:  key - string
    # 		  value - anything
    # Output: void
    def insertDH(self, key, value):
        # 2. Compute index of key
        index = self.hash1(key)
        prev = self.buckets[index]
        count = 1
        while self.buckets[index] is not None:
            index = self.hash1(key) + count * self.hash2(key)
            count += 1
        # Add a new node at the end of the list with provided key/value
        self.buckets[index] = Node(key, value)
        # 1. Increment size
        self.size += 1

    # Find a data value based on key
    # Input:  key - string
    # Output: value stored under "key" or None if not found
    def find(self, key):
        # 1. Compute hash
        index = self.hash1(key)
        count = 1
        while self.buckets[index] is not None and self.buckets[index].key != key:
            index = self.hash1(key) + count * self.hash2(key)
        # 4. Now, node is the requested key/value pair or None
        if self.buckets[index] is None:
            # Not found
            return None
        else:
            # Found - return the data value
            return index

    def removeDH(self, key):
        # 2. Compute index of key
        index = self.find(key)

        if index is None:
            return None
        else:
            # 4. The key was found.
            self.size -= 1
            result = self.buckets[index].value
            # Delete this element in linked list
            self.buckets[index] = None
            # Return the deleted result
            return result


    def __str__(self):
        elements = []
        for i in range(self.capacity):
            node = self.buckets[i]
            while node:
                elements.append((node.key, node.value))
                node = node.next
        return str(elements)

    def __len__(self):
        return self.size

    def __contains__(self, key):
        try:
            self.find(key)
            return True
        except KeyError:
            return False

    def printAll(self):
        for i, bucket in enumerate(self.buckets):
            print(i, end=" ")
            if bucket is not None:
                node = bucket

                print(f"--> Key: {node.key}, Value: {node.value}", end=" ")
            print("\n")