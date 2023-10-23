import json
import sprites

# Stores the properties of a block


class Block:
    def __init__(self, prop, sprite):
        self.name = prop['name']
        self.drops = prop['drops']
        self.breaks_with = prop['breakWith']
        self.mine_strength = prop['mineStrength']
        self.damage = prop['damage']
        self.collision = prop['collision']
        self.sprite = sprite


with open('assets/blocks.json', 'r') as fp:
    props = json.loads(fp.read())['blocks']

BLOCKS = []
for block, img in zip(props, sprites.BLOCKS):
    BLOCKS.append(
        Block(
            block,
            img
        )
    )
