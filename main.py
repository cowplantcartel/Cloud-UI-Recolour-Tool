
# Check for inkscape path
# if inkscape path is not found, open browse dialog
# if inkscape path is found, open main app
# if browse dialog returns succesful exe, open main app

from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import webbrowser
import sv_ttk
from utils import is_valid_inkscape
import sys
from gui import run_app

# File paths
if getattr(sys, 'frozen', False):
    base_path = Path(sys.executable).parent # when running .exe
else:
    base_path = Path(__file__).parent # when running from .py

# Return a valid path for inkscape.exe if it is found, otherwise return ""
def valid_inkscape():
    # Check for previously saved path
    prev_saved_path = base_path / "inkscape_path.txt"
    if prev_saved_path.is_file():
        saved_path = prev_saved_path.read_text(encoding="utf-8").strip()   
        # If the path is a valid inkscape .exe, return path     
        if saved_path != "":
            if is_valid_inkscape(saved_path) == True:
                print("Valid saved inkscape path found, continuing to main app")
                return saved_path   
            
    # Check common install locations for a valid path
    print("No valid saved inkscape path found, checking common install locations")
    possible_paths = [
        r"C:\Program Files\Inkscape\bin\inkscape.exe",
        r"C:\Program Files (x86)\Inkscape\bin\inkscape.exe",
    ] 
    for path in possible_paths:
        if is_valid_inkscape(path) == True:
            # if it's a valid path, save the path to the main folder for later and return path
            print("Valid inkscape location found, saving path to .txt and continuing to main app")
            settings_path = base_path / "inkscape_path.txt"
            settings_path.write_text(path)
            return path
    print("No valid inkscape path found, opening inkscape dialog")
    return "" # no valid path found

def run_inkscape_dialog():
    inkscape_dialog = tk.Tk()
    icon_path = base_path / "PinkPlumbob.ico"
    if icon_path.exists():
        inkscape_dialog.iconbitmap(icon_path)
    inkscape_dialog.title("Inkscape Path Required")
    inkscape_dialog.geometry("400x250") # window size

    sv_ttk.set_theme("light")
    
    ttk.Label(inkscape_dialog, text="Unable to locate inkscape.exe. You can manually search for it by clicking the 'Browse...' button.\n\nIf you have not yet installed Inkscape you can download it from:", wraplength=380).grid(row=0, column=0, columnspan=2, padx=10, pady=10)
    
    def open_link(event):
        webbrowser.open("https://inkscape.org/release/")
    
    link = tk.Label(inkscape_dialog, text="https://inkscape.org/release/", fg="blue", cursor="hand2")
    link.grid(row=1, column=0, padx=10, pady=5, sticky="w")
    link.bind("<Button-1>", open_link)

    entry_inkscape = ttk.Entry(inkscape_dialog, width=33)
    entry_inkscape.grid(row=2, column=0, padx=(10,5), pady=5)
    
    # Manually search for Inkscape.exe
    # Browse button to locate inkscape.exe
    def browse_file(entry_widget):
        file_path = filedialog.askopenfilename(
            title="Locate inkscape.exe",
            filetypes=[("Executable Files", "*.exe"), ("All Files", "*.*")]
        )
        if file_path:
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, file_path)

    btn_browse = ttk.Button(inkscape_dialog, text="Browse...", command=lambda: browse_file(entry_inkscape))
    btn_browse.grid(row=2, column=1, padx=(5,10), pady=5)

    def on_continue():
        path = entry_inkscape.get().strip()
        if is_valid_inkscape(path):
            # Save the valid path for later use
            print("Valid inkscape location found, saving path to .txt and continuing to main app")
            settings_path = base_path / "inkscape_path.txt"
            settings_path.write_text(path)

            # close the dialog
            inkscape_dialog.destroy()
            
            run_app(inkscape_path=path)
        else:
            messagebox.showerror("Invalid Entry", "The path entered is not a valid inkscape.exe.")

    ttk.Button(inkscape_dialog, text="Continue", command=on_continue).grid(row=3, column=1, padx=(5,10), pady=5)

    inkscape_dialog.mainloop()

if __name__ == "__main__":
    path = valid_inkscape()
    if path == "":
        run_inkscape_dialog()
    else:
        run_app(inkscape_path=path)