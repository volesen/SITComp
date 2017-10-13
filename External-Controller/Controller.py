import math

class Controller(object):
    def __init__(self, deviation_insensitivity, clockwise_direction):
        #Constants
        self.MAP_HEIGHT = 4.0
        self.MAP_WIDTH = 7.0

        #These numbers descripe the x and y coordinates of respectively vertical and horizontal lines 
        #that if crossed determine which way the robot must turn.
        #There are no protections in place for incorrect edge numbers i.e. "left" being higher 
        #than "right". Violation of these guidelines will potentially cause unexpected behavior
        self.REGION_EDGE = {
            "top": 0.75,
            "left": 0.75,
            "bottom": 3.25,
            "right": 6.25
        }

        #This is NOT for proportional control
        #A higher value makes the robot turn less.
        self.DEVIATION_INSENSITIVITY = deviation_insensitivity
        #Which way the robot should be driving
        self.CLOCKWISE_DIRECTION = clockwise_direction


    #Primary function
    def get_motor_signal(self, current_angle, current_position):
        drive_direction = self.position_to_drive_direction(current_position)
        deviation_angle = Controller.calculate_deviation_angle(current_angle, drive_direction)
        
        return self.deviation_to_motor_signal(deviation_angle)


    def position_to_drive_direction(self, position):
        """This algorithm has a problem if the robot is inside of the rectangle
        that the region edges create. 
        TODO: (non-critical) Think of fix when you have time."""

        #Find which regions robot is in (can be in two at most)
        region_top, region_left, region_bottom, region_right = \
        position[1] < self.REGION_EDGE["top"], \
        position[0] < self.REGION_EDGE["left"], \
        position[1] > self.REGION_EDGE["bottom"], \
        position[0] > self.REGION_EDGE["right"]
        
        #This next part is hard to understand. There are 16 different possible scenarios.
        #I've optimized it so that we do fewer checks and assignments which makes it hard to
        #explain how it works in all 16 different scenarios.

        #Find clockwise movement direction
        movement_direction = 0.0
        
        if region_right:
            movement_direction = Controller.rotate_90_degrees(movement_direction)

        if region_bottom:
            movement_direction = 180.0

            if region_left:
                movement_direction = Controller.rotate_90_degrees(movement_direction)
    
        elif not region_top and not region_right:
            movement_direction = 270.0

        #Adjust for for counterclockwise movement direction
        if not self.CLOCKWISE_DIRECTION:
            if sum([region_top, region_left, region_bottom, region_right]) == 2:
                movement_direction = Controller.rotate_90_degrees(movement_direction)
            else:
                movement_direction = (movement_direction + 180) % 360


        return movement_direction
    
    def calculate_deviation_angle(current_angle, desired_angle):
        #Makes deviation angle be in ]-180; 180]
        #Assuming current_angle and desired_angle are both in [0; 360[
        deviation_angle = current_angle - desired_angle
        if deviation_angle > 180:
            deviation_angle -= 360
        
        return deviation_angle

    def deviation_to_motor_signal(self, deviation_angle):
        scaler = math.tanh(deviation_angle / self.DEVIATION_INSENSITIVITY)
        
        #TODO: More thought needs to be put into this one
        #this is just a temporary hacky solution...
        #The two motor speeds (left_motor, right_motor)
        if scaler > 0:
            return [255 - scaler*255, 255]
        else: 
            #scaler is negative or zero so addition reduces value
            return [255, 255 + scaler*255]

    #region - Helper functions
    def transform_image_position_to_map(self, image_position, image_width, image_height):
        map_x = image_position[0] / image_width * self.MAP_WIDTH
        map_y = image_position[1] / image_height * self.MAP_HEIGHT

        return [map_x, map_y]

    def rotate_90_degrees(angle):
        #Rotate clockwise 90-degrees
        return (angle + 90.0) % 360

    #endregion
