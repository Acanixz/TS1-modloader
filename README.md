# TS1-modloader

![TS1-modloader Logo](src/assets/images/icon.png)

The Sims 1 Modloader is a simple GUI application for managing The Sims 1 Custom Content.

## Features

- Easy-to-use graphical interface for installing and managing custom content
- Organize your mods, skins, objects, and other CC in one place
- FAQ for newcomers on TS1 modding
- Compatible with The Sims 1 Legacy Collection

## Installation

1. Download the latest release from the [Releases](https://github.com/Herick/TS1-modloader/releases) page
2. Extract the archive to your preferred location
3. Run `TS1-modloader.exe`

## Usage

1. Launch the application
2. Set your Sims 1 installation directory
3. Add mods using the "Add Mod" button
4. Confirm your mods before starting and press play!

## Supported Content Types

- `.iff` files (objects, skins)
- `.far` archives
- `.bmp` wallpapers and floors
- `.cmx` and `.skn` skin files

## Requirements

- Windows 10 or later
- The Sims 1 (any version)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Repository installation (Prerequisites)

- [Python 3.14](https://www.python.org/downloads/release/python-3140/)
- [Visual Studio Code](https://code.visualstudio.com/download)
- [Python VSCode Extension](https://marketplace.visualstudio.com/items?itemName=ms-python.python)

### Repository installation
1. Open the repository folder in VS Code
2. Press CTRL + Shift + P and Search for ``Python: Create Environment``
3. Select a ``.venv`` environment and then check ``requirements.txt``
4. Wait for the installation to complete

Once python is installed, you'll be able to compile the code through this command:
```
pyinstaller --onefile --name TS1-Modloader --icon=src/assets/images/icon.ico --add-data "src/assets;assets" src/main.pyw
```

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.