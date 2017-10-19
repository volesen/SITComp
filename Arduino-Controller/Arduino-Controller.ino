#include <SoftwareSerial.h>

//Motor brake and current sensing pins
//Look into these, brake might need to be pulled low

//Constants
//Quadratic acceleration
// float Acceleration_Factor = 2000;
//Linear acceleration
float Acceleration_Constant = 2.4;

//Motor control pins
int Motor_Left_Pin_PWM = 10;
int Motor_Left_Pin_Direction = 11;
int Motor_Right_Pin_PWM = 9;
int Motor_Right_Pin_Direction = 8;

//Signed PWM values for each motor
int Motor_Left_Value = 0;
int Motor_Right_Value = 0;

float Motor_Left_CurrentValue = 0;
float Motor_Right_CurrentValue = 0;

//Communication pins
int BT_TX = 2; //Yellow from BT goes here
int BT_RX = 3; //Green from BT goes here

SoftwareSerial bluetooth(BT_RX, BT_TX);


void setup()
{
    //TODO: Remove the following line, it is for debugging
    Serial.begin(9600);

    //Set up pins
    pinMode(Motor_Left_Pin_PWM, OUTPUT);
    pinMode(Motor_Left_Pin_Direction, OUTPUT);
    pinMode(Motor_Right_Pin_PWM, OUTPUT);
    pinMode(Motor_Right_Pin_Direction, OUTPUT);

    pinMode(BT_TX, OUTPUT);
    pinMode(BT_RX, INPUT);

    //Make sure on-time is long enough for stand still -> low speed changes
    //Frequency is set to 31250 / 256 = 122,07 hz
    //31250 = Base frequency of pin 10 and 9
    //0x04 selects divisor of 256
    TCCR1B = TCCR1B & 0b11111000 | 0x04;

    //Begin bluetooth serial connection
    bluetooth.begin(9600);
    bluetooth.setTimeout(200);
}

void loop() 
{
    Receive_MotorValues();
    Update_MotorValues();
    Apply_MotorValues();
    

    // Serial.print(Motor_Left_CurrentValue);
    // Serial.print(",");
    // Serial.println(Motor_Right_CurrentValue);
}

#pragma region Motor speed
void Update_MotorValues() 
{
    Motor_Left_CurrentValue = Calculate_Value(Motor_Left_Value, Motor_Left_CurrentValue);
    
    Motor_Right_CurrentValue = Calculate_Value(Motor_Right_Value, Motor_Right_CurrentValue);
}

float Calculate_Value(int value, float currentValue)
{
    //Linear acceleration
    if (abs(currentValue - value) < Acceleration_Constant)
        return value;
    else
        return (value - currentValue > 0 ? 1 : -1) * Acceleration_Constant + currentValue;
    
    //Quadratic acceleration
    // float ValueDelta = (float)value - currentValue;
    
    // if (abs(ValueDelta) < 10) //To evade division by zero
    //     return (float)value;
    // else
    //     return (ValueDelta > 0 ? 1 : -1) * Acceleration_Factor * pow(ValueDelta, -2) + currentValue;
}

void Apply_MotorValues()
{
    Apply_MotorValue(Motor_Left_Pin_PWM,
                     Motor_Left_Pin_Direction,
                     (int)Motor_Left_CurrentValue);

    Apply_MotorValue(Motor_Right_Pin_PWM,
                     Motor_Right_Pin_Direction,
                     (int)Motor_Right_CurrentValue);
}

void Apply_MotorValue(int pin_PWM, int pin_Direction, int value)
{
    analogWrite(pin_PWM, abs(value));
    digitalWrite(pin_Direction, value < 0 ? HIGH : LOW);
}

#pragma endregion

#pragma region Communication
String Received = "";

///<summary>
///Reads bluetooth serial buffer until command found
///Updates motor values with found command.
///</summary>
///<remarks>
///Stops reading buffer once a command has been found.
///Is able to receive half a command and then the rest in the next call.
///</remarks>
///<returns>
///true if valid command found. false if no command found in whole buffer.
///</returns>
bool Receive_MotorValues()
{
    while (bluetooth.available() > 0)
    {
        if ((Received.length() == 1 && Received.charAt(0) != '(') ||
            Received.length() > 10)
            Received = ""; //Invalid input was prevented


        //Start input sequence
        if (bluetooth.peek() == '(')
            Received = (char)bluetooth.read();
        //End input sequence
        else if (bluetooth.peek() == ')')
        {
            Received += (char)bluetooth.read();
            
            if (Received.length() > 6 && Received.length() < 12)
            {
                //Find comma separator (-1 if not found)
                int Separator_Location = Received.indexOf(',');
                
                //Make sure Seperator exists and exists within expected range
                if (Separator_Location > 2 && Separator_Location < 6)
                {
                    //This is not 100% safe.
                    //Not a full check of Received. Invalid input can still exist.
                    //Not writing full check unless we see that invalid input happens often.

                    //If bad input makes it here, motor values will be set to zero
                    Motor_Left_Value = Received.substring(1, Separator_Location).toInt();
                    Motor_Right_Value = Received.substring(Separator_Location + 1, Received.length() - 1).toInt();
                    
                    Received = "";

                    return true;
                }
            }

            Received = ""; //Invalid input was prevented, continue reading buffer
            continue;
        }
        //Continue reading input
        else
            Received += (char)bluetooth.read();
    }

    //No valid input was found
    return false;
}

#pragma endregion