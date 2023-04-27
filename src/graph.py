from helper import distance
from roadSegment import RoadSegment

def createGraph(tree):
  segments = tree.getSegmentList()
  graph = dict()
  for segment in segments:
    p1 = tuple(segment.p1)
    p2 = tuple(segment.p2)
    if p1 not in graph:
      graph[p1] = []
    if p2 not in graph:
      graph[p2] = []
    graph[p1].append(p2)
    graph[p2].append(p1)
  return graph

def BFS(tree, graph, start, end):
  print(tree.root.pointInRadius(start, 1))
  start_segment = min(tree.root.pointInRadius(start, 1), key=lambda x: x[1])[0]
  end_segment = min(tree.root.pointInRadius(end, 1), key=lambda x: x[1])[0]
  start_actual = start_segment.p1 if distance(start, start_segment.p1) < distance(start, start_segment.p2) else start_segment.p2
  end_actual = end_segment.p1 if distance(end, end_segment.p1) < distance(end, end_segment.p2) else end_segment.p2
  start_actual = tuple(start_actual)
  end_actual = tuple(end_actual)
  q = [(start_actual, None)]
  visited = set()
  path = dict()
  while len(q) > 0:
    curr, parent = q.pop(0)

    for neighbor in graph[curr]:
      if neighbor not in path:
        q.append((neighbor, curr))
    
    path[curr] = parent

    if curr == end_actual:
      break
  
  curr = end_actual
  pathway = []
  while curr != None:
    pathway.append(curr)
    curr = path[curr]

  segmentPath = []
  for i in range(1, len(pathway)):
    segmentPath.append(RoadSegment(pathway[i - 1], pathway[i]))
  return segmentPath