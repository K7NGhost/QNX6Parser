import struct

class MBRPartition:
    def __init__(self, entry_bytes):
        (
            self.boot_indicator,
            self.start_chs,
            self.partition_type,
            self.end_chs,
            self.start_lba,
            self.num_sectors
        ) = struct.unpack("<B3sB3sII", entry_bytes)

    def __repr__(self):
        return f"<MBRPartition type=0x{self.partition_type:02X} start_lba={self.start_lba} sectors={self.num_sectors}>"
    
    def set_start_lba(self, value):
        self.start_lba = value