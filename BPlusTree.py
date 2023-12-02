import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import graphviz

splits = 0
parent_splits = 0
fusions = 0
parent_fusions = 0


class Node(object):
    """Base node object. It should be index node
    Each node stores keys and children.
    Attributes:
        parent
    """

    def __init__(self, parent=None):
        """Child nodes are stored in values. Parent nodes simply act as a medium to traverse the tree.
        :type parent: Node"""
        self.keys: list = []
        self.values: list[Node] = []
        self.parent: Node = parent

    def index(self, key):
        """Return the index where the key should be.
        :type key: str
        """
        for i, item in enumerate(self.keys):
            if key < item:
                return i

        return len(self.keys)

    def __getitem__(self, item):
        return self.values[self.index(item)]

    def __setitem__(self, key, value):
        i = self.index(key)
        self.keys[i:i] = [key]
        self.values.pop(i)
        self.values[i:i] = value

    def split(self):
        """Splits the node into two and stores them as child nodes.
        extract a pivot from the child to be inserted into the keys of the parent.
        @:return key and two children
        """
        global splits, parent_splits
        splits += 1
        parent_splits += 1

        left = Node(self.parent)

        mid = len(self.keys) // 2

        left.keys = self.keys[:mid]
        left.values = self.values[:mid + 1]
        for child in left.values:
            child.parent = left

        key = self.keys[mid]
        self.keys = self.keys[mid + 1:]
        self.values = self.values[mid + 1:]

        return key, [left, self]

    def __delitem__(self, key):
        i = self.index(key)
        del self.values[i]
        if i < len(self.keys):
            del self.keys[i]
        else:
            del self.keys[i - 1]

    def fusion(self):
        global fusions, parent_fusions
        fusions += 1
        parent_fusions += 1

        index = self.parent.index(self.keys[0])
        # merge this node with the next node
        if index < len(self.parent.keys):
            next_node: Node = self.parent.values[index + 1]
            next_node.keys[0:0] = self.keys + [self.parent.keys[index]]
            for child in self.values:
                child.parent = next_node
            next_node.values[0:0] = self.values
        else:  # If self is the last node, merge with prev
            prev: Node = self.parent.values[-2]
            prev.keys += [self.parent.keys[-1]] + self.keys
            for child in self.values:
                child.parent = prev
            prev.values += self.values

    def borrow_key(self, minimum: int):
        index = self.parent.index(self.keys[0])
        if index < len(self.parent.keys):
            next_node: Node = self.parent.values[index + 1]
            if len(next_node.keys) > minimum:
                self.keys += [self.parent.keys[index]]

                borrow_node = next_node.values.pop(0)
                borrow_node.parent = self
                self.values += [borrow_node]
                self.parent.keys[index] = next_node.keys.pop(0)
                return True
        elif index != 0:
            prev: Node = self.parent.values[index - 1]
            if len(prev.keys) > minimum:
                self.keys[0:0] = [self.parent.keys[index - 1]]

                borrow_node = prev.values.pop()
                borrow_node.parent = self
                self.values[0:0] = [borrow_node]
                self.parent.keys[index - 1] = prev.keys.pop()
                return True

        return False


