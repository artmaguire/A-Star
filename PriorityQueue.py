import heapq

__heap__ = []

def push(node):
    heapq.heappush(__heap__, node)

def push_many(nodes):
    for node in nodes:
        push(node)

def pop():
    return heapq.heappop(__heap__)
