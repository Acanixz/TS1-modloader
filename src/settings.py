import json
import os
from tkinter import Tk, filedialog
from typing import Optional

class Settings:
    # Constructor
    def __init__(self, settings_file: str = "settings.json"):
        self.settings_file = settings_file
        self.game_path: Optional[str] = None
        self.last_played: Optional[str] = None
        self.locked_mods: list[str] = []  # Mods that have been started with and cannot be removed
        self.load()

    # Load settings from file
    def load(self):
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, "r") as f:
                    data = json.load(f)
                    self.game_path = data.get("game_path")
                    self.last_played = data.get("last_played")
                    self.locked_mods = data.get("locked_mods", [])
            except (json.JSONDecodeError, IOError):
                self.game_path = None
                self.last_played = None
                self.locked_mods = []
        else:
            self.game_path = None
            self.last_played = None
            self.locked_mods = []

    # Save settings to file
    def save(self):
        data = {
            "game_path": self.game_path,
            "last_played": self.last_played,
            "locked_mods": self.locked_mods
        }
        with open(self.settings_file, "w") as f:
            json.dump(data, f, indent=4)

    # Update last played timestamp
    def set_last_played(self, timestamp: str):
        self.last_played = timestamp
        self.save()

    # Get last played timestamp
    def get_last_played(self) -> Optional[str]:
        return self.last_played

    # Lock mods that the game has started with (prevents removal)
    def lock_mods(self, mod_ids: list[str]):
        for mod_id in mod_ids:
            if mod_id not in self.locked_mods:
                self.locked_mods.append(mod_id)
        self.save()

    # Check if a mod is locked
    def is_mod_locked(self, mod_id: str) -> bool:
        return mod_id in self.locked_mods

    # Get list of locked mods
    def get_locked_mods(self) -> list[str]:
        return self.locked_mods.copy()

    # Unlock a specific mod (for conflict resolution)
    def unlock_mod(self, mod_id: str):
        if mod_id in self.locked_mods:
            self.locked_mods.remove(mod_id)
            self.save()

    # Select game path using a folder dialog
    def select_game_path(self) -> bool:
        root = Tk()
        root.withdraw()
        folder = filedialog.askdirectory(title="Select The Sims 1 Game Folder")
        root.destroy()

        if folder:
            self.game_path = folder
            self.save()
            return True
        return False

    # Returns the game path
    def get_game_path(self) -> Optional[str]:
        return self.game_path