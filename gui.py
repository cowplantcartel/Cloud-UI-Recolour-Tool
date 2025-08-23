import re
import sys
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox
import sv_ttk
from utils import hex_to_rgb_string, color_chooser, recolour_files, export_png, generate_shades, lighten_hex_50, invert_hex, validate_all_inputs, validate_hex_input, enforce_hash_prefix, validate_opacity
from recolour import run_recolour

# File paths
if getattr(sys, 'frozen', False):
    base_path = Path(sys.executable).parent # when running .exe
else:
    base_path = Path(__file__).parent # when running from .py

ui_path = base_path / "Base UI"
creations_path = base_path / "Creations"

entries = {}
color_previews = {}

# Default colour presets
default_colours = {
    "Main Font": {
        "Light": "#545354",
        "Colourful": "#545354",
        "Dark": "#ebebeb"
    },
    "Darkest Accent": {
        "Light": "#b179ff",
        "Colourful": "#b179ff",
        "Dark": "#b179ff"
    },
    "Dark Accent": {
        "Light": "#c398ff",
        "Colourful": "#c398ff",
        "Dark": "#c398ff"
    },
    "Main Accent": {
        "Light": "#dbb6ff",
        "Colourful": "#d4b6ff",
        "Dark": "#d4b6ff"
    },
    "Light Accent": {
        "Light": "#e7d6ff",
        "Colourful": "#e7d6ff",
        "Dark": "#e7d6ff"
    },
    "Background Light": {
        "Light": "#e7d6ff",
        "Colourful": "#e7d6ff",
        "Dark": "#333333"
    },
    "Background Dark": {
        "Light": "#d4b6ff",
        "Colourful": "#d4b6ff",
        "Dark": "#333333"
    },
    "HUD Background 1": {
        "Light": "#f2f2f2",
        "Colourful": "#c398ff",
        "Dark": "#1a1a1a"
    },
    "HUD Background 2": {
        "Light": "#f9f9f9",
        "Colourful": "#e7d6ff",
        "Dark": "#1a1a1a"
    },
    "HUD Accent Light": {
        "Light": "#ffffff",
        "Colourful": "#f7f0ff",
        "Dark": "#333333"
    },
    "HUD Accent Dark": {
        "Light": "#b3b3b3",
        "Colourful": "#c398ff",
        "Dark": "#000000"
    },
    "MISC": {
        "Light": "#cccccc",
        "Colourful": "#c398ff",
        "Dark": "#000000"
    },
    "Opacity": {
        "Light": "0.75",
        "Colourful": "0.80",
        "Dark": "0.85"
    }
}

# Update shades in Detailed Controls section based on selection
def update_shades(hex_code, preset_val):
    if re.fullmatch(r"#([0-9a-fA-F]{6})", hex_code):
        shades = generate_shades(hex_code)
        labels = ["Light Accent", "Main Accent", "Dark Accent", "Darkest Accent"]
        for label, shade in zip(labels, shades):
            if label in entries:
                entries[label].delete(0, tk.END)
                entries[label].insert(0, shade)
                if label in color_previews:
                    color_previews[label].config(bg=shade)

        # Update backgrounds
        if preset_val != "Dark":
            entries["Background Dark"].delete(0, tk.END)
            entries["Background Dark"].insert(0, shades[1])
            entries["Background Light"].delete(0, tk.END)
            entries["Background Light"].insert(0, shades[0])
            color_previews["Background Dark"].config(bg=shades[1])
            color_previews["Background Light"].config(bg=shades[0])
            
        if preset_val == "Colourful":
            # HUD Background 1 = light accent
            entries["HUD Background 1"].delete(0, tk.END)
            entries["HUD Background 1"].insert(0, shades[0])
            color_previews["HUD Background 1"].config(bg=shades[0])
            # HUD Background 2 = light accent
            entries["HUD Background 2"].delete(0, tk.END)
            entries["HUD Background 2"].insert(0, shades[0])
            color_previews["HUD Background 2"].config(bg=shades[0])
            # HUD Accent Light = halfway between white and light accent
            hud_accent_light_shade = lighten_hex_50(shades[0])
            entries["HUD Accent Light"].delete(0, tk.END)
            entries["HUD Accent Light"].insert(0, hud_accent_light_shade)
            color_previews["HUD Accent Light"].config(bg=hud_accent_light_shade)
            # HUD Accent Dark = dark accent
            entries["HUD Accent Dark"].delete(0, tk.END)
            entries["HUD Accent Dark"].insert(0, shades[2])
            color_previews["HUD Accent Dark"].config(bg=shades[2])
            # MISC
            entries["MISC"].delete(0, tk.END)
            entries["MISC"].insert(0, shades[0])
            color_previews["MISC"].config(bg=shades[0])

