Flash Game Manager 🎮

A desktop tool built with Python, PyQt5, and pandas to help you organize, manage, and launch your local Flash game collection.
📘 Features

    Game library browser: Displays all detected SWF/Flash files in a sortable table.

    Search and filter: Live search box and dropdown filters to quickly find games by name or metadata.

    Game metadata management: Add/edit notes, tags, playtime, favorites, and custom launch commands.

    Launch directly: Integrate with external SWF players or emulators (e.g. Ruffle, Flashpoint).

    Import/export library: Load or save your collection using CSV or Excel via pandas.

    Cross-platform support: Compatible with Windows, macOS, and Linux (requires Python 3.7+).

⚙️ Requirements

    Python 3.7 or newer

    PyQt5

    pandas

##First Install python if you dont have it.
Install dependencies:

pip install -r requirements.txt

(Standard library modules used: sys, os, time, subprocess, platform, re – no requirements.txt entries needed.)
🚀 Getting Started

    Clone the repository

git clone https://github.com/TheCrks/Flash_Game_Manager.git
cd Flash_Game_Manager

Install dependencies

pip install -r requirements.txt

Launch the application

    python main.py

    Add your game directory via the UI:

        Points the manager to scan for .swf files.

        Customize launch commands (e.g. using Ruffle SWF player or Flashpoint).

    Start playing by double-clicking games within the UI.
    Bring joy back to your Flash library!

🛠 Configuration

    Database: The app saves metadata (notes, tags, play count) in a local CSV/Excel. You can edit or export it easily.

    Custom players: In settings, specify executables and command-line arguments:

        Example: ruffle-player "%f" to launch the currently selected Flash file.

💡 Tips & Compatibility

    You can download my flash game archive from intert arhcive:
    https://archive.org/details/flash_arch
    IF you do copy the files of this repo to where the flash games are (override if asked) and run the interface.
    All thegames from the archive will be included in.
    If you want to add new games to the app follow these steps (may require administrator previlages, run as administrator in that case):
      -Download the game as either .swf or .exe
      -Open the app
      -Go the Add game Menu
      -Select the game you downloaded
      -Add extra info if you want (publisher, categories)
      -Click Add new game
      -Done you can delete the file you downloaded if you want the app wil automaticly copy it to the script directory
      
📚 Related Projects

    Ruffle – Fast, safe, and portable Flash emulator
    Universal Blue

    Flashpoint Archive – Massive Flash game library with a desktop launcher
    GitHub+8flashpointarchive.org+8GitHub+8

🧩 Contributing

Contributions are welcome! Whether it’s refining the UI, improving search/filter tools, extending metadata support, or fixing platform-specific quirks—please open issues or pull requests.
Suggested contributions:

    Save/load additional Flash metadata (e.g. .sol save support via Ruffle).

    Localization, keyboard shortcuts, or enhanced CSV/Excel export options.

    Packaging for macOS (.app) or Linux (AppImage, Snap, Flatpak).
