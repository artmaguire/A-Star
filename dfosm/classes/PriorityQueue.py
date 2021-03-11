import heapq


class PriorityQueue:
    def __init__(self):
        self.__heap__ = []

    def push(self, node):
        heapq.heappush(self.__heap__, node)

    def push_many(self, nodes):
        for node in nodes:
            self.push(node)

    def pop(self):
        try:
            item = heapq.heappop(self.__heap__)
        except IndexError:
            item = None

        return item

    def heapify(self):
        return heapq.heapify(self.__heap__)

    def size(self):
        return len(self.__heap__)

    def to_list(self):
        return list(item for item in self.__heap__)
