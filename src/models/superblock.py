import struct
import uuid

from models.rootnode import RootNode


class SuperBlock():
    def __init__(self, data):
        (
        self.magic,
        self.checksum,
        self.serial,
        self.c_time,
        self.a_time,
        self.flags,
        self.version1,
        self.version2,
        volumeid_raw,
        self.block_size,
        self.num_of_inodes,
        self.free_inodes,
        self.num_of_blocks,
        self.free_blocks,
        self.alloc_groups,
        ) = struct.unpack("<IIQIIIHH16sIIIIII", data[:72])

        self.volumeid = str(uuid.UUID(bytes=volumeid_raw))

        self.root_node_inode = RootNode(data[72:152])
        self.root_node_bitmap = RootNode(data[152:232])
        self.root_node_longfilename = RootNode(data[232:312])

    def __repr__(self):
        return (
            f"<SuperBlock magic=0x{self.magic:X}, volumeid={self.volumeid}, "
            f"block_size={self.block_size}, inodes={self.num_of_inodes}, blocks={self.num_of_blocks}>"
        )