from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog, 
                               QProgressDialog, QMessageBox)
from PySide6.QtCore import (Qt, QThread, Signal, QObject, QThreadPool)
from qnx6_parser import QNX6Parser
from parser_worker import ParserWorker

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.file_path = None
        self.resize(400,400)
        central_layout = QVBoxLayout(self)
        self.threadpool = QThreadPool()
        thread_count = self.threadpool.maxThreadCount()
        print(f"Multithreading with maximum {thread_count} threads")
        
        upper_area_container = QWidget()
        upper_area_container.setObjectName("container")
        upper_layout = QVBoxLayout(upper_area_container)
        upper_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        central_layout.addWidget(upper_area_container)
        
        self.input_label = QLabel("No File Selected.")
        self.input_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        upper_layout.addWidget(self.input_label)
        
        self.input_button = QPushButton()
        self.input_button.setText("Select File")
        self.input_button.setMinimumWidth(150)
        self.input_button.clicked.connect(lambda: self.upload_file())
        upper_layout.addWidget(self.input_button)
        
        self.output_label = QLabel("No Directory Selected.")
        self.output_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        upper_layout.addWidget(self.output_label)
        
        self.output_button = QPushButton()
        self.output_button.setText("Select Output Destination")
        self.output_button.clicked.connect(lambda: self.select_directory())
        upper_layout.addWidget(self.output_button)
        
        self.analyze_button = QPushButton()
        self.analyze_button.setText("Parse Image")
        self.analyze_button.setMinimumWidth(150)
        self.analyze_button.clicked.connect(lambda: self.parse_image())
        upper_layout.addWidget(self.analyze_button)
        
        self.test_parse_button = QPushButton()
        self.test_parse_button.setText("Test Parse Image")
        self.test_parse_button.setMinimumWidth(150)
        self.test_parse_button.clicked.connect(lambda: self.test_parse_image())
        upper_layout.addWidget(self.test_parse_button)
        
        lower_bar_container = QWidget()
        lower_bar_container.setObjectName("container")
        lower_bar_layout = QVBoxLayout(lower_bar_container)
        lower_bar_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        lower_bar_layout.setObjectName("lower_bar_layout")
        central_layout.addWidget(lower_bar_container)
        
        self.progress_dialog = QProgressDialog("Parsing...", "Cancel", 0, 100)
        self.progress_dialog.setWindowTitle("Parsing QNX6 Filesystem")
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
    
    def select_directory(self):
        self.output_dir = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if self.output_dir:
            self.output_label.setText(f"Selected: {self.output_dir}")
    
    def thread_complete(self):
        print("THREAD COMPLETE!!!")
        QMessageBox.information(self, "FINISHED", "Finished parsing image!")
    
    def test_parse_image(self):
        input_label = r""
        output_label = r""
        
        worker = ParserWorker(input_label, output_label)
        worker.signals.finished.connect(self.thread_complete)
        worker.signals.progress.connect(self.progress_dialog.setValue)
        
        self.threadpool.start(worker)
        

    def parse_image(self):
        if not (self.file_path and self.output_dir):
            QMessageBox.critical(self, "Error", "Select file and destination.")
            return
        
        worker = ParserWorker(self.file_path, self.output_dir)
        worker.signals.finished.connect(self.thread_complete)
        worker.signals.progress.connect(self.progress_dialog.setValue)
        
        self.threadpool.start(worker)


            





