import struct
import uuid


class GPTPartition:
    def __init__(self, entry_bytes):
        (
            self.partition_type_guid,
            self.unique_partition_guid,
            self.first_lba,
            self.last_lba,
            self.attributes,
            name_raw
        ) = struct.unpack("<16s16sQQQ72s", entry_bytes)

        self.partition_type_guid = uuid.UUID(bytes_le=self.partition_type_guid)
        self.unique_partition_guid = uuid.UUID(bytes_le=self.unique_partition_guid)
        self.name = name_raw.decode("utf-16le").rstrip('\x00')

    def __repr__(self):
        return f"<GPTPartition name='{self.name}' start_lba={self.first_lba} end_lba={self.last_lba}>"