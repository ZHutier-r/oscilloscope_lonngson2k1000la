from PyQt5.QtWidgets import *
from PyQt5.QtGui import  QPen
from PyQt5.QtCore import Qt, QTimer,QRandomGenerator,QPointF
from  PyQt5.QtChart import QChart,QLineSeries, QValueAxis,QScatterSeries
import spi as _spi

class MyChart(QChart):
    def __init__(self, parent = None):
        super(MyChart, self).__init__(parent)
        self.spi = _spi.SPI("/dev/spidev0.1")
        self.spi.mode = _spi.SPI.MODE_0
        self.spi.bits_per_word = 8
        self.spi.speed = 500000
        self.point_list=[]
        self.point_list2=[]
        self.outputlist=[]
        self.series = None
        self.series2 = None
        self.axisX = QValueAxis()
        self.axisY = QValueAxis()
        self.get_in = 0
        self.step = 0
        self.x = 0
        self.y = 1
        self.xlist=[]
        self.ylist=[]
        self.time_mode=0 #0-20ms/div 1-2us/div 2-100ns/div
        self.vol_mode=0 #0-1V/div 1-0.1V/div 2-2mv/div
        self.freqcy=0
        #创建一个定时器
        self.setTitle("Vpp= 0V f=50Hz")
        self.timer = QTimer()
        self.timer.timeout.connect(self.handleTimeout)
        self.timer.setInterval(1000)
        # self.series = QScatterSeries(self)
        self.series = QLineSeries(self)
        redPen = QPen(Qt.red)
        redPen.setWidth(3)
        #self.series.setMarkerSize(10)
        #self.series.setPen(redPen)
        self.series.append(self.x, self.y)
        self.addSeries(self.series)
        self.addAxis(self.axisX, Qt.AlignBottom)
        self.addAxis(self.axisY, Qt.AlignLeft)
        self.series.attachAxis(self.axisX)
        self.series.attachAxis(self.axisY)
        self.axisX.setTickCount(11)
        self.axisY.setTickCount(9)
        self.axisX.setRange(0, 400)
        self.axisY.setRange(-0.4, 0.4)
        self.timer.start()
    def handleTimeout(self):
        self.point_list=[]
        self.point_list2=[]
        self.xlist=[]
        self.ylist=[]
        k=0
        while(1):
            rec=self.spi.read(1)
            k=int.from_bytes(rec,byteorder="big")
            if k == 255:
                break
        k=0
        print(self.vol_mode)
        for i in range(4):
            received = self.spi.read(1)
            #print(received)
            k=k*16*16+int.from_bytes(received,byteorder="big")
        self.freqcy=0
        if k>0:
            self.freqcy=300000000/k
        print('f=')
        print(self.freqcy)
        if self.get_in==0 or self.get_in==2:
            self.Vpp=0
            Vppmin=256
            Vppmax=-255
            self.x=0
            self.series.clear()
            xdis=0
            if self.time_mode==0:
                xdis=0.5
            if self.time_mode==1:
                xdis=0.05
            if self.time_mode==2:
                xdis=2.5*5.0
                print(xdis)
                k1=0
                while(1):
                    rec=self.spi.read(1)
                    k=int.from_bytes(rec,byteorder="big")
                    if k<=130 and k>=128:
                        if k>k1:
                            break
                    k1=k
            print(self.time_mode)
            for i in range(398):
                self.x=self.x+xdis
                # self.y=QRandomGenerator.global_().bounded(5) - 2.5                
                # k=int.from_bytes(rec,byteorder="big")
                # self.y=QRandomGenerator.global_().bounded(5) - 2.5
                rec=self.spi.read(1)
                # print(int.from_bytes(rec,byteorder="big"))
                self.y=int.from_bytes(rec,byteorder="big")/255.0*8.0-3.87
                if self.vol_mode==0 and self.time_mode==2:
                    self.y=self.y*1.16
                if self.vol_mode==1:
                    self.y=self.y/10.0
                if self.vol_mode==2:
                    self.y=self.y+0.90
                    self.y=self.y*2.0
                if self.y<Vppmin:
                    Vppmin=self.y
                if self.y>Vppmax:
                    Vppmax=self.y
                #rec=self.spi.read(1)
                self.xlist.append(self.x)
                self.ylist.append(self.y)
                tmp_point=QPointF(self.x,self.y)
                self.point_list.append(tmp_point)
            self.series.append(self.point_list)
            self.outputlist=[self.xlist,self.ylist]
            self.Vpp=Vppmax-Vppmin
            if self.get_in==2:
                self.get_in=1
        s_fre="frequency=%.2f"%self.freqcy+"Hz Vpp=%.2f"%self.Vpp
        self.setTitle(s_fre)
        if self.x == 402:
            self.timer.stop()