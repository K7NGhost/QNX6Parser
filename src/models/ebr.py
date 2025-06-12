import struct
from models.partition import Partition

class EBR():
    def __init__(self, entry_bytes: bytes, current_lba: int, base_lba: int):
        
        (
            self.unused,
            self.first_entry,
            self.second_entry,
            self.unused_entry1,
            self.unused_entry2,
            self.signature
        ) = struct.unpack("<446s16s16s16s16s2s", entry_bytes)
        
        self.logical_partition = Partition("MBR", self.first_entry)
        self.second_partition = Partition("MBR", self.second_entry)
        
        self.absolute_lba = self.logical_partition.get_start_lba() + current_lba
        print(f"current lba of first entry {self.logical_partition.get_start_lba()} and current lba {current_lba}")
        self.logical_partition.set_start_lba(self.absolute_lba)
        
        self.next_ebr = None
    
    @classmethod
    def from_disk(cls, f_stream, base_lba, current_lba):
        f_stream.seek(current_lba * 512)
        entry_bytes = f_stream.read(512)

        ebr = cls(entry_bytes, current_lba, base_lba)

        next_start = ebr.second_partition.get_start_lba()
        if next_start != 0:
            next_ebr_lba = base_lba + next_start
            ebr.next_ebr = cls.from_disk(f_stream, base_lba, next_ebr_lba)

        return ebr
    
    def get_all_logical_partitions(self):
        partitions = [self.logical_partition]
        if self.next_ebr:
            partitions.extend(self.next_ebr.get_all_logical_partitions())
        return partitions
        