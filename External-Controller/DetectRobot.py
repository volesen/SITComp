from Camera import Camera
from PerspectiveTransform import Transform

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
		self.w = (ø - self.ø)/dt

		self.p = p
		self.ø = ø

		self.t = time.time()

	def direction(self):
		direction = np.array(np.cos(self.ø), np.sin(self.ø))

		return direction

	def closed_loop_update(self):
		# we assume constant velocity
		dt = time.time() - self.t
		self.p += self.v * self.direction() * dt
		self.ø += self.w * dt 

	def get_position_angle(self):
		return (self.p, self.ø)

class DetectRobot(object):
	"""Detect robot from camera input with aruco markers"""
	
	def __init__(self, dimmensions, camera, track_dim, file):
		"""
		Initializes a class instance

		Args:
			dimmensions: dimmensions of image [pixel]
			camera: camera object
		Returns:
			none
		"""
		self.state = State(0,np.array([4,3.125]),0 )

		self.dimmensions = dimmensions
		self.aruco_dict = aruco.Dictionary_get(aruco.DICT_4X4_50)
		self.aruco_params = aruco.DetectorParameters_create()
		self.camera = camera
		self.load_camera_coeff(file)
		distorted_img = self.camera.get_img()
		self.transform = Transform(self.undistort(distorted_img), track_dim)

	def load_camera_coeff(self, file):
		"""
		Loads and assigns camera coefficient from
		npy-file and assigns to class variables

		Args:
			file: path to camera coefficients
		Return:
			none
		"""
		coeff = np.load(file)
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

	def detect_corners(self, marker_id):
		"""
		Detects and calculates position of an aruco marker

		Args:
			marker_id: id of aruco marker
		Returns:
			tuple: x position, y position, yaw
		Raises:
			NoDetction: no aruco marker detected
		"""
		# get current frame
		distorted_img = self.camera.get_img()

		#undistort image
		img = self.undistort(distorted_img)

		# convert to greyscale (aruco.detectMarkers() requires a greyscale image)
		img_grey = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) 

		# detect corners
		corners, ids, rejected_points = aruco.detectMarkers(img_grey, self.aruco_dict, parameters = self.aruco_params)

		if ids is not None:
			if np.any(ids == marker_id):

				# find index of marker_id in ids
				marker_index = np.nonzero(ids == marker_id)[0][0]

				# return corner of marker_id'th marker
				return corners[marker_index][0]
			else:
				raise Exception('DetectionError')
		else:
			raise Exception('DetectionError')

	def detect_position_angle(self, marker_id):
		try:
			#get corners
			corners = self.detect_corners(marker_id)
			# perspective transform corners
			transformed_corner = self.transform.transform_corners(corners)

			#calculate center of aruco marker
			center = transformed_corner[0] + 0.5 * (transformed_corner[2] - transformed_corner[0])

			#calculate direction vector
			angle = transformed_corner[1] - transformed_corner[2]

			#calculate angle between x-axis and the direction vector in the interval [-pi, pi]
			angle = np.degrees(np.arctan2(angle[1], angle[0]))

		except DetectionError:
			self.state.closed_loop_update()
		else:
			self.state.update(center, angle)

		return self.state.get_position_angle()

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
