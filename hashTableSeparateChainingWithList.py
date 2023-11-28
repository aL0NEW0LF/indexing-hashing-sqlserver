# Node data structure - essentially a LinkedList node
class Node:
    def __init__(self, key, value):
        self.key = key
        self.value = value

    def __str__(self):
        return "<Node: (%s, %s)" % (self.key, self.value)

    def __repr__(self):
        return str(self)


# Hash table with separate chaining
class HashTableSC:
    # Initialize hash table
    def __init__(self, INITIAL_CAPACITY = 50):
        self.capacity = INITIAL_CAPACITY
        self.size = 0
        self.buckets = [[] for _ in range(self.capacity)]

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
        bucket = self.buckets[index]
        # Go to the node corresponding to the hash
        bucket.append(Node(key, value))

    # Find a data value based on key
    # Input:  key - string
    # Output: value stored under "key" or None if not found
    def find(self, key):
        # 1. Compute hash
        index = self.hash(key)
        # 2. Go to first node in list at bucket
        bucket = self.buckets[index]
        for node in bucket:
            if node.key is None:
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
        bucket = self.buckets[index]
        # 2. Iterate to the requested node
        for node in bucket:
            if key in node.key:
                bucket.remove(node)
                return node
        return f"{key} not found"

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
                for node in bucket:
                    print(f"--> Key: {node.key}, Value: {node.value}", end=" ")
            print("\n")