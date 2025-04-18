# -*- coding: utf-8 -*-
"""
Created on Fri Feb 28 09:54:35 2025

@author: reynoben
"""
import serial
import time
import numpy as np
import re
# import sys
# import linecache
from multiprocessing import Process, Queue, Value
from queue import Empty

class ArduinoCommunicator:
    def __init__(self, port, con, baudrate=115200):
        self.port = port
        self.baudrate = baudrate
        self.ser = None
        self.buffer = ""
        self.connected = con
        
    def connect(self):
        try:
            self.ser = serial.Serial('COM'+ self.port, timeout=0.1)
            time.sleep(2)
            self.connected.value = 1
            print(f'\n\n -----Connected to Arduino on {self.port}----- \n\n')
        except Exception as e:
            print(f'Failed to connect: {e}')
            self.connected.value = 0
        
    def send(self, msg):
        if self.connected.value:
            self.ser.write(msg.encode())
            # print(f'Sent: {msg}')
        else:
            print('Arduino not connected')
        
    def read(self, delimiter):
       # if not self.connected.value:
       #     return []
       msg=''
       startChars = ['%', '+']
       for sc in startChars:
           if sc != delimiter:
               break
       self.buffer += self.ser.read(self.ser.in_waiting).decode().strip()
       messages = []
       # print(self.buffer)
       while delimiter in self.buffer:
           npBuff = np.array(list(self.buffer))
           dndx = min(np.where(npBuff == delimiter)[0])
           if sc in self.buffer:
               sndx = min(np.where(npBuff == sc)[0])
           else:
               sndx = 0
           testA = (sndx==0)
           testB = (dndx < sndx)
           if testA or testB:
               msg, self.buffer = self.buffer[:dndx + 1], self.buffer[dndx + 1:]
           elif sndx < dndx:
               msg, self.buffer = self.buffer[sndx+1:dndx + 1], self.buffer[:sndx+1] + self.buffer[dndx + 1:]
           print("InRead DEBUG:", msg, self.buffer, testA, testB, sndx, dndx)
           messages.append(msg)
       # print(messages)
       return messages
    
    def findUnread(self):
        evMsg = []
        hsMsg = []
        # while '%' in self.buffer or '+' in self.buffer:
        #     if '%' in self.buffer:
        #         msg, self.buffer = self.buffer.split('%', 1)
        #         hsMsg.append(msg + '%')
        #     elif '+' in self.buffer:
        #         msg, self.buffer = self.buffer.split('+', 1)
        #         evMsg.append(msg + '+')
   
        pattern = re.compile(r'[^%+]+[%+]') # Regex pattern to match any sequence ending in '+' or '%'
        matches = pattern.findall(self.buffer)  # Find all valid messages
        for msg in matches:
            if msg.endswith('%'):
                hsMsg.append(msg)
            elif msg.endswith('+'):
                evMsg.append(msg)
        self.buffer = re.sub(pattern, '', self.buffer).strip()
    
        # return hsMsg, evMsg
        print("!!!REMAINING BUFFER", self.buffer)
        if '%' not in self.buffer or '+' not in self.buffer:
            self.buffer = ''
            print("\t CLEARED BUFFER \t")
        return hsMsg, evMsg
    
    def close(self):
        if self.connected.value:
            self.ser.close()
            self.connected.value = False
            print('Connection closed')

class ArduinoEventProcessor:
    EVENT_MAPPING = {
        'N': 'NewVial', 'E': 'Error', 'F': 'Wrong_Reward', 'L': 'Lick_reward_1',
        'R': 'Lick_reward', 'M': 'Lick_Middle', 'O': 'Shutter_Opened', 'C': 'Shutter_Closed',
        'S': 'Reward_Sent', 'W': 'State0', 'Y': 'State1', 'Z': 'State2', '#': 'Timeout_Main',
        '$': 'Timeout_Reward', '?': 'Trial_Stopped'
    }
    
    def __init__(self, trialState):
        self.trialState = trialState
    
    def process(self, line):
        msg = line.split('+')[0]
        if msg:
            if msg[0] in self.EVENT_MAPPING:
                if msg in ('W', 'Y', 'Z'):
                    self.trialState.value = {'W': 0, 'Y': 1, 'Z': 2}[msg]
                    return "ts"
                else:
                    vMsg = self.EVENT_MAPPING.get(msg[0])
                    vMsg = vMsg+':\t'+str(msg[1:])
                    print("*EVENT:", vMsg)
                    return vMsg 
            else:
                return f"unk{msg}"

