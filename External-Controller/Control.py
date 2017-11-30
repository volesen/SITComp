import numpy as np
import time

class State(object):
	"""docstring for State"""
	def __init__(self, p, ø):
		self.p = p #position
		self.ø = ø #angle
		self.v = 0 #velocity
		self.w = 0 #angular velocity
		self.t = time.time()
	
	def update(self, p, ø):
		dt = time.time() - self.t
		self.v = (p - self.p)/dt
		self.w = (w - self.w)/dt

		self.p = p
		self.ø = ø

		self.t = time.time()

	def direction(self):
		direction = np.array(np.cos( self.ø), np.sin(self.ø))

		return direction

	def closed_loop_update(self):
		# we assume constant velocity
		dt = time.time() - self.t
		self.p += self.v * self.direction() * dt
		self.ø += self.w * dt 

	def get_position_angle(self):
		return (self.p, self.ø)
		
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