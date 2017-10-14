import serial

# import bluetooth

# sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
# sock.connect(("98:d3:34:90:d3:12", 1))
# print("connected")
# sock.settimeout(4.0)
# sock.recv(2)
# sock.close()

class BluetoothSerial(object):
    def __init__(self, port, baudrate):
        self.READ_TIMEOUT = 0.2
        self.WRITE_TIMEOUT = 0.2
        
        self.com = serial.Serial()
        self.com.port = port 			#"COM3"
        self.com.baudrate = baudrate 	#9600

    def open(self):
        self.com.open()
    
    def close(self):
        self.com.close()

    def send_motor_signal(self, signal):
        if not self.com.is_open:
            raise ConnectionError("Cannot send signal when communication is closed. Call open() to open communication.")
        else:
            #Turn PWM values into strings
            motor_left_signal = str(signal[0])
            motor_right_signal = str(signal[1])
            #Make sure string has plus sign for positive direction
            if signal[0] >= 0:
                motor_left_signal = "+" + motor_left_signal
            if signal[1] >= 0:
                motor_right_signal = "+" + motor_right_signal
            
            #Encode and send PWM values
            self.com.write("({!s},{!s})".format(motor_left_signal, 
                                                motor_right_signal)
                                        .encode("ascii"))

    def get_battery_voltage(self):
        #This function must not take long
        #Always keep a voltage value in memory together with time since previous update
        #this function should then return the locally saved voltage value
        raise NotImplementedError()
