import numpy as np
from roadSegment import RoadSegment
from helper import newBoundingBox, calculateBoundingBox, calculateBoxArea

id = 0
class RNode:
  def __init__(self, capacity, seed=None):
    global id
    self.children = []
    if seed != None:
      self.children.append(seed)
      self.setBoundingBox(seed.boundingBox())
      self.capacity = capacity
      self.size = 1
    else:
      self.b1 = (0, 0)
      self.b2 = (0, 0)
      self.capacity = capacity
      self.size = 0
    self.id = id
    id += 1

  def __str__(self):
    return "RNode {} ---------\nCapacity: {}/{}\nBounding Box: {} {}\nChildren: {}".format(self.id, self.size, self.capacity, self.b1, self.b2, self.children)

  def __eq__(self, __o: object) -> bool:
    return self.id == __o.id

  def setBoundingBox(self, box):
    self.b1 = box[0]
    self.b2 = box[1]

  def getBoundingBox(self):
    return [self.b1, self.b2]

  def expandBoundingBox(self, segment):
    x1, y1 = segment.p1
    x2, y2 = segment.p2
    bx1, bx2 = self.b1[0], self.b2[0]
    by1, by2 = self.b1[1], self.b2[1]

    x = [x1, x2, bx1, bx2]
    y = [y1, y2, by1, by2]

    self.b1 = (min(x), min(y))
    self.b2 = (max(x), max(y))

  def overlap(self, segment, radius=0):
    x1, y1 = segment.p1
    x2, y2 = segment.p2
    sxmin, sxmax = min(x1, x2), max(x1, x2)
    symin, symax = min(y1, y2), max(y1, y2)

    bx1, bx2 = self.b1[0], self.b2[0]
    by1, by2 = self.b1[1], self.b2[1]
    bxmin, bxmax = min(bx1, bx2) - radius, max(bx1, bx2) + radius
    bymin, bymax = min(by1, by2) - radius, max(by1, by2) + radius

    if sxmax < bxmin or sxmin > bxmax:
      return False
    if symax < bymin or symin > bymax:
      return False
    return True

  def addChildNode(self, segment):
    newChild = RNode(self.capacity, seed=segment)
    self.expandBoundingBox(segment)
    self.children.append(newChild)
    return newChild

  def addChild(self, segment):
    self.children.append(segment)
    self.size += 1
    self.expandBoundingBox(segment)
    if self.size == self.capacity:
      self.split()

    
  def findOptimalLeaf(self, segment):
    leaves = []
    # Check if it's a leaf node or not
    if self.capacity == -1:
      # If it isn't add the child nodes to the list
      for child in self.children:
        optimalLeaf = child.findOptimalLeaf(segment)
        leaves.append(optimalLeaf)
    else:
      # If it is return the bounding box that would be there if we added
      # the new segment
      oldbox = segment.boundingBox()
      box = newBoundingBox(self, segment)
      oldarea = (oldbox[1][0] - oldbox[0][0]) * (oldbox[1][1] - oldbox[0][1])
      area = (box[1][0] - box[0][0]) * (box[1][1] - box[0][1])
      enlargement = np.abs(oldarea - area)
      return (self, enlargement)
    
    min_area = float('inf')
    min_leaf = None
    for leaf, area in leaves:
      if area < min_area:
        min_area = area
        min_leaf = leaf
    return (min_leaf, min_area)

  def intersect(self, segment):
    if not self.overlap(segment):
      return []
    segments = []
    if self.capacity == -1:
      for child in self.children:
        segments += child.intersect(segment)
    else:
      for child in self.children:
        isect = child.intersect(segment)
        if isect is not None:
          segments.append((child, tuple(isect)))
    return segments

  def pointInRadius(self, point, cutoff):
    segment = RoadSegment(point, point)
    if not self.overlap(segment, radius=cutoff):
      return []
    segments = []
    if self.capacity == -1:
      for child in self.children:
        segments += child.pointInRadius(point, cutoff)
    else:
      for child in self.children:
        radius = child.pointDistance(point)
        if radius <= cutoff and radius >= 0:
          segments.append((child, radius))
    return segments

  def selectSeeds(self):
    childA, childB = None, None
    idxA, idxB = -1, -1
    enlargement = float('-inf')
    for i in range(self.size):
      for j in range(i + 1, self.size):
        bounds = calculateBoundingBox(self.children[i], self.children[j])
        a = calculateBoxArea(bounds)
        a1 = calculateBoxArea(self.children[i].boundingBox())
        a2 = calculateBoxArea(self.children[j].boundingBox())
        diff = np.abs(a - a1) + np.abs(a - a2)
        if diff > enlargement:
          childA, childB = self.children[i], self.children[j]
          idxA, idxB = i, j
          enlargement = diff
    del self.children[max(idxA, idxB)]
    del self.children[min(idxA, idxB)]
    self.size = len(self.children)
    return childA, childB


  def split(self):
    if self.capacity != self.size or self.capacity == -1:
      return
    seedA, seedB = self.selectSeeds()


    # Adding node children while we have segment children is screwing with the algo, we have to extract the rest somehow
    nodeA = self.addChildNode(seedA)
    nodeB = self.addChildNode(seedB)

    enlargementA, enlargementB = float('inf'), float('inf')
    minAreaA, minAreaB = float('inf'), float('inf')
    idxA, idxB = -1, -1

    boxA = calculateBoxArea(seedA.boundingBox())
    boxB = calculateBoxArea(seedB.boundingBox())

    while self.size > 0:
      for i in range(self.size):
        child = self.children[i]
        if type(child) == RNode:
          continue
        areaA = calculateBoxArea(calculateBoundingBox(self.children[i], seedA))
        areaB = calculateBoxArea(calculateBoundingBox(self.children[i], seedA))
        areaChild = calculateBoxArea(self.children[i].boundingBox())
        
        newEnlargementA = np.abs(areaA - boxA)
        newEnlargementB = np.abs(areaB - boxB)

        if newEnlargementA < enlargementA:
          enlargementA = newEnlargementA
          minAreaA = areaA
          idxA = i

        if newEnlargementB < enlargementB:
          enlargementB = newEnlargementB
          minAreaB = areaB
          idxB = i
            
      if idxA != idxB:
        nodeA.addChild(self.children[idxA])
        nodeB.addChild(self.children[idxB])
        del self.children[max(idxA, idxB)]
        del self.children[min(idxA, idxB)]
      elif minAreaA < minAreaB:
        nodeA.addChild(self.children[idxA])
        del self.children[idxA]
      elif minAreaB < minAreaA:
        nodeB.addChild(self.children[idxB])
        del self.children[idxB]
      elif nodeA.size <= nodeB.size:
        nodeA.addChild(self.children[idxA])
        del self.children[idxA]
      else:
        nodeB.addChild(self.children[idxB])
        del self.children[idxB]

      # Resetting Values
      enlargementA, enlargementB = float('inf'), float('inf')
      minAreaA, minAreaB = float('inf'), float('inf')
      idxA, idxB = -1, -1

      
      self.size = len(self.children) - 2
    self.capacity = -1

  def draw(self, ctx, scale, dim, color=(1, 0, 0)):
    # Set line thickness and color
    line_thickness = 0.1
    red_color = (1, 0, 0)  # RGB color for red

    # Extract the x, y coordinates of the two corner points
    x1, y1 = self.b1
    x2, y2 = self.b2

    # Compute the width and height of the rectangle
    width = abs(x2 - x1)
    height = abs(y2 - y1)

    # Set the starting point to the top-left corner of the rectangle
    start_x = min(x1, x2)
    start_y = min(y1, y2)

    incr = (dim[0] / scale[0], dim[1] / scale[1])
    start_x = start_x + (incr[0] / 2)
    start_y = start_y + (incr[0] / 2)

    # Set the line thickness and color
    ctx.set_line_width(line_thickness)
    ctx.set_source_rgb(*color)

    # Draw the rectangle
    ctx.rectangle(start_x, start_y, width, height)

    # Stroke the rectangle
    ctx.stroke()

