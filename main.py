import inventory
from render import Renderer
from client import Client
from server import Server
import sys
import threading
from time import sleep, time
from game import Game
import pygame as pg
import ui
import mouse
import version
import json
import datetime
import glob

def run_server(renderer, filename):

    with open("assets/settings.json", "r") as fp:
        port = json.loads(fp.read())["port"]
    server = Server(port=int(port))
    server.filename = filename
    server.load_from_file()
    print(f"Server Started. Save: {filename}")
    if not server.running:
        renderer.running = False
    deltatime = 0
    while renderer.running:
        now = time()
        try:
            server.update(deltatime)
        except Exception as e:
            time_now = datetime.datetime.now().strftime("%B %d %Y - %I:%M%p")
            exclog = f"SERVER ERROR [{time_now}]: {e}\n"
            with open("assets/serverlog.txt", "a") as fp:
                fp.write(exclog)
        deltatime = time() - now
    server.save_to_file()
    server.shutdown()
    print("Server Shut Down")


def run_client(renderer, game):
    sleep(1)
    with open("assets/settings.json", "r") as fp:
        port = json.loads(fp.read())["port"]
    client = Client(port=port)
    print("Client Connected")
    while renderer.running:
        client.update(game)
    sleep(1)
    client.update(game)
    print("Client Disconnected")

def run_mp_client(renderer, game, ip, port):
    sleep(1)
    client = Client(ip=ip, port=port)
    print("Client Connected")
    while renderer.running:
        client.update(game)
    sleep(1)
    client.update(game)
    print("Client Disconnected")

def start_server(renderer, game, filename):
    if not filename.replace(".tumba","").split("/")[-1].split("\\")[-1]:
        print("Empty save name.")
        return
    server_thread = threading.Thread(target=run_server, args=[renderer,filename])
    server_thread.start()
    client_thread = threading.Thread(target=run_client, args=[renderer, game])
    client_thread.start()

    renderer.clear_gui()

    game.start()

def join_client(renderer, game, username_getter, ip_getter, port_getter):
    with open("assets/settings.json", "r") as fp:
        settings_json = json.loads(fp.read())
    settings_json["username"] = username_getter()
    with open("assets/settings.json", "w") as fp:
        fp.write(json.dumps(settings_json,indent=4))
    game.player.name = settings_json["username"]
    client_thread = threading.Thread(target=run_mp_client, args=[renderer, game, ip_getter(), port_getter()])
    client_thread.start()
    renderer.clear_gui()
    game.start()

def resume_game(renderer):
    renderer.clear_gui()


def quit_game(renderer):
    renderer.clear_gui()
    renderer.quit_game()
    sys.exit(0)


