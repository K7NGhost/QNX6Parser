from utils import MBR_SIGNATURE

class MBRHeader:
    def __init__(self, binary_data):
        if len(binary_data) < 512:
            raise ValueError("Data too short to be a valid MBR sector")
        
        self.boot_code = binary_data[:446]
        self.partition_table = binary_data[446:510]
        self.partition_type = binary_data[450:451]
        self.signature = binary_data[510:512] # Should be b'\x55\xAA

    def is_valid(self):
        return self.signature == MBR_SIGNATURE