class RTree:
  root = None
  def __init__(self, capacity):
    self.capacity = capacity

  def createRoot(self):
    self.root = RNode(self.capacity)

  def updateBoundingBox(node):
    if node.capacity != -1:
      x0, x1, y0, y1 = float('inf'), float('-inf'), float('inf'), float('-inf')
      segs = type(node.children[0]) == RoadSegment
      for child in node.children:
        box = child.boundingBox()
        xvals = [box[0][0], box[1][0]]
        yvals = [box[0][1], box[1][1]]
        x0 = min([x0] + xvals)
        x1 = max([x1] + xvals)
        y0 = min([y0] + yvals)
        y1 = max([y1] + yvals)
    else:
      b1, b2 = node.getBoundingBox()
      x0, x1, y0, y1 = min(b1[0], b2[0]), max(b1[0], b2[0]), min(b1[1], b2[1]), max(b1[1], b2[1])
      segs = type(node.children[0]) == RoadSegment
      for child in node.children:
        if not segs:
          RTree.updateBoundingBox(child)
        box = child.boundingBox() if segs else child.getBoundingBox()
        xvals = [box[0][0], box[1][0]]
        yvals = [box[0][1], box[1][1]]
        x0 = min([x0] + xvals)
        x1 = max([x1] + xvals)
        y0 = min([y0] + yvals)
        y1 = max([y1] + yvals)
    node.setBoundingBox([(x0, y0), (x1, y1)])
  
  def insert(self, segment):
    # Find optimal node and insert
    if self.root.capacity == -1:
      node, _ = self.root.findOptimalLeaf(segment)
    else:
      node = self.root
    node.addChild(segment)

    RTree.updateBoundingBox(self.root)

  def draw(self, surface, ctx, scale, dim, drawBounds=False):
    def traverseTree(ctx, scale, dim, root):
      if type(root) == RoadSegment:
        root.draw(ctx, scale, dim)
        return
      for child in root.children:
        traverseTree(ctx, scale, dim, child)
      if drawBounds:
        root.draw(ctx, scale, dim, color=((root.id / 5), 0, 0))
    traverseTree(ctx, scale, dim, self.root)
    surface.write_to_png("roadTest.png")

  def getSegmentList(self):
    def getChildren(node):
      if node.capacity > 0:
        return node.children
      segments = []
      for child in node.children:
        segments += getChildren(child)
      return segments
    return getChildren(self.root)