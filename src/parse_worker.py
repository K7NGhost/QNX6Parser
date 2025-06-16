from PySide6.QtCore import (QObject, Signal, Slot)

class ParseWorker(QObject):
    progress = Signal(int)
    finished = Signal()
    error = Signal(str)
    
    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path
        self.__cancel_requested = False
        
    def cancel(self):
        self.__cancel_requested = True
    
    @Slot()
    def run(self):
        try:
            from qnx6_parser import QNX6Parser
            
            parser = QNX6Parser(self.file_path)
            
            # Optionally: Add a hook to report progress during parse
            def report(step, total):
                if self._cancel_requested:
                    raise Exception("Parsing cancelled by user.")
                percent = int((step / total) * 100)
                self.progress.emit(percent)
            
            parser.set_progress_callback(report)
            
            parser.parseQNX6()
            if not self.__cancel_requested:
                self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))
    