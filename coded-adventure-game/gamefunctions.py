"""Game Functions Module.

This module has  several functions used in an adventure game.

"""

import pygame

if not pygame.get_init():
    pygame.init()

if not pygame.mixer.get_init():
    try:
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        print("Mixer initialized (inside gamefunctions).")
    except Exception as e:
        print("Mixer failed to initialize inside gamefunctions:", e)

import random
import sys
from wanderingMonster import WanderingMonster

# Ensure mixer is initialized even if game.py didn't initialize it yet
if not pygame.mixer.get_init():
    try:
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        print("gamefunctions: Mixer initialized automatically.")
    except Exception as e:
        print("gamefunctions: FAILED to init mixer:", e)



TILE_SIZE = 32

def load_image(path, fallback_color, size=(32, 32)):
    """
    Attempts to load an image. If it fails, returns a simple colored rectangle.
    Images are scaled to 'size' so they fit exactly in one tile.
    """
    try:
        image = pygame.image.load(path).convert_alpha()
        image = pygame.transform.scale(image, size)  # <-- THE FIX
        return image
    except Exception as e:
        print(f"WARNING: Could not load {path}. Using fallback rectangle. Error: {e}")
        surf = pygame.Surface(size)
        surf.fill(fallback_color)
        return surf


def play_sound(path):
    """Plays a sound and waits for it to finish."""
    try:
        if not pygame.mixer.get_init():
            pygame.mixer.init()

        sound = pygame.mixer.Sound(path)
        channel = sound.play()

        while channel.get_busy():
            pygame.time.delay(10)

    except Exception as e:
        print(f"Failed to play sound {path}: {e}")



TILE = 32
GRID_SIZE = 10
SCREEN_SIZE = TILE * GRID_SIZE
PLAYER_COLOR = (0, 120, 200)  # Blue player square
TOWN_COLOR = (0, 200, 0)      # Green circle for town
MONSTER_COLOR = (200, 0, 0)   # Red circle for monster
GRID_LINE_COLOR = (50, 50, 50)
BG_COLOR = (0, 0, 0)

