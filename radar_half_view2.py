from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

import sys, time, math, serial, queue

class SerialThread(QThread):
    rxd_value = pyqtSignal(str)

    def __init__(self, portname, baudrate, timeout):
        QThread.__init__(self)
        self.portname = portname
        self.baudrate = baudrate
        self.timeout = timeout
        self.tx_buffer = queue.Queue()
        self.running = True

        self.serial_port = serial.Serial()
        self.serial_port.port = self.portname
        self.serial_port.baudrate = self.baudrate
        self.serial_port.timeout = self.timeout
        self.serial_port.open()
        time.sleep(0.1)
        if self.serial_port.is_open:
            self.serial_port.flush()
        else:
            self.running = False

    def serial_out(self, buffer):
        self.tx_buffer.put(buffer)

    def run(self):
        print('start')
        while self.running:
            rxd = self.serial_port.read(self.serial_port.in_waiting or 1)
            if rxd:
                #print(rxd)
                if type(rxd) is str:
                    self.rxd_value.emit(rxd)
                else:
                    self.rxd_value.emit("".join([chr(b) for b in rxd]))

            if not self.tx_buffer.empty():
                txd = str(self.tx_buffer.get())
                self.serial_port.write(str(txd).encode('latin-1'))
        if self.serial_port.is_open:
            self.serial_port.close()
        print('bye')

    def stop(self):
        if self.serial_port.is_open:
            self.running = False

    def __str__(self):
        if self.serial_port.is_open:
            return self.serial_port.port
        else:
            return None

