#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sun Feb 19 22:19:08 2017

@author: M. Lapucci, F. Vittorini
@title:  WicRoller
"""

# Import some stuff
import socket
import time
import matplotlib.pyplot as plt
from sensor_stream import SensorStream
from data_parser import DataParser
         
def main():
     
    threshold = 60
    second_threshold = 10
    stream = SensorStream()
    CONTINUOUS_INCREMENT = False
          
    TCP_IP = '192.168.43.222' #192.168.1.X for home networks; .43.X for Samsung Galaxy S5 NEO
    TCP_PORT = 80
    BUFFER_SIZE = 1024
    sleep_time = 0.05
     
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((TCP_IP, TCP_PORT))
      
    parser = DataParser(acc_unit=100, gy_unit=128)
     
    #counter = self.stream.memory_size
    mov = 0
    rotating = False
     
    while True:
         
        raw_bytestream = s.recv(BUFFER_SIZE)
        parser.parse_data(raw_bytestream, stream)
        
        
        #UNCOMMENT TO GET DATA STREAM PLOT FOR DEBUGGING
        #if (counter >0):
        #    self.stream.setMemoryCell(self.stream.memory_size-counter)
        #elif(counter == 0):
        #    plt.plot(range(self.stream.memory_size),self.stream.memory)
        #    plt.show()
        #    plt.plot(range(self.stream.memory_size),self.stream.memory)
        #    plt.savefig('dataPlot.png')
        #counter -= 1
        
        x,y,z,gX,gY,gZ = stream.getValues()
 
        if(rotating and CONTINUOUS_INCREMENT):
            if(mov == 1):
                print("Rotating clockwise")
            if(mov == -1):
                print("Rotating anticlockwise") 
         
        if(mov<=0 and stream.gZ<-threshold):
            if(not CONTINUOUS_INCREMENT):
                print("Clockwise rotation")
            mov = 1
            rotating = True
        elif(mov>=0 and stream.gZ>threshold):
            if(not CONTINUOUS_INCREMENT):
                print("Antilockwise rotation")
            mov = -1
            rotating = True
        elif((mov>0 and stream.gZ>-second_threshold) or
             (mov<0 and stream.gZ<second_threshold)):
            mov = 0
            rotating = False
           
        time.sleep(sleep_time)
         
    s.close()
     
if __name__ == "__main__":
    main()