def open_map(player, map_state):
    """
    Launch a pygame map and return (action, map_state)
    action: "town" or "monster"
    map_state: persistent map dictionary, contains:
        - player_pos: [x,y]
        - town_pos: [x,y]
        - monsters: [ {serializable monster dict}, ... ]
        - player_move_count: int  (to track every-other-move)
        - encounter_idx: index of monster to encounter (set when returning "monster")
    """
    # Ensure pygame subsystems are active
    if not pygame.get_init():
        pygame.init()

    if not pygame.font.get_init():
        pygame.font.init()

    if not pygame.mixer.get_init():
        pygame.mixer.init()

    # Helper to ensure stored values are lists
    def _as_list(v):
        return list(v) if isinstance(v, (tuple, list)) else [0, 0]

    # Load map state (or defaults)
    player_pos = _as_list(map_state.get("player_pos", [0, 0]))
    town_pos = _as_list(map_state.get("town_pos", [0, 0]))
    monsters_data = map_state.get("monsters", None)
    player_move_count = int(map_state.get("player_move_count", 0))

    
    screen = pygame.display.set_mode((SCREEN_SIZE, SCREEN_SIZE))
    # Load images with fallback shapes
    player_img = load_image("images/player.png", PLAYER_COLOR, size=(TILE, TILE))
    monster_img = load_image("images/monster.png", MONSTER_COLOR, size=(TILE, TILE))
    town_img = load_image("images/town.png", TOWN_COLOR, size=(TILE, TILE))
    pygame.display.set_caption("Map")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 18)

    # If no monsters present or list empty, create two monsters
    monsters = []
    if monsters_data:
        # restore objects (but keep them serializable via dicts)
        for md in monsters_data:
            monsters.append(WanderingMonster.from_dict(md, tile_size=TILE_SIZE))

    else:
        # create two monsters not on player or town
        avoid = [tuple(player_pos), tuple(town_pos)]
        m1 = WanderingMonster.random_at(GRID_SIZE, town_pos, avoid_positions=avoid, tile_size=TILE_SIZE)

        monsters.append(m1)
        # Add second monster; ensure not same location
        avoid.append((m1.x, m1.y))
        m2 = WanderingMonster.random_at(GRID_SIZE, town_pos, avoid_positions=avoid, tile_size=TILE_SIZE)
        monsters.append(m2)
    left_town = False
    running = True

    # Helper to serialize monsters into map_state for persistence
    def serialize_monsters(lst):
        return [m.to_dict() for m in lst]

    while running:
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                # persist state before quitting program
                map_state["player_pos"] = player_pos
                map_state["town_pos"] = town_pos
                map_state["monsters"] = serialize_monsters(monsters)
                map_state["player_move_count"] = player_move_count
                pygame.quit()
                sys.exit(0)

            elif event.type == pygame.KEYDOWN:
                new_x, new_y = player_pos[0], player_pos[1]

                if event.key == pygame.K_UP:
                    new_y = max(0, player_pos[1] - 1)
                elif event.key == pygame.K_DOWN:
                    new_y = min(GRID_SIZE - 1, player_pos[1] + 1)
                elif event.key == pygame.K_LEFT:
                    new_x = max(0, player_pos[0] - 1)
                elif event.key == pygame.K_RIGHT:
                    new_x = min(GRID_SIZE - 1, player_pos[0] + 1)
                else:
                    continue

                # Apply movement
                if (new_x, new_y) != (player_pos[0], player_pos[1]):
                    player_pos[0], player_pos[1] = new_x, new_y
                    player_move_count += 1

                    # If player returned to town tile and has left previously, go back to town
                    if [player_pos[0], player_pos[1]] == town_pos:
                        if left_town:
                            map_state["player_pos"] = player_pos
                            map_state["town_pos"] = town_pos
                            map_state["monsters"] = serialize_monsters(monsters)
                            map_state["player_move_count"] = player_move_count
                            pygame.quit()
                            return ("town", map_state)
                    else:
                        left_town = True

                    # After player moves, move monsters every other player move
                    if player_move_count % 2 == 0:
                        # build list of occupied positions to prevent monster stacking (except on player)
                        occupied = [(m.x, m.y) for m in monsters if m.alive]
                        for m in monsters:
                            # pass current occupied positions excluding this monster's own pos
                            others = [p for p in occupied if p != (m.x, m.y)]
                            m.move(GRID_SIZE, town_pos, player_pos, occupied_positions=others)

                        # after moving, see if any monster ended up on the player
                        for idx, m in enumerate(monsters):
                            if m.alive and (m.x, m.y) == tuple(player_pos):
                                # store serialized monsters + encounter index for the caller
                                map_state["player_pos"] = player_pos
                                map_state["town_pos"] = town_pos
                                map_state["monsters"] = serialize_monsters(monsters)
                                map_state["player_move_count"] = player_move_count
                                map_state["encounter_idx"] = idx
                                pygame.quit()
                                return ("monster", map_state)

                    # If player stepped onto a monster tile, trigger encounter
                    for idx, m in enumerate(monsters):
                        if m.alive and (m.x, m.y) == tuple(player_pos):
                            map_state["player_pos"] = player_pos
                            map_state["town_pos"] = town_pos
                            map_state["monsters"] = serialize_monsters(monsters)
                            map_state["player_move_count"] = player_move_count
                            map_state["encounter_idx"] = idx
                            pygame.quit()
                            return ("monster", map_state)

        # DRAWING
        screen.fill(BG_COLOR)

        # Grid
        for gx in range(GRID_SIZE):
            for gy in range(GRID_SIZE):
                rect = pygame.Rect(gx * TILE, gy * TILE, TILE, TILE)
                pygame.draw.rect(screen, GRID_LINE_COLOR, rect, 1)

        # Town
        screen.blit(town_img, (town_pos[0] * TILE, town_pos[1] * TILE))


        for m in monsters:
            if m.alive:
                screen.blit(m.image, (m.x * TILE, m.y * TILE))


        # Player
        screen.blit(player_img, (player_pos[0] * TILE, player_pos[1] * TILE))


        # Debug overlay
        info = f"Pos: {player_pos}  Town: {town_pos}  Monsters: {[ (m.x,m.y,m.name,m.alive) for m in monsters ]}"
        text = font.render(info, True, (255, 255, 255))
        screen.blit(text, (4, SCREEN_SIZE - 18))

        pygame.display.flip()
        clock.tick(60)

    # Fallback
    map_state["player_pos"] = player_pos
    map_state["town_pos"] = town_pos
    map_state["monsters"] = serialize_monsters(monsters)
    map_state["player_move_count"] = player_move_count
    pygame.quit()
    return ("town", map_state)