# Extract colour values to replace
def colour_extractor(preset_val):

    # Grab the current values in the HEX code inputs
    font_main=entries["Main Font"].get()
    accent_darker=entries["Darkest Accent"].get()
    accent_dark=entries["Dark Accent"].get()
    accent_main=entries["Main Accent"].get()
    accent_light=entries["Light Accent"].get()
    background_light=entries["Background Light"].get()
    background_dark=entries["Background Dark"].get()
    hud_background1=entries["HUD Background 1"].get()
    hud_background2=entries["HUD Background 2"].get()
    hud_accent_light=entries["HUD Accent Light"].get()
    hud_accent_dark=entries["HUD Accent Dark"].get()
    misc=entries["MISC"].get()
    opacity = entries["Opacity"].get()
    
    # Colour selections for output file
    input_values = {
        "Main Font": font_main,
        "Darkest Accent": accent_darker,
        "Dark Accent": accent_dark,
        "Main Accent": accent_main,
        "Light Accent": accent_light,
        "Background Light": background_light,
        "Background Dark": background_dark,
        "HUD Background 1": hud_background1,
        "HUD Background 2": hud_background2,
        "HUD Accent Light": hud_accent_light,
        "HUD Accent Dark": hud_accent_dark,
        "MISC": misc,
        "Opacity": opacity
    }

    # Colour replacements for SVG files
    replacements_svg = {
        "#ff5599": accent_darker,
        "#ff80b2": accent_dark,
        "#ffaacc": accent_main,
        "#ffd5e5": accent_light,
        "rgb\\(255,170,204\\)": hex_to_rgb_string(accent_main), # main accent ffaacc
        "rgb\\(255,221,234\\)": hex_to_rgb_string(accent_light),
        "rgb\\(191,191,191\\)": hex_to_rgb_string(hud_accent_dark), # drop shadow in white boxes
        "rgb\\(192,191,192\\)": hex_to_rgb_string(hud_accent_dark), # relationship panel/opportunities tabs
        "rgb\\(255,163,200\\)": hex_to_rgb_string(background_dark), # CAS background dark
        "rgb\\(250,250,250\\)": hex_to_rgb_string(background_light), # CAS background light
        "#fafafa": background_light,
        "#fde7f0": background_light, # background gradient light, light mode default: accent_light
        "#ebc7d0": background_dark, # background gradient dark: light mode default: accent_main
        "#ffdbe9": background_dark, # startup loading screen
        "#f2f2f2": hud_background1, # DARK MODE HUD - main background
        "#f9f9f9": hud_background2,
        "#ffffff": hud_accent_light,
        "#b3b3b3": hud_accent_dark,
        "rgb\\(145,145,145\\)": hex_to_rgb_string(hud_accent_dark), #  build/buy category images
        "#999999": hud_accent_dark, # build/buy darker controls
        "#e6e6e6": misc, # WHAT IS THIS?
        "#cccccc": misc, # deselected tab, other misc stuff    
        "#808080": hud_accent_dark, # DARK MODE - unavailable tab
        "opacity:0.75": "opacity:" + opacity,
        "opacity:0.80": "opacity:" + opacity,
        "opacity:0.8": "opacity:" + opacity,
        "opacity:0.801": "opacity:" + opacity
    }

    # Colour replacements for LAYOUT files
    replacements_layout = {
        "0xffff5599": accent_darker.replace("#", "0xff"),
        "0xffff80b2": accent_dark.replace("#", "0xff"),
        "0xffffaacc": accent_main.replace("#", "0xff"),
        "0xffffd5e5": accent_light.replace("#", "0xff"),
        "0xff545354": font_main.replace("#", "0xff"), # TEXT COLOUR
        "0xfffaf7f9": hud_background1.replace("#", "0xff"), # divider colours
        "0xffcccccc": misc.replace("#", "0xff") # table alternate row colour
    }

    # Replace pie menu highlighted text
    # Use font_main for light and colourful modes and the inverse of font_main for dark mode
    if preset_val == "Dark":
        replacements_layout["0xff545355"] = invert_hex(font_main).replace("#", "0xff")
    else:
        replacements_layout["0xff545355"] = font_main.replace("#", "0xff")
    

    # Keep font SVG only for preview - it might break the other SVGs
    replacements_svg_preview = replacements_svg.copy()
    replacements_svg_preview["#545354"] = font_main

    return replacements_svg, replacements_svg_preview, replacements_layout, input_values

