import json
import os
from tkinter import Tk, filedialog
from typing import Optional

class Settings:
    # Constructor
    def __init__(self, settings_file: str = "settings.json"):
        self.settings_file = settings_file
        self.game_path: Optional[str] = None
        self.load()

    # Load settings from file
    def load(self):
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, "r") as f:
                    data = json.load(f)
                    self.game_path = data.get("game_path")
            except (json.JSONDecodeError, IOError):
                self.game_path = None
        else:
            self.game_path = None

    # Save settings to file
    def save(self):
        data = {"game_path": self.game_path}
        with open(self.settings_file, "w") as f:
            json.dump(data, f, indent=4)

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