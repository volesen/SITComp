import numpy as np
import cv2
import math

class Transform(object):
	"""Takes camera coordinates and transforms them to birds eye view for a defined rectangle"""

	def __init__(self, img, track_dimmnesions):
		"""
		Initializes a class instance

		Args:
			img: inital undistorted image to define perspective transform
			track_dimmensions: width and height of track [cm]
		Returns:
			none
		"""
		self.track_width, self.track_height = track_dimmnesions
		self.points = []
		
		cv2.namedWindow('Init')
		cv2.setMouseCallback('Init', self.set_point)

		# define corners of ROI when clicked
		while len(self.points) < 4:
			cv2.imshow('Init', img)
			if cv2.waitKey(20) & 0xFF == 27: # Close window on 'Esc'
				break

		cv2.destroyWindow('Init')
		
		self.M = self.set_perspective_transform(img, self.points)
		
		self.scale = np.array([
			[self.track_width / self.dst_width, 0],
			[0, self.track_height / self.dst_height]])

	def set_point(self, event, x, y, flags, param):
		"""
		Initializes points on mouseCallback's

		Args:
			event: event context
			x: x-coordinate
			y: y-coordinate
			flags: idk
			param: idk
		Returns:
			none
		"""
		if event == cv2.EVENT_LBUTTONDOWN:
			self.points.append((x,y))

	def order_points(self, pts):
		"""
		Sort points clockwise around center of ROI

		Args:
			points: corners of ROI (list of tuples)
		Returns:
			rect: ordered points
		"""
		pts = np.asarray(pts, dtype = "float32") #convert list of points to numpy array
		rect = np.empty((4, 2), dtype = "float32")

		# the top-left point will have the smallest sum, whereas
		# the bottom-right point will have the largest sum
		s = pts.sum(axis = 1)
		rect[0] = pts[np.argmin(s)]
		rect[2] = pts[np.argmax(s)]
	 
		# compute the difference between the points,
		# the top-right point will have the smallest difference,
		# whereas the bottom-left will have the largest difference
		diff = np.diff(pts, axis = 1)
		rect[1] = pts[np.argmin(diff)]
		rect[3] = pts[np.argmax(diff)]
	 
		# return the ordered coordinates
		return rect

	def set_perspective_transform(self, img, pts):
		# obtain a consistent order of the points and unpack them
		# individually
		rect = self.order_points(pts)
		(tl, tr, br, bl) = rect
		
		# compute the width of the new image, which will be the
		# maximum distance between bottom-right and bottom-left
		# x-coordiates or the top-right and top-left x-coordinates
		self.dst_width = int(max(np.linalg.norm(br-bl), np.linalg.norm(tr-tl)))

		# compute the height of the new image, which will be the
		# maximum distance between the top-right and bottom-right
		# y-coordinates or the top-left and bottom-left y-coordinates
		self.dst_height = int(max(np.linalg.norm(tr-br), np.linalg.norm(tl-bl)))
		
		# define corners of the ROI, after perspective transform (clockwise)
		dst = np.array([
			[0, 0],
			[self.dst_width, 0],
			[self.dst_width, self.dst_height],
			[0, self.dst_height]], dtype = "float32")
	 
		# compute perspective transform matrix
		perspective_transform_matrix = cv2.getPerspectiveTransform(rect, dst)

		return perspective_transform_matrix

	def transform_corners(self, points):
		# append third dimmension, z = 1, to all points
		points = np.hstack([points, np.ones([4,1])])

		# transform of points with the perspective transform matrix and transpose
		transformed_points = np.matmul(points, self.M.T).T

		# divide the x,y-coordinates by the z-coordinate and transpose
		transformed_points = np.divide(transformed_points[:-1], transformed_points[-1]).T

		# apply scale matrix
		scaled_points = np.matmul(transformed_points, self.scale)

		return scaled_points