# Create the tool GUI
def run_app(inkscape_path):
    root = tk.Tk()
    icon_path = base_path / "PinkPlumbob.ico"
    if icon_path.exists():    
        root.iconbitmap(icon_path)
    root.title("Cloud UI Recolour Tool v1.0.0")
    root.geometry("1300x796") # window size

    sv_ttk.set_theme("light")

    # Make ttk.LabelFrame larger and bold
    s = ttk.Style()
    s.configure('Larger.TLabelframe.Label', font=('TkDefaultFont', 12, 'bold'))  

    # Main container grid layout 
    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(1, weight=1)

    # --------------------------------- #
    # GUI LEFT SIDE: Inputs and buttons
    # --------------------------------- #
    canvas = tk.Canvas(root, width=500, highlightthickness=0)
    canvas.grid(row=0, column=0, sticky="nsew")
    
    scrollbar = ttk.Scrollbar(root, orient="vertical", command=canvas.yview)
    scrollbar.grid(row=0, column=0, sticky="nse")
    canvas.configure(yscrollcommand=scrollbar.set)

    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    canvas.bind_all("<MouseWheel>", _on_mousewheel)

    input_frame = ttk.Frame(canvas)
    canvas.create_window((0, 0), window=input_frame, anchor="nw")

    def update_scrollbar(event=None):
        # Update scrollregion to fit content
        canvas.configure(scrollregion=canvas.bbox("all"))

        # Show scrollbar only if content taller than canvas
        if canvas.bbox("all")[3] > canvas.winfo_height():
            scrollbar.grid(row=0, column=0, sticky="nse")
        else:
            scrollbar.grid_remove()

    # Recalculate whenever content changes or window resizes
    input_frame.bind("<Configure>", update_scrollbar)
    canvas.bind("<Configure>", update_scrollbar)
       
    # --------------------------------- #
    # 1. UI Name Section 
    # --------------------------------- #
    frame_ui_name = ttk.LabelFrame(input_frame, text="1. UI Name", style = "Larger.TLabelframe")
    frame_ui_name.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
    ttk.Label(frame_ui_name, text="Enter a name for your custom UI. This will be used to name your exported packages.", wraplength=500).grid(row=0,column=0, padx=10, pady=2, sticky="w")
    entry_ui_name = ttk.Entry(frame_ui_name, width=55)
    entry_ui_name.insert(0, "My Custom UI")
    entry_ui_name.grid(row=1, column=0, padx=5, pady=10)

    # --------------------------------- #
    # 2. Basic Controls Section
    # --------------------------------- #
    frame_basic = ttk.LabelFrame(input_frame, text="2. Customise UI", style = "Larger.TLabelframe")
    frame_basic.grid(row=4, column=0, padx=10, pady=10)
    ttk.Label(frame_basic, text="Choose the main colour and overall theme of the UI.").grid(row=4, column=0, padx=5, pady=5)

    # INPUT: Colour preset
    radio_frame = ttk.Frame(frame_basic)
    radio_frame.grid(row=5, column=0)

    # When a new colour preset is selected, update the colours & opacity in the Detailed Controls section
    def on_preset_change():
        preset_name = selected_option.get()
        apply_colour_preset(preset_name)
        update_shades(entry_accent.get(), selected_option.get())

        # Update opacity entry when changing presets
        if "Opacity" in default_colours and preset_name in default_colours["Opacity"]:
            entry_opacity.delete(0, tk.END)
            entry_opacity.insert(0, default_colours["Opacity"][preset_name])

    # Create radio buttons with Light selected to start with
    options = ["Light", "Colourful", "Dark"]
    selected_option = tk.StringVar(value=options[0]) 
    ttk.Label(radio_frame, text="Colour Preset:").grid(row=0, column=0, padx=(0,5), sticky="w")
    ttk.Radiobutton(radio_frame, text="Light", variable=selected_option, value="Light", command=on_preset_change).grid(row=0, column=1)
    ttk.Radiobutton(radio_frame, text="Colourful", variable=selected_option, value="Colourful", command=on_preset_change).grid(row=0, column=2)
    ttk.Radiobutton(radio_frame, text="Dark", variable=selected_option, value="Dark", command=on_preset_change).grid(row=0, column=3)

    # INPUT: Main accent
    color_accent_frame = ttk.Frame(frame_basic)
    color_accent_frame.grid(row=6, column=0, padx=5, pady=5)
    ttk.Label(color_accent_frame, text="Main Accent Colour:").grid(row=0, column=0, padx=5, pady=4, sticky="w")
    hex_vcmd = root.register(validate_hex_input)
    entry_accent = ttk.Entry(color_accent_frame, width=10, validate="key", validatecommand=(hex_vcmd, "%P"))
    entry_accent.insert(0, "#dbb6ff")
    entry_accent.grid(row=0, column=1, padx=5, pady=5, sticky="w")    

    # When the main accent colour is changed, updated the preview box colour
    def update_accent_preview(event):
        val = entry_accent.get()
        if re.fullmatch(r"#([0-9a-fA-F]{6})", val):
            accent_preview.config(bg=val)
            update_shades(val, selected_option.get())

    entry_accent.bind("<KeyRelease>", update_accent_preview)

    # Ensure "#" is always in front of the hex code in the input box
    def on_accent_focus_out(event):
        enforce_hash_prefix(event)
        update_accent_preview(event)

    entry_accent.bind("<FocusOut>", on_accent_focus_out)

    # Preview box
    accent_preview = tk.Label(color_accent_frame, width=2, bg="#dbb6ff", relief="sunken")
    accent_preview.grid(row=0, column=2, sticky="w", padx=(5,0))

    # Edit button
    def on_edit_accent():
        color_chooser(entry_accent, accent_preview)()
        update_shades(entry_accent.get(), selected_option.get())

    accent_btn = ttk.Button(color_accent_frame, text="Edit", command=on_edit_accent)
    accent_btn.grid(row=0, column=3, sticky="w", padx=(5,5))

    # --------------------------------- #
    # 3. Detailed Customisation Section (optional)
    # --------------------------------- #
    frame_detailed = ttk.LabelFrame(input_frame, text="3. Detailed Customisation (Optional)", style = "Larger.TLabelframe")
    frame_detailed.grid(row=7, column=0, padx=10, pady=(10,12))
    ttk.Label(frame_detailed, text="Fine-tune individual colours and the opacity here or skip to use preset defaults.", wraplength=480).grid(row=0,column=0, padx=5, pady=2)

    # Collapsible section
    is_visible = tk.BooleanVar(value=False)
    color_input_frame = ttk.Frame(frame_detailed)
    
    def toggle_color_section():
        if is_visible.get():
            color_input_frame.grid_remove()
            toggle_button.config(text="Show Detailed Controls ▶")
        else:
            color_input_frame.grid(row=2, column=0, columnspan=3, sticky="n", pady=(10, 0))
            toggle_button.config(text="Hide Detailed Controls ▼")
        is_visible.set(not is_visible.get())

    toggle_button = ttk.Button(frame_detailed, text="Show Detailed Controls ▶", command=toggle_color_section, width=55)
    toggle_button.grid(row=1, column=0, columnspan=3, padx=5, pady=(10,0))

    preset = selected_option.get()
    colour_keys = [k for k in default_colours.keys() if k != "Opacity"]
    for i, label_text in enumerate(colour_keys): 
        default = default_colours[label_text][preset]

        # Colour input label
        ttk.Label(color_input_frame, text=label_text).grid(row=i, column=0, padx=5, pady=4, sticky="e")

        # Colour input box    
        entry = ttk.Entry(color_input_frame, width=10, validate="key", validatecommand=(hex_vcmd, "%P"))
        entry.insert(0, default)
        entry.grid(row=i, column=1, padx=5, pady=5, sticky="w")
        entries[label_text] = entry

        # Colour preview box
        preview = tk.Label(color_input_frame, width=2, bg=default, relief="sunken")
        preview.grid(row=i, column=2, sticky="w", padx=(5,0))
        color_previews[label_text] = preview

        entry.bind("<FocusOut>", lambda e, prev=preview: enforce_hash_prefix(e, prev))

        # Colour edit button
        btn = ttk.Button(color_input_frame, text="Edit", command=color_chooser(entry, preview))
        btn.grid(row=i, column=3, sticky="w", padx=(5,0))

        # Update preview box when selected colour changes
        def update_preview(event, ent=entry, prev=preview):
            val = ent.get()
            if re.fullmatch(r"#([0-9a-fA-F]{6})", val):
                prev.config(bg=val)
        entry.bind("<KeyRelease>", update_preview)

        def apply_colour_preset(preset_name):
            for label, entry in entries.items():
                if label == "Opacity":
                    continue  # Skip opacity for color preview
                if label in default_colours and preset_name in default_colours[label]:
                    hex_value = default_colours[label][preset_name]
                    entry.delete(0, tk.END)
                    entry.insert(0, hex_value)
                    if label in color_previews:
                        color_previews[label].config(bg=hex_value)

            # Set opacity separately
            if "Opacity" in default_colours and preset_name in default_colours["Opacity"]:
                entry_opacity.delete(0, tk.END)
                entry_opacity.insert(0, default_colours["Opacity"][preset_name])

    # Add opacity control
    ttk.Label(color_input_frame, text="Opacity").grid(row=len(colour_keys), column=0, padx=5, pady=5, sticky="e")

    vcmd = root.register(validate_opacity)
    entry_opacity = ttk.Entry(color_input_frame, width=10, validate="key", validatecommand=(vcmd, "%P"))
    entry_opacity.insert(0, default_colours["Opacity"][preset])
    entry_opacity.grid(row=len(colour_keys), column=1, padx=5, pady=5, sticky="w")
    entries["Opacity"] = entry_opacity

    last_row = len(default_colours) + 7

    tk.Label(frame_detailed, text="").grid(row=last_row, column=0, padx=5, pady=1)

    # --------------------------------- #
    # 4. Show Preview & Run
    # --------------------------------- #

    frame_run = ttk.LabelFrame(input_frame, text="4. Run", style = "Larger.TLabelframe")
    frame_run.grid(row=last_row + 1, column=0, padx=10, pady=10)
    ttk.Label(frame_run, text="Generate a preview from your current selections", wraplength=500).grid(row=last_row,column=0, padx=5, pady=2, sticky="w")

    # Preview UI
    def preview_UI():
        if not validate_all_inputs(input_ui_name = entry_ui_name, input_entries = entries):
            return  # Abort if invalid inputs

        try:
            _, replacements_svg_preview, _, _ = colour_extractor(selected_option.get())
            recolour_files(
                file_input_path=base_path / "UI_Preview.svg",
                colour_replacements=replacements_svg_preview,
                file_output_path=base_path / "UI_Preview_Edited.svg"
            )
            export_png(
                inkscape_path,
                input_path=base_path / "UI_Preview_Edited.svg",
                output_path=base_path / "UI_Preview.png"
            )
            img = tk.PhotoImage(file=base_path / "UI_Preview.png")
            image_label.configure(image=img, text="")
            image_label.image = img
        except Exception as e:
            print("Preview failed:", e)
            image_label.configure(text=f"Failed to load preview.\nCheck that UI_Preview.svg is in the same folder as Cloud UI Recolour Tool.exe\n{e}")
    
    ttk.Button(frame_run, text="✨ Show Preview ✨", command=preview_UI, width=55).grid(
        row=last_row + 1, column=0, columnspan=3, padx=5, pady=(5,10), sticky="w"
    )

    # Settings toggles
    ttk.Label(frame_run, text="Build the UI mod from your current selections", wraplength=500).grid(row=last_row + 2, column=0, padx=5, pady=5, sticky="w")

    include_logos = tk.BooleanVar(value=True)
    include_patches = tk.BooleanVar(value=True)
    delete_processing_files = tk.BooleanVar(value=True)

    ttk.Checkbutton(frame_run, text="Generate language logos", variable=include_logos).grid(row=last_row + 3, sticky="w", padx=5)
    ttk.Checkbutton(frame_run, text="Generate patches", variable=include_patches).grid(row=last_row + 4, sticky="w", padx=5)
    ttk.Checkbutton(frame_run, text="Delete processing files", variable=delete_processing_files).grid(row=last_row + 5, sticky="w", padx=5)

    # Create UI 
    def on_create_ui():

        # Check that inputs are real hex codes etc
        if not validate_all_inputs(input_ui_name = entry_ui_name, input_entries = entries):
            return  # Abort if invalid inputs    
        elif not ui_path.exists():        
            # If the Base UI folder does not exist, show warning box
            messagebox.showwarning("Missing Base UI", f"Base UI folder was not found. Please ensure the Base UI folder is in the same folder as Cloud UI Recolour Tool.exe")
        else:
            # Grab required inputs for recolour function
            replacements_svg, _, replacements_layout, input_values = colour_extractor(selected_option.get())
            # Log output for debugging
            log_file_path = base_path / "console_log.txt"
            log_file = log_file_path.resolve()

            class Logger:
                def __init__(self, path):
                    self.file = open(path, "w", buffering=1)
                def write(self, text):
                    self.file.write(text)
                def flush(self):
                    self.file.flush()
                def close(self):
                    self.file.close()

            def run_recolour_with_log(**kwargs):
                logger = Logger(log_file)
                original_stdout = sys.stdout
                original_stderr = sys.stderr

                try:
                    sys.stdout = logger
                    sys.stderr = logger
                    run_recolour(**kwargs)  # your existing function call
                finally:
                    sys.stdout = original_stdout
                    sys.stderr = original_stderr
                    logger.close()
            
            # Run the main recolouring function
            run_recolour_with_log(
                ui_path=base_path,
                ui_name=entry_ui_name.get(),
                replacements_layout=replacements_layout,
                replacements_svg=replacements_svg,
                inkscape_path=inkscape_path,
                colour_values=input_values,
                run_logos=include_logos.get(),
                run_patches=include_patches.get(),
                run_processing=delete_processing_files.get()
            )

    ttk.Button(frame_run, text="✨ Create UI ✨", command=on_create_ui, width=55).grid(
        row=last_row + 6, column=0, columnspan=3, padx=5, pady=5, sticky="w"
    )

    ttk.Label(frame_run, text="Note: This tool will freeze once Create UI is clicked - this is normal, it is just generating the files in the background. A message will pop up once the UI packages have been generated.", wraplength=500).grid(row=last_row + 7, column=0, padx=5, pady=5, sticky="w")
    
    # --------------------------------- #
    # GUI RIGHT SIDE: UI preview image
    # --------------------------------- #
    preview_frame = ttk.Frame(root)
    preview_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

    preview_frame.grid_rowconfigure(0, weight=1)
    preview_frame.grid_columnconfigure(0, weight=1)

    image_label = tk.Label(
        preview_frame,
        text="Click 'Show Preview' to see what the UI will look like",
        background="lightgray",
        anchor="center",
        width=756,
        height=756
    )
    image_label.grid(row=0, column=0, sticky="nsew")

    # Get all the box borders to be the same width
    input_frame.grid_columnconfigure(0, weight=1)
    frame_ui_name.grid(sticky="ew")
    frame_basic.grid(sticky="ew")
    frame_detailed.grid(sticky="ew")
    frame_run.grid(sticky="ew")

    root.mainloop()
