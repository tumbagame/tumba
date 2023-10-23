from generation import Generator
from random import randint
from chunking import Chunk


class World:
    def __init__(self, generate=False):
        self.chunks = {}
        self.generator = Generator(randint(0, 65535))
        self.generate = generate

    def get_chunk(self, chunk_x, chunk_y):
        if (chunk_x, chunk_y) not in self.chunks:
            if self.generate:
                self.chunks[(chunk_x, chunk_y)] = self.generator.generate(
                    chunk_x, chunk_y
                )
            else:
                self.chunks[(chunk_x, chunk_y)] = Chunk()

        return self.chunks[(chunk_x, chunk_y)]

    def collide(self, pos, size):
        chunk_x = int(pos.x / 1024)
        chunk_y = int(pos.y / 1024)

        for x in range(-1, 2):
            for y in range(-1, 2):
                cx = chunk_x + x
                cy = chunk_y + y
                if self.get_chunk(cx, cy).collide(
                    pos.x - cx * 1024, pos.y - cy * 1024, size.x, size.y
                ):
                    return True

        return False

    def get_block(self, block_x, block_y):
        chunk_x = block_x // 32
        chunk_y = block_y // 32
        return self.get_chunk(chunk_x, chunk_y).get_block(block_x % 32, block_y % 32)

    def set_block(self, block_x, block_y, block):
        chunk_x = block_x // 32
        chunk_y = block_y // 32
        self.get_chunk(chunk_x, chunk_y).set_block(block_x % 32, block_y % 32, block)
