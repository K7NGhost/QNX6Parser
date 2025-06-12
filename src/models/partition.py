from models.gpt_partition import GPTPartition
from models.mbr_partition import MBRPartition

class Partition:
    def __init__(self, scheme, entry_bytes):
        self.scheme = scheme.upper()
        if self.scheme == "MBR":
            self.partition = MBRPartition(entry_bytes)
        elif self.scheme == "GPT":
            self.partition = GPTPartition(entry_bytes)
        else:
            raise ValueError(f"Unsupported partition scheme: {scheme}")

    def __repr__(self):
        return repr(self.partition)
    
    def get_start_lba(self):
        if self.scheme == "MBR":
            return self.partition.start_lba
        elif self.scheme == "GPT":
            return self.partition.first_lba
        
    def get_partition_type(self):
        if self.scheme == "MBR":
            return self.partition.partition_type
        if self.scheme == "GPT":
            return self.partition.partition_type_guid
        
    def set_start_lba(self, value):
        self.partition.set_start_lba(value)