import numpy as np
from enum import Enum
import random
from helper import rotate

class AbstractModule:
  def __gt__(self, other):
    return self.delay > other.delay
  def __lt__(self, other):
    return self.delay < other.delay
  def __eq__(self, other):
    return self.delay == other.delay

# class InsertionModule(AbstractModule):
#   def __init__(self, attr, status):
#     self.attr = attr
#     self.status = status

class RoadModule(AbstractModule):
  def __init__(self, delay, rule, road, progress=0, col=(0, 0, 0, 1)):
    self.delay = delay
    self.progress = progress
    self.rule = rule
    self.road = road
    self.col = col

  def iterate(self):
    global ANGLE_RANGE

    if self.progress > 0:
      self.progress -= 1
      return [self]
    else:
      rot = np.random.rand(1)[0]
      successor = [RoadModule(self.delay, None, self.road.succeed(), progress=self.delay, col=self.col)]
      if random.random() > 0.5:
        factor = np.sign(random.random() - 0.5)
        col = np.random.rand(3)
        # angle = np.random.uniform(-ANGLE_RANGE, ANGLE_RANGE)
        angle = np.random.normal(0, ANGLE_RANGE / 4)
        rotated = rotate(self.road.dir, factor * np.deg2rad(90 + angle))
        successor.append(BranchModule(5, None, \
                            RoadAttribute(length=0.5, \
                                      dir=rotated,\
                                      pos=self.road.pos + self.road.dir * self.road.length), \
                                      col=(col[0], 0, col[2], 1)))
      return successor
    
  def __str__(self):
    return "Road Module - Delay: {}/{} - Position: {} - Direction: {}".format(str(self.delay - self.progress), str(self.delay), str(self.road.pos), str(self.road.dir))

class BranchModule(AbstractModule):
  def __init__(self, delay, rule, road, col=(0, 0, 0, 1)):
    self.delay = delay
    self.progress = delay
    self.rule = rule
    self.road = road
    self.col = col
  
  def iterate(self):
    if self.progress == 0:
      return [RoadModule(self.delay, self.rule, self.road, col=self.col)]
    self.progress -= 1
    return [self]

  def __str__(self):
    return "Branch Module - Delay: {}/{} - Position: {} - Direction: {}".format(str(self.delay - self.progress), str(self.delay), str(self.road.pos), str(self.road.dir))

class RoadAttribute(AbstractModule):
  def __init__(self, length = 1, \
               dir = np.array([1, 0]), \
               pos = np.array([0, 0]), \
               momentum = np.array([0.5, 0.5])):
    self.length = length
    self.pos = pos
    self.dir = dir / np.sqrt(dir[0] ** 2 + dir[1] ** 2)
    self.momentum = momentum
  
  def succeed(self):
    rng = np.random.rand(2)
    return RoadAttribute(self.length, \
                         self.dir + (rng - np.array(self.momentum)) * 0.2, \
                         self.pos + self.dir * self.length, \
                         (self.momentum[0] + (rng[0] - 0.5) * 0.1, self.momentum[1] + (rng[1] - 0.5) * 0.1))

class RoadState(Enum):
  UNASSIGNED = 0
  SUCCEED = 1
  FAILED = 2