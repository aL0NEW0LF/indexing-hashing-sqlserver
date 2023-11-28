from hashTableSeparateChainingWithLinkedList import HashTable
from hashTableSeparateChainingWithList import HashTableSC
from hashTableDoubleHashing import HashTableDH

if __name__ == '__main__':
    ht = HashTableDH()

    ht.insertDH("test_key", "test_value")
    ht.insertDH("test_key2", "test_value2")
    ht.insertDH("test_key", "test_value3")

    ht.printAll()