class ArduinoController(Process):
    def __init__(self, port, sVal):
        super().__init__()
        self.queue = Queue()
        self.sVal = sVal
        self.arduino = ArduinoCommunicator(port, self.sVal['connect'])
        self.event_processor = ArduinoEventProcessor(self.sVal['trialState'])
        self.running = True
        self.rec = False
        self.log_file = None
       
        
    def logEvent(self, event):
        if self.rec and self.log_file:
            for ev in event: 
                with open(self.log_file, "a") as log:
                    log.write(f"{event}\n")
        else:
            pass
        
    def run(self):
        self.arduino.connect()
        while True:
            while self.arduino.connected.value:
                if self.running:
                    try:
                        userEvent = self.queue.get(block=False)
                        print(f'Received from GUI (UserCommand): {userEvent}')
                        if userEvent == 'Rec':
                            self.rec = True
                            self.log_file = self.queue.get()
                        # elif userEvent == 'Stop':
                        #     self.stop()
                    except Empty:
                        pass
                    if len(self.arduino.buffer):
                        print('READING BUFFER:', self.arduino.buffer)
                        hsMsg, evMsg = self.arduino.findUnread() # check to see if handshaking failed
                        if len(hsMsg):
                            for hs in hsMsg:
                                if hs.endswith('%'):
                                    print(f'^^^ERROR: Missed {hs} during handshake')
                        if len(evMsg):
                            for ev in evMsg:
                                if ev.endswith('+'):
                                    self.logEvent(ev)

                    if self.sVal['com'].value > 0:
                        self.send_command()
                        self.sVal['com'].value = 0
                    line = self.arduino.read('+')
                    if line:
                        for l in line:
                            event = self.event_processor.process(l)
                            if event == "ts":
                                # print("---------Trial State Changed: ", self.event_processor.trialState.value,"---------")
                                pass
                            if event.startswith("unk"):
                                print("^^^ERROR: Unknown Event", event.split('k')[1]) #most likely reading handshake: Only should happen after handhake fail
                            elif len(event):
                                self.logEvent(event)
                                if self.sVal['auto'].value == 1:
                                    if event.startswith("NewVial"):
                                        self.sVal["NewVial"].value = 1
                                    elif event.startswith("Reward_Sent"):
                                        self.sVal["RewardVal"].value = 1
                                    elif event.startswith("Wrong_Reward"):\
                                        self.sVal["RewardVal"].value = 2
                                if event.startswith("Trial_Stopped"):
                                    self.stop()
                                elif event.startswith("Error"):
                                    self.sVal['Error'].value = 1
                    time.sleep(0.001)
    
    def send_command(self):
        comval = self.sVal['com'].value
        self.commands = {
            1: f'A{self.sVal["vial"].value}x',
            2: f'B{self.sVal["vialDir"].value}x',
            3: f'D{self.sVal["dmVal"].value}x',
            4: f'E{self.sVal["drVal"].value}x',
            5: 'S0x',
            6: f'O{self.sVal["orVal"].value}x',
            7: f'F{self.sVal["mimVal"].value}x',
            8: f'G{self.sVal["mirVal"].value}x'
        }
        cmd = self.commands.get(comval, '')
        # if comval == 1:
        #     print("Sending: ", self.sVal['vial'].value, cmd)
        if cmd:
            self.arduino.send(cmd)
            cnfrm = self.handshake()
            if cnfrm:
                return
            else:
                print(f'^^^ERROR: Failed to handshake: {cmd} in {self.attempt} attempts')
                
    def handshake(self, timeout=2):
      start_time = time.time()
      self.attempt = 1
      # while time.time() - start_time > timeout:
      while self.attempt < 100:
            if time.time() - start_time > timeout:
                break
            response = self.arduino.read('%')
            if response:
                for r in response:
                    if '+' in r:
                        print(f"^^^ERROR: Handshake Read Event {r}")
                    else:
                        print(f'*HANDSHAKE: {response} in {self.attempt} attempts')
                return True
            else:
                time.sleep(0.001)
                self.attempt += 1
      return False
      # return False  
  
    def stop(self):
        self.running = False
        self.arduino.ser.flush()
        time.sleep(0.2)
        # self.arduino.close()
        print("------trial stopped successfully!------")
        

# if __name__ == "__main__":
#     sVal = {
#         'com': Value('i', 0), 'is_busy': Value('i', 0), 'dmVal': Value('i', 0), 'drVal': Value('i', 0),
#         'mimVal': Value('i', 0), 'mirVal': Value('i', 0), 'orVal': Value('i', 0), 'vial': Value('i', 0),
#         'vialDir': Value('i', 0), 'trialState': Value('i', 0)
#     }
#     arduino_process = ArduinoController('16', sVal)
#     arduino_process.start()
    
#     try:
#         while True:
#             event = arduino_process.queue.get()
#             print(f'Event received: {event}')
#     except KeyboardInterrupt:
#         arduino_process.stop()
#         arduino_process.join()

