def encode_int(number):
    return (max(0, min(0xffffffff, int(number) + 0x80000000))).to_bytes(4, 'little')

def decode_int(bytes):
    return int.from_bytes(bytes, 'little') - 0x80000000

def encode_short(number):
    return (max(0, min(0xffff, int(number) + 0x8000))).to_bytes(2, 'little')

def decode_short(bytes):
    return int.from_bytes(bytes, 'little') - 0x8000

def encode_byte(number):
    return int(number).to_bytes(1, 'little')

def decode_byte(value):
    return int.from_bytes(value, 'little')

def encode_string(text, length):
    return text.ljust(length,' ')[:length].encode()

class PacketDecoder:
    def __init__(self, data):
        self.index = 0
        self.data = data
    
    def pop_data(self, num_bytes):
        output = self.data[self.index:self.index + num_bytes]
        self.index += num_bytes
        return output

if __name__ == "__main__":
    print(encode_string("abc", 8))