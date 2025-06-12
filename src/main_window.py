from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog)
from PySide6.QtCore import Qt
from qnx6_parser import QNX6Parser

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.file_path = None
        self.resize(400,400)
        central_layout = QVBoxLayout(self)
        central_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.central_widget = QWidget(self)
        self.central_widget.setObjectName(u"container")
        
        
        self.input_label = QLabel()
        central_layout.addWidget(self.input_label)
        
        self.input_button = QPushButton()
        self.input_button.setText("Select File")
        self.input_button.setMinimumWidth(150)
        self.input_button.clicked.connect(lambda: self.upload_file())
        central_layout.addWidget(self.input_button)
        
        self.analyze_button = QPushButton()
        self.analyze_button.setText("Parse Image")
        self.analyze_button.setMinimumWidth(150)
        self.analyze_button.clicked.connect(lambda: self.parse_image())
        central_layout.addWidget(self.analyze_button)

    def upload_file(self):
        self.file_path, _ = QFileDialog.getOpenFileName(self, "Select File")
        if self.file_path:
            self.input_label.setText(self.file_path)

    def parse_image(self):
        qnx6_parser = QNX6Parser(self.file_path)
        qnx6_parser.parseQNX6()
        print("Done!!!")
            





