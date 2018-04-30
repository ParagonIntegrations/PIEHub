import serial



# Initialize serial connection
ser = serial.Serial(port="/dev/ttyAMA0" ,baudrate=500000 ,timeout=10)
ser.close()
ser.open()

while True:
    data = ser.readline().strip()
    decodeddata = data.decode()

    if decodeddata != "":
        print(decodeddata)

