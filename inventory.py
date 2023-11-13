import blockprop
import crafting


class InventorySlot:
    def __init__(self, item=-1, count=0):
        self.item = item
        self.count = count

    def has_item(self):
        return self.item != -1 and self.count > 0

    def __repr__(self):
        return f"[{self.item}, {self.count}]"


class Inventory:
    def __init__(self):
        self.slots = [InventorySlot() for _ in range(24)]

    def is_possible_recipie(self, recipie):
        for requirement in recipie.recipie:
            is_possible = False

            for item in self.slots:
                if item.item == requirement.item and item.count >= requirement.count:
                    is_possible = True

            if not is_possible:
                return False
        return True

    def get_possible_recipies(self):
        recipies = []
        for r in crafting.RECIPIES:
            if self.is_possible_recipie(r):
                recipies.append(r)
        return recipies
        # return [InventorySlot(1, 1)]

    def find_item(self, item):
        for index, slot in enumerate(self.slots):
            if slot.item == item:
                return index
        return -1

    def add_item(self, item, count=1):
        if item == -1 or count == 0:
            return
        first_open_spot = -1
        for i, slot in enumerate(self.slots):
            if not slot.has_item() and first_open_spot == -1:
                first_open_spot = i

            if slot.item == item:
                slot.count += count
                return

        if first_open_spot != -1:
            self.slots[first_open_spot].item = item
            self.slots[first_open_spot].count = count

    def remove_item(self, index, count=1):
        self.slots[index].count -= count
        if not self.slots[index].has_item():
            self.slots[index] = InventorySlot()

    def block_getter(self, index):
        return lambda: self.slots[index]

    def recipie_getter(self, index):
        def func():
            possible = self.get_possible_recipies()
            if index >= len(possible):
                return InventorySlot()
            return InventorySlot(possible[index].result.item, 1)

        return func

    def craft(self, index):
        recipie = self.get_possible_recipies()[index]
        self.add_item(recipie.result.item, recipie.result.count)
        for requirement in recipie.recipie:
            slot = self.find_item(requirement.item)
            self.remove_item(slot, requirement.count)

    def serialize(self):
        out_data = []
        for slot in self.slots:
            item_count = slot.count if slot.has_item() else 0
            out_data.append(slot.item if slot.has_item() else 255)
            out_data.append(255 if item_count > 255 else item_count)
        return bytes(out_data)

    def load(self, in_bytes):
        for i in range(24):
            item_raw = in_bytes[i * 2 : i * 2 + 2]
            self.slots[i].item = -1 if (item_raw[0] == 255) else item_raw[0]
            self.slots[i].count = item_raw[1]
