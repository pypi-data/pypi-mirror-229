class Node:
    """A basic node for linked data structures."""

    def __init__(self, data=None, next_node: 'Node' = None):
        """
        Initialize a new node.
        :param data: The data to be stored in the node.
        :param next_node: The next node in the linked structure.
        """
        self._data = data
        self._next = next_node

    def __eq__(self, other):
        if isinstance(other, Node):
            return self.data == other.data and self.next == other.next
        return False

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, data):
        self._data = data

    @property
    def next(self) -> 'Node':
        return self._next

    @next.setter
    def next(self, ptr: 'Node'):
        if not isinstance(ptr, (Node, type(None))):
            raise TypeError("The pointer should be a Node or None")
        self._next = ptr
