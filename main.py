import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt,QPointF
from  PyQt5.QtChart import QChartView
from part import MyChart
import dsp as DSP
from sysfs_pin import Pin

class ControL(QWidget):
    vol_mode=0
    time_mode=0
    voltage_trigger=0
    def __init__(self,parent=None):

        super(ControL, self).__init__(parent)

        self.setStyleSheet('background-color:rgb(245,212,217)')
        # 按照从上到下的顺序添加控件
        vlayout_tot= QHBoxLayout()
        vlayout_left=QVBoxLayout()
        vlayout_parameter=QHBoxLayout()
        vlayout_right = QVBoxLayout()
        vlayout_right_up = QHBoxLayout()
        vlayout_right_middle = QHBoxLayout()
        self.pin1=Pin(53)
        self.pin1.init(mode=Pin.IN)
        self.pin2=Pin(52)
        self.pin2.init(mode=Pin.IN)
        self.pin3=Pin(54)
        self.pin3.init(mode=Pin.IN)

        self.pin4=Pin(60)
        self.pin4.init(mode=Pin.IN)
        self.pin5=Pin(61)
        self.pin5.init(mode=Pin.IN)
        self.pin6=Pin(62)
        self.pin6.init(mode=Pin.IN)

        right_up=QWidget()
        rightside = QWidget()
        leftside=QWidget()
        right_middle=QWidget()
        parameter=QWidget()

        right_up.setLayout(vlayout_right_up)
        rightside.setLayout(vlayout_right)
        right_middle.setLayout(vlayout_right_middle)
        leftside.setLayout(vlayout_left)
        parameter.setLayout(vlayout_parameter)

        self.btn1=QPushButton("保存波形")       
        self.btn2=QPushButton("载入波形")
        self.btn3=QPushButton("DFT")
        self.btn1.setStyleSheet('background-color:rgb(242,156,177)')
        self.btn2.setStyleSheet('background-color:rgb(242,156,177)')
        self.btn3.setStyleSheet('background-color:rgb(242,156,177)')
        self.btn1.clicked.connect(self.save)
        self.btn2.clicked.connect(self.load)
        self.btn3.clicked.connect(self.wave_dft)

        self.path=QLineEdit('my.txt')

        self.trigger_label=QLabel(" ")
        self.trigger_slider=QSlider(Qt.Horizontal)
        self.trigger_slider.setMaximum(99)
        self.trigger_slider.setStyleSheet('''
  QSlider{border-style: outset;border-radius: 10px;}
  QSlider:add-page{background-color: rgb(242,156,177);height:5px;}
  QSlider:groove{height: 12px;background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 white, stop:1 red);margin: 2px 0;}
  QSlider:handle{background: QRadialGradient(cx:0, cy:0, radius: 1, fx:0.5, fy:0.5, stop:0 white, stop:1 red);width: 16px;height: 16px;margin: -5px 0px -5px 0px;border-radius:11px;border: 3px solid #ffffff;}
''')

        self.voltage_bar=QProgressBar(self)
        self.voltage_bar.setMinimum(0)
        self.voltage_bar.setMaximum(2)
        self.voltage_bar.setValue(0)
        self.voltage_bar.setTextVisible(False)
        self.time_bar=QProgressBar(self)
        self.time_bar.setMinimum(0)
        self.time_bar.setMaximum(2)
        self.time_bar.setValue(0)
        self.time_bar.setTextVisible(False)
        self.voltage_bar.setStyleSheet("QProgressBar::chunk "
                          "{"
                          "background-color: rgb(242,120,156);"
                          "}")
        self.time_bar.setStyleSheet("QProgressBar::chunk "
                          "{"
                          "background-color: rgb(242,120,156);"
                          "}")
        self.trigger_single = QPushButton("单次触发")
        self.trigger_syn = QPushButton("同步触发")
        self.modeget_btn=QPushButton("模式获取")
        self.trigger_single.setStyleSheet('background-color:rgb(242,156,177)')
        self.trigger_syn.setStyleSheet('background-color:rgb(242,156,177)')
        self.trigger_syn.clicked.connect(self.syntrigger)
        self.trigger_single.clicked.connect(self.singletrigger)
        self.modeget_btn.clicked.connect(self.allmodeget)
        self.voltage_bar_label=QLabel()
        self.voltage_bar_label.setText("1V/div")
        self.voltage_bar_label.setAlignment(Qt.AlignCenter)
        self.time_bar.setMaximum(2)
        self.time_bar_label=QLabel()
        self.time_bar_label.setText("20ms/div")
        self.time_bar_label.setAlignment(Qt.AlignCenter)
        vlayout_right_up.addWidget(self.btn1)
        vlayout_right_up.addWidget(self.btn2)
        vlayout_right_up.addWidget(self.btn3)
        vlayout_right_middle.addWidget(self.trigger_single)
        vlayout_right_middle.addWidget(self.trigger_syn)
        vlayout_right.addWidget(right_up)
        vlayout_right.addWidget(self.path)
        vlayout_right.addWidget(right_middle)
        vlayout_right.addWidget(self.modeget_btn)
        vlayout_right.addWidget(self.trigger_label)
        vlayout_right.addWidget(self.trigger_slider)
        vlayout_right.addWidget(self.voltage_bar_label)
        vlayout_right.addWidget(self.voltage_bar)
        vlayout_right.addWidget(self.time_bar_label)
        vlayout_right.addWidget(self.time_bar)
        self.chart = MyChart()
        self.chart.legend().hide()
        self.chartView = QChartView(self.chart)

        vlayout_left.addWidget(self.chartView)
        vlayout_tot.addWidget(leftside,2)
        vlayout_tot.addWidget(rightside,1)
        self.setLayout(vlayout_tot)
        
        self.trigger_slider.valueChanged.connect(self.get_volatge_trigger)
    def allmodeget(self):
        A=self.pin1._read()
        B=self.pin2._read()
        C=self.pin3._read()
        if A:
            self.voltage_bar.setValue(1)
            self.voltage_bar_label.setText("0.1V/div")
            self.chart.axisY.setRange(-0.4, 0.4)
            self.chart.vol_mode=1
        if B:
            self.voltage_bar.setValue(0)
            self.voltage_bar_label.setText("2mV/div")
            self.chart.axisY.setRange(-8.0, 8.0)
            self.chart.vol_mode=2
        if C:
            self.voltage_bar.setValue(2)
            self.voltage_bar_label.setText("1V/div")
            self.chart.axisY.setRange(-4.0, 4.0)
            self.chart.vol_mode=0
        A=self.pin4._read()
        B=self.pin5._read()
        C=self.pin6._read()
        if A:
            self.time_bar.setValue(0)
            self.time_bar_label.setText("20ms/div")
            self.chart.axisX.setRange(0, 200)
            self.chart.time_mode=0
            print(0)
        if B:
            self.time_bar.setValue(1)
            self.time_bar_label.setText("2us/div")
            self.chart.axisX.setRange(0, 20)
            self.chart.time_mode=1
        if C:
            self.time_bar.setValue(2)
            self.time_bar_label.setText("100ns/div")
            self.chart.axisX.setRange(0, 1000)
            self.chart.time_mode=2
    def syntrigger(self):
        self.chart.get_in=0
    def singletrigger(self):
        self.chart.get_in=2
    def save(self):
        file_path="datasum/"+self.path.text()
        file = open(file_path, 'w')
        file.write(str(self.chart.outputlist))
        file.close()
    def load(self):
        file_path="datasum/"+self.path.text()
        file=open(file_path,"r")
        inlist=file.read()
        Len=len(inlist)
        inlist=inlist[2:Len-2]
        inlist=inlist.split(']')
        inlist[1]=inlist[1][3:len(inlist[1])]
        x_list=inlist[0].split(',')
        y_list=inlist[1].split(',')
        x_list=list(map(float,x_list))
        y_list=list(map(float,y_list))
        self.chart.get_in=1
        Len=len(x_list)
        self.chart.point_list=[]
        print(Len)
        self.chart.point_list=[]
        Vppmax=-10.0
        Vppmin=10.0
        for k in range(Len):
            tmp_point=QPointF(x_list[k],y_list[k])
            if y_list[k]>Vppmax:
                Vppmax=y_list[k]
            if y_list[k]<Vppmin:
                Vppmin=y_list[k]
            self.chart.point_list.append(tmp_point)
        self.chart.series.clear()
        self.chart.series.append(self.chart.point_list)
        self.chart.Vpp=Vppmax-Vppmin
        title="frequency=%.2f"%self.chart.freqcy+"Hz Vpp=%.2f"%self.chart.Vpp
        self.chart.setTitle(title)
        file.close()
    def wave_dft(self):
        print('dft')
        self.chart.ylist=DSP.dft(self.chart.ylist)
        Len=len(self.chart.ylist)
        self.chart.get_in=1
        self.chart.point_list=[]
        for k in range(Len):
            tmp_point=QPointF(self.chart.xlist[k],self.chart.ylist[k])
            self.chart.point_list.append(tmp_point)
        self.chart.series.clear()
        self.chart.series.append(self.chart.point_list)
    
    def get_volatge_trigger(self):
        self.voltage_trigger=self.trigger_slider.value()
        a="触发电平:"+str(self.voltage_trigger)+"V"
        self.trigger_label.setText(a)
    def handleTimeout(self):
        print('0')

if __name__=="__main__":
    app=QApplication(sys.argv)
    win=ControL()
    win.show()
    desktop=QApplication.desktop()
    winwidth=int(desktop.width()*0.9)
    winheight=int(desktop.height()*0.9)
    win.setGeometry(10,10,winwidth,winheight)
    n=app.exec_()
    sys.exit(n)