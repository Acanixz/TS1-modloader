import subprocess
import os
from typing import Optional
import tkinter as tk
from tkinter import messagebox

from settings import Settings
from modloader import ModLoader
from ui import UI

def display_boot_message():
    root = tk.Tk()
    root.withdraw()
    messagebox.showinfo(
        "TS1 ModLoader - Welcome",
        "Welcome to TS1 ModLoader!\n\nThis tool helps you manage mod files for The Sims 1.\n" \
        "Preventing file conflicts and making mod management easier for newcomers.\n\n" \
        "NOTE: This ModLoader is intended for new installations of The Sims 1. " \
        "If you have existing mods, please backup your game folder before proceeding."
    )

    messagebox.showinfo(
        "TS1 ModLoader - Setup Required",
        "Please select your The Sims 1 installation folder to continue.\n\n" \
        "You can change this later in the settings."
    )
    root.destroy()

def main():
    # Initialize UI
    ui = UI()
    ui.run()

# Initialize submodules
settings = Settings()
# Edge case: First boot without a configured game path
if not settings.get_game_path():
    # Show message and prompt for game folder
    display_boot_message()
    print("Game path not set. Please select the game folder.")

    if settings.select_game_path():
        print(f"Game path set to: {settings.get_game_path()}")
    else:
        messagebox.showerror(
            "TS1 ModLoader - Setup Failed",
            "The Sims 1 installation folder was not selected.\n\n" \
            "The application will now exit."
        )
        print("No folder selected. Exiting.")
        exit(0)

 # Initialize ModLoader
mod_loader = ModLoader(settings)
print(f"Loaded {len(mod_loader.mods)} mods from manifest")

# Initializes The Sims 1 in the selected game path
def play():
    game_path = settings.get_game_path()
    if not game_path:
        print("Game path is not set. Please set the game path first.")
        return

    print("Verifying mod installation..")
    if not mod_loader.validate_installation():
        print("Mod validation failed due to conflicts.")
        print("Please resolve the conflicts and try again.")
        return

    print("Applying mods...")
    mod_loader.install_all()

    print(f"Launching The Sims 1 from: {game_path}")
    # subprocess.Popen([os.path.join(game_path, "Sims.exe")])

if __name__ == "__main__":
    main()