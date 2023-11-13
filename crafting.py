import json

with open("assets/recipies.json") as fp:
    recipies = json.loads(fp.read())["recipies"]


class RecipieItem:
    def __init__(self, item, count):
        self.item = item
        self.count = count


class Recipie:
    def __init__(self, result, recipie):
        self.result = result
        self.recipie = recipie


RECIPIES = []

for recipie in recipies:
    rec_items = []
    for item in recipie["recipie"]:
        rec_items.append(RecipieItem(item["item"], item["count"]))

    RECIPIES.append(
        Recipie(
            RecipieItem(recipie["result"], recipie["amount"]),
            rec_items,
        )
    )
