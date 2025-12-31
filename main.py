import subprocess
import os
from settings import Settings
from modloader import ModLoader

# Initialize submodules
settings = Settings()
mod_loader = ModLoader(settings)
print(f"Loaded {len(mod_loader.mods)} mods from manifest.")

def main():
    # Load settings
    if not settings.get_game_path():
        print("Game path not set. Please select the game folder.")
        if settings.select_game_path():
            print(f"Game path set to: {settings.get_game_path()}")
        else:
            print("No folder selected. Exiting.")
            return

    print("Starting game")
    play()

# Initializes The Sims 1 in the selected game path
def play():
    settings = Settings()
    game_path = settings.get_game_path()
    if not game_path:
        print("Game path is not set. Please set the game path first.")
        return

    print("Verifying mod installation..")
    if not mod_loader.validate_installation():
        print("Mod installation validation failed due to conflicts.")
        print("Please resolve the conflicts and try again.")
        return

    print("Applying mods...")
    mod_loader.install_all()

    print(f"Launching The Sims 1 from: {game_path}")
    # subprocess.Popen([os.path.join(game_path, "Sims.exe")])

if __name__ == "__main__":
    main()