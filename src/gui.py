import wx
import wx.py
import signal
import subprocess
import wx.lib.scrolledpanel as scrolled

from config import *

import threading
import Queue
import time
from subprocess import Popen, PIPE
import sys
import os


class BashProcessThread(threading.Thread):
    def __init__(self, readlineFunc):
        threading.Thread.__init__(self)
        self.readlineFunc = readlineFunc
        self.outputQueue = Queue.Queue()
        self.setDaemon(True)

    def run(self):
        while True:
            line = self.readlineFunc()
            self.outputQueue.put(line)

    def getOutput(self):
        lines = []
        while True:
            try:
                line = self.outputQueue.get_nowait()
                lines.append(line)
            except Queue.Empty:
                break
        return ''.join(lines)

class Interpretor(object):
    def __init__(self, locals, rawin, stdin, stdout, stderr):
        self.introText = "shell inbuilt unsupported"
        self.locals = locals
        self.revision = 1.0
        self.rawin = rawin
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr

        self.more = False
        self.bp = Popen('bash', shell=False, stdout=PIPE, stdin=PIPE, stderr=PIPE)

        self.outputThread = BashProcessThread(self.bp.stdout.readline)
        self.outputThread.start()

        self.errorThread = BashProcessThread(self.bp.stderr.readline)
        self.errorThread.start()

    def getAutoCompleteKeys(self):
        return [ord('\t')]

    def getAutoCompleteList(self, *args, **kwargs):
        return []

    def getCallTip(self, command):
        return ""

    def push(self, command):
        command = command.strip()
        command = command.replace('(', ' ').replace(')', ' ').strip()
        print 'SHELL', command
        
        if not command: 
            return
        self.bp.stdin.write(command+"\n")
        time.sleep(0.1)

        self.stdout.write(self.outputThread.getOutput())
        self.stderr.write(self.errorThread.getOutput())
        
class Validator(wx.PyValidator):
     def __init__(self):
         wx.PyValidator.__init__(self)

     def Clone(self):
         return Validator()

     def Validate(self, win):
         textCtrl = self.GetWindow()
         text = textCtrl.GetValue()
         a = text.split('.')
         if len(a) != 4:
            wx.MessageBox("Enter IP Address", "Error")
            textCtrl.SetBackgroundColour("pink")
            textCtrl.SetFocus()
            textCtrl.Refresh()
            return False
         for x in a:
            if not x.isdigit():
                wx.MessageBox("Invalid IP Address", "Error")
                textCtrl.SetBackgroundColour("pink")
                textCtrl.SetFocus()
                textCtrl.Refresh()
                return False
            i = int(x)
            if i < 0 or i > 255:
                wx.MessageBox("Invalid IP Address", "Error")
                textCtrl.SetBackgroundColour("pink")
                textCtrl.SetFocus()
                textCtrl.Refresh()
                return False
         textCtrl.SetBackgroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOW))
         textCtrl.Refresh()
         return True

     def TransferToWindow(self):
         return True # Prevent wxDialog from complaining.

class getmsg(threading.Thread):
    def __init__(self,th,tc1):
        threading.Thread.__init__(self)
        self.th = th
        self.tc1=tc1
    def run(self):
        while True:
            x = self.th.get_message()
            for i in x:
                self.tc1.AppendText("Them : "+i+"\n")
            time.sleep(1)
                
class PageOne(wx.Panel):
    def __init__(self, parent,th):
        self.th = th

        wx.Panel.__init__(self, parent)
        self.tc1 = wx.TextCtrl(parent = self, id = -1, pos = (10, 10), size = (320, 200), style = wx.TE_MULTILINE|wx.TE_READONLY|wx.TE_AUTO_URL|wx.TE_RICH)
        self.tc2 = wx.TextCtrl(parent = self, id = -1, pos = (10, 220), size = (320, 80), style = wx.TE_MULTILINE)
        button1 = wx.Button(self, -1, "send",pos=(240,310))
        button1.Bind(wx.EVT_BUTTON, self.OnClick)
        self.gm=getmsg(th,self.tc1)
        self.gm.start()

    def OnClick(self,event):
        str = self.tc2.GetValue()
        self.th.put_message(str)
        self.tc2.Clear()
        self.tc1.AppendText("Me: "+str+"\n")
        
