import numpy as np
import random
import cairo

from rTree import RTree, RNode
from roadSegment import RoadSegment
from lsystem import AbstractModule, RoadModule, BranchModule, RoadAttribute, RoadState
from helper import distance, normalize, drawRoad, drawIntersection, drawBranchPos

imageCounter = 0

def generate(iterations, dim = (1000, 1000), scale = (50, 50)):

  # Initialising necessary variables
  tree = RTree(20)
  tree.createRoot()
  q = []
  branches = []
  q.append(RoadModule(0, None, RoadAttribute(length=0.5)))
  q.append(RoadModule(0, None, RoadAttribute(dir=np.array([-1, 0]), length=0.5)))
  surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, dim[0], dim[1])
  context = cairo.Context(surface)
  context.scale(scale[0], scale[1])
  junctions = []

  # Main Loop
  for i in range(iterations):
    if i % 100 == 0:
      print(i)
    if len(q) == 0:
      break

    # Current Module
    road = q.pop(0)

    # Checking if current road ends up at a junction
    roadEndPoint = road.road.pos + road.road.dir * road.road.length
    terminated = False
    for junction in junctions:
      if distance(junction, roadEndPoint) < 0.25:
        road.road.dir = normalize(junction - road.road.pos)
        road.road.length = distance(junction, road.road.pos)
        terminated = True

    # Making sure road module isn't off screen
    x, y = road.road.pos[0], road.road.pos[1]
    ratX = dim[0] / scale[0]
    ratX /= 2
    ratY = dim[1] / scale[1]
    ratY /= 2
    if np.abs(x) > ratX or np.abs(y) > ratY:
      terminated = True

    
    # If it's a road module, we draw it
    if isinstance(road, RoadModule) and road.progress == 0:
      col = np.random.rand(3)
      p0 = road.road.pos
      p1 = road.road.pos + road.road.dir * road.road.length
      newSegment = RoadSegment(p0, p1)
      intersections = tree.root.intersect(newSegment)
      radii = tree.root.pointInRadius(p1, 0.2) + tree.root.pointInRadius(newSegment.getPoint(0.5), 0.2)
      distances = [(np.array(intersection[1]), distance(p0, np.array(intersection[1]))) for intersection in intersections if distance(p0, np.array(intersection[1])) > 0.0001]
      p1, _ = min(distances, key=lambda x: x[1]) if len(distances) > 0 else (p1, None)

      if len(distances) > 0:
        terminated = True
      elif len(radii) > 0:
        minSegment = min(radii, key=lambda x: x[1])[0]
        d1 = distance(p0, minSegment.p1)
        d2 = distance(p0, minSegment.p2)
        p1 = minSegment.p1 if d1 < d2 else minSegment.p2
        terminated = True
      
      newSegment = RoadSegment(p0, p1)
      tree.insert(newSegment)
      drawRoad(context, road, scale, dim)

      if terminated:
        drawIntersection(context, p1, scale, dim)
    
    # Iterating if module not terminated
    if not terminated:
      for module in road.iterate():
        q.append(module)
        if isinstance(module, BranchModule):
            junctions.append(module.road.pos)
    
  # Drawing branch modules
  global imageCounter

  # Saving the image without branch markers
  surface.write_to_png("road{}.png".format(str(imageCounter).zfill(3)))

  for branch in junctions:
    drawBranchPos(context, branch, scale, dim)
  
  # Saving the image with branch markers
  surface.write_to_png("road{}b.png".format(str(imageCounter).zfill(3)))
  imageCounter += 1
  return tree