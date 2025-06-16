from datetime import datetime
from io import BufferedReader
import struct
from models.dir_entry import DirEntry
from models.inode import iNode


class File():
    def __init__(self, directory, inode: iNode, f_stream: BufferedReader, blocksize, offset):
        self.__dir_entry = directory
        self.__inode = inode
        self.__block_size = blocksize
        self.__f_stream = f_stream
        self.__superblock_endoffset = offset
        
        if self.__dir_entry:
            self.parent_id = self.__dir_entry.parent_inode
            self.filename = self.__dir_entry.name
        else:
            self.parent_id = None
            self.filename = "deleted_" + str(self.__inode.index)
        self.file_id = self.__inode.index
        self.file_size = self.__inode.size
        self.created_time = self.__inode.ctime
        self.modified_time = self.__inode.mtime
        self.accessed_time = self.__inode.atime
        self.file_data = self.get_data_from_inode(self.__inode)
        self.mode = self.__inode.mode
        
        if self.is_directory(self.__inode.mode):
            self.file_type = "directory"
        elif self.is_regular_file(self.__inode.mode):
            self.file_type = "file"
        else:
            self.file_type = "Other"
        
        #self.__f_stream.close()
        
    def __repr__(self):
        return (
            f"<File "
            f"id={self.file_id}, "
            f"name='{self.filename}', "
            f"size={len(self.file_data)} bytes, "
            f"created='{self.fmt(self.created_time)}', "
            f"modified='{self.fmt(self.modified_time)}', "
            f"accessed='{self.fmt(self.accessed_time)}'>"
        )
    
    def fmt(self, ts):
            return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")
        
    def is_directory(self, mode):
        return (mode & 0xF000) == 0x4000
    
    def is_regular_file(self, mode):
        return (mode & 0xF000) == 0x8000
    
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
                    
            
        
        