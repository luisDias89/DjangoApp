import serial
import time

# ligação Serial com o Arduino, initilizado após biblioteca de Motor com RaspBery
ser = serial.Serial(
        port='/dev/ttyUSB0', #Replace ttyS0 with ttyAM0 for Pi1,Pi2,Pi0
        baudrate = 115200,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS,
        timeout=1
)
time.sleep(1)
if ser.isOpen():
    #ser.write(str.encode("\r\n\r\n"))
    time.sleep(1)  # Wait for initialization
    ser.flushInput()  # Flush startup text in serial input
    print('Sending GCode')




def askGRBL(ser, comandoAsk):
        if ser.isOpen():
            print('Sending: ' + comandoAsk)
            ser.write(comandoAsk.encode() +
                                    str.encode('\n'))  # Send g-code block
            # Wait for response with carriage return
            grbl_out = ser.readlines()
            for line in grbl_out:
                print(line.strip().decode("utf-8"))
                #ser.write(str.encode('G0X0Y0Z0') + str.encode('\n'))


def main():
    print(" ------ Codigo teste de funções ------------")

    print("\n Inicio teste, envio e resposta SERIALPORT")
    askGRBL(ser,'$X')
    askGRBL(ser,'$0')
    #askGRBL(ser,'$$')
    askGRBL(ser,'G91')
    askGRBL(ser,'G01 X-1 Z-1 F2000')
    askGRBL(ser,'G01 A-2 F5000')
    askGRBL(ser,'G01 A2 F5000')
    askGRBL(ser,'G01 A-2 F5000')
    askGRBL(ser,'G01 A2 F5000')
    askGRBL(ser,'G01 A-2 F5000')
    askGRBL(ser,'G01 A2 F5000')
    askGRBL(ser,'G01 A-2 F5000')
    askGRBL(ser,'G01 A2 F5000')
    askGRBL(ser,'G01 X-1 Z-1 F300')
    askGRBL(ser,'G01 X-1 Z-1 F1000')
    askGRBL(ser,'G01 X-1 Z-1 F300')
    askGRBL(ser,'G01 X-1 Z-1 F1000')
    askGRBL(ser,'G01 X-1 Z-1 F300')
    askGRBL(ser,'G01 X-1 Z-1 F1000')
    askGRBL(ser,'G01 X7 Z7 F1000')



if __name__ == "__main__":
    main()
