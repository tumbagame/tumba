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


def run_server(renderer):
    server = Server()
    print("Server Started")
    deltatime = 0
    while renderer.running:
        now = time()
        server.update(deltatime)
        deltatime = time() - now
    server.shutdown()
    print("Server Shut Down")


def run_client(renderer, game):
    sleep(1)
    client = Client()
    print("Client Connected")
    while renderer.running:
        client.update(game)
    sleep(1)
    client.update(game)
    print("Client Disconnected")


def start_server(renderer, game):
    server_thread = threading.Thread(target=run_server, args=[renderer])
    server_thread.start()
    client_thread = threading.Thread(target=run_client, args=[renderer, game])
    client_thread.start()

    renderer.clear_gui()

    game.start()


def resume_game(renderer):
    renderer.clear_gui()


def quit_game(renderer):
    renderer.quit_game()
    renderer.clear_gui()
    sys.exit(0)


def create_crafting_gui(game, renderer):
    slots = []
    for i in range(16):
        slots.append(
            ui.ItemSlot(
                120 + 34 * (i % 8),
                40 + (i // 8) * 34,
                game.player.inventory.recipie_getter(i),
                game.crafting_setter(i),
            )
        )
    return ui.GUI(
        ui.Image("assets/sprites/ui/inventorybg.png", 30, 30),
        ui.Label("Crafting", 40, 40),
        ui.Button("Done", 40, 80, lambda: resume_game(renderer)),
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


def show_settings(renderer):
    renderer.show_gui(
        ui.GUI(
            ui.Image("assets/sprites/ui/inventorybg.png", 30, 30),
            ui.Label("Settings", 40, 40),
            ui.Label("Username", 40, 80),
            ui.TextInput(120, 80),
            ui.Label("Mouse Sensitivity", 40, 100),
            ui.Button("-", 120, 100),
            ui.Button("+", 130, 100),
            ui.Label("10", 145, 100),
            ui.Label("Server Port", 40, 120),
            ui.TextInput(120, 120),
        ).can_escape()
    )


def main():
    pg.init()
    game = Game("player")
    renderer = Renderer()

    title_gui = ui.GUI(
        ui.Image("assets/sprites/titlebg.png", 0, 0),
        ui.Image("assets/sprites/title.png", 20, 20),
        ui.Button("Start Game", 40, 80, lambda: start_server(renderer, game)),
        ui.Button("Join Game", 40, 120),
    )

    menu_gui = ui.GUI(
        ui.Label("Menu", 40, 40),
        ui.Button("Resume", 40, 80, lambda: resume_game(renderer)),
        ui.Button("Settings", 40, 120, lambda: show_settings(renderer)),
        ui.Button("Quit", 40, 160, lambda: quit_game(renderer)),
    )

    inventory_gui = create_inventory_gui(game, renderer)

    renderer.show_gui(title_gui)
    blank_mouse = mouse.Mouse()
    deltatime = 0
    while renderer.running:
        now = time()
        renderer.update(game)
        game_mouse = blank_mouse if renderer.in_gui else renderer.mouse
        game_keys = [] if renderer.in_gui else renderer.keys_down
        game.update(game_keys, game_mouse, deltatime)
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
