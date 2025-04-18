#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 23 10:26:20 2019

@author: bioelectrics
"""
import sys, linecache
from multiprocessing import Process
from queue import Empty
import time
import serial
import numpy as np
import os

# import pickle
        
class arduinoCtrl(Process):
    def __init__(self, ardq, ardq_p2read, com, is_busy, dmVal, drVal, mimVal, mirVal, orVal, vial, vialDir, expData, trialState):
        super().__init__()
        self.ardq = ardq
        self.ardq_p2read = ardq_p2read
        self.com = com
        self.is_busy = is_busy
        self.dmVal = dmVal
        self.drVal = drVal
        self.mimVal = mimVal
        self.mirVal = mirVal
        self.vial = vial
        self.vialDir = vialDir
        self.expData = expData
        self.orVal = orVal
        self.trialState = trialState
        
    def run(self):
        self.startSerial()
        self.record = False 
        self.start = False
        val2keep = ''
        event = '' 
        while True:
            if not self.serSuccess:
                self.com.value = -1
                continue
            try:
                # if self.is_busy.value ==0:
                if self.com.value > 0:
                    self.comFun()
                    # print("comFun finished!")
                if self.start:
                    if self.ser.in_waiting:
                        line = ''
                        while self.ser.in_waiting:
                            c = self.ser.read()
                            line = c.decode().strip()
                            if len(line): 
                                if line == 'N':
                                    self.ardq_p2read.put('NewVial')
                                    event = "NewVial"
                                elif line == 'E':
                                    event = 'Arduino_Logic_Error'
                                    self.ardq_p2read.put('Error')
                                elif line == 'F':
                                    event = "Wrong_Reward"
                                    self.ardq_p2read.put('WrongReward')                                    
                                elif line == '#':
                                    event = 'Timeout_Main'
                                elif line == '$':
                                    event = 'Timeout_Reward'
                                elif line == 'L':
                                    event = 'Lick_reward_1'
                                elif line == 'R':
                                    event = 'Lick_reward_2'
                                elif line == 'M':
                                    event = 'Lick_Middle'
                                elif line == 'O':
                                    event = 'Shutter_Opened'                       
                                elif line == 'C':
                                    event = 'Shutter_Closed'
                                elif line == 'S':
                                    event = 'Reward_Sent'
                                    self.ardq_p2read.put('RewardSent')
                                elif line == 'W':
                                    self.trialState.value = 0
                                    event = 'State0'
                                elif line == 'Y':
                                    self.trialState.value = 1
                                    event = 'State1'
                                elif line == 'Z':
                                    self.trialState.value = 2
                                    event = 'State2'
                                elif line == '+':
                                    try:
                                        self.evTime = int(val2keep)
                                        print(event, self.evTime)
                                    except:
                                        if val2keep == '':
                                            print(event)
                                        else: 
                                           print("Improper val2keep format:", val2keep)
                                    # self.ser.flush()
                                    val2keep = ''
                                    break
                                elif line == '!' or line == '%':
                                    val2keep = val2keep
                                else:
                                    val2keep = val2keep+line
                                    continue
                        if self.record and len(event):
                                self.events.write("%s\t%s\n\r" % (event,self.evTime))
                                event = '' 
                                self.evTime = ''

                msg = self.ardq.get(block=False)
                try:
                    if msg == 'Release':
                        self.ser.close()
                        self.ardq_p2read.put('done')
                    elif msg == 'Reconnect':
                        if self.serSuccess:
                            self.ser.close()
                            time.sleep(1)
                            print('------Resetting Arduino------')
                        self.startSerial()
                        self.ardq_p2read.put('done')
                    elif msg == 'recPrep':
                        path_base = self.ardq.get()
                        self.events = open('%s_events.txt' % path_base, 'w')
                        self.record = True
                        self.ardq_p2read.put('done')
                    elif msg == 'Start':
                        self.ser.reset_input_buffer()
                        self.ser.reset_input_buffer()
                        self.ser.flush()
                        self.start = True
                        self.com.value = 5
                        self.comFun()
                        self.ardq_p2read.put('done')
                    elif msg == 'Stop':
                        if self.record:
                            self.events.close()
                            self.start = False
                            self.record = False
                            self.ardq_p2read.put('done')
                except:
                    exc_type, exc_obj, tb = sys.exc_info()
                    f = tb.tb_frame
                    lineno = tb.tb_lineno
                    filename = f.f_code.co_filename
                    linecache.checkcache(filename)
                    line = linecache.getline(filename, lineno, f.f_globals)
                    print('EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj))
                    
                    self.ardq_p2read.put('done')
            
            except Empty:
                pass
    
    def comFun(self):
        stA = time.time()
        comVal = self.com.value
        attmpt = 0
        event = ''
        msg = 'none'
        # evTime = time.time()-self.startExp
        while True:
            try:
                # failFlag = False
                attmpt+=1
                stB = time.time()                    
                if comVal == 1:
                    event = f'ChangeVial{self.vial.value}_Acidity{self.vialDir.value}'
                    msg = f'A{self.vial.value}x'
                elif comVal == 2:
                    msg = f'B{self.vialDir.value}x'
                elif comVal == 3:
                    msg = f'D{self.dmVal.value}x'
                elif comVal == 4:
                    msg = f'E{self.drVal.value}x'
                elif comVal == 5:
                    msg = 'S0x'
                elif comVal == 6:
                    msg = f'O{self.orVal.value}x'
                    print(f"Acid is Associated with Reward {self.orVal.value}")
                elif comVal == 7:
                    msg = f'F{self.mimVal.value}x'
                elif comVal == 8:
                    msg = f'G{self.mirVal.value}x'
                self.ser.write(msg.encode())
                # print("msgOUt",msg)
                line = ''
                # time2Read = 0
                while True:
                    try:
                        if (time.time() > (stB + 0.1)):
                            break
                        elif self.ser.in_waiting:
                            while self.ser.in_waiting:
                                c = self.ser.read()
                                line += str(c.decode().strip())
                                # print(line)
                                if line.endswith('%'):
                                    print("line In",line)
                                    # time.sleep(0.01)
                                    break
                            #     elif (time.time() > (stB + 0.1)):
                            #         failFlag = True
                            #         break
                            # if failFlag:
                            #     break
                            if self.record and len(event):
                                self.events.write("%s\t%s\n\r" % (event))
                            print('%s in %d attempt(s)' % (line,attmpt))
                            self.is_busy.value = 1;
                            self.com.value = 0
                            return                            
                        if (time.time() > (stA + 2)):
                            print('Arduino send fail - %d - %s in %d tries' % (comVal,msg,attmpt))
                            self.com.value = 0
                            return
                    except:
                        pass
            
            except:
                exc_type, exc_obj, tb = sys.exc_info()
                f = tb.tb_frame
                lineno = tb.tb_lineno
                filename = f.f_code.co_filename
                linecache.checkcache(filename)
                line = linecache.getline(filename, lineno, f.f_globals)
                print('EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj))
              
    def startSerial(self):
        self.serSuccess = False
        try:
            self.ser = serial.Serial('COM'+str(self.expData['COM']), write_timeout = 0.001)
            self.serSuccess = True
            self.ardq_p2read.put('Success')
        except:
            exc_type, exc_obj, tb = sys.exc_info()
            f = tb.tb_frame
            lineno = tb.tb_lineno
            filename = f.f_code.co_filename
            linecache.checkcache(filename)
            line = linecache.getline(filename, lineno, f.f_globals)
            print('EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj))
            
            self.com.value = -1
            print('\n ---Failed to connect to Arduino--- \n')
            self.ardq_p2read.put('Failed')
            
        
        time.sleep(2)
        if self.serSuccess == True:
            print(f'---Arduino ready on COM {self.expData["COM"]}---\n')
            
        self.ardq_p2read.put('done')
    

# pickleFile = open("pickle.txt", 'wb')
# pickle.dump(line, pickleFile)
# pickleFile.close()