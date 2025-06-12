from datetime import datetime
from io import BufferedReader
import struct
from models.dir_entry import DirEntry
from models.inode import iNode


class File():
    def __init__(self, directory: DirEntry, inode: iNode, f_stream: BufferedReader, blocksize, offset):
        self.__dir_entry = directory
        self.__inode = inode
        self.__block_size = blocksize
        self.__f_stream = f_stream
        self.__superblock_endoffset = offset
        
        self.file_id = self.__inode.index
        self.filename = self.__dir_entry.name
        self.created_time = self.fmt(self.__inode.ctime)
        self.modified_time = self.fmt(self.__inode.mtime)
        self.accessed_time = self.fmt(self.__inode.atime)
        self.file_data = self.get_data_from_inode(self.__inode)
        
        #self.__f_stream.close()
        
    def __repr__(self):
        return (
            f"<File "
            f"id={self.file_id}, "
            f"name='{self.filename}', "
            f"size={len(self.file_data)} bytes, "
            f"created='{self.created_time}', "
            f"modified='{self.modified_time}', "
            f"accessed='{self.accessed_time}'>"
        )
    
    def fmt(self, ts):
            return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")
    
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
                    
            
        
        