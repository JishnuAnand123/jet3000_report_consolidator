import customtkinter as ctk
from tkinter import filedialog
import config
from monitor import FolderMonitorEngine

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")


class FileMonitorApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("ICT File Router & Monitor")
        self.geometry("640x580")

        self.source_folders = []
        self.destination_folder = ""
        self.engine = None

        self._build_ui()

    def _build_ui(self):
        # Source Directories Frame
        self.lbl_sources = ctk.CTkLabel(
            self, text="Source Folders:", font=("Arial", 13, "bold"))
        self.lbl_sources.pack(anchor="w", padx=20, pady=(15, 2))

        self.btn_add_src = ctk.CTkButton(
            self, text="+ Add Source Folder", command=self.add_source_folder)
        self.btn_add_src.pack(anchor="w", padx=20, pady=5)

        self.txt_sources = ctk.CTkTextbox(self, height=75, width=600)
        self.txt_sources.pack(padx=20, pady=5)
        self.txt_sources.configure(state="disabled")

        # Destination Directory Frame
        self.lbl_dest = ctk.CTkLabel(
            self, text="Destination Folder:", font=("Arial", 13, "bold"))
        self.lbl_dest.pack(anchor="w", padx=20, pady=(10, 2))

        self.btn_set_dest = ctk.CTkButton(
            self, text="Select Destination", command=self.set_destination)
        self.btn_set_dest.pack(anchor="w", padx=20, pady=5)

        self.lbl_dest_path = ctk.CTkLabel(
            self,
            text="No destination selected",
            font=("Arial", 12, "bold"),
            text_color="#1E88E5"
        )
        self.lbl_dest_path.pack(anchor="w", padx=20, pady=2)

        # Active Mode Indicator Label
        self.action_var = ctk.StringVar(value=config.DEFAULT_ACTION)

        self.lbl_mode_indicator = ctk.CTkLabel(
            self,
            text=f"Active File Operation: {self.action_var.get().upper()} MODE",
            font=("Arial", 12, "bold"),
            text_color="#4CAF50" if self.action_var.get() == "copy" else "#FF9800"
        )
        self.lbl_mode_indicator.pack(anchor="w", padx=20, pady=(12, 2))

        # Checkbox Mode Toggle
        if config.ALLOW_ACTION_TOGGLE:
            self.chk_mode = ctk.CTkCheckBox(
                self,
                text="Move files instead of Copy (Cut Mode)",
                variable=self.action_var,
                onvalue="move",
                offvalue="copy",
                command=self.update_mode_indicator
            )
            self.chk_mode.pack(anchor="w", padx=20, pady=(2, 10))

        # Start / Stop Control Button
        self.btn_toggle = ctk.CTkButton(
            self, text="Start Monitoring", fg_color="green", command=self.toggle_monitoring)
        self.btn_toggle.pack(pady=10)

        # Log Terminal Output
        self.txt_log = ctk.CTkTextbox(self, height=130, width=600)
        self.txt_log.pack(padx=20, pady=10)

    def set_inputs_enabled(self, enabled: bool):
        """Locks path selection controls while monitoring is active."""
        state = "normal" if enabled else "disabled"
        self.btn_add_src.configure(state=state)
        self.btn_set_dest.configure(state=state)

    def update_mode_indicator(self):
        mode = self.action_var.get().upper()
        if mode == "COPY":
            self.lbl_mode_indicator.configure(
                text="Active File Operation: COPY MODE",
                text_color="#4CAF50"
            )
        else:
            self.lbl_mode_indicator.configure(
                text="Active File Operation: CUT / MOVE MODE",
                text_color="#FF9800"
            )

    def log(self, message):
        self.txt_log.insert("end", f"{message}\n")
        self.txt_log.see("end")

    def add_source_folder(self):
        folder = filedialog.askdirectory(title="Select Source Folder")
        if folder and folder not in self.source_folders:
            self.source_folders.append(folder)
            self.txt_sources.configure(state="normal")
            self.txt_sources.insert("end", f"{folder}\n")
            self.txt_sources.configure(state="disabled")

    def set_destination(self):
        folder = filedialog.askdirectory(title="Select Destination Folder")
        if folder:
            self.destination_folder = folder
            self.lbl_dest_path.configure(text=folder, text_color="#00ACC1")

    def toggle_monitoring(self):
        if self.engine is None:
            if not self.source_folders or not self.destination_folder:
                self.log(
                    "Error: Please select source folder(s) and a destination.")
                return

            self.engine = FolderMonitorEngine(
                source_folders=self.source_folders,
                destination_folder=self.destination_folder,
                mode_getter=lambda: self.action_var.get(),
                log_callback=self.log
            )
            self.engine.start()
            # Lock source and destination inputs
            self.set_inputs_enabled(False)
            self.btn_toggle.configure(text="Stop Monitoring", fg_color="red")
            self.log("System initialized. Active monitoring engaged...")
        else:
            self.engine.stop()
            self.engine = None
            # Unlock source and destination inputs
            self.set_inputs_enabled(True)
            self.btn_toggle.configure(
                text="Start Monitoring", fg_color="green")
            self.log("Monitoring paused.")


if __name__ == "__main__":
    app = FileMonitorApp()
    app.mainloop()