class PageTwo(scrolled.ScrolledPanel):
    def __init__(self, parent):
        self.cfg = Config()
        scrolled.ScrolledPanel.__init__(self, parent, -1)

        self.SetExtraStyle(wx.WS_EX_VALIDATE_RECURSIVELY)   

        vbox = wx.BoxSizer(wx.VERTICAL)
        
        Lbl = wx.StaticBox(self, -1, 'Client', size = (310,50))
        vbox1 = wx.StaticBoxSizer(Lbl, wx.VERTICAL)
            
        hbox=wx.BoxSizer(wx.HORIZONTAL) 
        ca = wx.StaticText(self, -1, "Address  ")
        hbox.Add(ca,5)
        str = self.cfg.read('client','address')
        self.tca = wx.TextCtrl(self, -1, str, (300,20), size = (130,40))        
        hbox.Add(self.tca,5)
        vbox1.Add(hbox,1)
        
        hbox=wx.BoxSizer(wx.HORIZONTAL)
        cp = wx.StaticText(self, -1, "Port  ")
        hbox.Add(cp,5)  
        str = self.cfg.read('client','port')
        self.tcp = wx.TextCtrl(self, -1, str, (100,20))     
        hbox.Add(self.tcp,3)    
        vbox1.Add(hbox,1)

        vbox.Add(vbox1,2)

        Lbl2 = wx.StaticBox(self, -1, 'Server', size = (310,50))
        vbox2 = wx.StaticBoxSizer(Lbl2, wx.VERTICAL)
        hbox=wx.BoxSizer(wx.HORIZONTAL) 
        sa = wx.StaticText(self, -1, "Address  ")
        hbox.Add(sa,5)
        str = self.cfg.read('server','address')
        self.tsa = wx.TextCtrl(self, -1, str, (100,20), size = (130,40))        
        hbox.Add(self.tsa,5)
        vbox2.Add(hbox,1)
        vbox.Add(vbox2,1)

        Lbl3 = wx.StaticBox(self, -1, 'Destination', size = (310,50))
        vbox3 = wx.StaticBoxSizer(Lbl3, wx.VERTICAL)
        hbox=wx.BoxSizer(wx.HORIZONTAL) 
        da = wx.StaticText(self, -1, "Address  ")
        hbox.Add(da,5)
        str = self.cfg.read('destination','address')
        self.tda = wx.TextCtrl(self, -1, str, (100,20), size = (130,40))        
        hbox.Add(self.tda,5)
        vbox3.Add(hbox,1)

        hbox=wx.BoxSizer(wx.HORIZONTAL) 
        dp = wx.StaticText(self, -1, "Port  ")
        hbox.Add(dp,5)
        str = self.cfg.read('destination','port')
        self.tdp = wx.TextCtrl(self, -1, str, (100,20))     
        hbox.Add(self.tdp,3)
        vbox3.Add(hbox,1)
        vbox.Add(vbox3,2)
        

        Lbl4 = wx.StaticBox(self, -1, 'Audio' , size = (310,50))
        vbox4 = wx.StaticBoxSizer(Lbl4, wx.VERTICAL)
        hbox=wx.BoxSizer(wx.HORIZONTAL) 
        
        af = wx.StaticText(self, -1, "format  ")
        hbox.Add(af,4)
        formatlist = [ 'paInt 8','paInt 16','paInt 24','paInt 32' ]
        self.choice1 = wx.Choice(self, -1, choices=formatlist)
        self.choice1.SetSelection(1)
        self.choice1.SetFocus()
        #self.choice1.Bind(wx.EVT_CHOICE, self.OnClick) 
        hbox.Add(self.choice1,3)

        vbox4.Add(hbox,1)
        
        hbox=wx.BoxSizer(wx.HORIZONTAL) 
        ac = wx.StaticText(self, -1, "channels  ")
        hbox.Add(ac,5)
        str = self.cfg.read('audio','channels')
        self.tac = wx.TextCtrl(self, -1, str, (100,20))     
        hbox.Add(self.tac,3)
        vbox4.Add(hbox,1)

        hbox=wx.BoxSizer(wx.HORIZONTAL) 
        ar = wx.StaticText(self, -1, "rate  ")
        hbox.Add(ar,5)
        str = self.cfg.read('audio','rate')
        self.tar = wx.TextCtrl(self, -1, str, (100,20))     
        hbox.Add(self.tar,3)
        vbox4.Add(hbox,1)
        
        hbox=wx.BoxSizer(wx.HORIZONTAL) 
        afpb = wx.StaticText(self, -1, "frames_per_buffer  ")
        hbox.Add(afpb,5)
        str = self.cfg.read('audio','frames_per_buffer')
        self.tafpb = wx.TextCtrl(self, -1, str, (100,20))       
        hbox.Add(self.tafpb,3)
        vbox4.Add(hbox,1)

        vbox.Add(vbox4,4)

        Lbl5 = wx.StaticBox(self, -1, 'Crypto', size = (310,50))
        vbox5 = wx.StaticBoxSizer(Lbl5, wx.VERTICAL)
            
        hbox = wx.BoxSizer(wx.HORIZONTAL)   
        cca = wx.StaticText(self, -1, "algorithm  ")
        hbox.Add(cca,7)
        cryptlist = [ 'AES', 'BlowFish','Cast','DES3' ]
        self.choice2 = wx.Choice(self, -1, choices=cryptlist)
        self.choice2.SetSelection(0)
        self.choice2.SetFocus()
        #self.choice2.Bind(wx.EVT_CHOICE, self.OnClick) 
        hbox.Add(self.choice2,5)
        vbox5.Add(hbox,1)
        
        hbox=wx.BoxSizer(wx.HORIZONTAL) 
        ccb = wx.StaticText(self, -1, "block_mode  ")
        hbox.Add(ccb,6)
        blocklist = [ 'CBC' , 'ECB']
        self.choice3 = wx.Choice(self, -1, choices=blocklist)
        self.choice3.SetSelection(0)
        self.choice3.SetFocus()
        #self.choice3.Bind(wx.EVT_CHOICE, self.OnClick)         
        hbox.Add(self.choice3,3)
        vbox5.Add(hbox,1)

        hbox=wx.BoxSizer(wx.HORIZONTAL) 
        ccbs = wx.StaticText(self, -1, "block_size  ")
        hbox.Add(ccbs,5)
        str = self.cfg.read('crypto','block_size')
        self.tccbs = wx.TextCtrl(self, -1, str, (100,20))       
        hbox.Add(self.tccbs,3)
        vbox5.Add(hbox,1)
        
        hbox=wx.BoxSizer(wx.HORIZONTAL) 
        t1 = wx.StaticText(self, -1, "key size  ")
        hbox.Add(t1,5)
        str = self.cfg.read('crypto','key_size')
        tc2 = wx.TextCtrl(self, -1, str, (100,20))      
        hbox.Add(tc2,3)
        vbox5.Add(hbox,1)

        vbox.Add(vbox5,4)

        vbox6 = wx.BoxSizer(wx.VERTICAL)
        hbox=wx.BoxSizer(wx.HORIZONTAL)
        button1=wx.Button(self,-1, "Save Changes")
        button1.Bind(wx.EVT_BUTTON, self.OnClick)
        hbox.Add(button1,5)
        vbox6.Add(hbox,1)
        vbox.Add(vbox6,1)


        self.SetSizer(vbox)
        self.SetAutoLayout(1)
        self.SetupScrolling()

        self.tca.SetValidator(Validator())
        self.tsa.SetValidator(Validator())
        self.tda.SetValidator(Validator()) 


    def OnClick(self,event):

        if(self.Validate() == True):
            wx.MessageBox("Please restart the App to apply the new configuration")
        self.cfg.save('client','address',self.tca.GetValue())
        self.cfg.save('client','port',self.tcp.GetValue())
        print self.tsa.GetValue()
        self.cfg.save('server','address',self.tsa.GetValue())

        self.cfg.save('destination','address',self.tda.GetValue())
        self.cfg.save('destination','port',self.tdp.GetValue())

        self.cfg.save('audio','format','paInt 16')
        self.cfg.save('audio','channels',self.tac.GetValue())
        self.cfg.save('audio','rate',self.tar.GetValue())
        self.cfg.save('audio','frames_per_buffer',self.tafpb.GetValue())

        self.cfg.save('crypto','algorithm','AES')
        self.cfg.save('crypto','block_mode','CBC')
        self.cfg.save('crypto','block_size',self.tccbs.GetValue())
