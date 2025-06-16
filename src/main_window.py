from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog, 
                               QProgressDialog, QMessageBox)
from PySide6.QtCore import (Qt, QThread, Signal, QObject)
from qnx6_parser import QNX6Parser

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.file_path = None
        self.resize(400,400)
        central_layout = QVBoxLayout(self)
        
        upper_area_container = QWidget()
        upper_area_container.setObjectName("container")
        upper_layout = QVBoxLayout(upper_area_container)
        upper_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        central_layout.addWidget(upper_area_container)
        
        self.input_label = QLabel()
        upper_layout.addWidget(self.input_label)
        
        self.input_button = QPushButton()
        self.input_button.setText("Select File")
        self.input_button.setMinimumWidth(150)
        self.input_button.clicked.connect(lambda: self.upload_file())
        upper_layout.addWidget(self.input_button)
        
        self.analyze_button = QPushButton()
        self.analyze_button.setText("Parse Image")
        self.analyze_button.setMinimumWidth(150)
        self.analyze_button.clicked.connect(lambda: self.parse_image())
        upper_layout.addWidget(self.analyze_button)
        
        lower_bar_container = QWidget()
        lower_bar_container.setObjectName("container")
        lower_bar_layout = QVBoxLayout(lower_bar_container)
        lower_bar_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        lower_bar_layout.setObjectName("lower_bar_layout")
        central_layout.addWidget(lower_bar_container)
        
        self.progress_dialog = QProgressDialog("Parsing...", "Cancel", 0, 100)
        self.progress_dialog.setWindowTitle("Parsing QNX6 Filesystem")
        self.progress_dialog.setAutoClose(True)
        self.progress_dialog.setAutoReset(True)
        self.progress_dialog.setWindowModality(Qt.WindowModality.ApplicationModal)
        #self.progress_dialog.setMinimumWidth(1000)
        self.progress_dialog.setValue(0)
        self.progress_dialog.show()
        lower_bar_layout.addWidget(self.progress_dialog)
        
        # self.setStyleSheet("""
        #                    QWidget#container {
        #                        border: 1px solid red;
        #                    }
        #                    """)
        
    def upload_file(self):
        self.file_path, _ = QFileDialog.getOpenFileName(self, "Select File")
        if self.file_path:
            self.input_label.setText(self.file_path)

    def parse_image(self):
        if self.file_path: 
            qnx6_parser = QNX6Parser(self.file_path)
            qnx6_parser.parseQNX6()
            QMessageBox.information(self, "DONE", "Finished parsing QNX6 fs")
        else:
            QMessageBox.critical(self, "Error", "No file path selected")
            





