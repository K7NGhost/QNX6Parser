from PySide6.QtCore import (QObject, Signal)

class WorkerSignals(QObject):
    progress = Signal(int)
    finished = Signal()