# Return a WanderingMonster instance (unplaced) for other uses
def new_random_monster():
    """Return a freshly randomized WanderingMonster instance (not placed on map)."""
    return WanderingMonster.random_at(GRID_SIZE, (0, 0))


# Attempts to buy quantityToPurchase items given an item price and starting money.
# Returns how many items were purchased and how much money remains.
def purchase_item(itemPrice,startingMoney,quantityToPurchase=1):
    """
    Attempts to buy quantityToPurchase items given an item price and starting money
    Returns how many items were purchased and how much money remains.

    Parameters:
        itemPrice (int): The price of one item.
        startingMoney(int): The player's current money.
        quantityToPurchase(int, optional): The number of items that the player wants to buy (Defaults to one).

    Returns:
        tuple[int, int]: A tuple containing the number of items purchased
        and the amount of money remaining.        

    """

    max_affordable_items = startingMoney//itemPrice
    num_purchased = min(quantityToPurchase,max_affordable_items)
    leftover_money = startingMoney - (num_purchased * itemPrice)
    return num_purchased, leftover_money




def fight_monster(player, player_hp, player_gold, monster):
    """Fight loop"""
    character_health = player_hp
    monster_health = monster["health"]
    monster_damage = monster["power"]

    print(f"\nA {monster['name']} appears! {monster['description']}")

    if player and check_special_item(player):
        print("The monster is instantly defeated by your special item!")
        player_gold += monster["money"]
        print(f"You found {monster['money']} gold!")
        return character_health, player_gold
            
    while character_health > 0 and monster_health > 0:
        action = input("\n1) Attack  2) Flee: ")

        if action == "1":
            # Play sword swing sound
            play_sound("sounds/sword_slice.wav")


            character_damage = random.randint(25, 75)
        
            if player.get("equippedWeapon"):
                weapon = player["equippedWeapon"]
                character_damage += weapon.get("damage_boost", 0)
                weapon["currentDurability"] -= 1
                print(f"You attack with {weapon['name']}! Durability left: {weapon['currentDurability']}")

                # Remove weapon if durability reaches 0
                if weapon["currentDurability"] <= 0:
                        print(f"Your {weapon['name']} broke!")
                        player["inventory"].remove(weapon)
                        player["equippedWeapon"] = None

                
            monster_health = monster_health - character_damage
            character_health = character_health - monster_damage

            if character_health < 0:
                character_health = 0
            if monster_health < 0:
                monster_health = 0
                
            print(f"You hit the {monster['name']} for {character_damage} damage.")
            print(f"The {monster['name']} hit you for {monster_damage} damage.")

            # Monster attack sound
            play_sound("sounds/monster_roar.wav")


        elif action == "2":
            print("You get too scared. An onlooker to the battle, Sir Robin, joins you momentarily as you bravely run back to town.")
            return character_health, player_gold
        else:
            print("That's not a command, silly.")

    if character_health <= 0 and monster_health > 0:
            print('You lost. Never underestimate an opponent!')
            character_health = 1
            
            
    if monster_health <= 0:
            play_sound("sounds/victory.wav")  # Victory sound
            print(f"You defeated the {monster['name']}!")
            player_gold += monster["money"]
            print(f"You found {monster['money']} gold!")

    return character_health, player_gold



    

def print_welcome(name: str, width: int):
    """
    Prints a centered welcome message for the player.

    Parameters:
        name (str): The player's name.
        width (int): The width to center the message within.

    Returns:
        None
    """
    message = f"Hello, {name}!"
    print(message.center(width))


def print_shop_menu(item1Name: str, item1Price: float, item2Name: str, item2Price: float):
    """Prints a formatted shop menu with two items and their prices.
    
    Parameters:
        item1Name(str): Name of shop's first item.
        item1Price(float): Price of shop's first item.
        item2Name(str): Name of shop's second item.
        item2Price(float): Price of shop's second item.

    Returns:
        None
    """
    print("/" + "-" * 22 + "\\")
    print(f"| {item1Name:<12} {f'${item1Price:.2f}':>8} |")
    print(f"| {item2Name:<12} {f'${item2Price:.2f}':>8} |")
    print("\\" + "-" * 22 + "/")


