import serial
ser = serial.Serial(0, 19200, timeout=1)

print ser.portstr
ser.write("hello")

ser.close() 
