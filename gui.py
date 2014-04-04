import wx
import wx.py
#import run
import subprocess
import wx.lib.scrolledpanel as scrolled
import threading, time
from config import *



class PageOne(wx.Panel):
	def __init__(self, parent,th):
		self.th=th

		wx.Panel.__init__(self, parent)
		tc1 = wx.TextCtrl(self, -1, '', (10,10), (320,200))
		#run.TextChat
		self.tc2 = wx.TextCtrl(self, -1, '', (10,220), (320,80))
		button1=wx.Button(self, -1, "send",pos=(240,310))
		button1.Bind(wx.EVT_BUTTON, self.OnClick)

	def OnClick(self,event):
		self.th.put_message(self.tc2.GetValue())		
		
		
class PageTwo(scrolled.ScrolledPanel):
	def __init__(self, parent):
		self.cfg = Config()
		scrolled.ScrolledPanel.__init__(self, parent, -1)
		
		vbox = wx.BoxSizer(wx.VERTICAL)
		hbox=wx.BoxSizer(wx.HORIZONTAL)	
		
		vbox = wx.BoxSizer(wx.VERTICAL)
		c = wx.StaticText(self, -1, "Client")
		vbox.Add(c,1)
			
		hbox=wx.BoxSizer(wx.HORIZONTAL)	
		ca = wx.StaticText(self, -1, "Address  ")
		hbox.Add(ca,3)
		str = self.cfg.read('client','address')
		self.tca = wx.TextCtrl(self, -1, str, (100,20))		
		hbox.Add(self.tca,3)
		vbox.Add(hbox,1)
		
		hbox=wx.BoxSizer(wx.HORIZONTAL)
		cp = wx.StaticText(self, -1, "Port  ")
		hbox.Add(cp,3)	
		str = self.cfg.read('client','port')
		self.tcp = wx.TextCtrl(self, -1, str, (100,20))		
		hbox.Add(self.tcp,3)
		vbox.Add(hbox,1)

		s = wx.StaticText(self, -1, "Server:")
		vbox.Add(s,1)	
		hbox=wx.BoxSizer(wx.HORIZONTAL)	
		sa = wx.StaticText(self, -1, "Address  ")
		hbox.Add(sa,3)
		str = self.cfg.read('server','address')
		self.tsa = wx.TextCtrl(self, -1, str, (100,20))		
		hbox.Add(self.tsa,3)
		vbox.Add(hbox,1)

		d = wx.StaticText(self, -1, "Destination:")
		vbox.Add(d,1)
			
		hbox=wx.BoxSizer(wx.HORIZONTAL)	
		da = wx.StaticText(self, -1, "Address  ")
		hbox.Add(da,3)
		str = self.cfg.read('destination','address')
		self.tda = wx.TextCtrl(self, -1, str, (100,20))		
		hbox.Add(self.tda,3)
		vbox.Add(hbox,1)
		
		hbox=wx.BoxSizer(wx.HORIZONTAL)	
		dp = wx.StaticText(self, -1, "Port  ")
		hbox.Add(dp,3)
		str = self.cfg.read('destination','port')
		self.tdp = wx.TextCtrl(self, -1, str, (100,20))		
		hbox.Add(self.tdp,3)
		vbox.Add(hbox,1)
		
		a = wx.StaticText(self, -1, "Audio:")
		vbox.Add(a,1)
			
		hbox=wx.BoxSizer(wx.HORIZONTAL)	
		af = wx.StaticText(self, -1, "format  ")
		hbox.Add(af,3)
		str = self.cfg.read('audio','format')
		self.taf = wx.TextCtrl(self, -1, str, (100,20))		
		hbox.Add(self.taf,3)
		vbox.Add(hbox,1)
		
		hbox=wx.BoxSizer(wx.HORIZONTAL)	
		ac = wx.StaticText(self, -1, "channels  ")
		hbox.Add(ac,3)
		str = self.cfg.read('audio','channels')
		self.tac = wx.TextCtrl(self, -1, str, (100,20))		
		hbox.Add(self.tac,3)
		vbox.Add(hbox,1)

		hbox=wx.BoxSizer(wx.HORIZONTAL)	
		ar = wx.StaticText(self, -1, "rate  ")
		hbox.Add(ar,3)
		str = self.cfg.read('audio','rate')
		self.tar = wx.TextCtrl(self, -1, str, (100,20))		
		hbox.Add(self.tar,3)
		vbox.Add(hbox,1)
		
		hbox=wx.BoxSizer(wx.HORIZONTAL)	
		afpb = wx.StaticText(self, -1, "frames_per_buffer  ")
		hbox.Add(afpb,3)
		str = self.cfg.read('audio','frames_per_buffer')
		self.tafpb = wx.TextCtrl(self, -1, str, (100,20))		
		hbox.Add(self.tafpb,3)
		vbox.Add(hbox,1)

		cc = wx.StaticText(self, -1, "Crypto:")
		vbox.Add(cc,1)
			
		hbox=wx.BoxSizer(wx.HORIZONTAL)	
		cca = wx.StaticText(self, -1, "algorithm  ")
		hbox.Add(cca,3)
		str = self.cfg.read('crypto','algorithm')
		self.tcca = wx.TextCtrl(self, -1, str, (100,20))		
		hbox.Add(self.tcca,3)
		vbox.Add(hbox,1)
		
		hbox=wx.BoxSizer(wx.HORIZONTAL)	
		ccb = wx.StaticText(self, -1, "block_mode  ")
		hbox.Add(ccb,3)
		str = self.cfg.read('crypto','block_mode')
		self.tccb = wx.TextCtrl(self, -1, str, (100,20))		
		hbox.Add(self.tccb,3)
		vbox.Add(hbox,1)

		hbox=wx.BoxSizer(wx.HORIZONTAL)	
		ccbs = wx.StaticText(self, -1, "block_size  ")
		hbox.Add(ccbs,3)
		str = self.cfg.read('crypto','block_size')
		self.tccbs = wx.TextCtrl(self, -1, str, (100,20))		
		hbox.Add(self.tccbs,3)
		vbox.Add(hbox,1)
		
		hbox=wx.BoxSizer(wx.HORIZONTAL)	
		t1 = wx.StaticText(self, -1, "key size  ")
		hbox.Add(t1,3)
		str = self.cfg.read('crypto','key_size')
		tc2 = wx.TextCtrl(self, -1, str, (100,20))		
		hbox.Add(tc2,3)
		vbox.Add(hbox,1)


		hbox=wx.BoxSizer(wx.HORIZONTAL)	
		t1 = wx.StaticText(self, -1, "init_vector  ")
		hbox.Add(t1,3)
		tc2 = wx.TextCtrl(self, -1, '', (100,20))		
		hbox.Add(tc2,3)
		vbox.Add(hbox,1)
		
		hbox=wx.BoxSizer(wx.HORIZONTAL)	
		t1 = wx.StaticText(self, -1, "key  ")
		hbox.Add(t1,3)
		tc2 = wx.TextCtrl(self, -1, '', (100,20))		
		hbox.Add(tc2,3)
		vbox.Add(hbox,1)

		button1=wx.Button(self, -1, "Save Changes")
		vbox.Add(button1,2)
		button1.Bind(wx.EVT_BUTTON, self.OnClick)

		self.SetSizer(vbox)
		self.SetAutoLayout(1)
   		self.SetupScrolling()

	def OnClick(self,event):
		self.cfg.save('client','address',self.tca.GetValue())
		self.cfg.save('client','port',self.tcp.GetValue())
		print self.tsa.GetValue()
		self.cfg.save('server','address',self.tsa.GetValue())

		self.cfg.save('destination','address',self.tda.GetValue())
		self.cfg.save('destination','port',self.tdp.GetValue())

		self.cfg.save('audio','format',self.taf.GetValue())
		self.cfg.save('audio','channels',self.tac.GetValue())
		self.cfg.save('audio','rate',self.tar.GetValue())
		self.cfg.save('audio','frames_per_buffer',self.tafpb.GetValue())

		self.cfg.save('crypto','algorithm',self.tcca.GetValue())
		self.cfg.save('crypto','block_mode',self.tccb.GetValue())
		self.cfg.save('crypto','block_size',self.tccbs.GetValue())



