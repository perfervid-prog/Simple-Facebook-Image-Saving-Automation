import customtkinter as ctk
from tkinter import filedialog
import threading
import time
import os
import json
from fb_post_image_saver import FbPostImageSaver
from browser_engine import ProBrowserSaver

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("FB Image Saver Pro")
        self.geometry("700x600")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.settings_file = "settings.json"
        self.saved_path = self.load_settings()

        self.saver_thread = None
        self.basic_saver = None
        self.pro_saver = None

        # --- UI Elements ---
        
        # Header
        self.header = ctk.CTkLabel(self, text="Facebook Image Saver Pro", font=ctk.CTkFont(size=24, weight="bold"))
        self.header.pack(pady=(20, 10))

        # Main Tabview
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(padx=20, pady=10, fill="both", expand=True)
        
        self.tab_basic = self.tabview.add("Basic Mode (Manual Focus)")
        self.tab_pro = self.tabview.add("Pro Mode (Browser Driven)")

        # --- Basic Mode UI ---
        self.setup_basic_tab()

        # --- Pro Mode UI ---
        self.setup_pro_tab()

        # Status Console (Common to both)
        self.console_frame = ctk.CTkFrame(self)
        self.console_frame.pack(padx=20, pady=10, fill="x")
        
        self.progress_label = ctk.CTkLabel(self.console_frame, text="Progress: 0%", font=ctk.CTkFont(size=12))
        self.progress_label.pack(pady=(5, 0))
        
        self.progress_bar = ctk.CTkProgressBar(self.console_frame)
        self.progress_bar.set(0)
        self.progress_bar.pack(padx=20, pady=5, fill="x")

        self.status_box = ctk.CTkTextbox(self.console_frame, height=120)
        self.status_box.pack(padx=10, pady=10, fill="both")
        self.status_box.insert("0.0", "Welcome to FB Image Saver Pro!\nChoose a mode above and get started.")

    def setup_basic_tab(self):
        # Folder Selection
        self.basic_path_frame = ctk.CTkFrame(self.tab_basic, fg_color="transparent")
        self.basic_path_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(self.basic_path_frame, text="Save Folder:").pack(side="left", padx=10)
        self.basic_path = ctk.StringVar(value=self.saved_path)
        self.basic_entry = ctk.CTkEntry(self.basic_path_frame, textvariable=self.basic_path, width=300)
        self.basic_entry.pack(side="left", padx=10)
        ctk.CTkButton(self.basic_path_frame, text="Browse", width=80, command=lambda: self.browse_folder(self.basic_path)).pack(side="left")

        # Config
        self.config_frame = ctk.CTkFrame(self.tab_basic, fg_color="transparent")
        self.config_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(self.config_frame, text="Images:").grid(row=0, column=0, padx=10, pady=5)
        self.basic_count = ctk.CTkEntry(self.config_frame, width=80)
        self.basic_count.insert(0, "10")
        self.basic_count.grid(row=0, column=1, padx=10, pady=5)

        ctk.CTkLabel(self.config_frame, text="Start Num:").grid(row=0, column=2, padx=10, pady=5)
        self.basic_start = ctk.CTkEntry(self.config_frame, width=80)
        self.basic_start.insert(0, "1")
        self.basic_start.grid(row=0, column=3, padx=10, pady=5)

        ctk.CTkLabel(self.config_frame, text="Delay:").grid(row=1, column=0, padx=10, pady=5)
        self.basic_delay = ctk.CTkSlider(self.config_frame, from_=0.5, to=5.0)
        self.basic_delay.set(1.5)
        self.basic_delay.grid(row=1, column=1, columnspan=3, sticky="ew", padx=10)

        # Buttons
        self.basic_start_btn = ctk.CTkButton(self.tab_basic, text="RUN BASIC AUTO", command=self.start_basic)
        self.basic_start_btn.pack(pady=20)
        
        ctk.CTkLabel(self.tab_basic, text="Note: Point mouse at image and wait for 5s.", font=ctk.CTkFont(slant="italic")).pack()

    def setup_pro_tab(self):
        # Folder Selection
        self.pro_path_frame = ctk.CTkFrame(self.tab_pro, fg_color="transparent")
        self.pro_path_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(self.pro_path_frame, text="Save Folder:").pack(side="left", padx=10)
        self.pro_path = ctk.StringVar(value=self.saved_path)
        self.pro_entry = ctk.CTkEntry(self.pro_path_frame, textvariable=self.pro_path, width=300)
        self.pro_entry.pack(side="left", padx=10)
        ctk.CTkButton(self.pro_path_frame, text="Browse", width=80, command=lambda: self.browse_folder(self.pro_path)).pack(side="left")

        # URL Input
        self.url_frame = ctk.CTkFrame(self.tab_pro, fg_color="transparent")
        self.url_frame.pack(fill="x", pady=10)
        ctk.CTkLabel(self.url_frame, text="Post URL (Optional):").pack(side="left", padx=10)
        self.pro_url = ctk.CTkEntry(self.url_frame, width=380, placeholder_text="https://facebook.com/...")
        self.pro_url.pack(side="left", padx=10)

        # Info
        info_txt = "PRO MODE FEATURES:\n- Automatically handles +X grids\n- Detects end of gallery automatically\n- Works in background"
        ctk.CTkLabel(self.tab_pro, text=info_txt, justify="left", font=ctk.CTkFont(size=12)).pack(pady=5)

        # Pro Delay Slider
        self.pro_delay_frame = ctk.CTkFrame(self.tab_pro, fg_color="transparent")
        self.pro_delay_frame.pack(fill="x", pady=5)
        ctk.CTkLabel(self.pro_delay_frame, text="Speed (Delay):").pack(side="left", padx=10)
        self.pro_delay = ctk.CTkSlider(self.pro_delay_frame, from_=0.1, to=3.0)
        self.pro_delay.set(1.0) # Faster default
        self.pro_delay.pack(side="left", fill="x", expand=True, padx=10)

        # Buttons
        self.pro_start_btn = ctk.CTkButton(self.tab_pro, text="RUN PRO AUTO", fg_color="green", hover_color="darkgreen", command=self.start_pro)
        self.pro_start_btn.pack(pady=20)

        self.stop_btn = ctk.CTkButton(self, text="STOP ALL", fg_color="red", hover_color="#990000", command=self.stop_all)
        self.stop_btn.pack(pady=10)

    def browse_folder(self, var):
        path = filedialog.askdirectory()
        if path:
            var.set(path)
            self.save_settings(path)
            # Sync the other tab's path variable
            if var == self.basic_path:
                self.pro_path.set(path)
            else:
                self.basic_path.set(path)

    def load_settings(self):
        default_path = os.path.join(os.path.expanduser("~"), "Downloads")
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, "r") as f:
                    return json.load(f).get("save_folder", default_path)
            except:
                return default_path
        return default_path

    def save_settings(self, path):
        try:
            with open(self.settings_file, "w") as f:
                json.dump({"save_folder": path}, f)
        except Exception as e:
            self.log(f"Failed to save settings: {e}")

    def log(self, message):
        self.status_box.insert("end", f"\n> {message}")
        self.status_box.see("end")

    def update_progress(self, current, total, status):
        if total > 0:
            progress = current / total
            self.progress_bar.set(progress if progress <= 1 else 1)
            self.progress_label.configure(text=f"Progress: {current} images saved")
        self.log(status)

    def update_ui_main_thread(self, current, total, status):
        self.after(0, lambda: self.update_progress(current, total, status))

    def start_basic(self):
        try:
            count = int(self.basic_count.get())
            start_num = int(self.basic_start.get())
            delay = self.basic_delay.get()
            path = self.basic_path.get()

            self.basic_saver = FbPostImageSaver(count, path, start_num, delay, self.update_ui_main_thread)
            self.log("Starting Basic Mode in 5 seconds...")
            threading.Thread(target=lambda: (time.sleep(5), self.basic_saver.run()), daemon=True).start()
        except Exception as e:
            self.log(f"Error: {e}")

    def start_pro(self):
        try:
            path = self.pro_path.get()
            url = self.pro_url.get()
            delay = self.pro_delay.get()
            
            self.pro_saver = ProBrowserSaver(path, delay=delay, callback=self.update_ui_main_thread)
            self.log(f"Starting Pro Mode (Delay: {delay:.1f}s)...")
            threading.Thread(target=lambda: self.pro_saver.run(url if url else None), daemon=True).start()
        except Exception as e:
            self.log(f"Error: {e}")

    def stop_all(self):
        if self.basic_saver: self.basic_saver.stop()
        if self.pro_saver: self.pro_saver.stop()
        self.log("Stopping all processes...")

if __name__ == "__main__":
    app = App()
    app.mainloop()
