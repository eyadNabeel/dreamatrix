import numpy as np
import random

def newBoundingBox(box, segment):
  x1, y1 = segment.p1
  x2, y2 = segment.p2
  bx1, bx2 = box.b1[0], box.b2[0]
  by1, by2 = box.b1[1], box.b2[1]

  x = [x1, x2, bx1, bx2]
  y = [y1, y2, by1, by2]

  return [(min(x), min(y)), (max(x), max(y))]

def calculateBoundingBox(s1, s2):
  s1x1, s1y1 = s1.p1
  s1x2, s1y2 = s1.p2
  s2x1, s2y1 = s2.p1
  s2x2, s2y2 = s2.p2

  x = [s1x1, s1x2, s2x1, s2x2]
  y = [s1y1, s1y2, s2y1, s2y2]

  return [(min(x), min(y)), (max(x), max(y))]

def calculateBoxArea(b):
  l = np.abs(b[0][1] - b[1][1])
  w = np.abs(b[0][0] - b[1][0])
  return l * w

def drawLine(ctx, start, end, thickness=0.02, color=(0, 0, 0, 1)):
  ctx.set_line_width(thickness)
  ctx.set_source_rgba(color[0], color[1], color[2], color[3])
  ctx.move_to(float(start[0]), float(start[1]))
  ctx.line_to(float(end[0]), float(end[1]))
  ctx.stroke()

def normalize(v):
  return v / np.linalg.norm(v)

def rotate(v, angle):
  matrix = np.array([[np.cos(angle), -np.sin(angle)],\
                     [np.sin(angle), np.cos(angle)]])
  return np.matmul(matrix, v)

def drawRoad(ctx, module, scale, dimensions, color=(0, 0, 0, 1)):
  features = module.road
  incr = (dimensions[0] / scale[0], dimensions[1] / scale[1])
  startPos = (features.pos[0] + (incr[0] / 2),  features.pos[1] + (incr[0] / 2))
  endPos = startPos + features.dir * features.length
  drawLine(ctx, startPos, endPos, thickness=0.05, color=color)

def drawBranch(ctx, module, scale, dimensions):
  features = module.road
  incr = (dimensions[0] / scale[0], dimensions[1] / scale[1])
  pos = (features.pos[0] + (incr[0] / 2),  features.pos[1] + (incr[0] / 2))
  ctx.arc(pos[0], pos[1], 0.08, 0, 2*np.pi)
  ctx.set_source_rgb(0.0, 0.7 + (random.random() * 0.6) - 0.3, 0.0)
  ctx.fill()

def drawBranchPos(ctx, pos, scale, dimensions):
  incr = (dimensions[0] / scale[0], dimensions[1] / scale[1])
  pos = (pos[0] + (incr[0] / 2),  pos[1] + (incr[0] / 2))
  ctx.arc(pos[0], pos[1], 0.08, 0, 2*np.pi)
  ctx.set_source_rgb(0.0, 0.7 + (random.random() * 0.6) - 0.3, 0.0)
  ctx.fill()

def drawIntersection(ctx, pos, scale, dimensions):
  incr = (dimensions[0] / scale[0], dimensions[1] / scale[1])
  pos = (pos[0] + (incr[0] / 2),  pos[1] + (incr[0] / 2))
  ctx.arc(pos[0], pos[1], 0.08, 0, 2*np.pi)
  ctx.set_source_rgb(0.7 + (random.random() * 0.6) - 0.3, 0.0, 0.0)
  ctx.fill()

def drawRadius(pos, radius, ctx, scale, dimensions, color=(1, 0, 0)):
  incr = (dimensions[0] / scale[0], dimensions[1] / scale[1])
  pos = (pos[0] + (incr[0] / 2),  pos[1] + (incr[0] / 2))
  ctx.arc(pos[0], pos[1], radius, 0, 2*np.pi)
  ctx.set_source_rgb(color[0], color[1], color[2])
  ctx.fill()

def distance(a, b):
  v = b - a
  return np.sqrt(v[0] ** 2 + v[1] ** 2)