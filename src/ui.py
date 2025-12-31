import os
import sys
import tkinter as tk
from tkinter import ttk
from settings import Settings
from tkinter import messagebox

# The Sims 1 Color Palettes
PRIMARY_COLOR = "#395577"  # Background primary
SECONDARY_COLOR = "#2B4059"  # Background secondary / Button background
TEXT_PRIMARY_COLOR = "#FDE68A"  # Text primary
TEXT_SECONDARY_COLOR = "#FFFFFF"  # Text secondary

# Font settings
FONT_FAMILY = "Montserrat"
FALLBACK_FONT_FAMILY = "Segoe UI"

class UI:
    def __init__(self, settings : Settings, play_callback=None):
        self.settings = settings
        self.play_callback = play_callback
        self.primary_color = PRIMARY_COLOR
        self.secondary_color = SECONDARY_COLOR
        self.text_primary_color = TEXT_PRIMARY_COLOR
        self.text_secondary_color = TEXT_SECONDARY_COLOR
        self.font_family = FONT_FAMILY
        self.fallback_font_family = FALLBACK_FONT_FAMILY

        # Load window
        self.root = tk.Tk()
        self.root.title("TS1 ModLoader")
        self.root.configure(bg=self.primary_color)
        # Slightly wider window to accommodate scrollbar without clipping text
        self.root.geometry("900x600")
        self.root.resizable(False, False)

        # Assets directory for images
        self.assets_dir = os.path.join(os.path.dirname(__file__), "assets", "images")
        
        # Create main layout
        self.create_sidebar()
        self.create_content_area()
        
        # Show initial page
        self.show_page("Play")

    def _load_image(self, filename, max_width, max_height):
        """Load and downscale an image to fit within max bounds."""
        path = os.path.join(self.assets_dir, filename)
        try:
            img = tk.PhotoImage(file=path)
        except tk.TclError:
            return None

        width, height = img.width(), img.height()
        scale = max(
            (width + max_width - 1) // max_width,
            (height + max_height - 1) // max_height,
            1,
        )
        if scale > 1:
            img = img.subsample(scale)
        return img
    
    def create_sidebar(self):
        """Create the left sidebar with navigation buttons"""
        self.sidebar = tk.Frame(self.root, bg=self.secondary_color, width=200)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar.pack_propagate(False)
        
        # Sidebar buttons
        self.menu_buttons = {}
        menu_items = ["Play", "Mods", "Settings", "Frequent Questions", "About"]
        
        for item in menu_items:
            btn = tk.Button(
                self.sidebar,
                text=item,
                bg=self.secondary_color,
                fg=self.text_secondary_color,
                activebackground=self.primary_color,
                activeforeground=self.text_primary_color,
                font=(self.font_family, 11, "bold"),
                bd=0,
                pady=15,
                cursor="hand2",
                command=lambda page=item: self.show_page(page)
            )
            btn.pack(fill=tk.X, padx=10, pady=5)
            self.menu_buttons[item] = btn
    
    def create_content_area(self):
        """Create the main content area on the right"""
        self.content_frame = tk.Frame(self.root, bg=self.primary_color)
        self.content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Dictionary to store different pages
        self.pages = {}
        
        # Create all pages
        self.create_play_page()
        self.create_mods_page()
        self.create_settings_page()
        self.create_faq_page()
        self.create_about_page()
    
    def create_play_page(self):
        """Create the Play page"""
        page = tk.Frame(self.content_frame, bg=self.primary_color)
        
        title = tk.Label(
            page,
            text="Play The Sims 1",
            font=(self.font_family, 20, "bold"),
            bg=self.primary_color,
            fg=self.text_primary_color
        )
        title.pack(pady=(50, 30))
        
        play_button = tk.Button(
            page,
            text="Launch Game",
            font=(self.font_family, 14, "bold"),
            bg=self.secondary_color,
            fg=self.text_primary_color,
            activebackground=self.primary_color,
            activeforeground=self.text_primary_color,
            bd=0,
            padx=40,
            pady=15,
            cursor="hand2",
            command=self.launch_game
        )
        play_button.pack(pady=20)
        
        self.pages["Play"] = page
    
    def create_mods_page(self):
        """Create the Mods page"""
        page = tk.Frame(self.content_frame, bg=self.primary_color)
        
        title = tk.Label(
            page,
            text="Mod Manager",
            font=(self.font_family, 20, "bold"),
            bg=self.primary_color,
            fg=self.text_primary_color
        )
        title.pack(pady=(30, 20))
        
        # Placeholder for mod list
        label = tk.Label(
            page,
            text="Mod management coming soon...",
            font=(self.font_family, 12),
            bg=self.primary_color,
            fg=self.text_secondary_color
        )
        label.pack(pady=20)
        
        self.pages["Mods"] = page
    
    def create_settings_page(self):
        """Create the Settings page"""
        page = tk.Frame(self.content_frame, bg=self.primary_color)
        
        title = tk.Label(
            page,
            text="Settings",
            font=(self.font_family, 20, "bold"),
            bg=self.primary_color,
            fg=self.text_primary_color
        )
        title.pack(pady=(30, 20))
        
        # Game Path section
        game_path_label = tk.Label(
            page,
            text="Game Path:",
            font=(self.font_family, 12, "bold"),
            bg=self.primary_color,
            fg=self.text_primary_color
        )
        game_path_label.pack(pady=(20, 10), padx=20, anchor=tk.W)
        
        # Frame for game path display and button
        path_frame = tk.Frame(page, bg=self.primary_color)
        path_frame.pack(pady=(0, 20), padx=20, anchor=tk.W, fill=tk.X)
        
        # Game path display
        self.game_path_var = tk.StringVar(value=self.settings.get_game_path() or "No path selected")
        path_display = tk.Label(
            path_frame,
            textvariable=self.game_path_var,
            font=(self.font_family, 11),
            bg=self.secondary_color,
            fg=self.text_secondary_color,
            padx=15,
            pady=10,
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        path_display.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        # Browse button
        browse_button = tk.Button(
            page,
            text="Browse",
            font=(self.font_family, 11, "bold"),
            bg=self.secondary_color,
            fg=self.text_primary_color,
            activebackground=self.primary_color,
            activeforeground=self.text_primary_color,
            bd=0,
            padx=20,
            pady=10,
            cursor="hand2",
            command=self.select_game_path
        )
        browse_button.pack(pady=(0, 20), padx=20, anchor=tk.W)
        
        self.pages["Settings"] = page
    
    def create_faq_page(self):
        """Create the Frequent Questions page"""
        page = tk.Frame(self.content_frame, bg=self.primary_color)
        
        title = tk.Label(
            page,
            text="Frequent Questions",
            font=(self.font_family, 20, "bold"),
            bg=self.primary_color,
            fg=self.text_primary_color
        )
        title.pack(pady=(30, 10))

        # Scrollable FAQ container
        scroll_container = tk.Frame(page, bg=self.primary_color)
        scroll_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 20))

        faq_canvas = tk.Canvas(
            scroll_container,
            bg=self.primary_color,
            highlightthickness=0
        )
        faq_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(
            scroll_container,
            orient=tk.VERTICAL,
            command=faq_canvas.yview
        )
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        faq_canvas.configure(yscrollcommand=scrollbar.set)

        faq_content = tk.Frame(faq_canvas, bg=self.primary_color)
        window_id = faq_canvas.create_window((0, 0), window=faq_content, anchor="nw")

        def _resize_scroll_region(event):
            faq_canvas.configure(scrollregion=faq_canvas.bbox("all"))

        def _match_canvas_width(event):
            faq_canvas.itemconfigure(window_id, width=event.width)

        def _on_mousewheel(event):
            # Enable mouse wheel scrolling while cursor is anywhere over the FAQ container
            faq_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        faq_content.bind("<Configure>", _resize_scroll_region)
        faq_canvas.bind("<Configure>", _match_canvas_width)

        scroll_container.bind(
            "<Enter>",
            lambda _: faq_canvas.bind_all("<MouseWheel>", _on_mousewheel)
        )
        scroll_container.bind(
            "<Leave>",
            lambda _: faq_canvas.unbind_all("<MouseWheel>")
        )

        faqs = [
            (
                "1. How do I install mods?",
                "You can add mods by adding a new entry manually in the Mods page.\nMods cannot be automatically downloaded yet."
            ),
            (
                "2. What is the difference between Downloads and Overrides?",
                "Downloads are custom contents like objects, skins, and more which adds new items to the game.\n\n" \
                "Overrides replace existing objects or files in the game, changing the appearance or behavior of not only objects, but also the game itself (e.g., custom patches)."
            ),
            (
                "3. What are Maxis Overrides?",
                "Similar to Overrides, Maxis Overrides are objects that replace objects originally created by Maxis, meaning they don't have custom content IDs.\n\n" \
                "A side effect of this is that these objects will display as duplicate item conflicts if viewed on other Sims 1 tools."
            ),
            (
                "4. How do I uninstall mods?",
                "You can remove mods from the Mods page by selecting the mod and clicking the 'Uninstall' button.\n\n" \
                "However, ensure that you backup your game folder before uninstalling mods, as missing objects and skins may cause issues. Including corrupted save files."
            ),
            (
                "5. Where can I find more mods?",
                "There are many modding communities and websites where you can find additional mods for The Sims 1. Here are some of them:\n\n" \
                "- Mod The Sims (modthesims.info)\n" \
                "- The Sims Resource (thesimsresource.com)\n" \
                "- Sims 1 Mods by Corylea(corylea.com/Sims1ModsByCorylea.html)\n" \
                "- The Secret Society of Woobsha (woobsha.com)\n" \
                "- SimLogical (simlogical.com)\n\n" \
                "Remember to always check the mod compatibility and installation instructions provided by the mod creators."
                "\nNote: Always ensure that the mods are installed through the ModLoader to avoid conflicts and issues."
            ),
        ]

        for question, answer in faqs:
            tk.Label(
                faq_content,
                text=question,
                font=(self.font_family, 12, "bold"),
                bg=self.primary_color,
                fg=self.text_primary_color
            ).pack(pady=(20, 5), padx=20, anchor=tk.W)

            tk.Label(
                faq_content,
                text=answer,
                font=(self.font_family, 10),
                bg=self.primary_color,
                fg=self.text_secondary_color,
                wraplength=520,
                justify=tk.LEFT
            ).pack(pady=(0, 15), padx=40, anchor=tk.W)
        
        self.pages["Frequent Questions"] = page
    
    def create_about_page(self):
        """Create the About page"""
        page = tk.Frame(self.content_frame, bg=self.primary_color)
        title = tk.Label(
            page,
            text="About TS1 ModLoader",
            font=(self.font_family, 20, "bold"),
            bg=self.primary_color,
            fg=self.text_primary_color
        )
        title.pack(pady=(30, 20))
        
        info_label = tk.Label(
            page,
            text="The Sims 1 ModLoader\nVersion 1.0",
            font=(self.font_family, 12),
            bg=self.primary_color,
            fg=self.text_secondary_color,
            justify=tk.CENTER
        )
        info_label.pack(pady=(0, 15))

        self.creator_image = self._load_image("acanixz.png", max_width=220, max_height=110)
        if self.creator_image:
            creator_image_label = tk.Label(
                page,
                image=self.creator_image,
                bg=self.primary_color,
                bd=0
            )
        else:
            creator_image_label = tk.Label(
                page,
                text="Creator Character Image",
                font=(self.font_family, 11, "bold"),
                width=26,
                height=4,
                bg=self.secondary_color,
                fg=self.text_secondary_color,
                relief=tk.GROOVE,
                bd=2
            )
        creator_image_label.pack(pady=(164, 0))

        creator_label = tk.Label(
            page,
            text="Created by Acanixz",
            font=(self.font_family, 12, "bold"),
            bg=self.primary_color,
            fg=self.text_primary_color,
            justify=tk.CENTER
        )
        creator_label.pack(pady=(0, 10))

        links_label = tk.Label(
            page,
            text="This tool is open-source and available on GitHub.\n" \
                 "https://github.com/Acanixz/TS1-modloader",
            font=(self.font_family, 12),
            bg=self.primary_color,
            fg=self.text_secondary_color,
            justify=tk.CENTER
        )
        links_label.pack(pady=(0, 15))

        legal_label = tk.Label(
            page,
            text="The Sims is a trademark of Electronic Arts Inc. All rights reserved.\n" \
                 "This tool is not affiliated with or endorsed by Electronic Arts Inc.",
            font=(self.font_family, 11),
            bg=self.primary_color,
            fg=self.text_secondary_color,
            justify=tk.CENTER,
            wraplength=520
        )
        legal_label.pack(pady=(0, 15))
        
        self.pages["About"] = page
    
    def show_page(self, page_name):
        """Switch between different pages"""
        # Hide all pages
        for page in self.pages.values():
            page.pack_forget()
        
        # Show selected page
        if page_name in self.pages:
            self.pages[page_name].pack(fill=tk.BOTH, expand=True)
        
        # Highlight active button
        for name, btn in self.menu_buttons.items():
            if name == page_name:
                btn.configure(bg=self.primary_color, fg=self.text_primary_color)
            else:
                btn.configure(bg=self.secondary_color, fg=self.text_secondary_color)
    
    def launch_game(self):
        """Launch The Sims 1 game"""
        if self.play_callback:
            self.play_callback()
        else:
            print("Play callback not set")
    
    def select_game_path(self):
        """Open folder dialog to select game path"""
        if self.settings.select_game_path():
            path = self.settings.get_game_path()
            self.game_path_var.set(path or "No path selected")
            # Create a message box to inform user that the application will be restarted
            messagebox.showinfo(
                "TS1 ModLoader - Restart Required",
                "The application will now restart to apply the new game path."
            )
            self.root.destroy()
            os.execl(sys.executable, sys.executable, *sys.argv)

    
    def run(self):
        self.root.mainloop()