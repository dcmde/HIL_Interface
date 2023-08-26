import sys, time
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QLineEdit, QComboBox, QVBoxLayout, QHBoxLayout, QWidget, QSizePolicy
from PyQt5.QtCore import Qt, QTimer
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from message_decoder import *

def send_uart(p_value, i_value, d_value):
    # Function to send data over UART
    print(f"Sending data - P: {p_value}, I: {i_value}, D: {d_value}")


class MainWindow(QMainWindow):
    def __init__(self,ser_itf):
        super().__init__()
        self.setWindowTitle('Data Display')
        self.setGeometry(100, 100, 4000, 3500)
        self.window_size = 10

        self.figure1 = plt.figure()
        self.canvas1 = FigureCanvas(self.figure1)

        self.ax1 = self.figure1.add_subplot(221)
        self.ax2 = self.figure1.add_subplot(222)
        self.ax3 = self.figure1.add_subplot(223)
        self.ax4 = self.figure1.add_subplot(224)

        self.p_label = QLabel('P:', self)
        self.i_label = QLabel('I:', self)
        self.d_label = QLabel('D:', self)

        self.p_entry = QLineEdit(self)
        self.i_entry = QLineEdit(self)
        self.d_entry = QLineEdit(self)

        self.p_entry.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        self.i_entry.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        self.d_entry.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)

        self.p_entry.setFixedWidth(200)
        self.i_entry.setFixedWidth(200)
        self.d_entry.setFixedWidth(200)

        # Set default values of 1 to the QLineEdit entries
        self.p_entry.setText('1')
        self.i_entry.setText('1')
        self.d_entry.setText('1')

        self.update_button = QPushButton('Update')
        self.update_button.clicked.connect(self.update_data)

        self.mode_combo = QComboBox()
        self.mode_combo.addItem('Identification')
        self.mode_combo.addItem('PID')
        self.mode_combo.addItem('Reset')

        self.mode_combo.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        self.mode_combo.setFixedWidth(200)

        self.pause_button = QPushButton('Pause')
        self.pause_button.setFixedWidth(200)  # Set fixed width for "Pause" button
        self.pause_button.clicked.connect(self.toggle_pause)

        self.data_layout1 = QVBoxLayout()
        self.data_layout1.addWidget(self.canvas1)

        self.input_layout = QVBoxLayout()
        self.input_layout.addWidget(self.p_label)
        self.input_layout.addWidget(self.p_entry)
        self.input_layout.addWidget(self.i_label)
        self.input_layout.addWidget(self.i_entry)
        self.input_layout.addWidget(self.d_label)
        self.input_layout.addWidget(self.d_entry)
        self.input_layout.addWidget(self.update_button)
        self.input_layout.addWidget(self.mode_combo)
        self.input_layout.addWidget(self.pause_button)

        self.main_layout = QHBoxLayout()
        self.main_layout.addLayout(self.input_layout)
        self.main_layout.addLayout(self.data_layout1)

        self.central_widget = QWidget()
        self.central_widget.setLayout(self.main_layout)
        self.setCentralWidget(self.central_widget)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_display)
        self.timer.start(1)  # Update every 1 ms (1 kHz)

        self.data_index = 0
        self.paused = False

        self.time_plot_len = 40

        self.data_array = np.zeros(self.time_plot_len)
        self.time_array = np.arange(self.time_plot_len)-self.time_plot_len

        self.pres_data_array = np.zeros(self.time_plot_len)
        self.temp_data_array = np.zeros(self.time_plot_len)
        self.pid_speed_data_array = np.zeros(self.time_plot_len)
        self.pid_voltage_data_array = np.zeros(self.time_plot_len)
        self.idle_ang_data_array = np.zeros(self.time_plot_len)
        self.time_array = np.arange(self.time_plot_len)-self.time_plot_len

        self.decoder = message_decoder()

        self.ser_itf = ser_itf

    def toggle_pause(self):
        self.paused = not self.paused
        if self.paused:
            self.pause_button.setText('Resume')
        else:
            self.pause_button.setText('Pause')

    def update_data(self):
        if self.paused:
            return

        # Get P, I, D values from the entry fields
        p_value = float(self.p_entry.text())
        i_value = float(self.i_entry.text())
        d_value = float(self.d_entry.text())

        # Get the selected mode from the combo box
        mode = self.mode_combo.currentText()

        # Send data using the send_uart function
        send_uart(p_value, i_value, d_value)

        # Perform mode-specific actions
        if mode == 'Identification':
            print('Identification mode selected')
        elif mode == 'PID':
            print('PID mode selected')
        elif mode == 'Reset':
            print('Reset mode selected')

    def update_display(self):
        if self.paused:
            return

        data1 = 0

        self.ax1.cla()
        self.ax2.cla()
        self.ax3.cla()
        self.ax4.cla()

        self.ser_itf.flushInput()
        time.sleep(.01)
        byte = self.ser_itf.read(1)
        cpt = 1
        while(byte and cpt):
            
            if(self.decoder.decode(byte)):
                cpt = cpt - 1 
                
                msg_type, msg_data = self.decoder.get_message()

                if msg_type == Header.PRESSURE:

                    self.pres_data_array = np.append(self.pres_data_array, msg_data[2])
                    self.pres_data_array = self.pres_data_array[1:]
                    self.temp_data_array = np.append(self.temp_data_array, msg_data[1]/100)
                    self.temp_data_array = self.temp_data_array[1:]

                    self.ax1.set_title("Pressure")
                    self.ax2.set_title("Temperature")
                    self.ax1.set_ylabel('Pressure [Pa]')
                    self.ax2.set_ylabel('Temperature [C]')

                    self.ax1.plot(self.time_array, self.pres_data_array, 'bo-')
                    self.ax2.plot(self.time_array, self.temp_data_array, 'ro-')

                elif msg_type == Header.PID:

                    self.pid_speed_data_array = np.append(self.pid_speed_data_array, msg_data[1])
                    self.pid_speed_data_array = self.pid_speed_data_array[1:]
                    self.pid_voltage_data_array = np.append(self.pid_voltage_data_array, msg_data[2])
                    self.pid_voltage_data_array = self.pid_voltage_data_array[1:]

                    self.ax3.plot(self.time_array, self.pid_voltage_data_array, 'bo-')
                    self.ax4.plot(self.time_array, self.pid_speed_data_array, 'ro-')

                    self.ax3.set_title("PID : Voltage command")
                    self.ax4.set_title("PID : Speed")
                    self.ax3.set_ylabel('[V]')
                    self.ax4.set_ylabel('[?]]')

                elif msg_type == Header.IDLE:
                    self.idle_ang_data_array = np.append(self.idle_ang_data_array, msg_data[1])
                    self.idle_ang_data_array = self.idle_ang_data_array[1:]

                    self.ax3.plot(self.time_array, self.idle_ang_data_array)

                    self.ax3.set_title("IDLE : Angular pos")
                    self.ax3.set_ylabel('[?]')

                elif msg_type == Header.OPEN:
                    pass
            
            byte = self.ser_itf.read(1)

        plt.tight_layout()
        self.canvas1.draw()



def run(ser_itf):
    app = QApplication(sys.argv)
    window = MainWindow(ser_itf)
    window.show()
    sys.exit(app.exec_())


#if __name__ == '__main__':
import serial

ser = serial.Serial(port='/dev/ttyUSB0',baudrate=460800,timeout=0)
ser.flush()
run(ser)
