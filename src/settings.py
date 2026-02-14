import json
import os
import sys
from tkinter import Tk, filedialog, messagebox
from typing import Optional

class Settings:
    # Constructor
    def __init__(self, settings_file: str = "settings.json"):
        self.settings_file = settings_file
        self.game_path: Optional[str] = None
        self.last_played: Optional[str] = None
        self.installation_type: Optional[str] = None  # "steam", "native", or None
        self.load()

    # Load settings from file
    def load(self):
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, "r") as f:
                    data = json.load(f)
                    self.game_path = data.get("game_path")
                    self.last_played = data.get("last_played")
                    self.installation_type = data.get("installation_type")
            except (json.JSONDecodeError, IOError):
                self.game_path = None
                self.last_played = None
                self.installation_type = None
        else:
            self.game_path = None
            self.last_played = None
            self.installation_type = None

    # Save settings to file
    def save(self):
        data = {
            "game_path": self.game_path,
            "last_played": self.last_played,
            "installation_type": self.installation_type
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

    # Validate that Sims.exe exists in the given path
    def validate_game_path(self, path: str) -> bool:
        """Check if Sims.exe exists in the given path."""
        if not path or not os.path.isdir(path):
            return False
        sims_exe = os.path.join(path, "Sims.exe")
        return os.path.isfile(sims_exe)

    # Detect installation type based on path and platform
    def detect_installation_type(self, path: str) -> Optional[str]:
        """Detect if this is a Steam or native installation.
        Returns: 'steam', 'native', or None if unclear.
        """
        # Windows is always native
        if sys.platform == "win32":
            return "native"
        
        # On Linux/macOS, check if path contains Steam indicators
        path_lower = path.lower()
        if "/steam/steamapps/" in path_lower or "/.steam/" in path_lower or "/steam/" in path_lower:
            return "steam"
        
        # If on Linux/macOS and not Steam, unclear - could be Wine/disk installation
        return None

    # Select game path using a folder dialog
    def select_game_path(self) -> bool:
        root = Tk()
        root.withdraw()
        
        while True:
            folder = filedialog.askdirectory(title="Select The Sims 1 Game Folder")
            
            if not folder:
                # User cancelled
                root.destroy()
                return False
            
            # Validate that Sims.exe exists
            if not self.validate_game_path(folder):
                result = messagebox.askretrycancel(
                    "Invalid Game Path",
                    f"The selected folder does not contain Sims.exe:\n{folder}\n \n"
                    "Please select the folder where The Sims 1 is installed.\n \n"
                    "Tip: Look for the folder containing Sims.exe, GameData, and Downloads folders."
                )
                if not result:
                    # User cancelled
                    root.destroy()
                    return False
                # User wants to retry - loop continues
                continue
            
            # Valid path found - detect installation type
            detected_type = self.detect_installation_type(folder)
            
            # If type is unclear (Linux non-Steam), ask user
            if detected_type is None:
                response = messagebox.askyesno(
                    "Installation Type",
                    "Is this a Steam installation of The Sims 1?\n \n"
                    "• Select 'Yes' if you installed via Steam\n"
                    "• Select 'No' if you're using a disk/CD or Wine installation"
                )
                detected_type = "steam" if response else "wine"
            
            # Save valid path and type
            self.game_path = folder
            self.installation_type = detected_type
            self.save()
            root.destroy()
            return True

    # Returns the game path
    def get_game_path(self) -> Optional[str]:
        return self.game_path
    
    # Returns the installation type
    def get_installation_type(self) -> Optional[str]:
        return self.installation_type
    
    # Set installation type manually
    def set_installation_type(self, install_type: str):
        """Set installation type: 'steam', 'native', or 'wine'."""
        self.installation_type = install_type
        self.save()