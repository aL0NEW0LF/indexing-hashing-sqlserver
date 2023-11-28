# Node data structure - essentially a LinkedList node
class Node:
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.next = None

    def __str__(self):
        return "<Node: (%s, %s), next: %s>" % (self.key, self.value, self.next is not None)

    def __repr__(self):
        return str(self)


# Hash table with separate chaining
class HashTable:
    # Initialize hash table
    def __init__(self, INITIAL_CAPACITY = 50):
        self.capacity = INITIAL_CAPACITY
        self.size = 0
        self.buckets = [None] * self.capacity

    # Generate a hash for a given key
    # Input:  key - string
    # Output: Index from 0 to self.capacity
    def hash(self, key):
        hashsum = 0
        # For each character in the key
        for index, c in enumerate(key):
            # Add (index + length of key) ^ (current char code)
            hashsum += (index + len(key)) ** ord(c)
            # Perform modulus to keep hashsum in range [0, self.capacity - 1]
            hashsum = hashsum % self.capacity
        return hashsum

    # Insert a key,value pair to the hashtable
    # Input:  key - string
    # 		  value - anything
    # Output: void
    def insertSC(self, key, value):
        # 1. Increment size
        self.size += 1
        # 2. Compute index of key
        index = self.hash(key)
        # Go to the node corresponding to the hash
        node = self.buckets[index]
        # 3. If bucket is empty:
        if node is None:
            # Create node, add it, return
            self.buckets[index] = Node(key, value)
            return
        # 4. Iterate to the end of the linked list at provided index
        prev = node
        while node is not None:
            prev = node
            node = node.next
        # Add a new node at the end of the list with provided key/value
        prev.next = Node(key, value)

    # Insert a key,value pair to the hashtable
    # Input:  key - string
    # 		  value - anything
    # Output: void
    def insertLP(self, key, value):
        # 1. Increment size
        self.size += 1
        # 2. Compute index of key
        index = self.hash(key)
        prev = self.buckets[index]
        # 3. If bucket is empty:
        if self.buckets[index] is None:
            # Create node, add it, return
            self.buckets[index] = Node(key, value)
            return

        while self.buckets[index] is not None:
            index = index + 1

        # Add a new node at the end of the list with provided key/value
        self.buckets[index] = Node(key, value)
        prev.next = Node(key, value)

    # Find a data value based on key
    # Input:  key - string
    # Output: value stored under "key" or None if not found
    def find(self, key):
        # 1. Compute hash
        index = self.hash(key)
        # 2. Go to first node in list at bucket
        node = self.buckets[index]
        # 3. Traverse the linked list at this node
        while node is not None and node.key != key:
            node = node.next
        # 4. Now, node is the requested key/value pair or None
        if node is None:
            # Not found
            return None
        else:
            # Found - return the data value
            return node

    # Remove node stored at key
    # Input:  key - string
    # Output: removed data value or None if not found
    def removeSC(self, key):
        # 1. Compute hash
        index = self.hash(key)
        node = self.buckets[index]
        prev = None
        # 2. Iterate to the requested node
        while node is not None and node.key != key:
            prev = node
            node = node.next
        # Now, node is either the requested node or none
        if node is None:
            # 3. Key not found
            return None
        else:
            # 4. The key was found.
            self.size -= 1
            result = node.value
            # Delete this element in linked list
            if prev is None:
                self.buckets[index] = node.next  # May be None, or the next match
            else:
                prev.next = prev.next.next  # LinkedList delete by skipping over
            # Return the deleted result
            return result

    def removeLP(self, key):
        # 1. Compute hash
        index = self.hash(key)
        node = self.buckets[index]
        prev = self.buckets[index]
        # 2. Iterate to the requested node
        while node is not None and node.key != key:
            node = node.next
        # Now, node is either the requested node or none
        if node is None:
            # 3. Key not found
            return None
        else:
            # 4. The key was found.
            self.size -= 1
            result = node.value
            # Delete this element in linked list
            if prev is None:
                self.buckets[index] = node.next  # May be None, or the next match
            else:
                prev.next = prev.next.next  # LinkedList delete by skipping over
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

                while node is not None:
                    print(f"--> Key: {node.key}, Value: {node.value}", end=" ")
                    node = node.next
            print("\n")