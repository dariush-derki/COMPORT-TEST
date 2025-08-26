import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QPushButton, QTextEdit, QComboBox
)
from PyQt5.QtGui import QPainter, QColor, QBrush, QPen, QRegion, QFont
from PyQt5.QtCore import Qt, QRect, QSize, QIODevice
from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo

class CircularSerialWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.serial = QSerialPort()
        self.serial.readyRead.connect(self.receive_data)
        self.buffer = ""

        self.setWindowTitle("Serial Port Tester – Made by Dariush Derki")
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(QSize(700, 700))
        self.centerWindow()
        self.createCircularMask()
        self.setupUI()
        self.show()

    def centerWindow(self):
        screen_geometry = QApplication.primaryScreen().geometry()
        x = screen_geometry.center().x() - self.width() // 2
        y = screen_geometry.center().y() - self.height() // 2
        self.move(x, y)

    def createCircularMask(self):
        rect = QRect(0, 0, self.width(), self.height())
        circular_region = QRegion(rect, QRegion.Ellipse)
        self.setMask(circular_region)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        pen = QPen(QColor(0, 120, 215))
        pen.setWidth(8)
        painter.setPen(pen)
        painter.setBrush(QBrush(QColor(30, 30, 30)))
        painter.drawEllipse(0, 0, self.width(), self.height())

    def setupUI(self):
        font = QFont("Arial", 11, QFont.Bold)

        layout = QVBoxLayout()
        layout.setContentsMargins(30, 60, 30, 30)
        layout.setSpacing(8)

        # Title labels
        title_label = QLabel("COM PORT TEST - SERIAL PORT")
        title_label.setFont(QFont("Arial", 15, QFont.Bold))
        title_label.setStyleSheet("color: yellow;")
        layout.addWidget(title_label, alignment=Qt.AlignCenter)

        subtitle1 = QLabel("Made by")
        subtitle1.setFont(QFont("Arial", 12, QFont.Bold))
        subtitle1.setStyleSheet("color: red;")
        layout.addWidget(subtitle1, alignment=Qt.AlignCenter)

        subtitle2 = QLabel("DARIUSH DERKI")
        subtitle2.setFont(QFont("Arial", 12, QFont.Bold))
        subtitle2.setStyleSheet("color: red;")
        layout.addWidget(subtitle2, alignment=Qt.AlignCenter)

        # Top buttons
        top_btns = QHBoxLayout()
        self.connect_btn = QPushButton("🔌 Connect")
        self.disconnect_btn = QPushButton("❌ Disconnect")
        for btn in [self.connect_btn, self.disconnect_btn]:
            btn.setFont(font)
            btn.setFixedSize(120, 32)
            btn.setStyleSheet("background-color: #007acc; color: white; border-radius: 10px;")
            top_btns.addWidget(btn)
        layout.addLayout(top_btns)

        # Bottom buttons
        bottom_btns = QHBoxLayout()
        self.clear_btn = QPushButton("🧹 Clear")
        self.exit_btn = QPushButton("🚪 Exit")
        for btn in [self.clear_btn, self.exit_btn]:
            btn.setFont(font)
            btn.setFixedSize(120, 32)
            btn.setStyleSheet("background-color: #007acc; color: white; border-radius: 10px;")
            bottom_btns.addWidget(btn)
        layout.addLayout(bottom_btns)

        # Send button
        self.send_btn = QPushButton("🚀 Send")
        self.send_btn.setFont(font)
        self.send_btn.setFixedSize(120, 32)
        self.send_btn.setStyleSheet("background-color: #00cc66; color: white; border-radius: 10px;")
        layout.addWidget(self.send_btn, alignment=Qt.AlignCenter)

        # Port and baud rate selectors
        combo_layout = QHBoxLayout()
        self.port_combo = QComboBox()
        self.port_combo.setFont(QFont("Arial", 18, QFont.Bold))
        self.port_combo.setFixedWidth(100)
        self.port_combo.setStyleSheet("background-color: #333; color: yellow;")
        for port in QSerialPortInfo.availablePorts():
            self.port_combo.addItem(port.portName())
        combo_layout.addWidget(self.port_combo)

        self.baud_combo = QComboBox()
        self.baud_combo.addItems(["9600", "19200", "38400", "57600", "115200", "250000"])
        self.baud_combo.setFont(QFont("Arial", 18, QFont.Bold))
        self.baud_combo.setFixedWidth(100)
        self.baud_combo.setStyleSheet("background-color: #333; color: yellow;")
        combo_layout.addWidget(self.baud_combo)
        layout.addLayout(combo_layout)

        # Send label and box
        label_send = QLabel("📤 Message to Send:")
        label_send.setFont(font)
        label_send.setStyleSheet("background-color: orange; color: white; border-radius: 10px;")
        label_send.setFixedSize(200, 50)
        layout.addWidget(label_send, alignment=Qt.AlignCenter)

        self.input_text = QTextEdit()
        self.input_text.setFont(font)
        self.input_text.setFixedSize(300, 100)
        self.input_text.setStyleSheet("background-color: #001f4d; color: red;")
        layout.addWidget(self.input_text, alignment=Qt.AlignCenter)

        # Receive label and box
        label_recv = QLabel("📥 Received Messages:")
        label_recv.setFont(font)
        label_recv.setStyleSheet("background-color: orange; color: white; border-radius: 10px;")
        label_recv.setFixedSize(200, 50)
        layout.addWidget(label_recv, alignment=Qt.AlignCenter)

        self.output_text = QTextEdit()
        self.output_text.setFont(font)
        self.output_text.setFixedSize(300, 100)
        self.output_text.setStyleSheet("background-color: #001f4d; color: white;")
        self.output_text.setReadOnly(True)
        layout.addWidget(self.output_text, alignment=Qt.AlignCenter)

        # Connection status
        self.status_label = QLabel("⛔ Not Connected")
        self.status_label.setFont(font)
        self.status_label.setStyleSheet("color: orange;")
        layout.addWidget(self.status_label, alignment=Qt.AlignCenter)

        self.setLayout(layout)

        # Button connections
        self.connect_btn.clicked.connect(self.connect_serial)
        self.disconnect_btn.clicked.connect(self.disconnect_serial)
        self.send_btn.clicked.connect(self.send_data)
        self.clear_btn.clicked.connect(lambda: self.output_text.clear())
        self.exit_btn.clicked.connect(self.close)

    def connect_serial(self):
        port_name = self.port_combo.currentText()
        baud_rate = int(self.baud_combo.currentText())
        self.serial.setPortName(port_name)
        self.serial.setBaudRate(baud_rate)
        if self.serial.open(QIODevice.ReadWrite):
            self.status_label.setText("✅ Connected")
            self.status_label.setStyleSheet("color: lightgreen;")
        else:
            self.status_label.setText("❌ Connection Error")
            self.status_label.setStyleSheet("color: red")

    def disconnect_serial(self):
        if self.serial.isOpen():
            self.serial.close()
        self.status_label.setText("❌ Disconnected")
        self.status_label.setStyleSheet("color: red")

    def send_data(self):
        if self.serial.isOpen():
            data = self.input_text.toPlainText().strip()
            if data:
                self.serial.write(data.encode())
                self.output_text.setTextColor(QColor("green"))
                self.output_text.append(f"🟩 Sent: {data}")
                self.output_text.setTextColor(QColor("white"))

    def receive_data(self):
        data = self.serial.readAll().data().decode(errors='ignore').strip()
        if data:
            self.output_text.setTextColor(QColor("red"))
            self.output_text.append(f"🟥 Received: {data}")
            self.output_text.setTextColor(QColor("white"))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CircularSerialWindow()
    sys.exit(app.exec_())
