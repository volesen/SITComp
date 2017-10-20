from Communication import BluetoothSerial
from time import sleep

#Yes, I know the following imports tie it to Windows
#This is for the manual part. Consistent speed isn't important here. This is fast enough.
#pip install pypiwin32
import win32con
import win32api

#pip install pythonnet
import clr
from System.Windows import Forms
from System import Drawing

class HUD(Forms.Form):
    def __init__(self):
        self.InitializeComponent()

    def InitializeComponent(self):
        self.SuspendLayout()
        
        self.ClientSize = Drawing.Size(64, 64)
        self.FormBorderStyle = Forms.FormBorderStyle.FixedToolWindow
        self.BackColor = Drawing.Color.GhostWhite
        
        self.KeyDown += self.OnKeyDownEvent
        self.KeyUp += self.OnKeyUpEvent
        self.Closing += self.OnClosingEvent

        self.ResumeLayout(False)

        self.Input_Up = False
        self.Input_Down = False
        self.Input_Left = False
        self.Input_Right = False
        self.Input_Boost = False
        self.Input_Magnet = False

    def OnKeyDownEvent(self, sender, e):
        if e.KeyCode == Forms.Keys.W:
            self.Input_Up = True
        elif e.KeyCode == Forms.Keys.S:
            self.Input_Down = True
        elif e.KeyCode == Forms.Keys.A:
            self.Input_Left = True
        elif e.KeyCode == Forms.Keys.D:
            self.Input_Right = True
        elif e.KeyCode == Forms.Keys.Space:
            self.Input_Boost = True
        elif e.KeyCode == Forms.Keys.V:
            self.Input_Magnet = not self.Input_Magnet

        elif e.KeyCode == Forms.Keys.Escape:
            self.Close()

        e.Handled = True
    
    def OnKeyUpEvent(self, sender, e):
        if e.KeyCode == Forms.Keys.W:
            self.Input_Up = False
        elif e.KeyCode == Forms.Keys.S:
            self.Input_Down = False
        elif e.KeyCode == Forms.Keys.A:
            self.Input_Left = False
        elif e.KeyCode == Forms.Keys.D:
            self.Input_Right = False
        elif e.KeyCode == Forms.Keys.Space:
            self.Input_Boost = False

        e.Handled = True

    def OnClosingEvent(self, sender, e):
        pass    


def controls_to_motor_signal(up, down, left, right, speed_scaler = 0.6):
    #Speed scaler should be between 1 and 0

    #The following part has been coded to exhibit the following properties:
    # - Backwards has higher priority than forwards
    # - No turning if both turn keys down
    # - Turn keys turn robot if driving backwards/forwards
    # - Turns in opposite direction when going backwards
    # - Turn keys turn robot in place if standing still

    motor_signal = [0, 0]

    if left == right:
        if down:
            motor_signal = [-255, -255]
        elif up:
            motor_signal = [255, 255]
    elif left:
        motor_signal[1] = 255
    elif right:
        motor_signal[0] = 255

    if left != right:
        if down:
            motor_signal = [-motor_signal[1], -motor_signal[0]]
        elif not up:
            if right:
                motor_signal[1] = -255
            elif left:
                motor_signal[0] = -255


    return [int(signal * speed_scaler) for signal in motor_signal]

#Program starts here
print("Connecting to robot...")
com = BluetoothSerial("COM3", 9600)
try:
    com.open()
except:
    print("Connection failed. Program terminated.")
    exit()

print("Connection established")

#Create HUD
window = HUD()
window.Show()

while window.Visible:
    Forms.Application.DoEvents()

    if window.Input_Boost:
        speed_scaler = 1
    else:
        speed_scaler = 0.50

    motor_signal = controls_to_motor_signal(window.Input_Up, 
                                            window.Input_Down, 
                                            window.Input_Left, 
                                            window.Input_Right,
                                            speed_scaler)

    if window.Input_Magnet:
        aux_signal = 255
    else:
        aux_signal = 0

    sleep(0.016)
    
    com.send_motor_signal(motor_signal, aux_signal)
    

if not window.IsDisposed:
    window.Close()

print("Closing connection...")
com.close()

print("Connection closed. Program terminated.")
