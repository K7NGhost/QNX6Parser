import os
import struct
import uuid
from datetime import datetime
from collections import defaultdict
import re
import string

from models.dir_entry import DirEntry
from models.file import File
from models.inode import iNode
from models.long_dir_entry import LongDirEntry
from models.long_file import LongFile
from models.long_name_inode import LongNameiNode
from models.partition import Partition
from models.rootnode import RootNode
from models.superblock import SuperBlock
from models.guid_header import GUIDHeader
from models.ebr import EBR
from utils import GPT_SIGNATURE, SUPERBLOCK_SIZE, parse_extended_partition

class QNX6Parser():
    def __init__(self, file_path, output_dir):
        super().__init__()
        self._progress_callback = None
        self.file_path = file_path
        self.f_stream = open(self.file_path, "rb")
        self.superblock = None
        self.root_folder = os.path.join(output_dir, "extracted")
        print(self.root_folder)
        self.extraction_path = ""
    
    def set_progress_callback(self, callback):
        self._progress_callback = callback
    
    def _report(self, step, total):
        if self._progress_callback:
            self._progress_callback(step, total)

    def get_all_partitions(self):
        partitions = []
        self.f_stream.seek(512)
        gpt_sig = self.f_stream.read(8)
        if gpt_sig == GPT_SIGNATURE:
            print("GPT Detected")
            self.f_stream.seek(512)
            header_data = self.f_stream.read(512)
            guid_header = GUIDHeader(header_data)
            num_of_partitions = guid_header.num_of_partitions
            print(f"Number of partitions is {num_of_partitions}")
            self.f_stream.seek(1024)
            for partition_entry in range(0, num_of_partitions):
                entry_bytes = self.f_stream.read(128)
                if entry_bytes.strip(b'\x00'):
                    partition_type = entry_bytes[:16]
                    guid_str = str(uuid.UUID(bytes_le=partition_type)).upper()
                    print(guid_str)

                    if guid_str == "CEF5A9AD-73BC-4601-89F3-CDEEEEE321A1":
                        print("[+] Supported QNX6 Partition Detected, Appending")
                        partitions.append(Partition("GPT", entry_bytes))
                    elif guid_str == "83BD6B9D-7F41-11DC-BE0B-001560B84F0F":
                        print("[X] FreeBSD Boot partition Detected, Skipping...")

                    else:
                        print("[X] Unknown Partition Exiting...")
                else:
                    print("Empty array of bytes")
        else:
            print("MBR Detected")
            self.f_stream.seek(446)
            for partition_entry in range(0, 4):
                entry_bytes = self.f_stream.read(16)
                if entry_bytes.strip(b'\x00'):
                    partition_type = entry_bytes[4]
                    if partition_type == 0x05 or partition_type == 0x0F:
                        print("[+] (EBR) Extended Boot Record Detected, Processing...")
                        partition = Partition("MBR", entry_bytes)
                        print(f"The sector where the ebr starts is {partition.get_start_lba()}")
                        base_lba = partition.get_start_lba()
                        ebr = EBR.from_disk(self.f_stream, base_lba, base_lba)
                        logical_partitions = ebr.get_all_logical_partitions()
                        partitions = partitions + logical_partitions
                    elif partition_type == 0xB1 or partition_type == 0xB2 or partition_type == 0xB3 or partition_type == 0xB4:
                        print("[+] Supported QNX6 Partition Detected, Appending...")
                        partitions.append(Partition("MBR", entry_bytes))
                    elif partition_type == 0x4D or partition_type == 0x4E or partition_type == 0x4F:
                        print("[X] Unsupported QNX4 Partition Detected, Exiting...")
                        return 0
                        
        return partitions

    def parseQNX6(self):
        self.log_error("", 1)
        partitions = self.get_all_partitions()
        for index in range(0, len(partitions)):
            print(partitions[index])
            partition_string = f"partition_{index+1}"
            self.extraction_path = os.path.join(self.root_folder, partition_string)
            self.parse_partition(partitions[index])
            print("=" * 50)
            if self._progress_callback:
                self._report(index+1, len(partitions))
        print("Done!!!")

    def parse_partition(self, partition: Partition):
        start_sector = partition.get_start_lba()
        offset_into_partition = 16
        target_sector = start_sector + offset_into_partition

        superblock_offset = target_sector * 512
        self.f_stream.seek(superblock_offset)
        superblock_data = self.f_stream.read(SUPERBLOCK_SIZE)
        print(f"Byte Offset: {superblock_offset} (0x{superblock_offset:X})")
        self.superblock = SuperBlock(superblock_data)
        print(self.superblock)
        print(f"inodes: {self.superblock.root_node_inode}")
        print(f"bitmap: {self.superblock.root_node_bitmap}")
        print(f"longfilename: {self.superblock.root_node_longfilename}")
        superblock_endoffset = superblock_offset + SUPERBLOCK_SIZE
        
        if self.superblock.magic != 0x68191122:
            print("Not a QNX6 Partition")
            return
        
        try:
            
            second_superblock_offset = superblock_endoffset + (self.superblock.block_size * self.superblock.num_of_blocks)
            self.f_stream.seek(second_superblock_offset)
            second_superblock_data = self.f_stream.read(SUPERBLOCK_SIZE)
            print(f"Byte Offset: {second_superblock_offset} (0x{second_superblock_offset:X})")
            self.second_superblock = SuperBlock(second_superblock_data)
            print(self.second_superblock)
            print(f"inodes: {self.second_superblock.root_node_inode}")
            print(f"bitmap: {self.second_superblock.root_node_bitmap}")
            print(f"longfilename: {self.second_superblock.root_node_longfilename}")
            second_superblock_endoffset = second_superblock_offset + SUPERBLOCK_SIZE
        except Exception as e:
            self.log_error(e)
        
        

        inodes = self.parse_inodes(self.superblock, self.superblock.root_node_inode, superblock_endoffset)        
        print(f"Num of iNodes: {len(inodes)}")
        with open("inodes_output.txt", "w", encoding="utf-8") as f:
            for inode in inodes:
                f.write(repr(inode))
                f.write("\n\n")
                        
        self.inodes_map = self.build_inode_map(inodes)
        
        name_list = []
        print(name_list)
        long_names = self.parse_inodes(self.superblock, self.superblock.root_node_longfilename, superblock_endoffset)
        self.long_names_map = self.build_inode_map(long_names)
        print(f"Num of long iNodes: {len(long_names)}")
        with open("long_inodes_output.txt", "w", encoding="utf-8") as f:
            for long_inode in long_names:
                f.write(repr(f"index={long_inode.index} name={long_inode.name}"))
                f.write("\n")
        
        directories, long_dirs = self.parse_dir_entries(inodes, superblock_endoffset)
        print(f"Num of directories {len(directories)}")
        with open("directories_output.txt", "w", encoding="utf-8") as f:
            for directory in directories:
                f.write(repr(directory))
                f.write("\n")
        with open("long_directories_output.txt", "w", encoding="utf-8") as f:
            for directory in long_dirs:
                f.write(repr(directory))
                f.write("\n")
                
        self.dir_map = self.build_dir_map(directories)
        
        self.files = []
        for dir in directories:
            if dir.inode_number == 0:
                continue
            try:
                inode = self.inodes_map[dir.inode_number]
            except Exception as e:
                self.log_error(e)
                continue
            if inode:
                file = File(dir, inode, self.f_stream, self.superblock.block_size, superblock_endoffset)
                self.files.append(file)
                
        self.long_files = []
        for dir in long_dirs:
            if dir.inode_number == 0:
                continue
            try:
                inode = self.inodes_map[dir.inode_number]
                long_inode = self.long_names_map[dir.long_file_inumber]
            except Exception as e:
                self.log_error(e)
                print("Failed Here")
            if inode and long_inode:
                long_file = LongFile(dir, inode, long_inode, self.f_stream, self.superblock.block_size, superblock_endoffset)
                if len(long_file.filename) < 510:    
                    self.long_files.append(long_file)

        file_map = {file.file_id: file for file in self.files}
        long_file_map = {file.file_id: file for file in self.long_files}
        combined_map = long_file_map | file_map
        combined_list = self.files + self.long_files
        self.construct_files(self.extraction_path, combined_list, combined_map)
        
        deleted_files = self.get_deleted(inodes, superblock_endoffset)
        deleted_map = {file.file_id: file for file in deleted_files}
        deleted_extraction_path = os.path.join(self.extraction_path, "deleted")
        self.construct_files(deleted_extraction_path, deleted_files, deleted_map)
        print(deleted_files)
        
        visited = set()
        full_list = combined_list + deleted_files
        for file in full_list:
            if file.file_id not in visited:
                visited.add(file.file_id)
        
        unknown_inodes = []
        unknown_files = []
        for inode in inodes:
            if inode.index == 1:
                continue
            if inode.index not in visited:
                if inode.status == 3:
                    unknown_file = File(None, inode, self.f_stream, self.superblock.block_size, superblock_endoffset)
                    unknown_files.append(unknown_file)
                    visited.add(unknown_file.file_id)
                    unknown_inodes.append(inode)
        unknown_map = {file.file_id: file for file in unknown_files}
        unknown_extraction_path = os.path.join(self.extraction_path, "unknown")
        self.construct_files(unknown_extraction_path, unknown_files, unknown_map)
        #print(unknown_inodes)
        #print(len(unknown_inodes))
        print("=" * 50)
        for inode in inodes:
            if inode.index not in visited:
                print(inode)
        print(f"total inodes that are useful: {len(inodes)}")
        print(f"total inodes visited: {len(visited)}")
        #print(file_map)
        #self.construct_files(self.long_files, combined_map)
        
        
    def construct_files(self, extraction_path, files: list, file_map):
        paths = {}
        for f in files:
            p = self.build_paths(file_map, f)
            if p:
                paths[f.file_id] = p
        #print(paths.keys())
            
        # Construct all files
        for fid, path in paths.items():
            file = file_map[fid]
            #print(f"path={path}")
            full_path = os.path.join(extraction_path, path)
            # print(f"ID {fid}: {full_path}")
            # print(file)
            # print(full_path)

            try:
                
                if file.file_type == "directory":
                    os.makedirs(full_path, exist_ok=True)
                    continue
            
                os.makedirs(os.path.dirname(full_path), exist_ok=True)

                os.utime(os.path.dirname(full_path), (file.accessed_time, file.modified_time))
                #os.chmod(full_path, 0o666)
                try:
                
                    with open(full_path, 'wb') as out_file:
                        for data in file.file_data:
                            if data in (0, 0xFFFFFFFF):
                                continue
                            #cleaned_data = bytes(c for c in data if chr(c) in string.printable)
                            out_file.write(data)
                except Exception as e:
                    self.log_error(e)
            except Exception as e:
                self.log_error(e)
    
    def get_deleted(self, inodes: list, offset):
        deleted_files = []
        for inode in inodes:
            if inode.status == 2:
                deleted_file = File(None, inode, self.f_stream, self.superblock.block_size, offset)
                deleted_files.append(deleted_file)
        return deleted_files
    
    def build_paths(self, file_map, file_obj):
        parts = [file_obj.filename]
        visited = set()
        
        current = file_map.get(file_obj.parent_id)

        while current:
            if current.file_id in visited:
                print(f"Circular reference detected at ID {current.file_id}")
                raise RuntimeError("Circular reference detected")
            visited.add(current.file_id)
            
            if current != file_obj:
                # print("=" * 50)
                # print(parts)
                # print(f"current filename is {current.filename}")
                # print("=" * 50)
                parts.insert(0, current.filename)
                if current.parent_id not in file_map:
                    break  # We've reached the missing root
            #print(f"current: {current} -  parent ID: {current.parent_id}")
            current = file_map.get(current.parent_id)
            #print(f"current is now {current}")

        return os.path.join(*parts)
    
    def build_inode_map(self, inodes):
        return {i.index: i for i in inodes}
    
    def build_dir_map(self, dir_entries):
        dir_map = {}
        for entry in dir_entries:
            if entry.inode_number not in dir_map:
                dir_map[entry.inode_number] = []
            dir_map[entry.inode_number].append(entry)
        return dir_map
    

    # currently using BFS
    def parse_dir_entries(self, inodes: list, offset):
        
        dir_entries = []
        long_dir_entries = []
        block_size = self.superblock.block_size

        for inode in inodes:
            if (inode.mode & 0xF000) != 0x4000:
                continue
            pointers = inode.blockpointer_array
            current_levels = inode.levels
            if current_levels > 0:
                next_pointers = []
                for ptr in pointers:
                    if ptr in (0, 0xFFFFFFFF):
                        continue
                    block_offset = ptr * block_size + offset
                    self.f_stream.seek(block_offset)
                    
                    block_data = self.f_stream.read(block_size)
                    for i in range (0, block_size, 4):
                        if i + 4 > len(block_data):
                            break
                        p = struct.unpack("<I", block_data[i:i+4])[0]
                        next_pointers.append(p)
                pointers = next_pointers
                current_levels -= 1
            
            #print(pointers)
            for ptr in pointers:
                if ptr in (0, 0xFFFFFFFF):
                    continue
                #print(f"Looking at pointer {ptr}")
                block_offset = ptr * block_size + offset
                self.f_stream.seek(block_offset)
                block_data = self.f_stream.read(block_size)

                for i in range(0, block_size, 32):
                    if i + 32 > len(block_data):
                        break
                    
                    chunk = block_data[i:i+32]
                    if chunk.strip(b"\x00"):
                        entry = DirEntry(chunk)
                        if entry.name == "." or entry.name == "..":
                            continue
                        if entry.name_length > 27:
                            #print("it is a long folder")
                            longfile_entry = LongDirEntry(chunk)
                            longfile_entry.parent_inode = inode.index
                            if longfile_entry.long_file_inumber in self.long_names_map.keys() and longfile_entry.size <= 255:
                                long_dir_entries.append(longfile_entry)
                            continue
                        #print(entry)
                        entry.parent_inode = inode.index
                        dir_entries.append(entry)
                        
        return dir_entries, long_dir_entries
    
    
    def parse_inodes(self, super_block: SuperBlock, root_node: RootNode, offset):
        print("[+] Parsing iNodes...")
        # Key Formula PTR * blocksize + offset (end of superblock)
        # Question: Can pointers be zero?
        inode_size = 128
        block_size = super_block.block_size
        root = root_node

        current_level = root.levels
        pointers = root.pointer_array
        print(pointers)

        while current_level > 0:
            next_pointers = []
            # Skip unused pointers
            for ptr in pointers:
                #print(f"Current Pointer is {ptr}")
                block_offset = ptr * block_size + offset
                self.f_stream.seek(block_offset)

                # Each block contains up to (block_size / 4) 4-byte pointers
                block_data = self.f_stream.read(block_size)

                #print(f"  Read {len(block_data)} bytes from offset {block_offset} (0x{block_offset:X})")
                for i in range(0, block_size, 4):
                    if i + 4 > len(block_data):
                        break
                    p = struct.unpack("<I", block_data[i:i+4])[0]
                    next_pointers.append(p)
            pointers = next_pointers
            current_level -= 1 

        # At Level 0: pointers now point to blocks of actual inodes
        inodes = []
        if root == super_block.root_node_inode: 
            inode_index = 1
        if root == super_block.root_node_longfilename:
            inode_index = 0

        #print(pointers)
        print(f"Amount of pointers in the array are {len(pointers)}")
        counter = 0
        for ptr in pointers:
            block_offset = ptr * block_size + offset
            self.f_stream.seek(block_offset)
            block_data = self.f_stream.read(block_size)

            for i in range(0, block_size, inode_size):
                if i + inode_size > len(block_data):
                    break
                chunk = block_data[i:i+inode_size]
                # Skip empty
                if chunk.strip(b"\x00"):
                    if root == super_block.root_node_longfilename:
                        long_inode = LongNameiNode(block_data[i:i+512])
                        long_inode.index = inode_index
                        #print(f"{long_inode.name}")
                        inodes.append(long_inode)
                        inode_index += 1
                        break
                    elif root == super_block.root_node_inode:
                        inode_obj = iNode(chunk)
                        inode_obj.index = inode_index
                        if inode_obj.status not in (1, 2, 3):
                            inode_index += 1
                            continue
                        inodes.append(inode_obj)
                        inode_index += 1
                    else:
                        inode_index += 1
                else:
                    inode_index += 1
        print(f"Amount of inodes indexed={inode_index} and amount of inodes in superblock={self.superblock.num_of_inodes}")
        print(f"Amount of pointers invalid are {counter}")
        return inodes

    def log_error(self, err_msg: str, status=2):
        if status == 1:
            with open("error.log", "w", encoding="utf-8") as file:
                file.write("")
        if status == 2:
            with open("error.log", "a", encoding="utf-8") as file:
                file.write(f"{err_msg}\n")
    
    def close_stream(self):
        self.f_stream.close()


        