class HalfRadarView(QGraphicsView):
    def __init__(self, pointer_pos=0, signal_level=0, scaleViewShow=True, pointerViewShow=True, echoesViewShow=True, informationsViewShow=True):
        super().__init__()

        self.pointer_pos = pointer_pos
        self.signal_level = signal_level
        self.scaleViewShow = scaleViewShow
        self.pointerViewShow = pointerViewShow
        self.echoesViewShow = echoesViewShow
        self.informationsViewShow = informationsViewShow

        self.data = [0] * 181
        self._width = 1000
        self._hight = 600

        self._scene = QGraphicsScene(self)
        self.setScene(self._scene)
        self._scene.setBackgroundBrush(Qt.black)
        self.setSceneRect(0, 0, self._width, self._hight)
        
        self._background_pixmap = QPixmap(self._width, self._hight)
        self._background_pixmap.fill(Qt.transparent)
        self._background_painter = QPainter(self._background_pixmap)
        pen = QPen(QBrush(QColor(0, 255, 0, 255)), 1)
        self._background_painter.setPen(pen)
        text_font = QFont("Times", 16, QFont.Bold)
        self._background_painter.setFont(text_font)

        self._background_painter.drawArc(100, 100, 800, 800, 0 * 16, 180 * 16)
        self._background_painter.drawArc(200, 200, 600, 600, 0 * 16, 180 * 16)
        self._background_painter.drawArc(300, 300, 400, 400, 0 * 16, 180 * 16)
        self._background_painter.drawArc(400, 400, 200, 200, 0 * 16, 180 * 16)
        self._background_painter.drawLine(80, 500, 920, 500)
        self._background_painter.drawLine(500, 80, 500, 500)

        self._background_painter.drawLine(864, 290, 500, 500)
        self._background_painter.drawLine(710, 136, 500, 500)
        self._background_painter.drawLine(290, 136, 500, 500)
        self._background_painter.drawLine(136, 290, 500, 500)

        self._background_painter.drawText(QPoint(488, 75), "90")
        self._background_painter.drawText(QPoint(921, 500), "0")
        self._background_painter.drawText(QPoint(865, 290), "30")
        self._background_painter.drawText(QPoint(711, 136), "60")
        self._background_painter.drawText(QPoint(40, 500), "180")
        self._background_painter.drawText(QPoint(95, 290), "150")
        self._background_painter.drawText(QPoint(250, 136), "120")

        self._background_empty_pixmap = QPixmap(self._width, self._hight)
        self._background_empty_pixmap.fill(Qt.transparent)

        self._pointer_pixmap = QPixmap(self._width, self._hight)
        self._pointer_pixmap.fill(Qt.transparent)

        self._data_pixmap = QPixmap(self._width, self._hight)
        self._data_pixmap.fill(Qt.transparent)
        
        self._drawview = QPixmap(self._width, self._hight)
        self._drawview.fill(Qt.transparent)

    def update(self):
        self.data[self.pointer_pos] = self.signal_level

        x_pos = 400 * math.cos(math.radians(-1*self.__pointer_pos)) + 500
        y_pos = 400 * math.sin(math.radians(-1*self.__pointer_pos)) + 500

        self._pointer_pixmap.fill(Qt.transparent)
        self._pointer_painter = QPainter(self._pointer_pixmap)
        self._pointer_painter.fillRect(0, 0, self._width, self._hight, Qt.transparent)
        pen = QPen(QBrush(QColor(255, 255, 0, 255)), 5)
        self._pointer_painter.setPen(pen)
        self._pointer_painter.drawLine(x_pos, y_pos, 500, 500)
        self._pointer_painter.end()

        self._data_pixmap.fill(Qt.transparent)
        self._data_painter = QPainter(self._data_pixmap)
        self._data_painter.fillRect(0, 0, self._width, self._hight, Qt.transparent)
        pen = QPen(QBrush(QColor(255, 0, 0, 255)), 3)
        self._data_painter.setPen(pen)
        for i in range (0, 180):
            if self.data[i] != 0:
                x_pos = self.data[i] * math.cos(math.radians(-1*i)) + 500
                y_pos = self.data[i] * math.sin(math.radians(-1*i)) + 500
                self._data_painter.drawPoint(x_pos, y_pos)
        self._data_painter.end()

        self._scene.clear()
        self._painter = QPainter(self._drawview)
        self._painter.setRenderHint(QPainter.Antialiasing)
        if self.scaleViewShow == True:
            self._scene.addPixmap(self._background_pixmap)
        else:
            self._scene.addPixmap(self._background_empty_pixmap)
        self._painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
        if self.pointerViewShow == True:
            self._scene.addPixmap(self._pointer_pixmap)
        if self.echoesViewShow == True:
            self._scene.addPixmap(self._data_pixmap)
        self._painter.end()
        self._scene.update()

    @property
    def pointer_pos(self):
        return self.__pointer_pos

    @pointer_pos.setter
    def pointer_pos(self, pointer_pos):
        if (pointer_pos >= 0 and pointer_pos <= 180):
            self.__pointer_pos = pointer_pos
        else:
            raise ValueError("Pointer_pos value error")

    @property
    def signal_level(self):
        return self.__signal_level

    @signal_level.setter
    def signal_level(self, signal_level):
        if (signal_level >=1 and signal_level <= 400):
            self.__signal_level = signal_level
        else:
            self.__signal_level = 0

    @property
    def scaleViewShow(self):
        return self.__scaleViewShow

    @scaleViewShow.setter
    def scaleViewShow(self, scaleViewShow):
        if scaleViewShow == True or scaleViewShow == False:
            self.__scaleViewShow = scaleViewShow
        else:
            raise ValueError("value error")

    @property
    def pointerViewShow(self):
        return self.__pointerViewShow

    @pointerViewShow.setter
    def pointerViewShow(self, pointerViewShow):
        if pointerViewShow == True or pointerViewShow == False:
            self.__pointerViewShow = pointerViewShow
        else:
            raise ValueError("value error")

    @property
    def echoesViewShow(self):
        return self.__echoesViewShow

    @echoesViewShow.setter
    def echoesViewShow(self, echoesViewShow):
        if echoesViewShow == True or echoesViewShow == False:
            self.__echoesViewShow = echoesViewShow
        else:
            raise ValueError("value error")

    @property
    def informationsViewShow(self):
        return self.__informationsViewShow

    @echoesViewShow.setter
    def informationsViewShow(self, informationsViewShow):
        if informationsViewShow == True or informationsViewShow == False:
            self.__informationsViewShow = informationsViewShow
        else:
            raise ValueError("value error")

