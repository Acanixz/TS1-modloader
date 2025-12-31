import subprocess
import os
from settings import Settings
from modloader import ModLoader

def main():
    # Load settings
    settings = Settings()
    if not settings.get_game_path():
        print("Game path not set. Please select the game folder.")
        if settings.select_game_path():
            print(f"Game path set to: {settings.get_game_path()}")
        else:
            print("No folder selected. Exiting.")
            return
    
    # Initialize ModLoader
    mod_loader = ModLoader(settings)
    print(f"Loaded {len(mod_loader.mods)} mods from manifest.")

    print("Starting The Sims 1...")
    mod_loader.install_all()
    # play()

# Initializes The Sims 1 in the selected game path
def play():
    settings = Settings()
    game_path = settings.get_game_path()
    if not game_path:
        print("Game path is not set. Please set the game path first.")
        return

    print(f"Launching The Sims 1 from: {game_path}")
    subprocess.Popen([os.path.join(game_path, "Sims.exe")])

if __name__ == "__main__":
    main()