class PageThree(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        #t = wx.StaticText(self, -1, "This is a PageThree object", (50,50))
        wx.py.shell.Shell(self,size=(350,450),InterpClass=Interpretor)

class MainFrame(wx.Frame):
    def __init__(self,th,kand):
        wx.Frame.__init__(self, None,-1, title="VoIP",style= wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX,size=(350,450))

        self.kand = kand
        
        p = wx.Panel(self,pos=(0,0),size=(350,40))
        p1 = wx.Panel(self,pos=(0,40),size=(350,450))
        nb = wx.Notebook(p1,size=(350,450))
        self.cb1=wx.CheckBox(p, -1 ,'Mute', (0, 10))
        self.cb1.SetValue(True)
        
        page1 = PageOne(nb,th)
        page2 = PageTwo(nb)
        page3 = PageThree(nb)
        #self.button1=wx.Button(p, -1, "Connect",pos=(250,5))
        #self.button1.Bind(wx.EVT_BUTTON, self.OnClick)

        nb.AddPage(page1, "Chat")
        nb.AddPage(page2, "Settings")
        nb.AddPage(page3, "Shell")

        sizer = wx.BoxSizer(wx.VERTICAL)
        #sizer.Add(self.button1,0)
        sizer.Add(nb, 2)
        p.SetSizer(sizer)
        #self.SetSizer(vbox)
        self.Bind(wx.EVT_CHECKBOX, self.OnCb1, self.cb1)

        self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)

        
    def OnCb1(self, evt):
        #self.cb2.SetValue(evt.IsChecked())
        #self.th.enable()
        self.kand.switch()
    
    def OnCloseWindow(self, event):
    	# self.Destroy()
    	print 'closed'
    	p = subprocess.Popen(['ps', '-A'], stdout=subprocess.PIPE)
    	out, err = p.communicate()
    	for line in out.splitlines():
    		if 'python' in line:
    			pid = int(line.split(None, 1)[0])
    			os.kill(pid, signal.SIGKILL)
    #def OnClick(self, e):
    #   p = subprocess.call("run.py -c",shell=True)
    #   self.button1.SetLabel("disconnect")
    
class GUI(threading.Thread):
    def __init__(self,th,kand):
        self.th=th
        self.kand = kand
        self.app = wx.App()
        threading.Thread.__init__(self)

    def run(self):
        m = MainFrame(self.th, self.kand)
        m.Show()
        self.app.MainLoop()


if __name__ == "__main__":
    g = GUI()
    g.start()
    