import numpy as np
import cv2
from cv2 import aruco

from Camera import Camera
from PerspectiveTransform import Transform

class DetectRobot(object):
	"""Detect robot from camera input with aruco markers"""
	
	def __init__(self, dimmensions, camera, track_dim):
		"""
		Initializes a class instance

		Args:
			dimmensions: dimmensions of image [pixel]
			camera: camera object
		Returns:
			none
		"""
		self.dimmensions = dimmensions
		self.aruco_dict = aruco.Dictionary_get(aruco.DICT_4X4_50)
		self.aruco_params = aruco.DetectorParameters_create()
		self.camera = camera
		self.transform = Transform(self.camera.get_img(), track_dim)

	def load_camera_coeff(self, file):
		"""
		Loads and assigns camera coefficient from
		npy-file and assigns to class variables

		Args:
			file: path to camera coefficients
		Return:
			none
		"""
		coeff = np.load('cameraCalibration.npz')
		self.camera_matrix = coeff['mtx']
		self.dist = coeff['dist']

		# calculate optimal camera matrix and ROI
		self.optimal_camera_matrix, roi = cv2.getOptimalNewCameraMatrix(
			self.camera_matrix, 
			self.dist, 
			self.dimmensions,
			1,
			self.dimmensions)

		# calculate coefficients for undistortion
		self.map_x, self.map_y = cv2.initUndistortRectifyMap(
			self.camera_matrix,
			self.dist,
			None,
			self.optimal_camera_matrix,
			self.dimmensions,
			5)

	def undistort(self, img):
		"""
		Undistorts image based on camera calibration

		Args:
			img: distorted image
		Returns:
			undistorted_img: undistorted image (uncropped, hence same dimmensions as img)
		"""
		undistorted_img = cv2.remap(img, self.map_x, self.map_y, cv2.INTER_LINEAR)
		return undistorted_img

	def get_corners(self, img, marker_id):
		"""
		Detects and calculates position of an aruco marker

		Args:
			img: undistorted image
			marker_id: id of aruco marker
		Returns:
			tuple: x position, y position, yaw
		Raises:
			NoDetction: no aruco marker detected
		"""
		img_grey = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) # aruco.detectMarkers() requires a greyscale image
		corners, ids, rejected_points = aruco.detectMarkers(img_grey, self.aruco_dict, parameters = self.aruco_params)
		
		if ids is not None: # runtime error
			return corners
		else:
			raise Exception('DetectionError')

	def return_aruco_marker(self, n, length):
		"""
		Returns aruco marker from arcuco.DICT_4X4_50
		as a numpy array
		
		Args:
			n: n'th aruco marker from dictionary
			length: sidelength of aruco marker [pixels]
		Returns:
			img: n'th aruco marker from dictionary as a numpy array

		"""
		return cv2.aruco.drawMarker(self.aruco_dict, n, length)