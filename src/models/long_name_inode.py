import re
import struct

class LongNameiNode():
    def __init__(self, data):
        self.index = None
        # Read first 2 bytes as unsigned short (little endian)
        self.name_length = struct.unpack("<H", data[:2])[0]

        # Sanity check
        # if self.name_length > 510:
        #     raise ValueError(f"Name length too large: {self.name_length}")

        # Read the filename
        name_bytes = data[2:2 + self.name_length]
        self.name = name_bytes.decode("utf-8", errors="replace")
        self.name = self.sanitize_filename(self.name)
    def sanitize_filename(self, name: str) -> str:
        name = name.replace('\x00', '')
        name = re.sub(r'[<>:"/\\|?*\x00-\x1F]', '_', name)       # Windows-invalid chars
        name = re.sub(r'[^\w\s.\-()]', '_', name)                # Replace everything else nonstandard
        name = name.strip("._ ")                                 # Strip trailing dots/spaces (Windows)
        
        if len(name) > 100:
            name = name[:100] + f"_{self.index}"
            
        if not name or re.fullmatch(r'_+', name):
            return f"unnamed_{self.index}"
        
        return name
        
        return name or "unnamed"
        def __repr__(self):
            return f"<LongNameiNode name_length={self.name_length} file_name='{self.name}'>"