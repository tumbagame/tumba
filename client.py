import socket
from game import BlockSet
import netencode
import entity
from vector import Vector
import player
import copy
from chunking import Chunk
import time

class Client:
    def __init__(self, ip="0.0.0.0", port=2828):
        self.ip = ip
        self.port = port
        self.start_time = time.time()
    
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
        except ConnectionRefusedError as e:
            print("Connection Refused")
            return
        will_set = bool(game.to_set)
        if will_set:
            block_set = game.to_set.pop(0)
        else:
            block_set = BlockSet(0, 0, -2)

        if game.to_craft:
            to_craft = game.to_craft.pop(0)
        else:
            to_craft = -1

        if game.attack == -1:
            attack_flag = 255
        else:
            attack_flag = game.attack
            block_set.block = game.inventory_index
            game.attack = -1

        message = (
            netencode.encode_byte(game.player.id) + # 1 byte id
            netencode.encode_string(game.player.name, 8) + # 8 byte username
            netencode.encode_int(game.player.position.x) + # 4 byte x position
            netencode.encode_int(game.player.position.y) + # 4 byte y position
            netencode.encode_byte(will_set) + # 1 byte set flag
            netencode.encode_int(block_set.x) + # 4 byte block x
            netencode.encode_int(block_set.y) + # 4 byte block y
            netencode.encode_short(block_set.block) + # 2 byte block type
            netencode.encode_short(to_craft) + # 2 byte crafting      
            netencode.encode_byte(attack_flag)       
        )

        sock.sendall(message)
        data = sock.recv(2048)
        chunk_data = data[:1024]
        inventory_data = data[1024:1072]
        chunk_position = data[1072:1080]
        entity_data = data[1080:1160]
        player_data = data[1160:1296]
        entity_count = data[1296].to_bytes(1,'little')

        game.entity_count = netencode.decode_byte(entity_count)

        entity_decoder = netencode.PacketDecoder(entity_data)
        new_entities = []
        for i in range(8):
            entity_id = netencode.decode_byte(entity_decoder.pop_data(1))
            entity_type_raw = netencode.decode_byte(entity_decoder.pop_data(1))
            entity_type = entity_type_raw & 0b01111111
            entity_damaged = bool(entity_type_raw & 0b10000000)
            entity_x = netencode.decode_int(entity_decoder.pop_data(4))
            entity_y = netencode.decode_int(entity_decoder.pop_data(4))
            target = Vector(entity_x, entity_y)

            if entity_type == 0:
                continue

            existing_entity = game.find_entity(entity_id)
            if existing_entity is None:
                new_ent = entity.ENTITIES[entity_type].clone().with_id(entity_id).with_position(target).with_target(target)
            else:
                new_ent = existing_entity.with_target(target)

            new_ent.damage_cooldown = 1.0 if entity_damaged else 0.0

            new_entities.append(new_ent)

        game.entities = new_entities
        
        game.player.inventory.load(inventory_data)

        
        # game.onscreen_players = []
        new_players = []
        player_decoder = netencode.PacketDecoder(player_data)
        for i in range(8):
            player_id = netencode.decode_byte(player_decoder.pop_data(1))
            player_name = player_decoder.pop_data(8)
            if not player_name[0]:
                continue
            player_name = player_name.decode()
            player_x = netencode.decode_int(player_decoder.pop_data(4))
            player_y = netencode.decode_int(player_decoder.pop_data(4))

            existing_player = game.find_player(player_id)
            if existing_player is None:
                nplayer = player.Player(player_id,player_name,Vector(player_x, player_y))
                nplayer.target = nplayer.position
            else:
                nplayer = existing_player
                nplayer.target = Vector(player_x, player_y)
            
            new_players.append(nplayer)

        game.onscreen_players = new_players

        chunk_x = netencode.decode_int(chunk_position[0:4])
        chunk_y = netencode.decode_int(chunk_position[4:8])
        new_chunk = Chunk()
        new_chunk.load_bytes(chunk_data)
        new_chunk.load_surface()
        game.client_queue.add_event(lambda: game.world.set_chunk_reference(chunk_x, chunk_y, new_chunk))
        sock.close()
        game.tps = round(1/max(0.001, (time.time() - self.start_time)), 2)
        self.start_time = time.time()
