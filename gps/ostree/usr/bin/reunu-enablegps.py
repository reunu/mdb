import serial
ser = serial.Serial("/dev/ttyUSB2",115200)
ser.write(('AT+CGPS=1,1'+  '\r\n' ).encode())