class PageThree(wx.Panel):
	def __init__(self, parent):
		wx.Panel.__init__(self, parent)
		#t = wx.StaticText(self, -1, "This is a PageThree object", (50,50))
		wx.py.shell.Shell(self,size=(350,450))

class MainFrame(wx.Frame):
	def __init__(self,th):
		wx.Frame.__init__(self, None,-1, title="VoIP",style= wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX,size=(350,450))

		

		p = wx.Panel(self,pos=(0,0),size=(350,40))
		p1 = wx.Panel(self,pos=(0,40),size=(350,450))
		nb = wx.Notebook(p1,size=(350,450))
		chkbox=wx.CheckBox(p, -1 ,'Enable Voice', (0, 10))
		
		page1 = PageOne(nb,th)
		page2 = PageTwo(nb)
		page3 = PageThree(nb)
		#self.button1=wx.Button(p, -1, "Connect",pos=(250,5))
		#self.button1.Bind(wx.EVT_BUTTON, self.OnClick)

		nb.AddPage(page1, "chat")
		nb.AddPage(page2, "settings")
		nb.AddPage(page3, "ssh")

		sizer = wx.BoxSizer(wx.VERTICAL)
		#sizer.Add(self.button1,0)
		sizer.Add(nb, 2)
		p.SetSizer(sizer)
		#self.SetSizer(vbox)
   		
		
	#def OnClick(self, e):
	#	p = subprocess.call("run.py -c",shell=True)
	#	self.button1.SetLabel("disconnect")
	
class GUI(threading.Thread):
	def __init__(self,th):
		self.th=th
		self.app = wx.App()
		threading.Thread.__init__(self)

	def run(self):
		m = MainFrame(self.th)
		m.Show()
		self.app.MainLoop()


if __name__ == "__main__":
	g = GUI()
	g.start()
	