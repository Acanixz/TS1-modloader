import subprocess
import os
import sys
from typing import Optional
import tkinter as tk
from tkinter import messagebox
from datetime import datetime

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
    ui = UI(settings, play_callback=play, modloader=mod_loader)
    ui.run()

# Initialize submodules
os.chdir(os.getcwd())  # Ensure working directory is the script's directory
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
        sys.exit(0)

mod_loader = ModLoader(settings)

# Initializes The Sims 1 in the selected game path
def play():
    game_path = settings.get_game_path()
    if not game_path:
        print("Game path is not set. Please set the game path first.")
        return

    # Check for new (unlocked) mods that will be locked after this session
    current_mod_ids = list(mod_loader.mods.keys())
    new_mods = [mod_id for mod_id in current_mod_ids if not settings.is_mod_locked(mod_id)]
    
    if new_mods:
        # Warn user about new mods being locked
        result = messagebox.askyesno(
            "TS1 ModLoader - New Mods Detected",
            f"You are about to install {len(new_mods)} new mod(s).\n\n"
            "Once you start playing, these mods will be locked and cannot be removed "
            "to prevent save file corruption.\n\n"
            "Do you want to continue?"
        )
        if not result:
            print("User cancelled mod installation.")
            return

    print("Verifying mod installation..")
    if not mod_loader.validate_installation():
        print("Mod validation failed due to conflicts.")
        print("Please resolve the conflicts and try again.")
        return

    print("Applying mods...")
    mod_loader.install_all()

    # Lock currently installed mods (prevents removal after game start)
    current_mod_ids = list(mod_loader.mods.keys())
    settings.lock_mods(current_mod_ids)

    # Update last played timestamp
    timestamp = datetime.now().strftime("%B %d, %Y at %H:%M")
    settings.set_last_played(timestamp)

    print(f"Launching The Sims 1 from: {game_path}")
    subprocess.Popen([os.path.join(game_path, "Sims.exe")])

if __name__ == "__main__":
    main()