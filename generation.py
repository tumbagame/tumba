from opensimplex import OpenSimplex
from chunking import Chunk
import json

NEIGHBORS = [9, 17, 9, 16, 1, 9, 0, 9, 9, 18, 1, 17, 2, 9, 1, 9]


class Ore:
    def __init__(self, block, probability):
        self.block = block
        self.probability = probability


class Region:
    def __init__(self, region, is_default):
        self.is_default = is_default
        self.corner = region["corner"]
        if region["max"] == "":
            self.in_region = lambda y: y >= region["min"]
        elif region["min"] == "":
            self.in_region = lambda y: y <= region["max"]
        else:
            self.in_region = lambda y: (y <= region["max"]) and ((y >= region["min"]))
        self.holes = region["holes"]
        self.ores = []
        for ore in region["ores"]:
            self.ores.append(Ore(ore[0], 1 / ore[1]))

    def get_ore(self, x, y, rand_func):
        for ind, ore in enumerate(self.ores):
            rnd = rand_func(x, y, ind)
            if rnd < ore.probability:
                return ore.block

        return -1


class Biome:
    def __init__(self, biome):
        self.corner = biome["corner"]
        self.structures = biome["structures"]

    def get_structure(self, block_x, rand_func):
        ind = int(rand_func(block_x, 15) * len(self.structures))
        return self.structures[ind]


class Generator:
    def __init__(self, seed=1234):
        self.noise = OpenSimplex(seed)
        with open("assets/terrain.json") as fp:
            properties = json.loads(fp.read())
        self.size = properties["size"]
        self.height = properties["height"]
        self.sky = properties["sky"]
        self.biome_size = properties["biomeSize"]
        self.regions = {}
        self.default_region = properties["default"]
        self.structure_prob = properties["structureProb"]
        for region in properties["regions"]:
            self.regions[region] = Region(
                properties["regions"][region], region == self.default_region
            )

        self.biomes = []
        for biome in properties["biomes"]:
            self.biomes.append(Biome(biome))

    def _random(self, x, y, z=0):
        return self.noise.noise3(x * 999.99, y * 999.99, z * 999.99) * 0.5 + 0.5

    def _get_region(self, block_x, block_y):
        for region in self.regions:
            if self.regions[region].in_region(
                self._hill(block_x) + block_y + self._random(block_x, block_y) * 4
            ):
                return self.regions[region]

        return self.regions[self.default_region]

    def _cave(self, block_x, block_y):
        return self.noise.noise2(block_x * self.size, block_y * self.size)

    def _hill(self, block_x):
        return int(self.noise.noise2(block_x * self.size, 0) * self.height)

    def _biome(self, block_x):
        return self.noise.noise2(block_x * self.biome_size, -1) * 0.5 + 0.5

    def _terrain(self, block_x, block_y, threshold):
        if block_y < self._hill(block_x) and block_y > self.sky:
            return False
        if self._cave(block_x, block_y) < threshold:
            return True

        return False

    def _get_block(self, block_x, block_y):
        region = self._get_region(block_x, block_y)
        cave_threshold = region.holes
        num_neighbors = (
            (self._terrain(block_x, block_y - 1, cave_threshold))
            + (self._terrain(block_x + 1, block_y, cave_threshold) << 1)
            + (self._terrain(block_x, block_y + 1, cave_threshold) << 2)
            + (self._terrain(block_x - 1, block_y, cave_threshold) << 3)
        )

        block_offset = NEIGHBORS[num_neighbors]

        biome_index = int(
            self._biome(block_x + (self._random(block_x, block_y, 10) * 2 - 1) * 8)
            * (len(self.biomes))
        )
        biome = self.biomes[min(biome_index, len(self.biomes) - 1)]
        if self._random(block_x, 9) < self.structure_prob:
            structure = biome.get_structure(block_x, self._random)
            for i in range(len(structure) // 2):
                if block_y - structure[i * 2] == self._hill(block_x) - 1:
                    if self._terrain(
                        block_x, block_y - structure[i * 2] + 1, cave_threshold
                    ):
                        return structure[i * 2 + 1]

        if not self._terrain(block_x, block_y, cave_threshold):
            return -1

        ore = region.get_ore(block_x, block_y, self._random)
        if ore != -1:
            return ore

        if region.is_default:
            return biome.corner + block_offset

        return region.corner + block_offset

    def generate(self, chunk_x, chunk_y):
        chunk = Chunk()
        for x in range(32):
            for y in range(32):
                world_x = chunk_x * 32 + x
                world_y = chunk_y * 32 + y
                chunk.set_block(x, y, self._get_block(world_x, world_y))
        chunk.load_surface()
        return chunk
