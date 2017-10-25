import cv2

class Camera(object):
	""" Camera object for capturing pictures and video"""
	def __init__(self, camera, dimmensions):
		"""
		Initializes a class instance

		Args:
			camera: n'th camera (zero indexed)
			width: width of image [pixels]
			height: height of image [pixels]
		Returns:
			none
		"""
		self.camera = cv2.VideoCapture(camera)
		width, height = dimmensions
		self.camera.set(3, width)
		self.camera.set(4, height)

	def get_img(self):
		"""
		Detects and calculates position of an aruco marker

		Args:
			none
		Returns:
			img: image
		Raises:
			CameraError: image could not be taken
		"""
		ret, img = self.camera.read()
		if ret:
			return img
		else:
			raise Exception('CameraError')