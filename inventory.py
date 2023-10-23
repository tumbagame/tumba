import blockprop


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

    def block_getter(self, index):
        return lambda: self.slots[index]
