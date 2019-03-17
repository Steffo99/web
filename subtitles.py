import random

adj = [
    "Digital",
    "Cold",
    "Virtual",
    "Winter",
    "Snowy",
    "Internet",
    "Earth"
]

noun = [
    "Castle",
    "Fortress",
    "Tower",
    "Headquarters",
    "Room",
    "Place",
    "Base",
    "Building"
]


def generate_title():
    # Adjective + Noun
    chosen_adj = random.sample(adj, 1)[0]
    chosen_noun = random.sample(noun, 1)[0]
    return f"'s {chosen_adj} {chosen_noun}"