class Leaf(Node):
    def __init__(self, parent=None, prev_node=None, next_node=None):
        """
        Create a new leaf in the leaf link
        :type prev_node: Leaf
        :type next_node: Leaf
        """
        super(Leaf, self).__init__(parent)
        self.next: Leaf = next_node
        if next_node is not None:
            next_node.prev = self
        self.prev: Leaf = prev_node
        if prev_node is not None:
            prev_node.next = self

    def __getitem__(self, item):
        return self.values[self.keys.index(item)]

    def __setitem__(self, key, value):
        i = self.index(key)
        if key not in self.keys:
            self.keys[i:i] = [key]
            self.values[i:i] = [value]
        else:
            self.values[i - 1] = value

    def split(self):
        global splits
        splits += 1

        left = Leaf(self.parent, self.prev, self)
        mid = len(self.keys) // 2

        left.keys = self.keys[:mid]
        left.values = self.values[:mid]

        self.keys: list = self.keys[mid:]
        self.values: list = self.values[mid:]

        # When the leaf node is split, set the parent key to the left-most key of the right child node.
        return self.keys[0], [left, self]

    def __delitem__(self, key):
        i = self.keys.index(key)
        del self.keys[i]
        del self.values[i]

    def fusion(self):
        global fusions
        fusions += 1

        if self.next is not None and self.next.parent == self.parent:
            self.next.keys[0:0] = self.keys
            self.next.values[0:0] = self.values
        else:
            self.prev.keys += self.keys
            self.prev.values += self.values

        if self.next is not None:
            self.next.prev = self.prev
        if self.prev is not None:
            self.prev.next = self.next

    def borrow_key(self, minimum: int):
        index = self.parent.index(self.keys[0])
        if index < len(self.parent.keys) and len(self.next.keys) > minimum:
            self.keys += [self.next.keys.pop(0)]
            self.values += [self.next.values.pop(0)]
            self.parent.keys[index] = self.next.keys[0]
            return True
        elif index != 0 and len(self.prev.keys) > minimum:
            self.keys[0:0] = [self.prev.keys.pop()]
            self.values[0:0] = [self.prev.values.pop()]
            self.parent.keys[index - 1] = self.keys[0]
            return True

        return False


