
import requests
import json
import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
from PIL import Image, ImageTk
import io
import os
import pickle
import threading

class BitmojiEditor:
    def __init__(self, master):
        self.master = master
        master.title("Bitmoji Editor - Dougie")
        master.geometry("800x600")
        master.configure(bg="#E8F5E9")  # Light green background
        
        # Define color scheme
        self.bg_color = "#E8F5E9"  # Pale green
        self.accent_color = "#66BB6A"  # Medium green
        self.text_color = "#2E7D32"  # Dark green
        self.button_color = "#A5D6A7"  # Light green
        
        # Set up custom styles
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('TFrame', background=self.bg_color)
        self.style.configure('TLabel', background=self.bg_color, foreground=self.text_color, font=('Roboto', 11))
        self.style.configure('TButton', background=self.button_color, foreground=self.text_color, font=('Roboto', 11, 'bold'), relief='flat')
        self.style.map('TButton', background=[('active', self.accent_color)], relief=[('pressed', 'sunken')])
        self.style.configure('TNotebook', background=self.bg_color)
        self.style.configure('TNotebook.Tab', background=self.bg_color, foreground=self.text_color, font=('Roboto', 10))
        self.style.map('TNotebook.Tab', background=[('selected', self.accent_color)], foreground=[('selected', self.bg_color)])

        self.token = self.load_token()
        self.details = None
        self.sections = ["hats", "tops", "bottoms", "outerwear", "outfits"]
        self.accessories = self.load_accessories()
        self.section_frames = {}

        if self.token:
            self.start_editor()
        else:
            self.create_initial_widgets()

        # Bind the close event
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)

    def load_token(self):
        if os.path.exists("data.txt"):
            with open("data.txt", "r") as file:
                token = file.read().strip()
                return token
        return ""

    def load_accessories(self):
        if os.path.exists("saves.txt"):
            try:
                with open("saves.txt", "rb") as file:
                    return pickle.load(file)
            except (EOFError, pickle.UnpicklingError):
                print("Warning: saves.txt file is empty or corrupted. Starting with empty accessories.")
        return {section: {} for section in self.sections}

    def save_accessories(self):
        if any(self.accessories.values()):  # Only save if there's actual data
            with open("saves.txt", "wb") as file:
                pickle.dump(self.accessories, file)
        elif os.path.exists("saves.txt"):  # If no data and file exists, remove it
            os.remove("saves.txt")

    def create_initial_widgets(self):
        main_frame = ttk.Frame(self.master, padding="20")
        main_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        
        self.master.grid_rowconfigure(0, weight=1)
        self.master.grid_columnconfigure(0, weight=1)

        self.token_label = ttk.Label(main_frame, text="Enter Bitmoji Token:", font=('Roboto', 14))
        self.token_label.grid(row=0, column=0, pady=(0, 10), sticky="ew")

        self.token_entry = ttk.Entry(main_frame, width=50, font=('Roboto', 12))
        self.token_entry.grid(row=1, column=0, pady=10, sticky="ew")

        self.start_button = ttk.Button(main_frame, text="Start", command=self.start_editor, style='TButton')
        self.start_button.grid(row=2, column=0, pady=20, sticky="ew")
    
    def start_editor(self):
        if not self.token:
            self.token = self.token_entry.get()
            if not self.token:
                messagebox.showerror("Input Error", "Please enter a Bitmoji token.")
                return
        
        # Show a loading indicator
        self.loading_indicator = self.show_loading_indicator()

        # Fetch details in a separate thread
        threading.Thread(target=self.fetch_bitmoji_details).start()
    
    def show_loading_indicator(self):
        loading_popup = tk.Toplevel(self.master)
        loading_popup.title("Loading")
        loading_popup.geometry("200x100")
        loading_popup.configure(bg=self.bg_color)
        loading_popup.transient(self.master)
        loading_popup.grab_set()

        label = ttk.Label(loading_popup, text="Loading...", font=('Roboto', 12))
        label.pack(expand=True)

        spinner = ttk.Progressbar(loading_popup, mode='indeterminate')
        spinner.pack(expand=True)
        spinner.start()

        return loading_popup

    def hide_loading_indicator(self):
        if self.loading_indicator:
            self.loading_indicator.destroy()
            self.loading_indicator = None

    def fetch_bitmoji_details(self):
        url = "https://us-east-1-bitmoji.api.snapchat.com/api/avatar-builder-v3/avatar"
        headers = {
            "Accept": "application/json, text/plain, */*",
            "Bitmoji-Token": self.token,
            "User-Agent": "Mozilla/5.0"
        }
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            print("Fetched Bitmoji details:", json.dumps(data, indent=2))
            self.details = data
            self.hide_loading_indicator()
            if not self.details:
                messagebox.showerror("Error", "Failed to fetch Bitmoji details.")
                return
            with open("data.txt", "w") as file:
                file.write(self.token)
            self.clear_gui()
            self.create_editor_gui()
        except requests.RequestException as e:
            self.hide_loading_indicator()
            messagebox.showerror("Fetch Error", f"Failed to fetch Bitmoji details: {str(e)}")
            print('Error:', str(e))

    def clear_gui(self):
        for widget in self.master.winfo_children():
            widget.destroy()
    
    def create_editor_gui(self):
        self.main_frame = ttk.Frame(self.master)
        self.main_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        
        self.master.grid_rowconfigure(0, weight=1)
        self.master.grid_columnconfigure(0, weight=1)

        self.top_frame = ttk.Frame(self.main_frame)
        self.top_frame.grid(row=0, column=0, pady=20, sticky="ew")
        
        self.image_label = ttk.Label(self.top_frame)
        self.image_label.grid(row=0, column=0, padx=20, sticky="w")
        
        self.buttons_frame = ttk.Frame(self.top_frame)
        self.buttons_frame.grid(row=0, column=1, padx=20, sticky="e")
        
        self.save_button = ttk.Button(self.buttons_frame, text="Save", command=self.save_action, style='TButton')
        self.save_button.grid(row=0, column=0, pady=10, sticky="ew")

        self.tab_control = ttk.Notebook(self.main_frame)
        self.tab_control.grid(row=1, column=0, pady=20, sticky="nsew")

        for section in self.sections:
            tab = ttk.Frame(self.tab_control)
            self.tab_control.add(tab, text=section.capitalize())
            self.section_frames[section] = tab
            
            buttons_frame = ttk.Frame(tab)
            buttons_frame.grid(row=0, column=0, pady=10, sticky="ew")
            
            add_button = ttk.Button(buttons_frame, text="+ Add", command=lambda s=section: self.add_accessory(s), style='TButton')
            add_button.grid(row=0, column=0, padx=10, sticky="ew")
            
            remove_button = ttk.Button(buttons_frame, text="- Remove", command=lambda s=section: self.remove_accessory(s), style='TButton')
            remove_button.grid(row=0, column=1, padx=10, sticky="ew")
            
            self.update_section(section)

        self.update_preview()

    def add_accessory(self, section):
        name = simpledialog.askstring("Add Accessory", f"Enter name for the {section} accessory:", parent=self.master)
        if name:
            id = simpledialog.askstring("Add Accessory", f"Enter ID for the {section} accessory:", parent=self.master)
            if id:
                self.accessories[section][name] = id
                self.update_section(section)
                print(f"Added accessory: {name} (ID: {id}) to {section}")
    
    def remove_accessory(self, section):
        name = simpledialog.askstring("Remove Accessory", f"Enter name of the {section} accessory to remove:", parent=self.master)
        if name and name in self.accessories[section]:
            del self.accessories[section][name]
            self.update_section(section)
            print(f"Removed accessory: {name} from {section}")
    
    def update_section(self, section):
        frame = self.section_frames[section]
        for widget in frame.winfo_children():
            if isinstance(widget, ttk.Button) and widget.cget("text") not in ["+ Add", "- Remove"]:
                widget.destroy()
        
        accessories_frame = ttk.Frame(frame)
        accessories_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        
        row, col = 0, 0
        for name, id in self.accessories[section].items():
            button = ttk.Button(accessories_frame, text=name, command=lambda s=section, i=id: self.apply_accessory(s, i), width=15, style='TButton')
            img = self.fetch_accessory_image(section, id)
            if img:
                button.config(image=img, compound="top")
                button.image = img
            button.grid(row=row, column=col, padx=10, pady=10, sticky="ew")
            col += 1
            if col > 2:
                col = 0
                row += 1

    def apply_accessory(self, section, id):
        if section == "outfits":
            self.details["option_ids"]["outfit"] = id
        else:
            self.details["option_ids"][section[:-1]] = id
        print(f"Applied accessory: {section} (ID: {id})")
        self.update_preview()
    
    def build_bitmoji_url(self):
        base_url = "https://preview.bitmoji.com/bm-preview/v3/avatar/body"
        params = {
            "scale": "2",
            "gender": self.details["gender"],
            "style": self.details["style"],
            "rotation": "0",
            "version": "0"
        }
        
        for key, value in self.details["option_ids"].items():
            if value != -1:
                params[key] = value
        
        url = f"{base_url}?" + "&".join(f"{key}={value}" for key, value in params.items())
        print("Generated Bitmoji URL:", url)
        return url
    
    def fetch_accessory_image(self, section, id):
        base_urls = {
            "hats": "https://preview.bitmoji.com/bm-preview/v3/avatar/hat",
            "tops": "https://preview.bitmoji.com/bm-preview/v3/avatar/top",
            "bottoms": "https://preview.bitmoji.com/bm-preview/v3/avatar/bottom",
            "outerwear": "https://preview.bitmoji.com/bm-preview/v3/avatar/outerwear",
            "outfits": "https://preview.bitmoji.com/bm-preview/v3/avatar/outfit"
        }
        
        if section not in base_urls:
            return None

        url = base_urls[section]
        params = {
            "scale": "0.75",
            "gender": self.details["gender"],
            "style": self.details["style"],
            section[:-1]: id
        }

        url = f"{url}?" + "&".join(f"{key}={value}" for key, value in params.items())
        try:
            response = requests.get(url)
            response.raise_for_status()
            img_data = response.content
            img = Image.open(io.BytesIO(img_data))
            img = img.resize((60, 80), Image.LANCZOS)
            return ImageTk.PhotoImage(img)
        except requests.RequestException as e:
            print('Error fetching image:', str(e))
            return None
    
    def update_preview(self):
        bitmoji_url = self.build_bitmoji_url()
        img = self.display_image_from_url(bitmoji_url)
        if img:
            self.image_label.config(image=img)
            self.image_label.image = img
            print("Updated Bitmoji preview")
        else:
            messagebox.showerror("Image Error", "Failed to load image.")
            print("Failed to update Bitmoji preview")
    
    def display_image_from_url(self, url):
        try:
            response = requests.get(url)
            response.raise_for_status()
            img_data = response.content
            img = Image.open(io.BytesIO(img_data))
            img = img.resize((250, 375), Image.LANCZOS)
            return ImageTk.PhotoImage(img)
        except requests.RequestException as e:
            print('Error fetching image:', str(e))
            return None
    
    def save_action(self):
        url = "https://us-east-1-bitmoji.api.snapchat.com/api/avatar-builder-v3/avatar"
        headers = {
            "Accept": "application/json, text/plain, */*",
            "Bitmoji-Token": self.token,
            "User-Agent": "Mozilla/5.0"
        }
        
        data = {
            "gender": self.details["gender"],
            "style": self.details["style"],
            "mode": "edit",
            "option_ids": self.details["option_ids"]
        }
        
        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            print("Bitmoji updated successfully:", response.json())
            
            avatar_id = self.details["id"]
            base_id, session_id = avatar_id.rsplit("_", 1)
            session_number, version = session_id.split("-s")
            session_number = str(int(session_number) + 1)
            new_avatar_id = f"{base_id}_{session_number}-s{version}"

            self.details["id"] = new_avatar_id

            image_url = f"https://images.bitmoji.com/3d/avatar/30817224-{new_avatar_id}-v1.webp?ua=2"
            image_data = requests.get(image_url).content
            img = Image.open(io.BytesIO(image_data))
            img = img.resize((200, 300), Image.LANCZOS)
            img_tk = ImageTk.PhotoImage(img)

            save_popup = tk.Toplevel(self.master)
            save_popup.title("Save Successful")
            save_popup.geometry("250x400")
            save_popup.transient(self.master)
            save_popup.grab_set()

            img_label = ttk.Label(save_popup, image=img_tk)
            img_label.image = img_tk
            img_label.pack(pady=10)

            message_label = ttk.Label(save_popup, text="Bitmoji has been updated successfully!", font=('Roboto', 10, 'bold'))
            message_label.pack(pady=10)

            print("Bitmoji successfully saved")

            self.master.after(5000, save_popup.destroy)

        except requests.RequestException as e:
            messagebox.showerror("Save Error", f"Failed to update Bitmoji: {str(e)}")
            print('Error:', str(e))

    def on_closing(self):
        self.save_accessories()
        self.master.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    editor = BitmojiEditor(root)
    root.mainloop()
