from PySide6.QtCore import (QRunnable, Slot)
from worker_signals import WorkerSignals
from qnx6_parser import QNX6Parser

class ParserWorker(QRunnable):
    def __init__(self, file_path, output_dir, parse_second_sb=False):
        super().__init__()
        self.file_path = file_path
        self.output_dir = output_dir
        self.signals = WorkerSignals()
        self.parse_second_sb = parse_second_sb
        
    @Slot()
    def run(self):
        try:
            parser = QNX6Parser(self.file_path, self.output_dir)
            parser.should_parse_second_superblock = self.parse_second_sb
            def report(step, total):
                self.signals.progress.emit(int(step / total * 100))
            parser.set_progress_callback(report)
            parser.parseQNX6()
        except:
            print("Error")
        finally:
            self.signals.finished.emit()
            
            
    