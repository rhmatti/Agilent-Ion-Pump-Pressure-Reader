import time
import datetime
import serial
import serial.tools.list_ports

print('Available ports:')
print([comport.device for comport in serial.tools.list_ports.comports()])

port = 'COM5'           #Serial port of the pump controller
sample_rate = 60        #How often the pressure is sampled (in seconds)

#Attempts to establish a serial connection to the specified port
def establishConnection(port):
    try:
        ser = serial.Serial(port, 9600, timeout=1, bytesize=serial.EIGHTBITS, parity='N', stopbits=serial.STOPBITS_ONE)
        return ser
    except:
        print('Could not establish connection to specified port')

#Creates the necessary binary packet to ask the pump controller for the pressure reading
def makepacket():
    STX = b'\x02'
    ADDR = b'\x80'
    WIN = b'812'
    COM = b'\x30'
    ETX = b'\x03'

    payload = ADDR + WIN + COM
    payload += ETX

    CRC = payload[0]
    for b in payload[1:]:
        CRC ^= b
    CRC = hex(CRC)[2:].upper().zfill(2).encode()

    packet = STX + payload + CRC

    return packet

#Queries the Agilent Ion Pump controller for the current pressure reading
def getPressure():
    message = makepacket()
    ser.write(message)
    response = ser.readline()
    pressure = response[6:-3].decode()

    return float(pressure)

#Writes a pressure reading and timestamp to a log file
def write2File(filename, time, pressure):
    outputFile = open(filename, 'a')
    outputFile.write(f'{time}\t{pressure}\n')
    outputFile.close()

#Reads the pressure once every "sample_time" seconds and writes to a log file entitled "filename_datetime.txt"
def logPressures(sample_time):
    fileName = 'pressure_log'

    date = datetime.datetime.now().strftime("%m%d%y_%H%M")
    outputFile = open(f'{fileName}_{date}.txt', "w")
    outputFile.write('Time\tPressure (Torr)\n')
    outputFile.close()

    t0 = time.time()

    times = []
    pressures = []
    while True:
        current_time = time.time()
        current_pressure = getPressure()

        times.append(current_time)
        pressures.append(current_pressure)
        print(current_pressure)
        
        write2File(f'{fileName}_{date}.txt', current_time, current_pressure)

        time.sleep(sample_time)


#Attempts to begin logging pressures every 60 seconds using port

ser = establishConnection(port)
#message = STX+ADDR+WIN+COM+ETX+CRC+b'\r\n'
logPressures(sample_rate)
    


