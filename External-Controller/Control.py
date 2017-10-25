import numpy as np

class State(object):
	"""docstring for State"""
	def __init__(self, p, ø, v, w):
		self.p = p #position
		self.ø = ø #angle
		self.v = v #velocity
		self.w = w #angular velocity

	def update(self):
		pass

	def closed_loop_update(self):
		pass

waypoints = np.array([
	[0.75, 0.75],
	[6.25, 0.75],
	[6.25, 3.25],
	[0.75, 3.25]])

print(corner)


#print(np.linspace(corner[2][0], corner[1][0], 625))
#path_span = [np.array(np.arange(corner[i][0], corner[i-1][0], 0.1), np.arange(corner[i][1], corner[i-1][1]), 0.1) for i in range(len(corner))]

#print(path_span)

class PurePursuit(object):
	"""docstring for PurePursuit"""
	def __init__(self, arg):
		self.arg = arg
		

class PID(object):
	"""docstring for PID"""
	def __init__(self, k_p, k_i, k_d):
		self.k = np.array([k_p, k_i, k_d])
		self.e = np.array([0, 0, 0])

	def update(self, target, current, dt):
		e = target - current
		self.e[2] = (e - e[0]) / dt #derivative term
		self.e[1] = (e + e[0]) * dt #integral term
		self.e[0] = e #proportional term
		return np.dot(k, e)