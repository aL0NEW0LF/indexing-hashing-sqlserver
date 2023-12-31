import numpy as np

from BPlusTree import BPlusTree
from hashTableSeparateChainingWithLinkedList import HashTable
from hashTableSeparateChainingWithList import HashTableSC
from hashTableDoubleHashing import HashTableDH
import random  # for demo test

if __name__ == '__main__':
    ht = HashTableDH()

    ht.insertDH("test_key", "test_value")
    ht.insertDH("test_key2", "test_value2")
    ht.insertDH("test_key", "test_value3")

    ht.printAll()

    bplustree = BPlusTree()

    random_list = random.sample(range(1, 100), 50)
    for i in random_list:
        bplustree[i] = 'test' + str(i)
        print('Insert ' + str(i))
        bplustree.show()

    bplustree.plot_tree()

    random.shuffle(random_list)
    for i in random_list:
        print('Delete ' + str(i))
        bplustree.delete(i)
        bplustree.show()