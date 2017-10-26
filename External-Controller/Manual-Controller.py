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
        
        self.ClientSize = Drawing.Size(364, 222)
        self.FormBorderStyle = Forms.FormBorderStyle.FixedToolWindow
        self.KeyPreview = True
        self.BackColor = Drawing.Color.SlateGray

        self.CreateInstructions()
        self.CreateTrackBars()
        self.CreateKeyInput()

        self.ResumeLayout(False)
        

    def CreateInstructions(self):
        self.InstructionLabel = Forms.Label()
        self.InstructionLabel.Location = Drawing.Point(52, 176)
        self.InstructionLabel.Size = Drawing.Size(256, 354)
        self.InstructionLabel.Font = Drawing.Font(Drawing.FontFamily("Lucida Console"), b'8')
        self.InstructionLabel.ForeColor = Drawing.Color.GhostWhite
        self.InstructionLabel.Text = "    V:   Toggle magnet\n WASD:   Movement\nSPACE:   Activate boost"

        self.Controls.Add(self.InstructionLabel)


    def CreateTrackBars(self):
        #Create SpeedBar
        self.SpeedBar = Forms.TrackBar()
        self.SpeedBar.Location = Drawing.Point(8, 32)
        self.SpeedBar.Size = Drawing.Size(240, 24)
        self.SpeedBar.Maximum = 100
        self.SpeedBar.Minimum = 0
        self.SpeedBar.TickFrequency = 10
        self.SpeedBar.Value = 35
        
        self.Speed = self.SpeedBar.Value / 100.0
        self.SpeedBar.ValueChanged += self.OnSpeedChanged

        self.Controls.Add(self.SpeedBar)

        #Create SpeedBoostBar
        self.SpeedBoostBar = Forms.TrackBar()
        self.SpeedBoostBar.Location = Drawing.Point(8, 128)
        self.SpeedBoostBar.Size = Drawing.Size(240, 24)
        self.SpeedBoostBar.Maximum = 100
        self.SpeedBoostBar.Minimum = 0
        self.SpeedBoostBar.TickFrequency = 10
        self.SpeedBoostBar.Value = 85

        self.SpeedBoost = self.SpeedBoostBar.Value / 100.0
        self.SpeedBoostBar.ValueChanged += self.OnSpeedChanged

        self.Controls.Add(self.SpeedBoostBar)

        #Create labels
        self.SpeedLabel = Forms.Label()
        self.SpeedLabel.Location = Drawing.Point(256, 8)
        self.SpeedLabel.Size = Drawing.Size(128, 86)
        self.SpeedLabel.Font = Drawing.Font(Drawing.FontFamily("Impact"), b'24')
        self.SpeedLabel.ForeColor = Drawing.Color.GhostWhite
        self.SpeedLabel.Text = "SPEED\n" + str(self.SpeedBar.Value)

        self.Controls.Add(self.SpeedLabel)

        self.SpeedBoostLabel = Forms.Label()
        self.SpeedBoostLabel.Location = Drawing.Point(256, 104)
        self.SpeedBoostLabel.Size = Drawing.Size(128, 86)
        self.SpeedBoostLabel.Font = Drawing.Font(Drawing.FontFamily("Impact"), b'24')
        self.SpeedBoostLabel.ForeColor = Drawing.Color.GhostWhite
        self.SpeedBoostLabel.Text = "BOOST\n"+ str(self.SpeedBoostBar.Value)

        self.Controls.Add(self.SpeedBoostLabel)

    def OnSpeedChanged(self, sender, e):
        self.Speed = self.SpeedBar.Value / 100.0
        self.SpeedBoost = self.SpeedBoostBar.Value / 100.0
        
        self.SpeedLabel.Text = "SPEED\n" + str(self.SpeedBar.Value)
        self.SpeedBoostLabel.Text = "BOOST\n" + str(self.SpeedBoostBar.Value)

        e.Handled = True


    def CreateKeyInput(self):
        self.KeyDown += self.OnKeyDownEvent
        self.KeyUp += self.OnKeyUpEvent
        self.Closing += self.OnClosingEvent

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
            if self.Input_Magnet:
                self.BackColor = Drawing.Color.Crimson
            else:
                self.BackColor = Drawing.Color.SlateGray

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

#Application loop
while window.Visible:
    Forms.Application.DoEvents()

    if window.Input_Boost:
        speed_scaler = window.SpeedBoost
    else:
        speed_scaler = window.Speed

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
