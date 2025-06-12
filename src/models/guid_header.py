import struct
import uuid


class GUIDHeader():
    def __init__(self, binary_data):
        (
        self.signature,
        self.revision_number,
        self.header_size,
        self.crc32,
        self.reserved,
        self.current_LBA,
        self.backup_LBA,
        self.first_usable_LBA,
        self.last_usable_LBA,
        disk_guid_raw,
        self.starting_LBA,
        self.num_of_partitions,
        self.size_of_partition,
        self.crc32_of_partition,
        ) = struct.unpack("<8sIIIIQQQQ16sQIII", binary_data[:92])

        self.disk_GUID = str(uuid.UUID(bytes_le=disk_guid_raw))
        self.reserved2 = binary_data[92:]