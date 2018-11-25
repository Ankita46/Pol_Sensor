import sys
import time
import difflib
import pigpio
import serial

rx=26

try:
    import struct
except ImportError:
    import ustruct as struct
#in case no connections are there
pi=pigpio.pi()
if not pi.connected:
    exit(0)
pi.set_mode(rx,pigpio.INPUT)
pi.bb_serial_read_open(rx,9600,8)
buffer=[]

try:
    while True:
        time.sleep(1.5)
        (count,data)=pi.bb_serial_read(rx)
        buffer += data
     
        while buffer and buffer[0] != 0x42:
            buffer.pop(0)
     
        if len(buffer) > 200:
            buffer = []  # avoid an overrun if all bad data
            continue
     
        if buffer[1] != 0x4d:
            buffer.pop(0)
            continue

        frame_len = struct.unpack(">H", bytes(buffer[2:4]))[0]
        if frame_len != 28:
            buffer = []
            continue
       
     
        frame = struct.unpack(">HHHHHHHHHHHHHH", bytes(buffer[4:32]))
     
        pm10_standard, pm25_standard, pm100_standard, pm10_env, \
            pm25_env, pm100_env, particles_03um, particles_05um, particles_10um, \
            particles_25um, particles_50um, particles_100um, skip, checksum = frame
     
        check = sum(buffer[0:30])
     
        if check != checksum:
            buffer = []
            continue
     
        print("Concentration Units (standard)")
        print("---------------------------------------")
        print("PM 1.0: %d\tPM2.5: %d\tPM10: %d" %
              (pm10_standard, pm25_standard, pm100_standard))
        print("Concentration Units (environmental)")
        print("---------------------------------------")
        print("PM 1.0: %d\tPM2.5: %d\tPM10: %d" % (pm10_env, pm25_env, pm100_env))
        print("---------------------------------------")
        print("Particles > 0.3um / 0.1L air:", particles_03um)
        print("Particles > 0.5um / 0.1L air:", particles_05um)
        print("Particles > 1.0um / 0.1L air:", particles_10um)
        print("Particles > 2.5um / 0.1L air:", particles_25um)
        print("Particles > 5.0um / 0.1L air:", particles_50um)
        print("Particles > 10 um / 0.1L air:", particles_100um)
        print("---------------------------------------")
     
        buffer = buffer[32:]
        #print("Buffer ", buffer)

except Exception as e:
    print(e)
    pi.bb_serial_read_close(rx)
    pi.stop()
finally:
    print('finally')
    pi.bb_serial_read_close(rx)
    pi.stop()
    
        


    
    
