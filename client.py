import socket
from game import BlockSet


class Client:
    def __init__(self, ip="127.0.0.1", port=28):
        self.ip = ip
        self.port = port

    def update(self, game):
        player_chunkx = int((game.player.position.x - 512) / 1024)
        player_chunky = int((game.player.position.y - 512) / 1024)
        # for x in range(-1, 2):
        #     for y in range(-1, 2):
        #         game.world.get_chunk(player_chunkx+x, player_chunky+y)

        try:
            for chunk in game.world.chunks:
                if (
                    abs(chunk[0] - player_chunkx) < 4
                    and abs(chunk[1] - player_chunky) < 4
                ):
                    if not game.world.chunks[chunk].surface_loaded:
                        game.world.chunks[chunk].load_surface()
                elif game.world.chunks[chunk].surface_loaded:
                    game.world.chunks[chunk].unload_surface()

            total_loaded = 0
            for chunk in game.world.chunks:
                if game.world.chunks[chunk].surface_loaded:
                    total_loaded += 1
        except RuntimeError:
            pass
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.connect((self.ip, self.port))
        except ConnectionRefusedError:
            print("Connection Refused")
            return
        will_set = 1 if game.to_set else 0
        if will_set:
            block_set = game.to_set.pop(0)
        else:
            block_set = BlockSet(0, 0, -2)

        if game.to_craft:
            to_craft = game.to_Craft.pop(0)
        else:
            to_craft = -1

        message = (
            f"id:{game.player.id},name:{game.player.name},"
            + f"x:{round(game.player.position.x,2)},y:{round(game.player.position.y,2)},"
            + f"set:{will_set},bx:{block_set.x},by:{block_set.y},block:{block_set.block},"
            + f"craft:{to_craft}"
        )

        sock.sendall(message.encode())
        data = sock.recv(2048)

        chunk_data = data[:1024]
        inventory_data = data[1024:1072]
        rest_data = data[1072:].decode()

        game.player.inventory.load(inventory_data)

        game.tps = float(rest_data.split(",")[0])
        chunk_x = int(rest_data.split(",")[1])
        chunk_y = int(rest_data.split(",")[2])
        game.world.get_chunk(chunk_x, chunk_y).load_bytes(chunk_data)
        game.world.get_chunk(chunk_x, chunk_y).load_surface()
        sock.close()
