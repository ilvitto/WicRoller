# Import some stuff
from kivy.uix.boxlayout import BoxLayout

from subprocess import call
from subprocess import check_output
import socket
import time
import threading

from kivy.properties import NumericProperty

import matplotlib.pyplot as plt

from sensor_stream import SensorStream
from data_parser import DataParser
        

class WicRoller(BoxLayout):
    
    counter = NumericProperty(0)
    threshold = NumericProperty(60)
    second_threshold = NumericProperty(10)
    angle = NumericProperty(0)
    volume = NumericProperty(0)
    mode = NumericProperty(0)
    stream = SensorStream()
    
    def standard_interaction(self):
        
        TCP_IP = '192.168.43.222' #192.168.1.X for home networks; .43.X for Samsung Galaxy S5 NEO
        TCP_PORT = 80
        BUFFER_SIZE = 1024
        sleep_time = 0.05
        
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((TCP_IP, TCP_PORT))
         
        parser = DataParser(acc_unit=100, gy_unit=128)
        
        #counter = self.stream.memory_size
        mov = 0
        counter_pos = 0
        counter_neg = 0
        timer = 0
        prev_time = time.time()
        angle = 0
        mute = False
        last_vol = ''
        rotating = False
        timer_threshold = 0.4
        self.ids.volume.text = str(check_output(["./vol.sh"], shell=True))
        
        while True:
            
            raw_bytestream = s.recv(BUFFER_SIZE)
            parser.parse_data(raw_bytestream, self.stream)
            
            #if (counter >0):
            #    self.stream.setMemoryCell(self.stream.memory_size-counter)
            #elif(counter == 0):
            #    plt.plot(range(self.stream.memory_size),self.stream.memory)
            #    plt.show()
            #    plt.plot(range(self.stream.memory_size),self.stream.memory)
            #    plt.savefig('dataPlot.png')
            #counter -= 1
            
            x,y,z,gX,gY,gZ = self.stream.getValues()
            dt = time.time() - prev_time
            prev_time = time.time()
            dtheta = dt*gZ
            angle += dtheta
            delta_time = time.time()-timer
            
            #Linear increment after the time threshold
            if(delta_time > timer_threshold and rotating and not mute):
                if(mov == 1):
                    call(["amixer", "-D", "pulse", "sset", "Master", "1%+"])
                if(mov == -1):
                    call(["amixer", "-D", "pulse", "sset", "Master", "1%-"])
               
            self.ids.gZ.text = str(gZ)
            
            #Reset volume with a rapid anticlockwise movment
            #if(gZ > 254 and not mute):
            #    mute = True
            #    last_vol = str(check_output(["./vol.sh"], shell=True))
            #    call(["amixer", "-D", "pulse", "sset", "Master", "0%"])
            
            
            if(mov<=0 and self.stream.gZ<-self.threshold):
                counter_pos += 1
                if (not mute):
                    call(["amixer", "-D", "pulse", "sset", "Master", "5%+"])
                mov = 1
                timer = time.time()
                angle = 0
                rotating = True
            elif(mov>=0 and self.stream.gZ>self.threshold):
                counter_neg += 1
                if (not mute):
                    call(["amixer", "-D", "pulse", "sset", "Master", "5%-"])
                mov = -1
                timer = time.time()
                angle = 0
                rotating = True
            elif((mov>0 and self.stream.gZ>-self.second_threshold) or 
                 (mov<0 and self.stream.gZ<self.second_threshold)):
                mov = 0
                rotating = False
            
            #Restore volume to the previous value with a rapid clockwise movment
            #if(gZ<-254 and mute):
            #    mute = False
            #    last_vol = last_vol.rstrip()
            #    call(["amixer", "-D", "pulse", "sset", "Master", last_vol])
            
            #Useful variables not used
            #counter_neg, counter_pos, angle, delta_time
            
            self.ids.volume.text = str(check_output(["./vol.sh"], shell=True))
            
            time.sleep(sleep_time)
            
        s.close()
    
     
    def slider_interaction_2_mod(self):
        
        TCP_IP = '192.168.43.222' #192.168.1.X for home networks; .43.X for Samsung Galaxy S5 NEO
        TCP_PORT = 80
        BUFFER_SIZE = 1024
        sleep_time = 0.05
        
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((TCP_IP, TCP_PORT))
        
        parser = DataParser(acc_unit=100, gy_unit=128)
        
        #counter = self.stream.memory_size
        mov = 0
        counter_pos = 0
        counter_neg = 0
        timer = 0
        mute = False
        last_vol = ''
        rotating = False
        timer_threshold = 0.1
        self.ids.volume.text = str(check_output(["./vol.sh"], shell=True))
        self.volume = int(self.ids.volume.text.replace("%",""))
        self.mode = 0
        
        while True:
            
            raw_bytestream = s.recv(BUFFER_SIZE)
            parser.parse_data(raw_bytestream, self.stream)
            
            #if (counter >0):
            #    self.stream.setMemoryCell(self.stream.memory_size-counter)
            #elif(counter == 0):
            #    plt.plot(range(self.stream.memory_size),self.stream.memory)
            #    plt.show()
            #    plt.plot(range(self.stream.memory_size),self.stream.memory)
            #    plt.savefig('dataPlot.png')
            #counter -= 1
            
            x,y,z,gX,gY,gZ = self.stream.getValues()
            delta_time = time.time()-timer

            #Linear increment after the time threshold in Continous Mode
            if(delta_time > timer_threshold and rotating and not mute and self.mode == 1):
                if(mov == 1):
                    call(["amixer", "-D", "pulse", "sset", "Master", "1%+"])
                    self.volume = int(self.ids.volume.text.replace("%","")) + 1
                if(mov == -1):
                    call(["amixer", "-D", "pulse", "sset", "Master", "1%-"])
                    self.volume = int(self.ids.volume.text.replace("%","")) - 1
            
            #Reset volume with a rapid anticlockwise movment
            #if(gZ > 254 and not mute):
            #    mute = True
            #    last_vol = str(check_output(["./vol.sh"], shell=True))
            #    call(["amixer", "-D", "pulse", "sset", "Master", "0%"])
            #    self.volume = 0
            
            if(mov<=0 and self.stream.gZ<-self.threshold):
                counter_pos += 1
                if (not mute and self.mode == 0):
                    call(["amixer", "-D", "pulse", "sset", "Master", "5%+"])
                    self.volume = int(self.ids.volume.text.replace("%","")) + 5
                mov = 1
                timer = time.time()
                rotating = True
            elif(mov>=0 and self.stream.gZ>self.threshold):
                counter_neg += 1
                if (not mute and self.mode == 0):
                    call(["amixer", "-D", "pulse", "sset", "Master", "5%-"])
                    self.volume = int(self.ids.volume.text.replace("%","")) - 5
                mov = -1
                timer = time.time()
                rotating = True
            elif((mov>0 and self.stream.gZ>-self.second_threshold) or 
                 (mov<0 and self.stream.gZ<self.second_threshold)):
                mov = 0
                rotating = False
            
            #Restore volume to the previous value with a rapid clockwise movment
            #if(gZ<-254 and mute):
            #    mute = False
            #    last_vol = last_vol.rstrip()
            #    call(["amixer", "-D", "pulse", "sset", "Master", last_vol])
            #    self.volume = int(last_vol.replace("%",""))
            
            #Useful variables not used
            #counter_neg, counter_pos, angle, delta_time
            
            self.ids.volume.text = str(check_output(["./vol.sh"], shell=True))
            
            time.sleep(sleep_time)
            
        s.close()
        
    def slider_interaction_2_mod_mute(self):
        
        TCP_IP = '192.168.43.222' #192.168.1.X for home networks; .43.X for Samsung Galaxy S5 NEO
        TCP_PORT = 80
        BUFFER_SIZE = 1024
        sleep_time = 0.05
        
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((TCP_IP, TCP_PORT))
        
        parser = DataParser(acc_unit=100, gy_unit=128)
        
        #counter = self.stream.memory_size
        mov = 0
        counter_pos = 0
        counter_neg = 0
        timer = 0
        mute = False
        last_vol = ''
        rotating = False
        timer_threshold = 0.1
        self.ids.volume.text = str(check_output(["./vol.sh"], shell=True))
        self.volume = int(self.ids.volume.text.replace("%",""))
        self.mode = 0
        
        while True:
            
            raw_bytestream = s.recv(BUFFER_SIZE)
            parser.parse_data(raw_bytestream, self.stream)
            
            #if (counter >0):
            #    self.stream.setMemoryCell(self.stream.memory_size-counter)
            #elif(counter == 0):
            #    plt.plot(range(self.stream.memory_size),self.stream.memory)
            #    plt.show()
            #    plt.plot(range(self.stream.memory_size),self.stream.memory)
            #    plt.savefig('dataPlot.png')
            #counter -= 1
            
            x,y,z,gX,gY,gZ = self.stream.getValues()
            delta_time = time.time()-timer
            
            #Reset volume if overturn the device to the wrong position
            if not mute and z < 0:
                mute = True
                last_vol = str(check_output(["./vol.sh"], shell=True))
                call(["amixer", "-D", "pulse", "sset", "Master", "0%"])
            #Restore volume if overturn the device to the right position
            if mute and z > 0:
                mute = False
                last_vol = last_vol.rstrip()
                call(["amixer", "-D", "pulse", "sset", "Master", last_vol])
            
            #Linear increment after the time threshold in Continous Mode
            if(delta_time > timer_threshold and rotating and not mute and self.mode == 1):
                if(mov == 1):
                    call(["amixer", "-D", "pulse", "sset", "Master", "1%+"])
                    self.volume = int(self.ids.volume.text.replace("%","")) + 1
                if(mov == -1):
                    call(["amixer", "-D", "pulse", "sset", "Master", "1%-"])
                    self.volume = int(self.ids.volume.text.replace("%","")) - 1
            
            #Reset volume with a rapid anticlockwise movment
            #if(gZ > 254 and not mute):
            #    mute = True
            #    last_vol = str(check_output(["./vol.sh"], shell=True))
            #    call(["amixer", "-D", "pulse", "sset", "Master", "0%"])
            #    self.volume = 0
            
            if(mov<=0 and self.stream.gZ<-self.threshold):
                counter_pos += 1
                if (not mute and self.mode == 0):
                    call(["amixer", "-D", "pulse", "sset", "Master", "5%+"])
                    self.volume = int(self.ids.volume.text.replace("%","")) + 5
                mov = 1
                timer = time.time()
                rotating = True
            elif(mov>=0 and self.stream.gZ>self.threshold):
                counter_neg += 1
                if (not mute and self.mode == 0):
                    call(["amixer", "-D", "pulse", "sset", "Master", "5%-"])
                    self.volume = int(self.ids.volume.text.replace("%","")) - 5
                mov = -1
                timer = time.time()
                rotating = True
            elif((mov>0 and self.stream.gZ>-self.second_threshold) or 
                 (mov<0 and self.stream.gZ<self.second_threshold)):
                mov = 0
                rotating = False
            
            #Restore volume to the previous value with a rapid clockwise movment
            #if(gZ<-254 and mute):
            #    mute = False
            #    last_vol = last_vol.rstrip()
            #    call(["amixer", "-D", "pulse", "sset", "Master", last_vol])
            #    self.volume = int(last_vol.replace("%",""))
            
            #Useful variables not used
            #counter_neg, counter_pos, angle, delta_time
            
            self.ids.volume.text = str(check_output(["./vol.sh"], shell=True))
            
            time.sleep(sleep_time)
            
        s.close()
    
    def on_window_length(self, instance, value):
        self.stream.resetWindow(value)

    def start_simple_interface(self):
        threading.Thread(target = self.standard_interaction).start()
        self.counter += 1
        self.ids.gZ.text = "{}".format(self.counter)
    
    def start_slider_interface_2_mod(self):
        threading.Thread(target = self.slider_interaction_2_mod).start()
        self.counter += 1
        self.ids.volume.text = "Volume %"
    
    def start_slider_interface_2_mod_mute(self):
        threading.Thread(target = self.slider_interaction_2_mod_mute).start()
        self.counter += 1
        self.ids.volume.text = "Volume %"
    
    def changeMode(self):
        if(self.mode == 0):
            self.ids.mod.text = "Mode: Continuous"
        else:
            self.ids.mod.text = "Mode: Discrete"
        self.mode = (self.mode + 1)%2
    
    def setVolume(self, volume):
        self.volume = volume
        vol = str(volume)+"%"
        vol = vol.rstrip()
        call(["amixer", "-D", "pulse", "sset", "Master", vol])
        self.ids.volume.text = str(check_output(["./vol.sh"], shell=True))
    
    def setThreshold(self,value):
        self.threshold = int(value)
    
    def setSecondThreshold(self,value):
        self.second_threshold = int(value)