class MainWindow(QWidget):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.portname = ""
        self.baudrate = ""
        self.rxd_buffer = ""
        self.rxd_command = ""
        self.radar_range = 2

        self.initUI()

    def initUI(self):
        layout = QBoxLayout(QBoxLayout.TopToBottom)
        self.setLayout(layout)

        self.radar = HalfRadarView(pointer_pos=0)
        self.radar.update()
        layout.addWidget(self.radar)

        panel_groupbox = QGroupBox("Panel")
        layout.addWidget(panel_groupbox)

        panel_layout = QBoxLayout(QBoxLayout.LeftToRight)
        panel_groupbox.setLayout(panel_layout)

        portname_layout = QBoxLayout(QBoxLayout.TopToBottom)
        panel_layout.addLayout(portname_layout)
        label = QLabel("Port name :")
        portname_layout.addWidget(label)
        
        self.portname_combobox = QComboBox()
        self.portname_combobox.setFixedWidth(170)
        self.portname_combobox.setStyleSheet('QComboBox {color:darkBlue;}')
        portname_layout.addWidget(self.portname_combobox)
        for i in range(1, 256):
            buffer = "COM" + str(i)
            self.portname_combobox.addItem(buffer)

        baudrate_layout = QBoxLayout(QBoxLayout.TopToBottom)
        panel_layout.addLayout(baudrate_layout)
        label = QLabel("Baudrate :")
        baudrate_layout.addWidget(label)
        
        self.baudrate_combobox = QComboBox()
        self.baudrate_combobox.setFixedWidth(170)
        self.baudrate_combobox.setStyleSheet('QComboBox {color:darkBlue;}')
        baudrate_layout.addWidget(self.baudrate_combobox)
        self.baudrate_combobox.addItem('110')
        self.baudrate_combobox.addItem('300')
        self.baudrate_combobox.addItem('600')
        self.baudrate_combobox.addItem('1200')
        self.baudrate_combobox.addItem('2400')
        self.baudrate_combobox.addItem('4800')
        self.baudrate_combobox.addItem('9600')
        self.baudrate_combobox.addItem('14400')
        self.baudrate_combobox.addItem('19200')
        self.baudrate_combobox.addItem('38400')
        self.baudrate_combobox.addItem('57600')
        self.baudrate_combobox.addItem('115200')
        self.baudrate_combobox.addItem('128000')
        self.baudrate_combobox.setCurrentText('9600')

        connect_layout = QBoxLayout(QBoxLayout.TopToBottom)
        self.connect_button = QPushButton('Connect')
        self.connect_button.setFixedWidth(120)
        self.connect_button.setStyleSheet('QPushButton {background-color:darkGreen; color:white;}')
        self.connect_button.clicked.connect(self.connect_button_clicked)
        connect_layout.addStretch(1)
        connect_layout.addWidget(self.connect_button)
        panel_layout.addLayout(connect_layout)

        self.disconnect_button = QPushButton('Disconnect')
        self.disconnect_button.setFixedWidth(120)
        self.disconnect_button.setStyleSheet('QPushButton {background-color:#330000; color:gray;}')
        self.disconnect_button.setEnabled(False)
        self.disconnect_button.clicked.connect(self.disconnect_button_clicked)
        connect_layout.addWidget(self.disconnect_button)

        gap_layout = QBoxLayout(QBoxLayout.TopToBottom)
        panel_layout.addLayout(gap_layout)
        gap_label = QLabel('')
        gap_label.setFixedWidth(30)
        gap_layout.addWidget(gap_label)

        indicator_layout = QBoxLayout(QBoxLayout.TopToBottom)
        panel_layout.addLayout(indicator_layout)
        indicator_layout.addStretch(1)
        self.scale_checkbox = QCheckBox('Indicator Scale')
        #self.scale_checkbox.setFixedWidth(120)
        self.scale_checkbox.setChecked(True)
        self.scale_checkbox.stateChanged.connect(self.scale_checkbox_statechanged)
        indicator_layout.addWidget(self.scale_checkbox)
        self.pointer_checkbox = QCheckBox('Indicator Pointer')
        self.pointer_checkbox.setChecked(True)
        self.pointer_checkbox.stateChanged.connect(self.pointer_checkbox_stateChanged)
        indicator_layout.addWidget(self.pointer_checkbox)

        information_layout = QBoxLayout(QBoxLayout.TopToBottom)
        panel_layout.addLayout(information_layout)
        information_layout.addStretch(1)
        self.echoes_checkbox = QCheckBox('Echoes')
        #self.echoes_checkbox.setFixedWidth(120)
        self.echoes_checkbox.setChecked(True)
        self.echoes_checkbox.stateChanged.connect(self.echoes_checkbox_stateChanged)
        information_layout.addWidget(self.echoes_checkbox)
        self.informations_checkbox = QCheckBox('Informations')
        self.informations_checkbox.setChecked(True)
        information_layout.addWidget(self.informations_checkbox)

        gap_layout = QBoxLayout(QBoxLayout.TopToBottom)
        panel_layout.addLayout(gap_layout)
        gap_label = QLabel('')
        gap_label.setFixedWidth(30)
        gap_layout.addWidget(gap_label)

        speed_layout = QBoxLayout(QBoxLayout.TopToBottom)
        panel_layout.addLayout(speed_layout)
        speed_layout.addStretch(1)
        #label = QLabel('LOW   |   MEDIUM   |   FAST')
        #label.setAlignment(Qt.AlignCenter)
        #speed_layout.addWidget(label)
        self.range_label = QLabel('Range : 200cm')
        self.range_label.setStyleSheet('QLabel {color:red;}')
        speed_layout.addWidget(self.range_label)
        self.speed_slider = QSlider(Qt.Horizontal)
        self.speed_slider.setMinimum(1)
        self.speed_slider.setMaximum(3)
        self.speed_slider.setValue(2)
        self.speed_slider.setFixedWidth(200)
        self.speed_slider.valueChanged.connect(self.speed_slider_valueChanged)
        speed_layout.addWidget(self.speed_slider)

        panel_layout.addStretch(1)

    def connect_button_clicked(self):
        self.portname_combobox.setEnabled(False)
        self.baudrate_combobox.setEnabled(False)
        self.connect_button.setEnabled(False)
        self.disconnect_button.setEnabled(True)
        self.connect_button.setStyleSheet('QPushButton {background-color:#003300; color:gray;}')
        self.disconnect_button.setStyleSheet('QPushButton {background-color:darkRed; color:white;}')
        self.portname = self.portname_combobox.currentText()
        self.baudrate = self.baudrate_combobox.currentText()

        self.serial_thread = SerialThread(self.portname, self.baudrate, 0.1)
        self.serial_thread.rxd_value.connect(self.receive_serialport_data)
        self.serial_thread.start()
        #print(self.portname)
        #print(self.baudrate)

    def disconnect_button_clicked(self):
        self.portname_combobox.setEnabled(True)
        self.baudrate_combobox.setEnabled(True)
        self.connect_button.setEnabled(True)
        self.disconnect_button.setEnabled(False)
        self.connect_button.setStyleSheet('QPushButton {background-color:darkGreen; color:white;}')
        self.disconnect_button.setStyleSheet('QPushButton {background-color:#330000; color:gray;}')

        self.serial_thread.stop()
        #print('disconnect')

    def receive_serialport_data(self, val):
        self.rxd_buffer += val
        #print("size = {}\ttext = {}".format(len(self.rxd_buffer), self.rxd_buffer))
        head_index = self.rxd_buffer.find('+')
        tail_index = self.rxd_buffer.find('\r\n')
        if head_index != -1 and tail_index != -1:
            if head_index > tail_index:
                self.rxd_buffer = self.rxd_buffer[head_index:]
                #print("---> head > tail <---")
            else:
                self.rxd_command = self.rxd_buffer[head_index:tail_index]
                self.rxd_buffer = self.rxd_buffer[tail_index+2:]
                #print("cmd = {}\nsize = {}\n==============================".format(self.rxd_command, len(self.rxd_command)))
                self.instruction_formats(self.rxd_command)
        else:
            if len(self.rxd_buffer) > 255:
                if head_index != -1:
                    if head_index == 0:
                        self.rxd_buffer = self.rxd_buffer[1:]
                    else:
                        self.rxd_buffer = self.rxd_buffer[head_index:]
                    #print("---> cut head <---")
                else:
                    self.rxd_buffer = ""
                    #print(" ---> clear <---")

    def instruction_formats(self, cmd):
        if str.count(cmd, '=') == 1:
            instruct, data_set = str.split(cmd, '=')
            instruct = str.strip(instruct)
            data_set = str.strip(data_set)

            if instruct == '+res':
                if str.count(data_set, ',') == 1:
                    pos, signal_level = str.split(data_set, ',')
                    pos = int(str.strip(pos))
                    signal_level = int(str.strip(signal_level))

                    # radar_range offset
                    signal_level *= self.radar_range
                    if signal_level > 400:
                        signal_level = 0
                    if signal_level < 0:
                        signal_level = 0
                    # end radar_range offset

                    self.radar.pointer_pos = pos
                    self.radar.signal_level = signal_level
                    self.radar.update()

                    #print(pos)
                    #print(signal_level)
                    #print()

    def pointer_checkbox_stateChanged(self, state):
        if state == Qt.Checked:
            self.radar.pointerViewShow = True
        else:
            self.radar.pointerViewShow = False
        self.radar.update()

    def echoes_checkbox_stateChanged(self, state):
        if state == Qt.Checked:
            self.radar.echoesViewShow = True
        else:
            self.radar.echoesViewShow = False
        self.radar.update()

    def scale_checkbox_statechanged(self, state):
        if state == Qt.Checked:
            self.radar.scaleViewShow = True
        else:
            self.radar.scaleViewShow = False
        self.radar.update()

    def speed_slider_valueChanged(self):
        if self.speed_slider.value() == 1:
            self.range_label.setText('Range : 100cm.' )
            self.radar_range = 4
        elif self.speed_slider.value() == 2:
            self.range_label.setText('Range : 200cm.' )
            self.radar_range = 2
        elif self.speed_slider.value() == 3:
            self.range_label.setText('Range : 400cm.' )
            self.radar_range = 1

if __name__ == "__main__":
    App = QApplication(sys.argv)
    window = MainWindow()
    window.setWindowTitle("Half-RADAR")
    window.show()
    sys.exit(App.exec_())