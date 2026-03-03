import json

def save_game(player, filename = "savegame.json"):
    """Saves the game to a JSON file"""
    try:
        with open(filename, "w") as f:
            json.dump(player, f, indent = 4)
        print("Game successfully saved.")
    except Exception as e:
        print("Error saving game.")

def load_game(filename = "savegame.json"):
    """Load the game from JSON file as a dict."""
    try:
        with open(filename, "r") as f:
            player = json.load(f)
        print("Game loaded successfully.")
        return player
    except FileNotFoundError:
        print("No saved game found")
        return None
    except Exception as e:
        print("Error loading game.")
        return None
    