class BPlusTree(object):
    """B+ tree object, consisting of nodes.
    Nodes will automatically be split into two once it is full. When a split occurs, a key will
    'float' upwards and be inserted into the parent node to act as a pivot.
    Attributes:
        maximum (int): The maximum number of keys each node can hold.
    """
    root: Node

    def __init__(self, maximum=4):
        self.root = Leaf()
        self.maximum: int = maximum if maximum > 2 else 2
        self.minimum: int = self.maximum // 2
        self.depth = 0

    def find(self, key) -> Leaf:
        """ find the leaf
        Returns:
            Leaf: the leaf which should have the key
        """
        node = self.root
        # Traverse tree until leaf node is reached.
        while type(node) is not Leaf:
            node = node[key]

        return node

    def __getitem__(self, item):
        return self.find(item)[item]

    def query(self, key):
        """Returns a value for a given key, and None if the key does not exist."""
        leaf = self.find(key)
        return leaf[key] if key in leaf.keys else None

    def change(self, key, value):
        """change the value
        Returns:
            (bool,Leaf): the leaf where the key is. return False if the key does not exist
        """
        leaf = self.find(key)
        if key not in leaf.keys:
            return False, leaf
        else:
            leaf[key] = value
            return True, leaf

    def __setitem__(self, key, value, leaf=None):
        """Inserts a key-value pair after traversing to a leaf node. If the leaf node is full, split
              the leaf node into two.
              """
        if leaf is None:
            leaf = self.find(key)
        leaf[key] = value
        if len(leaf.keys) > self.maximum:
            self.insert_index(*leaf.split())

    def insert(self, key, value):
        """
        Returns:
            (bool,Leaf): the leaf where the key is inserted. return False if already has same key
        """
        leaf = self.find(key)
        if key in leaf.keys:
            return False, leaf
        else:
            self.__setitem__(key, value, leaf)
            return True, leaf

    def insert_index(self, key, values: list[Node]):
        """For a parent and child node,
                    Insert the values from the child into the values of the parent."""
        parent = values[1].parent
        if parent is None:
            values[0].parent = values[1].parent = self.root = Node()
            self.depth += 1
            self.root.keys = [key]
            self.root.values = values
            return

        parent[key] = values
        # If the node is full, split the  node into two.
        if len(parent.keys) > self.maximum:
            self.insert_index(*parent.split())
        # Once a leaf node is split, it consists of a internal node and two leaf nodes.
        # These need to be re-inserted back into the tree.

    def delete(self, key, node: Node = None):
        if node is None:
            node = self.find(key)
        del node[key]

        if len(node.keys) < self.minimum:
            if node == self.root:
                if len(self.root.keys) == 0 and len(self.root.values) > 0:
                    self.root = self.root.values[0]
                    self.root.parent = None
                    self.depth -= 1
                return

            elif not node.borrow_key(self.minimum):
                node.fusion()
                self.delete(key, node.parent)
        # Change the left-most key in node
        # if i == 0:
        #     node = self
        #     while i == 0:
        #         if node.parent is None:
        #             if len(node.keys) > 0 and node.keys[0] == key:
        #                 node.keys[0] = self.keys[0]
        #             return
        #         node = node.parent
        #         i = node.index(key)
        #
        #     node.keys[i - 1] = self.keys[0]

    def show(self, node=None, file=None, _prefix="", _last=True):
        """Prints the keys at each level."""
        if node is None:
            node = self.root
        print(_prefix, "`- " if _last else "|- ", node.keys, sep="", file=file)
        _prefix += "   " if _last else "|  "

        if type(node) is Node:
            # Recursively print the key of child nodes (if these exist).
            for i, child in enumerate(node.values):
                _last = (i == len(node.values) - 1)
                self.show(child, file, _prefix, _last)

    def output(self):
        return splits, parent_splits, fusions, parent_fusions, self.depth

    def readfile(self, reader):
        i = 0
        for i, line in enumerate(reader):
            s = line.decode().split(maxsplit=1)
            self[s[0]] = s[1]
            if i % 1000 == 0:
                print('Insert ' + str(i) + 'items')
        return i + 1

    def leftmost_leaf(self) -> Leaf:
        node = self.root
        while type(node) is not Leaf:
            node = node.values[0]
        return node

    def plot_tree(self, filename='./bplus_tree'):
        dot = graphviz.Digraph(comment='B+ Tree')
        self._plot_tree(dot, self.root)
        dot.render(filename, format='png', cleanup=True, view=True)

    def _plot_tree(self, dot, node, parent_label=None, link_label=None):
        if node is None:
            return

        if isinstance(node, Node):
            node_label = ', '.join(map(str, node.keys))
        elif isinstance(node, Leaf):
            node_label = ', '.join(map(str, node.keys))
        else:
            # Handle other types of nodes if necessary
            node_label = str(node)

        dot.node(str(id(node)), label=node_label)

        if parent_label is not None:
            dot.edge(str(parent_label), str(id(node)), label=link_label)

        if isinstance(node, Node):
            for i, child in enumerate(node.values):
                link_label = f'[{i}]'
                self._plot_tree(dot, child, parent_label=id(node), link_label=link_label)
        elif isinstance(node, Leaf):
            if node.next:
                link_label = 'next'
                self._plot_tree(dot, node.next, parent_label=id(node), link_label=link_label)

        return dot
    # def plot(self):
    #
    #     # Track node positions
    #     pos = {}
    #
    #     def set_pos(node, x, y):
    #         pos[node] = (x, y)
    #
    #     def get_pos(node):
    #         return pos.get(node, (0, 0))
    #
    #     # Plot self recursively
    #     def plot_node(node, x, y, angle_offset=np.pi/4):
    #
    #         set_pos(node, x, y)
    #
    #         if isinstance(node, Leaf):
    #             # Plot leaf node
    #             plt.Circle([x, y], 0.5, color='green')
    #             plt.text(x, y, str(node.keys))
    #
    #         else:
    #             # Plot internal node
    #             plt.Circle([x, y], 0.5, color='black')
    #             plt.text(x, y, str(node.keys))
    #
    #             # Plot lines to children
    #             x_increment = 1 / (len(node.keys) + 1)
    #
    #             num_children = len(node.values)
    #
    #             for i, child in enumerate(node.values):
    #                 angle_rad = (i / num_children) * (2 * np.pi) + angle_offset
    #                 child_x = x + x_increment * (i + 1) * np.cos(angle_rad)
    #                 child_y = y - 1 + x_increment * (i + 1) * np.sin(angle_rad)
    #
    #                 plt.plot([x, child_x], [y, child_y], color='black')
    #                 plot_node(child, child_x, child_y, angle_offset)
    #
    #     fig, ax = plt.subplots(figsize=(20, 20))
    #     plot_node(self.root, 0, 0)
    #     ax.margins(0.1)
    #     plt.axis('off')
    #     plt.show()