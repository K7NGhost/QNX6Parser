from datetime import datetime
import struct


class iNode():
    def __init__(self, data):
        # each inode is created sequentially
        # it is important to keep tabs on it's index
        self.index = None
        (
            self.size,
            self.uid,
            self.gid,
            self.ftime,
            self.mtime,
            self.atime,
            self.ctime,
            self.mode,
            self.ext_mode,
            *self.blockpointer_array,
            self.levels,
            self.status, # 0x1 = directory 0x2 = deleted 0x3 = normal
        ) = struct.unpack("<QIIIIIIHH16IBB", data[:102])

        self.blockpointer_array = list(self.blockpointer_array)
        
    def interpret_mode(self, mode: int) -> str:
        file_type = mode & 0xF000
        if file_type == 0x4000:
            return "Directory"
        elif file_type == 0x8000:
            return "Regular File"
        elif file_type == 0xA000:
            return "Symbolic Link"
        elif file_type == 0x2000:
            return "Character Device"
        elif file_type == 0x6000:
            return "Block Device"
        elif file_type == 0x1000:
            return "FIFO (Named Pipe)"
        elif file_type == 0xC000:
            return "Socket"
        else:
            return "Unknown"

    def __repr__(self):
        status_map = {
            0x1: "Dir Entry",
            0x2: "Deleted",
            0x3: "Normal"
        }

        def fmt(ts):
            return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")

        return (
            f"<iNode>\n"
            f"  iNode_id: {self.index}\n"
            f"  Size: {self.size}\n"
            f"  UID: {self.uid} | GID: {self.gid}\n"
            f"  Times:\n"
            f"    Created:  {fmt(self.ctime)}\n"
            f"    Modified: {fmt(self.mtime)}\n"
            f"    Accessed: {fmt(self.atime)}\n"
            f"    File Time: {fmt(self.ftime)}\n"
            f"  Mode: 0x{self.mode:04X} ({self.interpret_mode(self.mode)})\n"
            f"  Levels: {self.levels}\n"
            f"  Status: {status_map.get(self.status, f'Unknown (0x{self.status:02X})')}\n"
            f"  Block Pointers: {self.blockpointer_array}"
        )