def get_shop_items():
    """Return a list of purchasable items"""
    return [
        {"name": "Excalibur", "type": "weapon", "price": 100, "damage_boost": 20, "maxDurability": 10, "currentDurability": 10},
        {"name": "Holy Hand Grenade of Antioch", "type": "special", "price": 500, "note": "Blows one of thine enemies to tiny bits, in thy mercy."}
        ]


def visit_shop(player):
    """Lets player buy items from the shop"""
    shop_items = get_shop_items()
    print("\nWelcome to the shop!")
    print(f"You have {player['gold']} gold.")
    print("Available items:")

    for i, item in enumerate(shop_items, 1):
        print(f"{i}) {item['name'].title()} - {item['price']} gold")

    choice = input("Choose an item to buy or press enter to leave:")
    if not choice.isdigit():
        print("You are leaving the shop. Bye-Bye!")
        return player
    choice = int(choice)
    if 1 <= choice <= len(shop_items):
        item = shop_items[choice - 1]
        if player["gold"] >= item["price"]:
            player["gold"] -= item["price"]
            player["inventory"].append(item)
            print(f"You bought {item['name']}! Remaining gold: {player['gold']}")

        else:
            print("You don't have enough gold. Sorry!")
    else:
        print("That's not a choice")
    return player

def equip_weapon(player):
    weapons = [item for item in player["inventory"] if item["type"] == "weapon"]
    if not weapons:
        print("You do not have any weapons.")
        return

    print("\nChoose a weapon to equip:")
    for i, weapon in enumerate(weapons, 1):
        print(f"{i}) {weapon['name']} (Durability: {weapon['currentDurability']}/{weapon['maxDurability']})")
              
    choice = input("Enter number or press Enter to cancel: ")
    if not choice.isdigit():
        print("No weapon equipped.")
        return

    choice = int(choice)
    if 1 <= choice <= len(weapons):
        player["equippedWeapon"] = weapons[choice-1]
        print(f"You equipped {weapons[choice - 1]['name']}!")


def check_special_item(player):
    for item in player["inventory"]:
        if item["type"] == "special":
            use = input(f"You have {item['name']} that can instantly defeat the monster. Use it? (y/n): ").lower()
            if use == "y":
                player["inventory"].remove(item)
                print(f"You used {item['name']}! The monster is defeated instantly.")
                return True
    return False
    
        
        
    
    

    
def test_functions():
    """Runs tests for all functions in this module."""

    #item purchase function tests
    #Default value
    num_purchased, leftover_money = purchase_item(341, 2112)
    print(num_purchased)
    print(leftover_money)

    #Can afford all items
    num_purchased, leftover_money = purchase_item(123, 1000, 3)
    print(num_purchased)
    print(leftover_money)

    #Can't afford all items
    num_purchased, leftover_money = purchase_item(123, 201, 3)
    print(num_purchased)
    print(leftover_money)


    #monster fuction tests
    my_monster = new_random_monster()
    print(my_monster['name'])
    print(my_monster['description'])
    print(my_monster['health'])
    print(my_monster['power'])
    print(my_monster['money'])


    my_monster = new_random_monster()
    print(my_monster['name'])
    print(my_monster['description'])
    print(my_monster['health'])
    print(my_monster['power'])
    print(my_monster['money'])


    my_monster = new_random_monster()
    print(my_monster['name'])
    print(my_monster['description'])
    print(my_monster['health'])
    print(my_monster['power'])
    print(my_monster['money'])


    #print_welcome tests
    print_welcome("Jeff", 20)
    print_welcome("Audrey", 30)
    print_welcome("Logan", 25)


    #print_shop_menu tests
    print_shop_menu("Apple", 3, "Pear", 1.234)
    print_shop_menu("Egg", 0.23, "Bag of Oats", 12.34)
    print_shop_menu("Donut", 2.5, "Orange Juice", 2.0)

if __name__ == "__main__":
    test_functions()
