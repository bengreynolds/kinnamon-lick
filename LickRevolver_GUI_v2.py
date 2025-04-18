# -*- coding: utf-8 -*-
"""
Created on Tue Aug 27 11:57:58 2024

@author: reynoben
"""
import wx
import wx.grid as grid
import numpy as np
import os
from datetime import datetime
import shutil
import ruamel.yaml
from pathlib import Path
from multiprocessing import Array, Queue, Value
import ctypes
import arduinoCtrl_LickRevolver as arduino
import time
import glob
import pandas as pd
import keyboard
import threading
from arduinoCtrl_LickRevolver_v2 import ArduinoController

class MainFrame(wx.Frame):
    def __init__(self):
        self.screenSize = wx.Display().GetGeometry().GetSize()
        self.screenW = self.screenSize.GetWidth()
        self.screenH = self.screenSize.GetHeight()
        self.frameH = self.screenH*0.9
        self.frameW = self.screenW*0.6
        wx.Frame.__init__(self, None, title="Lickometer Serial Control Interface", size=(self.frameW, self.frameH))
        self.current_dir = os.path.dirname(os.path.abspath(__file__))
        statusFields = 4
        self.statusbar = self.CreateStatusBar(statusFields)
        self.statusbar.SetStatusWidths([-4, -1, -1, -1])
        for idx in range(statusFields):
            self.statusbar.SetStatusText("", idx)
                
        num_vials = 8
        self.titleFont =  wx.Font(10,wx.FONTFAMILY_DEFAULT,wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        # Create a panel to hold the layout
        main_panel = wx.Panel(self, style = wx.BORDER_SIMPLE)
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.Bind(wx.EVT_CLOSE, self.onClose)
        # Create the vertical panel on the right
        self.right_panel = wx.Panel(main_panel, size=(self.frameW*0.25,-1), style = wx.BORDER_SIMPLE)
        right_sizer = wx.BoxSizer(wx.VERTICAL)
        self.right_panel.SetForegroundColour(wx.Colour(33,33,33))
        self.right_panel.SetBackgroundColour(wx.Colour(220,220,220))
        
        # Button to load
        self.configPanel = wx.Panel(self.right_panel, style = wx.BORDER_RAISED, name = 'Configuration')
        self.configPanel.SetBackgroundColour(wx.Colour(190, 200, 210, 240))
        static_box = wx.StaticBox(self.configPanel, label="Configuration")
        static_box.SetFont(self.titleFont)
        config_sizer = wx.StaticBoxSizer(static_box, wx.HORIZONTAL)
        self.bNewCon =  wx.Button(self.configPanel, label="New Config")
        self.bLoadCon = wx.Button(self.configPanel, label="Load Config")
        config_sizer.Add(self.bNewCon, 1, wx.ALL | wx.EXPAND, 10)
        config_sizer.Add(self.bLoadCon, 1, wx.ALL | wx.EXPAND, 10)
        self.bLoadCon.Bind(wx.EVT_BUTTON, self.onLoadConfig)
        self.bNewCon.Bind(wx.EVT_BUTTON, self.onNewConfig)
        self.configPanel.SetSizer(config_sizer)
        right_sizer.Add(self.configPanel, 1, wx.ALL | wx.EXPAND, 5)
        # right_sizer.AddSpacer(25)
        
        
        
        # Start button
        self.actionPanel = wx.Panel(self.right_panel, style = wx.BORDER_RAISED, name = 'Actions')
        self.actionPanel.SetBackgroundColour(wx.Colour(190, 200, 210, 240))
        static_box = wx.StaticBox(self.actionPanel, label="Actions")
        static_box.SetFont(self.titleFont)
        actionSizer = wx.StaticBoxSizer(static_box, wx.VERTICAL)
        self.bInit = wx.Button(self.actionPanel, label="Initialize")
        actionSizer.Add(self.bInit, 0, wx.ALL | wx.EXPAND, 5)
        self.bInit.Bind(wx.EVT_BUTTON, self.OnInitialize)
        
        self.bStart = wx.Button(self.actionPanel, label="Start")
        actionSizer.Add(self.bStart, 0, wx.ALL | wx.EXPAND, 5)
        self.bStart.Bind(wx.EVT_BUTTON, self.onStart)
        
        self.bStop = wx.Button(self.actionPanel, label="Stop")
        actionSizer.Add(self.bStop, 0, wx.ALL | wx.EXPAND, 5)
        self.bStop.Bind(wx.EVT_BUTTON, self.onStop)
        
        self.bRec = wx.Button(self.actionPanel, label="Record")
        actionSizer.Add(self.bRec, 0, wx.ALL | wx.EXPAND, 5)
        self.bRec.Bind(wx.EVT_BUTTON, self.onRec)
        self.actionPanel.SetSizer(actionSizer)
        right_sizer.Add(self.actionPanel, 3, wx.ALL | wx.EXPAND, 5)
        # right_sizer.AddSpacer(25)
        # self.actionPanel.SetForegroundColour(wx.Colour(0,0,0))
        
        
        self.protPanel = wx.Panel(self.right_panel, style = wx.BORDER_RAISED, name = 'Protocols')
        self.protPanel.SetBackgroundColour(wx.Colour(190, 200, 210, 240))
        static_box = wx.StaticBox(self.protPanel, label="Protocols")
        static_box.SetFont(self.titleFont)
        protSizer = wx.StaticBoxSizer(static_box, wx.VERTICAL)
        # Modes
        self.modes = []
        cbox_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.mCheck = wx.CheckBox(self.protPanel, label="Manual")
        self.rCheck = wx.CheckBox(self.protPanel, label="Random")
        self.aCheck = wx.CheckBox(self.protPanel, label="Automated")
        self.mCheck.Bind(wx.EVT_CHECKBOX, self.onChangeMode)
        self.rCheck.Bind(wx.EVT_CHECKBOX, self.onChangeMode)
        self.aCheck.Bind(wx.EVT_CHECKBOX, self.onChangeMode)
        # self.mCheck.SetValue(True)
        self.modes.append([self.aCheck, self.rCheck,self.mCheck])
        cbox_sizer.Add(self.mCheck, 0, wx.ALL | wx.EXPAND, 5)
        cbox_sizer.Add(self.rCheck, 0, wx.ALL | wx.EXPAND, 5)
        cbox_sizer.Add(self.aCheck, 0, wx.ALL | wx.EXPAND, 5)
        protSizer.Add(cbox_sizer, 0, wx.ALL | wx.EXPAND, 5)
        
        self.protPath = os.path.join(self.current_dir, 'Protocols')
        allProt = [f for f in os.listdir(self.protPath) if f.endswith('.xls') or f.endswith('.xlsx')]
        self.prot = [os.path.basename(f) for f in allProt]
        
        prot_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.selProt = wx.Choice(self.protPanel, choices = self.prot)
        if len(self.prot):
            self.selProt.SetSelection(0)
        self.addProt = wx.Button(self.protPanel, label = 'Add Protocol')
        self.selProt.Bind(wx.EVT_CHOICE, self.onSelectProtocol)
        self.addProt.Bind(wx.EVT_BUTTON, self.onAddProtocol)
        prot_sizer.Add(self.selProt, 0, wx.ALL | wx.EXPAND, 5)
        prot_sizer.Add(self.addProt, 0, wx.ALL | wx.EXPAND, 5)
        protSizer.Add(prot_sizer, 0, wx.ALL | wx.EXPAND, 5)
        self.protPanel.SetSizer(protSizer)
        right_sizer.Add(self.protPanel, 1, wx.ALL | wx.EXPAND, 5)
        # right_sizer.AddSpacer(25)
        
        #Delays
        self.delayPanel = wx.Panel(self.right_panel, style = wx.BORDER_RAISED, name = 'User Controls')
        self.delayPanel.SetBackgroundColour(wx.Colour(190, 200, 210, 240))
        static_box = wx.StaticBox(self.delayPanel, label="User Controls")
        static_box.SetFont(self.titleFont)
        delaySizer = wx.StaticBoxSizer(static_box, wx.VERTICAL)
        
        delaySizer1 = wx.BoxSizer(wx.HORIZONTAL)
        delaySizer2 = wx.BoxSizer(wx.HORIZONTAL)
        labelDelRew = wx.StaticText(self.delayPanel, label="Reward Delay:")
        labelDelMain = wx.StaticText(self.delayPanel, label="Reward Main:")
        self.delRew = wx.SpinCtrl(self.delayPanel, value='0', min=0, max=1000)
        self.delMain = wx.SpinCtrl(self.delayPanel, value='0', min=0, max=1000)
        self.delRew.Bind(wx.EVT_SPINCTRL, self.onDelayReward)
        self.delMain.Bind(wx.EVT_SPINCTRL, self.onDelayMain)
        delaySizer1.Add(labelDelRew, 0, wx.ALL | wx.EXPAND, 5)
        delaySizer1.Add(self.delRew, 0,wx.ALL | wx.EXPAND, 5)
        delaySizer2.Add(labelDelMain, 0, wx.ALL | wx.EXPAND, 5)
        delaySizer2.Add(self.delMain, 0, wx.ALL | wx.EXPAND, 5)
        delaySizer.Add(delaySizer1, 0, wx.ALL | wx.EXPAND, 5)
        delaySizer.Add(delaySizer2, 0, wx.ALL | wx.EXPAND, 5)
        
        idleSizer1 = wx.BoxSizer(wx.HORIZONTAL)
        idleSizer2 = wx.BoxSizer(wx.HORIZONTAL)
        labelIdleRew = wx.StaticText(self.delayPanel, label="Max Idle Reward:")
        labelIdleMain = wx.StaticText(self.delayPanel, label="Max Idle Main:")
        self.idleRew = wx.SpinCtrl(self.delayPanel, value='0', min=0, max=10000)
        self.idleMain = wx.SpinCtrl(self.delayPanel, value='0', min=0, max=10000)
        self.idleRew.Bind(wx.EVT_SPINCTRL, self.onMaxIdleReward)
        self.idleMain.Bind(wx.EVT_SPINCTRL, self.onMaxIdleMain)
        idleSizer1.Add(labelIdleRew, 0, wx.ALL | wx.EXPAND, 5)
        idleSizer1.Add(self.idleRew, 0,wx.ALL | wx.EXPAND, 5)
        idleSizer2.Add(labelIdleMain, 0, wx.ALL | wx.EXPAND, 5)
        idleSizer2.Add(self.idleMain, 0, wx.ALL | wx.EXPAND, 5)
        delaySizer.Add(idleSizer1, 0, wx.ALL | wx.EXPAND, 5)
        delaySizer.Add(idleSizer2, 0, wx.ALL | wx.EXPAND, 5)

        orSizer = wx.BoxSizer(wx.HORIZONTAL)
        orlabel = wx.StaticText(self.delayPanel, label="Acid Orientation")
        self.orientation = wx.Choice(self.delayPanel, choices=['Reward 1', 'Reward 2'])
        self.orientation.SetSelection(0)
        self.orientation.Bind(wx.EVT_CHOICE, self.onSelectOrientation)
        orSizer.Add(orlabel, 0, wx.ALL | wx.EXPAND, 5)
        orSizer.Add(self.orientation, 0, wx.ALL | wx.EXPAND, 5)
        delaySizer.Add(orSizer, 0,wx.ALL | wx.EXPAND, 5)

        
        self.delayPanel.SetSizer(delaySizer)
        right_sizer.Add(self.delayPanel, 1, wx.ALL | wx.EXPAND, 5)

        # Labels and dropdowns
        self.manPanel = wx.Panel(self.right_panel, style=wx.BORDER_RAISED, name='Manual Config')
        self.manPanel.SetBackgroundColour(wx.Colour(190, 200, 210, 240))
        
        static_box = wx.StaticBox(self.manPanel, label="Vial Configuration")
        static_box.SetFont(self.titleFont)
        manSizer = wx.StaticBoxSizer(static_box, wx.VERTICAL)
        # labelSizer = wx.BoxSizer(wx.HORIZONTAL)
        # vial_main_label = wx.StaticText(self.manPanel, label="Vials")
        # pH_main_label = wx.StaticText(self.manPanel, label="pH")
        # font = wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        # vial_main_label.SetFont(font)
        # pH_main_label.SetFont(font)
        # labelSizer.Add(vial_main_label, 1, wx.ALL | wx.EXPAND, 5)
        # labelSizer.Add(pH_main_label, 1, wx.ALL | wx.EXPAND, 5)
        # manSizer.Add(labelSizer, 0, wx.ALL | wx.EXPAND, 5)
        self.checkboxes = []
        self.dropdowns = []
        gridSizer = wx.FlexGridSizer(rows=0, cols=4, hgap=10, vgap=5)  # 2 vials per row (4 elements per row: checkbox + dropdown for each)
        for i in range(num_vials):
            checkbox = wx.CheckBox(self.manPanel, label=f"{i+1}:")
            dropdown = wx.Choice(self.manPanel, choices=["Acidic", "Basic"])
            dropdown.SetSelection(0)
            dropdown.Enable(False)
            checkbox.Bind(wx.EVT_CHECKBOX, self.onCheckVialConfig)
            dropdown.Bind(wx.EVT_CHOICE, self.onSelectPH)
            gridSizer.Add(checkbox, 1, wx.ALL | wx.EXPAND, 5)
            gridSizer.Add(dropdown, 1, wx.ALL | wx.EXPAND, 5)
            self.checkboxes.append(checkbox)
            self.dropdowns.append(dropdown)
        manSizer.Add(gridSizer, 1, wx.ALL | wx.EXPAND, 5)
        self.manPanel.SetSizer(manSizer)
        right_sizer.Add(self.manPanel, 1, wx.ALL | wx.EXPAND, 5)

        
        self.right_panel.SetSizer(right_sizer)
        
        for i, check in enumerate(self.checkboxes):
            self.checkboxes[i].Enable(False)
            self.dropdowns[i].Enable(False)
        
        
        # Create left panel
        self.left_panel = wx.Panel(main_panel, style = wx.BORDER_SUNKEN)
        self.left_panel.SetBackgroundColour(wx.Colour(190, 200, 210, 240))
        self.gridPanel = wx.Panel(self.left_panel, style = wx.BORDER_SUNKEN)
        gridSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.gridPanel.SetSizer(gridSizer)
        # self.gridPanel.SetForegroundColour(wx.Colour(240,240,240))
       
        bottom_panel = wx.Panel(self.left_panel, size=(-1, self.frameH*0.05), style = wx.BORDER_RAISED)
        bottom_panel.SetBackgroundColour(wx.Colour(190, 200, 210, 240))
        bottom_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        self.vialButtons = []
        for i in range(1, 9):
            button = wx.Button(bottom_panel, label=str(i))
            bottom_sizer.Add(button, 0, wx.ALL, 5)
            button.Bind(wx.EVT_BUTTON, self.onVialChange)
            self.vialButtons.append(button)
        bottom_panel.SetSizer(bottom_sizer)
        left_sizer = wx.BoxSizer(wx.VERTICAL)
        left_sizer.Add(self.gridPanel, 1, wx.EXPAND | wx.ALL, 5)
        left_sizer.Add(bottom_panel, 0, wx.EXPAND | wx.ALL, 5)
        self.left_panel.SetSizer(left_sizer)
        
        main_sizer.Add(self.left_panel, 1, wx.EXPAND| wx.ALL, 5)
        main_sizer.Add(self.right_panel, 0, wx.EXPAND | wx.ALL, 5)
        main_panel.SetSizer(main_sizer)

        self.prev_configpath = os.path.join(self.current_dir, 'Config', 'prev_config.yaml')
        self.default_configpath = os.path.join(self.current_dir, 'Config', 'Default_LickConfig.yaml')
        self.date = datetime.now().strftime('%Y-%m-%d')
        if not os.path.exists(self.prev_configpath):
            self.onNewConfig(event=None)
        else:
            self.prevConfig = self.read_config(self.prev_configpath)
            self.configpath = self.prevConfig['Config']
            if os.path.exists(self.configpath):
                self.expData = self.read_config(self.configpath)
            else:
                self.configpath = self.default_configpath
                self.expData = self.read_config(self.configpath)
            self.updateGUI(self.expData) #FLAG
            self.onLoadConfig(event=None)
        self.start = False
        self.init = False
        self.rec = False
        # for c in self.checkboxes:
        #     c.Enable(True)
        # for d in self.dropdowns:
        #     d.Enable(True)
        for b in self.vialButtons:
            b.Enable(False)
 
        for child in self.actionPanel.GetChildren():
            if isinstance(child, wx.Button):
                if child.GetLabel() != "Initialize":
                    child.Enable(False)
        self.Layout()
        
        self.timer = None
    

    def read_config(self, cfg_path):
        cfg = 'none'
        ruamelFile = ruamel.yaml.YAML()
        path = Path(cfg_path)
        with open(path, 'r') as f:
            cfg = ruamelFile.load(f)
        return(cfg)
    
    
    def write_config(self, configName, cfg):
        with open(configName, 'w') as cf:
            ruamelFile = ruamel.yaml.YAML()
            ruamelFile.dump(cfg, cf)
            
    def OnInitialize(self, event):
        if hasattr(self, 'arduino_process'):
            self.arduino_process.terminate()
            self.queue.close()
            print('Previous Arduino Process Closed')
            
        self.queue = Queue()
        self.sVal = {
            'com': Value('i', 0), 'trialState': Value('i', 0), 'vial': Value('i', 0),
            'vialDir': Value('i', 0), 'dmVal': Value('i', self.delMain.GetValue()), 'drVal': Value('i', self.delRew.GetValue()),
            'mimVal': Value('i', self.idleMain.GetValue()), 'mirVal': Value('i', self.idleRew.GetValue()), 'orVal': Value('i', 0),
            'connect': Value('i', 0), 'auto': Value('i', 0), 'NewVial': Value('i', 0), 'RewardVal': Value('i', 0), 'Error': Value('i', 0)
        }
        print("Started Arduino Connection")
        self.arduino_process = ArduinoController(str(self.expData["COM"]), self.sVal)
        print("Starting")
        self.arduino_process.start()
        print("Started")
        sTime = time.time()
        while (time.time() - sTime < 5):
            if self.sVal['connect'].value == 1:
                print("Successfully Connected to Arduino")
                self.bStart.Enable(True)
                self.bRec.Enable(True)
                self.bInit.Enable(False)
                self.init = True
                # for c in self.checkboxes:
                #     c.Enable(True)
                # for d in self.dropdowns:'
                #     d.Enable(True)
                for b in self.vialButtons:
                    b.Enable(True)
        
                for child in self.actionPanel.GetChildren():
                    if isinstance(child, wx.Button):
                        if child.GetLabel() != "Initialize":
                            child.Enable(True)
                self.onDelayMain(event=None)
                self.onDelayReward(event=None)
                self.onMaxIdleMain(event=None)
                self.onMaxIdleReward(event=None)
                self.onSelectOrientation(event=None)
                self.statusbar.SetStatusText('Arduino COM%s: CONNECTED ' % self.expData["COM"], 3)
                self.statusbar.SetStatusText('Trial State:', 2)
                return
            else:
                continue
        print(time.time()-sTime)
        print("Failed Connection to Arduino")
        wx.MessageBox('Arduino Initialization Failed!','Error', wx.OK | wx.ICON_ERROR)
        self.statusbar.SetStatusText('Arduino COM%s: FAILED ' % self.expData["COM"], 3)
    
    def onNewConfig(self, event):
        dlg = wx.TextEntryDialog(self, "Please Name the Configuration File:", "Config Name")
        if dlg.ShowModal() == wx.ID_OK:
            ncn = dlg.GetValue()
        else:
            return
        dlg.Destroy()
        self.configpath = os.path.join(self.current_dir,'Config', f'{ncn}.yaml')
        shutil.copy(self.default_configpath, self.configpath)
        self.prevConfig['Config'] = self.configpath
        self.write_config(self.prev_configpath, self.prevConfig)
        self.onLoadConfig(event=None)
        
    
    def onLoadConfig(self, event):
        if event:
            dlg = wx.FileDialog(self, "Choose a file", defaultDir=os.path.join(self.current_dir,'Config'), style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
            if dlg.ShowModal() == wx.ID_CANCEL:
                return
            self.configpath = dlg.GetPath()
        if self.configpath != self.prev_configpath:
            self.prevConfig['Config'] = self.configpath
            self.write_config(self.prev_configpath, self.prevConfig)
        if os.path.exists(self.configpath):
            self.statusbar.SetStatusText('Current config: %s' % self.configpath, 0)
            self.expData = self.read_config(self.configpath)
            self.updateGUI(self.expData)
            self.statusbar.SetStatusText('Arduino COM%s: ' % self.expData["COM"], 3)
            
        # print('config', self.delRew.GetValue())
        
    def updateGUI(self, expdata):
        currmode = expdata['Mode'] #FLAG
        for mode in self.modes[0]:
            if mode.GetLabel() == currmode:
                mode.SetValue(True)
            else:
                mode.SetValue(False)
        if currmode == "Manual": 
            for i, check in enumerate(self.checkboxes):
                self.checkboxes[i].Enable(True)
                self.dropdowns[i].Enable(True)
        else: 
            for i, check in enumerate(self.checkboxes):
                self.checkboxes[i].Enable(False)
                self.dropdowns[i].Enable(False)
                
        self.delRew.SetValue(int(self.expData['Reward_delay']))
        self.delMain.SetValue(int(self.expData['Main_delay']))
        self.idleRew.SetValue(int(self.expData['Max_idle_main']))
        self.idleMain.SetValue(int(self.expData['Max_idle_reward']))
        self.orient = self.expData['Acid_orientation']
        if self.orient == "Reward 1":
            self.orientation.SetSelection(0)    
        if self.orient == "Reward 2":
            self.orientation.SetSelection(1)
        self.onSelectProtocol(event=None)
        
        
    def onChangeMode(self, event):
        if event:
            selMode = event.GetEventObject()
            for mode in self.modes[0]:
                if mode is not selMode:
                    mode.SetValue(False)
            self.expData['Mode'] = selMode.GetLabel()
        self.updateGUI(self.expData)
        
    def onSelectPH(self,event):
        pH_num = event.GetEventObject().GetLabel()
        
    def onCheckVialConfig(self, event):
        checkbox = event.GetEventObject()
        cndx = self.checkboxes.index(checkbox)
        dropdown = self.dropdowns[cndx]
        if checkbox.IsChecked():
            dropdown.Enable(True)
        else:
            dropdown.Enable(False)
        vial_num = event.GetEventObject().GetLabel()
    
    def updateExpData(self, event, key, value_widget, target_attr_name, com_value):
        value = value_widget.GetValue()
        self.expData[key] = value
        print(value)
        if self.init:
            if hasattr(self, target_attr_name):
                # target_attr = getattr(self, target_attr_name)
                # target_attr.value = int(value)
                self.sVal[target_attr_name].value = int(value)
            self.sVal['com'].value = com_value
            while self.sVal['com'].value != 0:
                time.sleep(0.1)

    
    def onDelayReward(self, event):
        self.updateExpData(event, 'Reward_delay', self.delRew, 'drVal', 4)
    
    def onDelayMain(self, event):
        self.updateExpData(event, 'Main_delay', self.delMain, 'dmVal', 3)
    
    def onMaxIdleMain(self, event):
        self.updateExpData(event, 'Max_idle_main', self.idleMain, 'mimVal', 7)
    
    def onMaxIdleReward(self, event):
        self.updateExpData(event, 'Max_idle_reward', self.idleRew, 'mirVal', 8)
    
    def onSelectOrientation(self, event):
        self.currOr = self.orientation.GetStringSelection()
        self.expData['Acid_orientation'] = self.currOr
        if self.init:
            self.sVal['orVal'].value = int(self.currOr.split()[-1])
            print(self.sVal['orVal'].value)
            self.sVal['com'].value = 6
            while self.sVal['com'].value != 0:
                time.sleep(0.1)
        # print(int(self.currOr.split()[-1]) )
        
    def updateStatus(self, event):
        if self.sVal['trialState']:
            # print("TrialState",self.sVal['trialState'].value)
            if self.sVal['trialState'].value == 0:
                self.statusbar.SetStatusText('Waiting for Next Input', 2)
            if self.sVal['trialState'].value == 1:
                self.statusbar.SetStatusText('Waiting for Main Lick', 2)
            if self.sVal['trialState'].value == 2:
                self.statusbar.SetStatusText('Waiting for Reward Lick', 2)
        
        if self.sVal['vial']:
            if self.sVal['vialDir']:
                if self.sVal['vialDir'].value == 0:
                    acidity = "Acidic"
                else:
                    acidity = "Basic"                
                self.statusbar.SetStatusText(f'Vial: {self.sVal["vial"].value}/{acidity}', 1)  
                
        self.timer = wx.CallLater(100, self.updateStatus, event)
        
    def onStart(self, event):
        self.write_config(self.configpath, self.expData)
        self.start = True
        self.bStart.Enable(False)  
        self.bStop.Enable(True)
        self.updateStatus(None)
        if not self.rec:
            for mode in self.modes[0]:
                if mode.GetValue():
                    currMode = mode.GetLabel()
                    self.sVal['com'].value = 5
                    while self.sVal['com'].value != 0:
                        time.sleep(0.1)
                    self.runProtocol(currMode)
            
    def onRec(self, event):
        if self.start == False:
            self.onStart(event=None)
        self.queue.put("Rec")
        it = 1
        self.data_path = os.path.join(self.current_dir, 'Data', f'{self.date}_{self.currProtName}', f'{self.date}_{self.currProtName}.txt')
        while os.path.exists(self.data_path):
            self.data_path = os.path.join(self.current_dir, 'Data',f'{self.date}_{self.currProtName}', f'{self.date}_{self.currProtName}_{it}.txt')
            it += 1
        self.queue.put(self.data_path)
        self.metaPath = os.path.join(os.path.dirname(self.data_path),'metadata.txt')
        shutil.copy(self.configpath, self.metaPath)
        
        self.vOrder = []
        self.aOrder = []
        self.rec = True
        for c in self.checkboxes:
            c.Enable(False)
        for d in self.dropdowns:
            d.Enable(False)
        for mode in self.modes:
            if mode.GetValue():
                currMode = mode.GetLabel()
                self.sVal['com'].value = 5
                while self.sVal['com'].value != 0:
                    time.sleep(0.1)
                self.runProtocol(currMode)
                
    def onAddProtocol(self, event):
        dlg = wx.TextEntryDialog(self,"Please Name the Protocol File:", "Protocol Name")
        if dlg.ShowModal() == wx.ID_OK:
            newprot = dlg.GetValue()
        dlg.Destroy()
        self.default_prot = os.path.join(self.protPath, 'Protocol_default.xlsx')
        new_protocol = os.path.join(self.protPath, f'{newprot}.xlsx')
        try:
            shutil.copy(self.default_prot, new_protocol)
            allProt = [f for f in os.listdir(self.protPath) if f.endswith('.xls') or f.endswith('.xlsx')]
            self.prot = [os.path.basename(f) for f in allProt]
            self.selProt.SetItems(self.prot)
            # self.selProt.SetSelection(0)
        except Exception as e:
            wx.MessageBox(f"An error occurred: {e}", "Error", wx.OK | wx.ICON_ERROR)
        
    def onSelectProtocol(self, event):
        self.currProtName = self.selProt.GetStringSelection()
        if self.currProtName:
            if np.size(self.gridPanel.GetChildren):
                for child in self.gridPanel.GetChildren():
                    child.Destroy()
            self.protocol_path = os.path.join(self.protPath, self.currProtName)
            pdf = pd.read_excel(self.protocol_path)
            listV = pdf['Vial'].tolist()
            listA = pdf['Acidity'].tolist()
            dfva = pd.DataFrame({
                'Vial': listV,
                'Acidity': listA
            })
            self.grid = wx.grid.Grid(self.gridPanel)
            self.grid.CreateGrid(len(dfva), len(dfva.columns))  # Set grid size based on DataFrame
            self.grid.SetColLabelValue(0, 'Vial')
            self.grid.SetColLabelValue(1, 'Acidity (1=Acidic)')
            self.grid.SetDefaultCellBackgroundColour(wx.Colour(240,240,240))
            self.grid.SetDefaultCellFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
            self.grid.SetDefaultCellAlignment(wx.ALIGN_CENTER, wx.ALIGN_CENTER)
            self.grid.SetLabelFont(self.titleFont)
            self.grid.SetColSize(0, self.frameW*0.3)  
            self.grid.SetColSize(1, self.frameW*0.3)
            # self.grid.SetColSize(2, 100)  
            for row_idx, (vial, acidity) in enumerate(zip(dfva['Vial'], dfva['Acidity'])):
                self.grid.SetCellValue(row_idx, 0, str(vial))  # Set Vial data
                self.grid.SetCellValue(row_idx, 1, str(acidity))  # Set Acidity data
            panel_sizer = self.gridPanel.GetSizer()  # Get the panel's sizer
            panel_sizer.Add(self.grid, 1, wx.EXPAND|wx.CENTER, 5)
            self.gridPanel.SetSizer(panel_sizer)
            self.gridPanel.Layout()
        
    def runProtocol(self, currMode):
        self.vOrder = []
        self.aOrder = []
        if currMode =='Manual':
            self.sVal['auto'].value = 0
            for b in self.vialButtons:
                b.Enable(True)
            wx.MessageBox('Select Vial', 'ACTION', wx.OK | wx.ICON_EXCLAMATION)
        else:
            self.sVal['auto'].value = 1
            for b in self.vialButtons:
                b.Enable(False)
                if self.grid:
                    listV = []
                    listA = []
                    num_rows = self.grid.GetNumberRows()
                    for row in range(num_rows):
                        vial = self.grid.GetCellValue(row, 0)  # Column 0 for 'Vial'
                        acidity = self.grid.GetCellValue(row, 1)  # Column 1 for 'Acidity'
                        listV.append(vial)
                        listA.append(acidity)
                    df = pd.DataFrame({
                        'Vial': listV,
                        'Acidity': listA
                    })
                    # protocol_path = os.path.join(self.protPath, self.currProtName)
                    df.to_excel(self.protocol_path, index=False)
                    
            threading.Thread(target=self.userInterrupt, daemon=True).start()
            
            if currMode == 'Automated':             #follows order of protocol
                self.autorunProt(listA, listV)
                
            elif currMode == 'Random':              #random order of protocol
                if len(listA) != len(listV):
                    raise ValueError("The length of vials and acidities must be the same")
                arrayV = np.array(listV)
                arrayA = np.array(listA)
                indices = np.arange(len(listV))
                np.random.shuffle(indices)
                rVials = arrayV[indices].tolist()
                rAcid = arrayA[indices].tolist()
                self.autorunProt(rAcid, rVials)
                
    def autorunProt(self, acidList, vialList):
        for vndx, vial2get in enumerate(vialList):
            if self.userQuit:
                print(f"User Quit Completed after vial {int(vial2get)-1}")
                self.onStop(event=None)
                break
            assocA = acidList[vndx]
            self.onVialChange(event=None, vial=vial2get, assoc=assocA)
            self.lickListener(vndx)

        
    def userInterrupt(self):
        self.userQuit=False
        while True:
            if keyboard.is_pressed("esc") or keyboard.is_pressed("q"):
                print("User Stop Requested! Exiting protocol after next event!")
                self.userQuit = True 
                break  

    def lickListener(self, vndx):
        while True:
            if self.sVal["NewVial"].value == 1:
                if vndx == 0:
                    print('Sending First')
                else:
                    print('Timeout: NewVial Sending')
                self.sVal["RewardVal"].value = 0
                self.sVal["NewVial"].value = 0
                break
            if self.sVal["RewardVal"].value > 0:
                if self.sVal["RewardVal"].value == 1:
                    print('Reward Sent')
                elif self.sVal["RewardVal"].value ==2:
                    print("WrongRewardLicked")
                self.sVal["RewardVal"].value = 0
            if self.sVal["Error"].value > 0:
                self.errorMessage()
                self.sVal["Error"].value = 0
                
        # hs = self.queue.get()
        # if hs == 'NewVial':
        #     if vndx == 0:
        #         print('Sending First')
        #     else:
        #         print('Timeout: NewVial Sending')
        # else:
        #     if hs in ["RewardSent", "WrongReward"]:
        #         rs = self.queue.get()
        #         if rs == 'NewVial':
        #             print('SendingNext')
        #     elif hs == 'Error':
        #         self.errorMessage()
        
            

    def onVialChange(self, event, vial=None, assoc=None):
        if event:
            vbLab = event.GetEventObject().GetLabel()
            self.sVal['vial'].value = int(vbLab)
            self.vialDirect = self.dropdowns[int(vbLab)-1].GetStringSelection()
            if self.vialDirect == 'Acidic':
                self.sVal['vialDir'].value = 0
            elif self.vialDirect == 'Basic':
                self.sVal['vialDir'].value = 1
        else:
            if vial is not None:
                self.sVal['vial'].value = int(vial)
                self.sVal['vialDir'].value = int(assoc)
            else:
                wx.MessageBox('NO VIAL SELECTED FOR RUNNING PROTOCOL', 'ERROR', wx.OK | wx.ERROR)
                return
        if self.start:
            print("current Vial:", self.sVal['vial'].value)
            self.sVal['com'].value = 2
            while self.sVal['com'].value != 0:
                time.sleep(0.1)
            self.sVal['com'].value = 1
            if self.rec:
                self.vOrder.append(self.sVal['vial'].value)
                self.aOrder.append(self.sVal['vialDir'].value)
        else:
            wx.MessageBox('Experiment Must be Started First', 'WARNING', wx.OK | wx.ICON_WARNING)
       
    def errorMessage(self):
        wx.messageBox('Arduino Logic Failure!', 'ERROR', wx.OK | wx.ERROR)
        
    def onStop(self, event):
        self.sVal['com'].value = 5
        while self.sVal['com'].value != 0:
            time.sleep(0.01)
        if self.rec:
            protdf = pd.DataFrame({
                'Vial': self.vOrder,
                'Acidity': self.aOrder
            })
            with open(self.metaPath, 'a') as f:
               f.write('\nVial and Acidity Data:\n')
               protdf.to_string(f, index=False)
        #     self.closeFiles([self.metaPath, self.configpath, self.protocol_path])
        # else:
        #     self.closeFiles([self.configpath, self.protocol_path])
          
        self.rec = False
        self.start = False
        self.bStart.Enable(True) 
        self.bStop.Enable(False) 
        # for c in self.checkboxes:
        #     c.Enable(True)
        # for d in self.dropdowns:
        #     d.Enable(True)
        for b in self.vialButtons:
            b.Enable(True)
        print("TrialStopped")
        
        if self.timer and self.timer.IsRunning():
          self.timer.Stop()
        
    # def closeFiles(self,fList):
    #     for f in fList:
    #         if not f.closed:
    #             f.close()
            
    def onClose(self, event):
        if self.timer and self.timer.IsRunning():
          self.timer.Stop()
        if self.init:
            self.arduino_process.terminate()
        self.Destroy()  
     
class MyApp(wx.App):
    def OnInit(self):
        frame = MainFrame()
        frame.Show()
        return True

if __name__ == "__main__":
    app = MyApp()
    app.MainLoop()
