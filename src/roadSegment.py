import numpy as np

class RoadSegment:
  def __init__(self, a, b, thickness=0.05, epsilon=0.0):
    self.p1 = np.array(a)
    self.p2 = np.array(b)
    self.thickness = thickness
    self.epsilon = epsilon

  def getPoint(self, alpha):
    return (1 - alpha) * self.p1 + alpha * self.p2

  def intersect(self, other):
    # Unpack the points
    x1, y1 = self.p1
    x2, y2 = self.p2
    x3, y3 = other.p1
    x4, y4 = other.p2

    # Calculate the determinants
    det_denominator = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)

    if det_denominator == 0:
        # The lines are parallel or coincident
        return None

    # Calculate the intersection point
    det_intersection = (x1 * y2 - y1 * x2) * (x3 - x4) - (x1 - x2) * (x3 * y4 - y3 * x4)
    intersection_x = det_intersection / det_denominator

    det_intersection = (x1 * y2 - y1 * x2) * (y3 - y4) - (y1 - y2) * (x3 * y4 - y3 * x4)
    intersection_y = det_intersection / det_denominator

    # Check if the intersection point is within the line segments
    if (min(x1, x2) <= intersection_x <= max(x1, x2) and
        min(y1, y2) <= intersection_y <= max(y1, y2) and
        min(x3, x4) <= intersection_x <= max(x3, x4) and
        min(y3, y4) <= intersection_y <= max(y3, y4)):
        return np.array([intersection_x, intersection_y])

    return None

  def looseIntersect(self, other):
    b1a, b1b = self.boundingBox()
    b2a, b2b = other.boundingBox()

    b1a[0], b1b[0]

    xoverlap, yoverlap = False, False

    if b2a[0] > b1a[0] and b2a[0] < b1b[0]:
      xoverlap = True

    if b2b[0] > b1a[0] and b2b[0] < b1b[0]:
      xoverlap = True

    if b2a[1] > b1a[1] and b2a[1] < b1b[1]:
      yoverlap = True

    if b2b[1] > b1a[1] and b2b[1] < b1b[1]:
      yoverlap = True

    return xoverlap and yoverlap

  def pointInBounds(self, point):
    b1, b2 = self.boundingBox()
    if point[0] > b1[0] and point[0] < b2[0]:
      if point[1] > b1[1] and point[1] < b2[1]:
        return self.pointDistance(point)
    return -1

  def pointDistance(self, point):
    l = np.linalg.norm(self.p2 - self.p1) ** 2
    if l == 0:
      return np.linalg.norm(self.p1 - point)
    t = max(0, min(1, np.dot(point - self.p1, self.p2 - self.p1) / l))
    proj = self.p1 + t * (self.p2 - self.p1)
    return np.linalg.norm(point - proj)
    # num = np.abs((self.p2[1] - self.p1[1]) * point[0] - (self.p2[0] - self.p1[0]) * point[1] + self.p2[0] * self.p1[1] - self.p2[1] * self.p1[0])
    # den = np.sqrt((self.p2[1] - self.p1[1])**2 + (self.p2[0] - self.p1[0])**2)
    # return num / den

  def boundingBox(self):
    return [(min(self.p1[0], self.p2[0]) - self.epsilon, min(self.p1[1], self.p2[1]) - self.epsilon),\
             (max(self.p1[0], self.p2[0]) + self.epsilon, max(self.p1[1], self.p2[1]) + self.epsilon)]

  def draw(self, ctx, scale, dim, color=(0, 0, 0)):
    incr = (dim[0] / scale[0], dim[1] / scale[1])
    startPos = (self.p1[0] + (incr[0] / 2),  self.p1[1] + (incr[0] / 2))
    endPos = (self.p2[0] + (incr[0] / 2),  self.p2[1] + (incr[0] / 2))
    ctx.set_line_width(self.thickness)
    ctx.set_source_rgba(color[0], color[1], color[2], 1)
    ctx.move_to(startPos[0], startPos[1])
    ctx.line_to(endPos[0], endPos[1])
    ctx.stroke()

  def __str__(self):
    return str(self.p1) + " → " + str(self.p2)