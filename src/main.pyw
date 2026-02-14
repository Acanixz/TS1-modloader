import subprocess
import os
import sys
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
        "Welcome to TS1 ModLoader!\n \n" \
        "This tool helps you manage mod files for The Sims 1. " \
        "Preventing file conflicts and making mod management easier for new players.\n \n" \
        "NOTE: This ModLoader is intended for ONLY new installations of The Sims 1. " \
        "If you have existing mods, do not continue this installation."
    )

    messagebox.showinfo(
        "TS1 ModLoader - Setup Required",
        "Please select your The Sims 1 installation folder to continue.\n" \
        "You can change this later in the settings.\n \n" \
        "Tip: Copy the path to Sims.exe in your clipboard before pressing OK."
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
            "The Sims 1 installation folder was not selected.\n \n" \
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

    # Validate that Sims.exe still exists before launching
    sims_exe = os.path.join(game_path, "Sims.exe")
    if not os.path.isfile(sims_exe):
        messagebox.showerror(
            "TS1 ModLoader - Game Not Found",
            f"Sims.exe not found in the game folder:\n{game_path}\n \n"
            "Please check your game installation or update the game path in Settings."
        )
        print(f"ERROR: Sims.exe not found at {sims_exe}")
        return

    # Check for new (unlocked) mods that will be locked after this session
    current_mod_ids = list(mod_loader.mods.keys())
    new_mods = [mod_id for mod_id in current_mod_ids if not mod_loader.is_mod_locked(mod_id)]
    
    if new_mods:
        # Warn user about new mods being locked
        result = messagebox.askyesno(
            "TS1 ModLoader - New Mods Detected",
            f"You are about to install {len(new_mods)} new mod(s).\n \n"
            "Once you start playing, these mods will be locked and cannot be removed "
            "to prevent save file corruption.\n \n"
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
    mod_loader.lock_mods(current_mod_ids)

    # Update last played timestamp
    timestamp = datetime.now().strftime("%B %d, %Y at %H:%M")
    settings.set_last_played(timestamp)

    # Launch the game based on platform and installation type
    installation_type = settings.get_installation_type()
    
    # Detect potential Steam installation mismatch
    game_path_lower = game_path.lower()
    is_likely_steam = "/steam/" in game_path_lower or "steamapps" in game_path_lower
    
    # Warn if Wine is selected but path looks like Steam
    if installation_type == "wine" and is_likely_steam:
        result = messagebox.askyesno(
            "TS1 ModLoader - Possible Configuration Issue",
            "Your game path appears to be a Steam installation:\n"
            f"{game_path}\n \n"
            "Wine may not work correctly with Steam installations.\n"
            "Steam games on Linux use Proton and should be launched via Steam.\n \n"
            "Do you want to continue anyway?\n \n"
            "Tip: Change to 'Steam' installation type in Settings for best results.",
            icon="warning"
        )
        if not result:
            print("User cancelled launch due to Steam/Wine mismatch warning.")
            return
    
    print(f"Launching The Sims 1 from: {game_path}")
    print(f"Installation type: {installation_type}")
    
    try:
        if sys.platform == "win32":
            # Windows: Direct launch
            subprocess.Popen([sims_exe], cwd=game_path)
            print("Game launched via direct execution (Windows)")
        
        elif installation_type == "steam":
            # Linux/macOS Steam: Use Steam protocol
            # App ID for The Sims Legacy Collection is 3314060
            subprocess.Popen(["xdg-open", "steam://rungameid/3314060"])
            print("Game launched via Steam protocol")
        
        elif installation_type == "wine":
            # Linux Wine installation: Check if Wine is available
            wine_check = subprocess.run(["which", "wine"], capture_output=True)
            if wine_check.returncode != 0:
                messagebox.showerror(
                    "TS1 ModLoader - Wine Not Found",
                    "Wine is not installed or not in your PATH.\n \n"
                    "Please install Wine to run The Sims 1:\n"
                    "  sudo apt install wine (Ubuntu/Debian)\n"
                    "  sudo dnf install wine (Fedora)\n"
                    "  sudo pacman -S wine (Arch)\n \n"
                    "Or change to Steam installation type in Settings if you have the Steam version."
                )
                print("ERROR: Wine not found")
                return
            
            # Verify Sims.exe is accessible before launching Wine
            if not os.access(sims_exe, os.R_OK):
                messagebox.showerror(
                    "TS1 ModLoader - File Access Error",
                    f"Cannot access Sims.exe:\n{sims_exe}\n \n"
                    "Please check file permissions."
                )
                print("ERROR: Cannot access Sims.exe")
                return
            
            print(f"Launching via Wine: wine '{sims_exe}'")
            process = subprocess.Popen(
                ["wine", sims_exe],
                cwd=game_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Give Wine a moment to start, then check if it's still running
            import time
            time.sleep(1)
            poll_result = process.poll()
            
            if poll_result is not None:
                # Process exited immediately - likely an error
                stderr_output = process.stderr.read().decode('utf-8', errors='ignore') if process.stderr else ""
                messagebox.showwarning(
                    "TS1 ModLoader - Wine Launch Issue",
                    f"Wine exited immediately (exit code: {poll_result}).\n \n"
                    "The game may not have launched successfully.\n \n"
                    "Possible issues:\n"
                    "• Steam installation requires 'Steam' launch type\n"
                    "• Missing Wine dependencies\n"
                    "• Corrupted game files\n \n"
                    "Check the console output for details."
                )
                if stderr_output:
                    print(f"Wine stderr: {stderr_output}")
                print(f"ERROR: Wine process exited with code {poll_result}")
            else:
                print("Game launched via Wine (process running)")
        
        else:
            # Fallback: Try direct execution or show error
            if sys.platform == "darwin":
                # macOS: Try Steam protocol as fallback
                subprocess.Popen(["open", "steam://rungameid/3314060"])
                print("Game launched via Steam protocol (macOS)")
            else:
                messagebox.showerror(
                    "TS1 ModLoader - Unknown Installation Type",
                    f"Unknown installation type: {installation_type}\n \n"
                    "Please update the installation type in Settings."
                )
                print(f"ERROR: Unknown installation type: {installation_type}")
                return
    
    except FileNotFoundError as e:
        messagebox.showerror(
            "TS1 ModLoader - Launch Failed",
            f"Failed to launch the game:\n{str(e)}\n \n"
            "Please check your installation and try again."
        )
        print(f"ERROR: Game launch failed: {e}")
    except Exception as e:
        messagebox.showerror(
            "TS1 ModLoader - Launch Failed",
            f"An unexpected error occurred:\n{str(e)}"
        )
        print(f"ERROR: Unexpected error during launch: {e}")

if __name__ == "__main__":
    main()