def create_crafting_gui(game, renderer):
    description = ui.Label("", 60, 120)

    slots = []
    for i in range(16):
        slots.append(
            ui.ItemSlot(
                120 + 34 * (i % 8),
                40 + (i // 8) * 34,
                game.player.inventory.recipie_getter(i),
                game.crafting_setter(i),
                description.set_label
            )
        )
    return ui.GUI(
        ui.Image("assets/sprites/ui/inventorybg.png", 30, 30),
        ui.Label("Crafting", 40, 40),
        ui.Button("Done", 40, 80, lambda: resume_game(renderer)),
        description,
        *slots,
    ).can_escape()


def create_inventory_gui(game, renderer):
    slots = []
    for i in range(24):
        slots.append(
            ui.ItemSlot(
                120 + 34 * (i % 8),
                40 + (i // 8) * 34,
                game.player.inventory.block_getter(i),
                game.inventory_index_setter(i),
            )
        )
    return ui.GUI(
        ui.Image("assets/sprites/ui/inventorybg.png", 30, 30),
        ui.Label("Inventory", 40, 40),
        ui.Button("Done", 40, 80, lambda: resume_game(renderer)),
        ui.Button(
            "Crafting",
            40,
            120,
            lambda: renderer.show_gui(create_crafting_gui(game, renderer)),
        ),
        *slots,
    ).can_escape()


def show_join(renderer, game):
    ip_input = ui.TextInput(100,60)
    port_input = ui.TextInput(100, 80)
    username_input = ui.TextInput(100, 100)
    with open("assets/settings.json", "r") as fp:
        settings_json = json.loads(fp.read())

    username_input.set_string(settings_json["username"])

    renderer.show_gui(ui.GUI(
        ui.Image("assets/sprites/titlebg.png", 0, 0),
        ui.Image("assets/sprites/ui/inventorybg.png", 30, 30),
        ui.Label("Join Multiplayer Game", 40, 40),
        
        ui.Label("Server IP", 40, 60),
        ip_input,
        ui.Label("Server Port", 40, 80),
        port_input,
        ui.Label("Username", 40, 100),
        username_input,

        ui.Button("Join", 40, 140, lambda: join_client(renderer, game, username_input.get_string, ip_input.get_string, port_input.get_int)),
        ui.Button("Quit", 80,140, lambda: quit_game(renderer))
    ))

def show_settings(renderer):
    username_text = ui.TextInput(120, 80)
    port_text = ui.TextInput(120, 120)
    sensitity_text = ui.Label("", 145, 100)
    with open("assets/settings.json", "r") as fp:
        settings_json = json.loads(fp.read())

    username_text.set_string(settings_json["username"])
    port_text.set_string(settings_json["port"])
    sensitity_text.set_label(str(settings_json["sensitivity"]))

    def save_settings():
        settings_json["username"] = username_text.get_string()
        settings_json["port"] = port_text.get_int()
        settings_json["sensitivity"] = int(sensitity_text.get_label())
        renderer.set_sensitivity(settings_json["sensitivity"])
        with open("assets/settings.json", "w") as fp:
            fp.write(json.dumps(settings_json,indent=4))

    renderer.show_gui(
        ui.GUI(
            ui.Image("assets/sprites/ui/inventorybg.png", 30, 30),
            ui.Label("Settings", 40, 40),
            ui.Label("Username", 40, 80),
            username_text,
            ui.Label("Mouse Sensitivity", 40, 100),
            ui.Button("-", 120, 100, lambda: sensitity_text.set_label(str(  max(1,int(sensitity_text.get_label()) - 1))  )),
            ui.Button("+", 130, 100, lambda: sensitity_text.set_label(str(  min(20, int(sensitity_text.get_label()) + 1)) )),
            sensitity_text,
            ui.Label("Server Port", 40, 120),
            port_text,
            ui.Button("Save", 40, 140, command=save_settings)
        ).can_escape()
    )

def world_select(renderer, game):
    world_saves = glob.glob("assets/saves/*.tumba")

    world_buttons = []
    button_x = 40
    button_y = 80
    for save in world_saves:
        savetext = save.replace(".tumba","").split("/")[-1].split("\\")[-1]
        btn = ui.Button(savetext, button_x, button_y, (lambda txt: (lambda: start_server(renderer,game,txt) ))(save) )
        x_size = btn.image.get_width()
        button_x += x_size + 4
        if button_x > 200:
            button_x = 40
            button_y += 20
        world_buttons.append(btn)

    world_name = ui.TextInput(40,60)
    renderer.show_gui(
        ui.GUI(
            ui.Image("assets/sprites/titlebg.png", 0, 0),
            ui.Image("assets/sprites/ui/inventorybg.png", 30, 30),
            ui.Label("Select World", 40,40),
            world_name,
            ui.Button("New World", 110,60, lambda: start_server(renderer,game, f"assets/saves/{world_name.get_string()}.tumba")),
            *world_buttons
        )
    )
    # start_server(renderer, game)

def main():
    pg.init()
    with open("assets/settings.json", "r") as fp:
        settings_json = json.loads(fp.read())
    username = settings_json["username"]
    sensitity = settings_json["sensitivity"]
    game = Game(username)
    renderer = Renderer()
    renderer.set_sensitivity(sensitity)


    

    title_gui = ui.GUI(
        ui.Image("assets/sprites/titlebg.png", 0, 0),
        ui.Image("assets/sprites/title.png", 20, 20),
        ui.Button("Start Game", 40, 80, lambda: world_select(renderer,game)),
        ui.Button("Join Game", 40, 120, lambda: show_join(renderer, game)),
    )

    menu_gui = ui.GUI(
        ui.Label("Menu", 80, 40),
        ui.Button("Resume", 80, 80, lambda: resume_game(renderer)),
        ui.Button("Settings", 80, 120, lambda: show_settings(renderer)),
        ui.Button("Quit", 80, 160, lambda: quit_game(renderer)),
    )

    inventory_gui = create_inventory_gui(game, renderer)

    renderer.show_gui(title_gui)
    blank_mouse = mouse.Mouse()
    deltatime = 0
    dtscale = 1
    while renderer.running:
        now = time()
        renderer.update(game, deltatime * dtscale)
        game_mouse = blank_mouse if renderer.in_gui else renderer.mouse
        game_keys = [] if renderer.in_gui else renderer.keys_down
        game.update(game_keys, game_mouse, deltatime * dtscale)
        if game.player.health < 1:
            dtscale *= 0.8
        else:
            dtscale = 1
        if game.in_menu:
            game.in_menu = False
            renderer.show_gui(menu_gui)
        if game.in_inventory:
            game.in_inventory = False
            renderer.show_gui(inventory_gui)

        deltatime = time() - now
    sys.exit(0)


if __name__ == "__main__":
    main()
