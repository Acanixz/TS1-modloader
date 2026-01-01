import os
import sys
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, messagebox
from settings import Settings

# The Sims 1 Color Palettes
PRIMARY_COLOR = "#395577"  # Background primary
SECONDARY_COLOR = "#2B4059"  # Background secondary / Button background
TEXT_PRIMARY_COLOR = "#FDE68A"  # Text primary
TEXT_SECONDARY_COLOR = "#FFFFFF"  # Text secondary

# Font settings
FONT_FAMILY = "Montserrat"
FALLBACK_FONT_FAMILY = "Segoe UI"

class UI:
    def __init__(self, settings : Settings, play_callback=None, modloader=None):
        self.settings = settings
        self.play_callback = play_callback
        self.modloader = modloader
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

        # Set window icon (try .ico first for Windows, then .png)
        ico_path = os.path.join(os.path.dirname(__file__), "assets", "images", "icon.ico")
        png_path = os.path.join(os.path.dirname(__file__), "assets", "images", "icon.png")
        
        if os.path.exists(ico_path):
            self.root.iconbitmap(ico_path)
        elif os.path.exists(png_path):
            icon = tk.PhotoImage(file=png_path)
            self.root.iconphoto(True, icon)
            self._icon = icon  # Keep reference to prevent garbage collection

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
        
        # Large banner/logo image
        self.play_banner = self._load_image("banner.png", max_width=500, max_height=250)
        if self.play_banner:
            banner_label = tk.Label(
                page,
                image=self.play_banner,
                bg=self.primary_color,
                bd=0
            )
        else:
            # Placeholder if no image
            banner_label = tk.Frame(
                page,
                bg=self.secondary_color,
                width=400,
                height=200
            )
            banner_label.pack_propagate(False)
            tk.Label(
                banner_label,
                text="The Sims 1\nModLoader",
                font=(self.font_family, 24, "bold"),
                bg=self.secondary_color,
                fg=self.text_primary_color,
                justify=tk.CENTER
            ).place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        banner_label.pack(pady=(40, 20))
        
        title = tk.Label(
            page,
            text="Play The Sims 1",
            font=(self.font_family, 20, "bold"),
            bg=self.primary_color,
            fg=self.text_primary_color
        )
        title.pack(pady=(10, 15))
        
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
        play_button.pack(pady=15)
        
        # Last played label
        last_played = self.settings.get_last_played()
        last_played_text = f"Last played: {last_played}" if last_played else "Not played yet"
        self.last_played_label = tk.Label(
            page,
            text=last_played_text,
            font=(self.font_family, 10),
            bg=self.primary_color,
            fg=self.text_secondary_color
        )
        self.last_played_label.pack(pady=(10, 20))
        
        self.pages["Play"] = page
    
    def create_mods_page(self):
        """Create the Mods page"""
        page = tk.Frame(self.content_frame, bg=self.primary_color)
        
        # Header frame with title and add button
        header_frame = tk.Frame(page, bg=self.primary_color)
        header_frame.pack(fill=tk.X, padx=20, pady=(30, 10))
        
        title = tk.Label(
            header_frame,
            text="Mod Manager",
            font=(self.font_family, 20, "bold"),
            bg=self.primary_color,
            fg=self.text_primary_color
        )
        title.pack(side=tk.LEFT)
        
        # Add New Mod button
        add_mod_button = tk.Button(
            header_frame,
            text="+ Add New Mod",
            font=(self.font_family, 11, "bold"),
            bg=self.secondary_color,
            fg=self.text_primary_color,
            activebackground=self.primary_color,
            activeforeground=self.text_primary_color,
            bd=0,
            padx=15,
            pady=8,
            cursor="hand2",
            command=self.open_add_mod_popup
        )
        add_mod_button.pack(side=tk.RIGHT)
        
        # Mod count label
        self.mod_count_label = tk.Label(
            page,
            text="",
            font=(self.font_family, 11),
            bg=self.primary_color,
            fg=self.text_secondary_color
        )
        self.mod_count_label.pack(anchor=tk.W, padx=20, pady=(0, 10))
        
        # Scrollable mod list container
        list_container = tk.Frame(page, bg=self.primary_color)
        list_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        mod_canvas = tk.Canvas(
            list_container,
            bg=self.primary_color,
            highlightthickness=0
        )
        mod_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = tk.Scrollbar(
            list_container,
            orient=tk.VERTICAL,
            command=mod_canvas.yview
        )
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        mod_canvas.configure(yscrollcommand=scrollbar.set)
        
        # Frame inside canvas to hold mod entries
        self.mod_list_frame = tk.Frame(mod_canvas, bg=self.primary_color)
        mod_window = mod_canvas.create_window((0, 0), window=self.mod_list_frame, anchor="nw")
        
        def _resize_mod_list(event):
            mod_canvas.configure(scrollregion=mod_canvas.bbox("all"))
        
        def _match_mod_canvas_width(event):
            mod_canvas.itemconfigure(mod_window, width=event.width)
        
        def _on_mod_mousewheel(event):
            # Only scroll if content is larger than visible area
            if self.mod_list_frame.winfo_height() > mod_canvas.winfo_height():
                mod_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        
        self.mod_list_frame.bind("<Configure>", _resize_mod_list)
        mod_canvas.bind("<Configure>", _match_mod_canvas_width)
        
        # Store canvas reference for mousewheel binding
        self.mod_canvas = mod_canvas
        
        list_container.bind(
            "<Enter>",
            lambda _: mod_canvas.bind_all("<MouseWheel>", _on_mod_mousewheel)
        )
        list_container.bind(
            "<Leave>",
            lambda _: mod_canvas.unbind_all("<MouseWheel>")
        )
        
        self.pages["Mods"] = page
        
        # Initial population of mod list
        self.refresh_mod_list()

    def refresh_mod_list(self):
        """Refresh the mod list display"""
        # Clear existing entries
        for widget in self.mod_list_frame.winfo_children():
            widget.destroy()
        
        # Reset scroll position to top
        self.mod_canvas.yview_moveto(0)
        
        # Update count label
        if self.modloader:
            mod_count = len(self.modloader.mods)
            self.mod_count_label.config(text=f"{mod_count} mod(s) installed")
            
            if mod_count == 0:
                # Show empty message
                tk.Label(
                    self.mod_list_frame,
                    text="No mods installed yet. Click '+ Add New Mod' to get started.",
                    font=(self.font_family, 11),
                    bg=self.primary_color,
                    fg=self.text_secondary_color
                ).pack(pady=30)
            else:
                # Create mod entries
                for mod in self.modloader.mods.values():
                    self._create_mod_entry(mod)
        else:
            self.mod_count_label.config(text="ModLoader not initialized")

    def _create_mod_entry(self, mod):
        """Create a single mod entry in the list"""
        # Outer frame for white border effect
        border_frame = tk.Frame(
            self.mod_list_frame,
            bg=self.text_secondary_color,  # White border
            padx=1,
            pady=1
        )
        border_frame.pack(fill=tk.X, pady=6, padx=15)
        
        # Inner frame with actual content
        entry_frame = tk.Frame(
            border_frame,
            bg=self.secondary_color,
            pady=8,
            padx=10
        )
        entry_frame.pack(fill=tk.BOTH, expand=True)
        
        # Only show delete button if mod is not locked (hasn't been started with yet)
        is_locked = self.settings.is_mod_locked(mod.id)
        if not is_locked:
            # Delete button (pack first so it doesn't shrink)
            delete_btn = tk.Button(
                entry_frame,
                text="✕",
                font=(self.font_family, 10, "bold"),
                bg=self.primary_color,
                fg="#FF6B6B",
                activebackground=self.secondary_color,
                activeforeground="#FF4444",
                bd=0,
                width=3,
                pady=2,
                cursor="hand2",
                command=lambda m=mod: self.confirm_delete_mod(m)
            )
            delete_btn.pack(side=tk.RIGHT, padx=(5, 0))
        else:
            # Show lock indicator for mods that have been started with
            lock_label = tk.Label(
                entry_frame,
                text="🔒",
                font=(self.font_family, 10),
                bg=self.secondary_color,
                fg=self.text_secondary_color,
                width=3
            )
            lock_label.pack(side=tk.RIGHT, padx=(5, 0))
        
        # Truncate mod name if too long (max ~60 chars to fit 3/4 width)
        max_chars = 60
        display_name = mod.name if len(mod.name) <= max_chars else mod.name[:max_chars-3] + "..."
        
        # Mod name (clickable)
        name_label = tk.Label(
            entry_frame,
            text=display_name,
            font=(self.font_family, 11),
            bg=self.secondary_color,
            fg=self.text_secondary_color,
            cursor="hand2",
            anchor=tk.W
        )
        name_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Bind click to show details
        name_label.bind("<Button-1>", lambda e, m=mod: self.show_mod_details(m))
        entry_frame.bind("<Button-1>", lambda e, m=mod: self.show_mod_details(m))
        border_frame.bind("<Button-1>", lambda e, m=mod: self.show_mod_details(m))
        
        # Hover effect for the entry
        def on_enter(e):
            entry_frame.config(bg=self.primary_color)
            name_label.config(bg=self.primary_color)
        
        def on_leave(e):
            entry_frame.config(bg=self.secondary_color)
            name_label.config(bg=self.secondary_color)
        
        entry_frame.bind("<Enter>", on_enter)
        entry_frame.bind("<Leave>", on_leave)
        name_label.bind("<Enter>", on_enter)
        name_label.bind("<Leave>", on_leave)
        border_frame.bind("<Enter>", on_enter)
        border_frame.bind("<Leave>", on_leave)

    def show_mod_details(self, mod):
        """Show mod details in a popup window"""
        popup = tk.Toplevel(self.root)
        popup.title(f"Mod Details - {mod.name}")
        popup.configure(bg=self.primary_color)
        popup.geometry("550x500")
        popup.resizable(False, False)
        popup.transient(self.root)
        popup.grab_set()
        
        # Center the popup
        popup.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (550 // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (500 // 2)
        popup.geometry(f"+{x}+{y}")
        
        # Scrollable content
        canvas = tk.Canvas(popup, bg=self.primary_color, highlightthickness=0)
        scrollbar = tk.Scrollbar(popup, orient=tk.VERTICAL, command=canvas.yview)
        content_frame = tk.Frame(canvas, bg=self.primary_color)
        
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        canvas_window = canvas.create_window((0, 0), window=content_frame, anchor="nw")
        
        # Labels that need dynamic wraplength
        wrappable_labels = []
        
        def configure_scroll(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas.itemconfigure(canvas_window, width=event.width)
            # Update wraplength for all wrappable labels
            new_wraplength = event.width - 10  # Small padding
            for lbl in wrappable_labels:
                lbl.configure(wraplength=new_wraplength)
        
        content_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>", configure_scroll)
        
        # Mouse wheel scrolling
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        
        # Bind mousewheel when mouse enters the popup
        popup.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>", on_mousewheel))
        popup.bind("<Leave>", lambda e: canvas.unbind_all("<MouseWheel>"))
        
        # Mod Name (Title)
        name_label = tk.Label(
            content_frame,
            text=mod.name,
            font=(self.font_family, 16, "bold"),
            bg=self.primary_color,
            fg=self.text_primary_color,
            wraplength=1,  # Will be updated dynamically
            justify=tk.LEFT,
            anchor=tk.W
        )
        name_label.pack(anchor=tk.W, fill=tk.X, pady=(0, 10))
        wrappable_labels.append(name_label)
        
        # Mod ID
        tk.Label(
            content_frame,
            text=f"ID: {mod.id}",
            font=(self.font_family, 9),
            bg=self.primary_color,
            fg=self.text_secondary_color
        ).pack(anchor=tk.W, pady=(0, 15))
        
        # Image section
        image_displayed = False
        if mod.image:
            try:
                img_path = os.path.join(str(self.modloader.cache_dir), mod.id, mod.image)
                if os.path.exists(img_path):
                    img = tk.PhotoImage(file=img_path)
                    # Scale if needed
                    width, height = img.width(), img.height()
                    max_size = 200
                    scale = max((width + max_size - 1) // max_size, (height + max_size - 1) // max_size, 1)
                    if scale > 1:
                        img = img.subsample(scale)
                    img_label = tk.Label(content_frame, image=img, bg=self.primary_color)
                    img_label.image = img  # Keep reference
                    img_label.pack(anchor=tk.W, pady=(0, 15))
                    image_displayed = True
            except Exception:
                pass
        
        # Show placeholder if no image
        if not image_displayed:
            placeholder_frame = tk.Frame(
                content_frame,
                bg=self.secondary_color,
                width=200,
                height=150
            )
            placeholder_frame.pack(anchor=tk.W, pady=(0, 15))
            placeholder_frame.pack_propagate(False)
            
            tk.Label(
                placeholder_frame,
                text="No Image",
                font=(self.font_family, 11),
                bg=self.secondary_color,
                fg=self.text_secondary_color
            ).place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        # Description
        tk.Label(
            content_frame,
            text="Description:",
            font=(self.font_family, 11, "bold"),
            bg=self.primary_color,
            fg=self.text_primary_color
        ).pack(anchor=tk.W, pady=(0, 5))
        
        desc_text = mod.description if mod.description else "No description provided."
        desc_label = tk.Label(
            content_frame,
            text=desc_text,
            font=(self.font_family, 10),
            bg=self.primary_color,
            fg=self.text_secondary_color,
            wraplength=1,  # Will be updated dynamically
            justify=tk.LEFT,
            anchor=tk.W
        )
        desc_label.pack(anchor=tk.W, fill=tk.X, pady=(0, 15))
        wrappable_labels.append(desc_label)
        
        # Downloads section
        tk.Label(
            content_frame,
            text=f"Download Files ({len(mod.download_files)}):",
            font=(self.font_family, 11, "bold"),
            bg=self.primary_color,
            fg=self.text_primary_color
        ).pack(anchor=tk.W, pady=(0, 5))
        
        if mod.download_files:
            for dl_file in mod.download_files:
                # Show just the filename (after mod_id/)
                display_name = dl_file.split("/")[-1] if "/" in dl_file else dl_file
                tk.Label(
                    content_frame,
                    text=f"  • {display_name}",
                    font=(self.font_family, 9),
                    bg=self.primary_color,
                    fg=self.text_secondary_color
                ).pack(anchor=tk.W)
        else:
            tk.Label(
                content_frame,
                text="  None",
                font=(self.font_family, 9),
                bg=self.primary_color,
                fg=self.text_secondary_color
            ).pack(anchor=tk.W)
        
        # Overrides section
        tk.Label(
            content_frame,
            text=f"Override Files ({len(mod.override_files)}):",
            font=(self.font_family, 11, "bold"),
            bg=self.primary_color,
            fg=self.text_primary_color
        ).pack(anchor=tk.W, pady=(15, 5))
        
        if mod.override_files:
            for src, target in mod.override_files:
                # Show filename and target
                filename = src.split("/")[-1] if "/" in src else src
                tk.Label(
                    content_frame,
                    text=f"  • {filename}",
                    font=(self.font_family, 9, "bold"),
                    bg=self.primary_color,
                    fg=self.text_secondary_color
                ).pack(anchor=tk.W)
                tk.Label(
                    content_frame,
                    text=f"    → {target}",
                    font=(self.font_family, 9),
                    bg=self.primary_color,
                    fg=self.text_secondary_color
                ).pack(anchor=tk.W)
        else:
            tk.Label(
                content_frame,
                text="  None",
                font=(self.font_family, 9),
                bg=self.primary_color,
                fg=self.text_secondary_color
            ).pack(anchor=tk.W)
        
        # Close button at bottom
        close_frame = tk.Frame(popup, bg=self.primary_color)
        close_frame.pack(side=tk.BOTTOM, pady=15)
        
        def close_popup():
            canvas.unbind_all("<MouseWheel>")
            popup.destroy()
        
        tk.Button(
            close_frame,
            text="Close",
            font=(self.font_family, 11, "bold"),
            bg=self.secondary_color,
            fg=self.text_secondary_color,
            activebackground=self.primary_color,
            activeforeground=self.text_secondary_color,
            bd=0,
            padx=25,
            pady=8,
            cursor="hand2",
            command=close_popup
        ).pack()

    def confirm_delete_mod(self, mod):
        """Show confirmation dialog before deleting a mod"""
        result = messagebox.askyesno(
            "Delete Mod",
            f"Are you sure you want to delete '{mod.name}'?\n\n" \
            "This will remove the mod from the manifest and delete its cached files.\n\n" \
            "Note: This action does not delete any files from the game folder, so this is only effective " \
            "if the game has not been launched with the mod installed yet.",
            parent=self.root
        )
        
        if result:
            try:
                self.modloader.remove_mod(mod.id)
                self.refresh_mod_list()
                messagebox.showinfo("Success", f"Mod '{mod.name}' has been deleted.", parent=self.root)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete mod: {str(e)}", parent=self.root)

    def open_add_mod_popup(self):
        """Open popup window to add a new mod"""
        if not self.modloader:
            messagebox.showerror("Error", "ModLoader not initialized. Please set a valid game path first.")
            return
        
        # Create popup window
        popup = tk.Toplevel(self.root)
        popup.title("Add New Mod")
        popup.configure(bg=self.primary_color)
        popup.geometry("600x650")
        popup.resizable(False, False)
        popup.transient(self.root)
        popup.grab_set()
        
        # Center the popup
        popup.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (600 // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (650 // 2)
        popup.geometry(f"+{x}+{y}")
        
        # Title
        tk.Label(
            popup,
            text="Add New Mod",
            font=(self.font_family, 16, "bold"),
            bg=self.primary_color,
            fg=self.text_primary_color
        ).pack(pady=(20, 15))
        
        # --- Bottom Buttons (pack first so they stay at bottom) ---
        button_frame = tk.Frame(popup, bg=self.primary_color)
        button_frame.pack(side=tk.BOTTOM, pady=15)
        
        # Scrollable content frame
        canvas = tk.Canvas(popup, bg=self.primary_color, highlightthickness=0)
        scrollbar = tk.Scrollbar(popup, orient=tk.VERTICAL, command=canvas.yview)
        content_frame = tk.Frame(canvas, bg=self.primary_color)
        
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(20, 0))
        
        canvas_window = canvas.create_window((0, 0), window=content_frame, anchor="nw")
        
        def configure_scroll(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas.itemconfigure(canvas_window, width=event.width)
        
        content_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>", configure_scroll)
        
        # Mouse wheel scrolling
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        canvas.bind_all("<MouseWheel>", on_mousewheel)
        
        # --- Form Fields ---
        
        # Mod ID
        tk.Label(
            content_frame,
            text="Mod ID: *",
            font=(self.font_family, 11, "bold"),
            bg=self.primary_color,
            fg=self.text_primary_color
        ).pack(anchor=tk.W, pady=(10, 5))
        
        mod_id_entry = tk.Entry(
            content_frame,
            font=(self.font_family, 10),
            bg=self.secondary_color,
            fg=self.text_secondary_color,
            insertbackground=self.text_secondary_color,
            relief=tk.FLAT,
            width=50
        )
        mod_id_entry.pack(anchor=tk.W, ipady=5, pady=(0, 10))
        
        # Mod Name
        tk.Label(
            content_frame,
            text="Mod Name: *",
            font=(self.font_family, 11, "bold"),
            bg=self.primary_color,
            fg=self.text_primary_color
        ).pack(anchor=tk.W, pady=(0, 5))
        
        mod_name_entry = tk.Entry(
            content_frame,
            font=(self.font_family, 10),
            bg=self.secondary_color,
            fg=self.text_secondary_color,
            insertbackground=self.text_secondary_color,
            relief=tk.FLAT,
            width=50
        )
        mod_name_entry.pack(anchor=tk.W, ipady=5, pady=(0, 10))
        
        # Description
        tk.Label(
            content_frame,
            text="Description:",
            font=(self.font_family, 11, "bold"),
            bg=self.primary_color,
            fg=self.text_primary_color
        ).pack(anchor=tk.W, pady=(0, 5))
        
        mod_desc_entry = tk.Text(
            content_frame,
            font=(self.font_family, 10),
            bg=self.secondary_color,
            fg=self.text_secondary_color,
            insertbackground=self.text_secondary_color,
            relief=tk.FLAT,
            width=50,
            height=3
        )
        mod_desc_entry.pack(anchor=tk.W, pady=(0, 10))
        
        # --- Download Files Section ---
        tk.Label(
            content_frame,
            text="Download Files (Custom Content):",
            font=(self.font_family, 11, "bold"),
            bg=self.primary_color,
            fg=self.text_primary_color
        ).pack(anchor=tk.W, pady=(10, 5))
        
        download_files_list = []  # List of (full_path, filename)
        
        download_listbox_frame = tk.Frame(content_frame, bg=self.secondary_color)
        download_listbox_frame.pack(anchor=tk.W, fill=tk.X, pady=(0, 5), padx=(0, 20))
        
        download_listbox = tk.Listbox(
            download_listbox_frame,
            font=(self.font_family, 9),
            bg=self.secondary_color,
            fg=self.text_secondary_color,
            selectbackground=self.primary_color,
            selectforeground=self.text_primary_color,
            relief=tk.FLAT,
            height=4,
            width=60
        )
        download_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        download_scrollbar = tk.Scrollbar(download_listbox_frame, command=download_listbox.yview)
        download_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        download_listbox.configure(yscrollcommand=download_scrollbar.set)
        
        download_btn_frame = tk.Frame(content_frame, bg=self.primary_color)
        download_btn_frame.pack(anchor=tk.W, pady=(0, 10))
        
        def add_download_files():
            files = filedialog.askopenfilenames(
                title="Select Download Files",
                filetypes=[("IFF Files", "*.iff"), ("All Files", "*.*")]
            )
            for f in files:
                filename = os.path.basename(f)
                if (f, filename) not in download_files_list:
                    download_files_list.append((f, filename))
                    download_listbox.insert(tk.END, filename)
        
        def remove_download_file():
            selection = download_listbox.curselection()
            if selection:
                idx = selection[0]
                download_listbox.delete(idx)
                download_files_list.pop(idx)
        
        tk.Button(
            download_btn_frame,
            text="Add Files",
            font=(self.font_family, 9),
            bg=self.secondary_color,
            fg=self.text_primary_color,
            activebackground=self.primary_color,
            activeforeground=self.text_primary_color,
            bd=0,
            padx=10,
            pady=5,
            cursor="hand2",
            command=add_download_files
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        tk.Button(
            download_btn_frame,
            text="Remove Selected",
            font=(self.font_family, 9),
            bg=self.secondary_color,
            fg=self.text_primary_color,
            activebackground=self.primary_color,
            activeforeground=self.text_primary_color,
            bd=0,
            padx=10,
            pady=5,
            cursor="hand2",
            command=remove_download_file
        ).pack(side=tk.LEFT)
        
        # --- Override Files Section ---
        tk.Label(
            content_frame,
            text="Override Files (Replace Game Files):",
            font=(self.font_family, 11, "bold"),
            bg=self.primary_color,
            fg=self.text_primary_color
        ).pack(anchor=tk.W, pady=(10, 5))
        
        override_files_list = []  # List of (full_path, filename, target_rel)
        
        override_listbox_frame = tk.Frame(content_frame, bg=self.secondary_color)
        override_listbox_frame.pack(anchor=tk.W, fill=tk.X, pady=(0, 5), padx=(0, 20))
        
        override_listbox = tk.Listbox(
            override_listbox_frame,
            font=(self.font_family, 9),
            bg=self.secondary_color,
            fg=self.text_secondary_color,
            selectbackground=self.primary_color,
            selectforeground=self.text_primary_color,
            relief=tk.FLAT,
            height=4,
            width=60
        )
        override_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        override_scrollbar = tk.Scrollbar(override_listbox_frame, command=override_listbox.yview)
        override_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        override_listbox.configure(yscrollcommand=override_scrollbar.set)
        
        override_btn_frame = tk.Frame(content_frame, bg=self.primary_color)
        override_btn_frame.pack(anchor=tk.W, pady=(0, 10))
        
        def add_override_file():
            # First select the source file
            src_file = filedialog.askopenfilename(
                title="Select Override Source File",
                filetypes=[("IFF Files", "*.iff"), ("All Files", "*.*")]
            )
            if not src_file:
                return
            
            filename = os.path.basename(src_file)
            
            # Then ask for the target path (relative to game folder)
            target_dialog = tk.Toplevel(popup)
            target_dialog.title("Set Target Path")
            target_dialog.configure(bg=self.primary_color)
            target_dialog.geometry("450x150")
            target_dialog.transient(popup)
            target_dialog.grab_set()
            
            # Center dialog
            target_dialog.update_idletasks()
            tx = popup.winfo_x() + (popup.winfo_width() // 2) - (450 // 2)
            ty = popup.winfo_y() + (popup.winfo_height() // 2) - (150 // 2)
            target_dialog.geometry(f"+{tx}+{ty}")
            
            tk.Label(
                target_dialog,
                text=f"File: {filename}",
                font=(self.font_family, 10),
                bg=self.primary_color,
                fg=self.text_secondary_color
            ).pack(pady=(15, 5))
            
            tk.Label(
                target_dialog,
                text="Target path (relative to game folder):",
                font=(self.font_family, 10, "bold"),
                bg=self.primary_color,
                fg=self.text_primary_color
            ).pack(pady=(5, 5))
            
            target_entry = tk.Entry(
                target_dialog,
                font=(self.font_family, 10),
                bg=self.secondary_color,
                fg=self.text_secondary_color,
                insertbackground=self.text_secondary_color,
                relief=tk.FLAT,
                width=45
            )
            target_entry.pack(ipady=5, pady=(0, 10))
            target_entry.insert(0, f"GameData/{filename}")
            
            def confirm_target():
                target_rel = target_entry.get().strip()
                if target_rel:
                    override_files_list.append((src_file, filename, target_rel))
                    override_listbox.insert(tk.END, f"{filename} → {target_rel}")
                    target_dialog.destroy()
            
            tk.Button(
                target_dialog,
                text="Confirm",
                font=(self.font_family, 10, "bold"),
                bg=self.secondary_color,
                fg=self.text_primary_color,
                activebackground=self.primary_color,
                activeforeground=self.text_primary_color,
                bd=0,
                padx=15,
                pady=5,
                cursor="hand2",
                command=confirm_target
            ).pack()
        
        def remove_override_file():
            selection = override_listbox.curselection()
            if selection:
                idx = selection[0]
                override_listbox.delete(idx)
                override_files_list.pop(idx)
        
        tk.Button(
            override_btn_frame,
            text="Add Override",
            font=(self.font_family, 9),
            bg=self.secondary_color,
            fg=self.text_primary_color,
            activebackground=self.primary_color,
            activeforeground=self.text_primary_color,
            bd=0,
            padx=10,
            pady=5,
            cursor="hand2",
            command=add_override_file
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        tk.Button(
            override_btn_frame,
            text="Remove Selected",
            font=(self.font_family, 9),
            bg=self.secondary_color,
            fg=self.text_primary_color,
            activebackground=self.primary_color,
            activeforeground=self.text_primary_color,
            bd=0,
            padx=10,
            pady=5,
            cursor="hand2",
            command=remove_override_file
        ).pack(side=tk.LEFT)
        
        # --- Bottom Button Functions ---
        def cancel_add_mod():
            canvas.unbind_all("<MouseWheel>")
            popup.destroy()
        
        def confirm_add_mod():
            mod_id = mod_id_entry.get().strip()
            mod_name = mod_name_entry.get().strip()
            mod_desc = mod_desc_entry.get("1.0", tk.END).strip() or None
            
            # Validation
            if not mod_id:
                messagebox.showerror("Error", "Mod ID is required.", parent=popup)
                return
            if not mod_name:
                messagebox.showerror("Error", "Mod Name is required.", parent=popup)
                return
            if not download_files_list and not override_files_list:
                messagebox.showerror("Error", "Please add at least one download or override file.", parent=popup)
                return
            
            # Check if mod ID already exists
            if mod_id in self.modloader.mods:
                messagebox.showerror("Error", f"A mod with ID '{mod_id}' already exists.", parent=popup)
                return
            
            try:
                self.modloader.add_mod(
                    mod_id=mod_id,
                    name=mod_name,
                    description=mod_desc,
                    image=None,
                    download_files=download_files_list,
                    override_files=override_files_list
                )
                messagebox.showinfo("Success", f"Mod '{mod_name}' added successfully!", parent=popup)
                canvas.unbind_all("<MouseWheel>")
                popup.destroy()
                self.refresh_mod_list()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add mod: {str(e)}", parent=popup)
        
        # Add buttons to the pre-created button_frame
        tk.Button(
            button_frame,
            text="Cancel",
            font=(self.font_family, 11, "bold"),
            bg=self.secondary_color,
            fg=self.text_secondary_color,
            activebackground=self.primary_color,
            activeforeground=self.text_secondary_color,
            bd=0,
            padx=25,
            pady=8,
            cursor="hand2",
            command=cancel_add_mod
        ).pack(side=tk.LEFT, padx=(0, 15))
        
        tk.Button(
            button_frame,
            text="Add Mod",
            font=(self.font_family, 11, "bold"),
            bg=self.secondary_color,
            fg=self.text_primary_color,
            activebackground=self.primary_color,
            activeforeground=self.text_primary_color,
            bd=0,
            padx=25,
            pady=8,
            cursor="hand2",
            command=confirm_add_mod
        ).pack(side=tk.LEFT)
    
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
                "5. Where are my Save Files stored?",
                "Save files in the original game are typically stored in the the 'UserData' folder within the game's installation directory.\n\n" \
                "On The Sims 1 Legacy Collection however, the default path is usually:\n" \
                r"C:\Users\%USERPROFILE%\Saved Games\Electronic Arts\The Sims 25" + "\n\n" \
                "This means that if you uninstall the game and wanna start over, don't forget to delete this folder to prevent loading old saves with missing mods."
            ),
            (
                "6. Where can I find more mods?",
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
        
        # Program logo
        self.about_logo = self._load_image("icon.png", max_width=150, max_height=150)
        if self.about_logo:
            logo_label = tk.Label(
                page,
                image=self.about_logo,
                bg=self.primary_color,
                bd=0
            )
            logo_label.pack(pady=(0, 15))
        
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
        creator_image_label.pack(pady=(20, 0))

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
            # Refresh mod list to show locked status
            self.refresh_mod_list()
            # Update last played label
            last_played = self.settings.get_last_played()
            if last_played:
                self.last_played_label.config(text=f"Last played: {last_played}")
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