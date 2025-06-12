# Constants
from io import BufferedReader
from models.partition import Partition
from models.ebr import EBR


MBR_SIGNATURE = b'\x55\xAA'
GPT_SIGNATURE = b'EFI PART'
SUPERBLOCK_SIZE = 0x1000

def parse_extended_partition(f_stream: BufferedReader, e_base: int, current_offset: int) -> list:
    logical_partitions = []

    while True:
        f_stream.seek(current_offset)
        data_entry = f_stream.read(512)
        ebr = EBR(data_entry)

        first_partition = Partition("MBR", ebr.first_entry)
        first_partition.set_start_lba(first_partition.get_start_lba())
        first_type = first_partition.get_partition_type()
        print(f"     The start lba of the partition is now {first_partition.get_start_lba()}")

        if first_type in [0xB1, 0xB2, 0xB3, 0xB4]:  # QNX6 types
            print("     [+] Supported QNX6 Partition Detected in First Entry, Appending...")
            logical_partitions.append(first_partition)
        else:
            print("     [X] Unknown Partition, Skipping First Entry...")

        second_partition = Partition("MBR", ebr.second_entry)
        second_type = second_partition.get_partition_type()

        if second_type in [0xB1, 0xB2, 0xB3, 0xB4]:
            print("     [+] Supported QNX6 Partition Found in Second Entry, Appending...")
            logical_partitions.append(second_partition)
            break
        if second_type in [0x05, 0x0F]:  # points to next EBR
            print("     [+] Found pointer to next EBR...")
            # Next EBR offset is relative to e_base
            next_offset = e_base + second_partition.get_start_lba() * 512
            current_offset = next_offset
        else:
            print("     [i] No more EBRs found.")
            break

    return logical_partitions
        
    logical_partitions.append(first_partition)
        
        
        
        