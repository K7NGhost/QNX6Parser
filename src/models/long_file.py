from io import BufferedReader
import struct
from models.inode import iNode
from models.long_dir_entry import LongDirEntry
from models.long_name_inode import LongNameiNode


class LongFile():
    def __init__(self, dir_entry: LongDirEntry, inode: iNode, long_inode: LongNameiNode, f_stream: BufferedReader, blocksize, offset):
        self.__dir_entry = dir_entry
        self.__inode = inode
        self.__long_inode = long_inode
        self.__block_size = blocksize
        self.__f_stream = f_stream
        self.__superblock_endoffset = offset
        
        self.file_id = self.__inode.index
        self.filename = self.__long_inode.name
        self.file_data = self.get_data_from_inode(self.__inode)
        
    def get_data_from_inode(self, inode: iNode):
        file_blocks = []
        
        pointers = inode.blockpointer_array
        current_levels = inode.levels
        if current_levels > 0:
            next_pointers = []
            for ptr in pointers:
                if ptr in (0, 0xFFFFFFFF):
                    continue
                block_offset = ptr * self.__block_size + self.__superblock_endoffset
                self.__f_stream.seek(block_offset)
                
                block_data = self.__f_stream.read(self.__block_size)
                
                for i in range(0, self.__block_size, 4):
                    if i + 4 > len(block_data):
                        break
                    p = struct.unpack("<I", block_data[i:i+4])[0]
                    next_pointers.append(p)
            pointers = next_pointers
            current_levels -= 1
        
        for ptr in pointers:
            if ptr in (0, 0xFFFFFFFF):
                continue
            
            block_offset = ptr * self.__block_size + self.__superblock_endoffset
            self.__f_stream.seek(block_offset)
            data_block = self.__f_stream.read(self.__block_size)
            file_blocks.append(data_block)
            
        return file_blocks
        