import pygame as pg
import json
import easygui
import sprites

# Internal dev tool to edit the properties for each block

FILE = 'assets/blocks.json'

with open(FILE, 'r') as fp:
    text = fp.read()


def get_default():
    return {
        'name': '',
        'drops': -1,
        'breakWith': 0,
        'mineStrength': 0,
        'damage': 1,
        'collision': True
    }


out_blocks = []
if not text:
    for _ in range((sprites.ATLAS.get_width()//32) * sprites.ATLAS.get_height()//32):
        out_blocks.append(get_default())
    with open(FILE, 'w') as fp:
        fp.write(json.dumps({'blocks': out_blocks}, indent=2))
else:
    out_blocks = json.loads(text)['blocks']

pg.init()
pg.display.set_caption(f'Edit - 0 - {out_blocks[0]["name"]}')
d = pg.display.set_mode((512, 512))

current_block = 0


while True:
    for e in pg.event.get():
        if e.type == pg.QUIT:
            pg.quit()
            quit()

        elif e.type == pg.KEYDOWN:
            if e.key == pg.K_RIGHT:
                current_block += 1
                pg.display.set_caption(
                    f'Edit - {current_block} - {out_blocks[current_block]["name"]}')
            elif e.key == pg.K_LEFT:
                current_block -= 1
                pg.display.set_caption(
                    f'Edit - {current_block} - {out_blocks[current_block]["name"]}')
            elif e.key == pg.K_SPACE:
                '''
                    'name': '',
                    'drops': -1,
                    'breakWith': 0,
                    'mineStrength': 0,
                    'damage': 1,
                    'collision': True
                '''
                prompt = easygui.multenterbox(
                    msg="Edit Block", fields=['Name', 'Drops', 'Breaks With', 'Mine Strength', 'Damage', 'Collision'],
                    values=[
                        out_blocks[current_block]["name"],
                        out_blocks[current_block]["drops"],
                        out_blocks[current_block]["breakWith"],
                        out_blocks[current_block]["mineStrength"],
                        out_blocks[current_block]["damage"],
                        1 if out_blocks[current_block]["collision"] else 0
                    ])
                if prompt is not None:
                    out_blocks[current_block]["name"] = prompt[0]
                    out_blocks[current_block]["drops"] = int(prompt[1])
                    out_blocks[current_block]["breakWith"] = int(prompt[2])
                    out_blocks[current_block]["mineStrength"] = int(prompt[3])
                    out_blocks[current_block]["damage"] = int(prompt[4])
                    out_blocks[current_block]["collision"] = prompt[5] == '1'
                    with open(FILE, 'w') as fp:
                        fp.write(json.dumps({'blocks': out_blocks}, indent=2))
                    pg.display.set_caption(
                        f'Edit - {current_block} - {out_blocks[current_block]["name"]}')

    d.fill((200, 100, 200))

    d.blit(
        pg.transform.scale(sprites.BLOCKS[current_block], (512, 512)), (0, 0)
    )

    pg.display.update()
