import colorsys
from struct import unpack
import tkinter as tk
from tkinter import colorchooser, messagebox
import subprocess
import re

# --------------------------------- #
# Colour functions
# --------------------------------- #

# Convert HEX code to RGB
def hex_to_rgb_string(hex_color):
    hex_color = hex_color.lstrip("#")
    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    return f"rgb({r},{g},{b})"

# For the chosen main accent colour, generate 1 lighter shade and two darker shades
def generate_shades(input_hex):
    # convert input HEX to RGB then HLS
    hex_color = input_hex.lstrip("#")
    r, g, b = int(hex_color[0:2], 16)/255.0, int(hex_color[2:4], 16)/255.0, int(hex_color[4:6], 16)/255.0
    h, l_orig, s = colorsys.rgb_to_hls(r, g, b)

    l_light = min(l_orig + 0.1, 1)
    l_dark = max(0, l_orig - 0.1)
    l_darkest = max(0, l_orig - 0.2)

    # convert back to RGB and then HEX
    r_light, g_light, b_light = colorsys.hls_to_rgb(h, l_light, s)
    r_dark, g_dark, b_dark = colorsys.hls_to_rgb(h, l_dark, s)
    r_darkest, g_darkest, b_darkest = colorsys.hls_to_rgb(h, l_darkest, s)

    r_light = int(r_light * 255)
    g_light = int(g_light * 255)
    b_light = int(b_light * 255)

    r_dark = int(r_dark * 255)
    g_dark = int(g_dark * 255)
    b_dark = int(b_dark * 255)

    r_darkest = int(r_darkest * 255)
    g_darkest = int(g_darkest * 255)
    b_darkest = int(b_darkest * 255)

    hex_light = f"#{r_light:02x}{g_light:02x}{b_light:02x}"
    hex_dark = f"#{r_dark:02x}{g_dark:02x}{b_dark:02x}"
    hex_darker = f"#{r_darkest:02x}{g_darkest:02x}{b_darkest:02x}"

    shades = [hex_light, input_hex, hex_dark, hex_darker]
    return shades

# Lighten a hex colour by 50% - used for HUD Accent Light
def lighten_hex_50(hex_code):
    # Convert hex to RGB
    hex_code = hex_code.lstrip('#')
    
    r = int(hex_code[0:2], 16) / 255.0
    g = int(hex_code[2:4], 16) / 255.0
    b = int(hex_code[4:6], 16) / 255.0

    # Convert RGB to HLS
    h, l, s = colorsys.rgb_to_hls(r, g, b)

    # Lighten by 50%
    l = l + (1.0 - l) * 0.5
    l = min(l, 1.0)

    # Convert back to RGB
    r, g, b = colorsys.hls_to_rgb(h, l, s)

    # Convert to hex
    return '#{:02X}{:02X}{:02X}'.format(int(r * 255), int(g * 255), int(b * 255)).lower()

# Invert colour - used for fonts
def invert_hex(hex_color):
    hex_color = hex_color.lstrip('#')

    # Convert to RGB
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)

    # Invert each channel
    inverted_r = 255 - r
    inverted_g = 255 - g
    inverted_b = 255 - b

    # Convert back to hex
    return '#{:02x}{:02x}{:02x}'.format(inverted_r, inverted_g, inverted_b)

# --------------------------------- #
# GUI functions
# --------------------------------- #

# Create a colour picker 
def color_chooser(entry, color_preview):
    def pick_color():
        current = entry.get()
        try:
            rgb, hex_color = colorchooser.askcolor(current)
            if hex_color:
                entry.delete(0, tk.END)
                entry.insert(0, hex_color)
                color_preview.config(bg=hex_color)
        except Exception:
            pass
    return pick_color

# Check if a path contains a working version of inkscape.exe
def is_valid_inkscape(path):
    try:
        result = subprocess.run(
            [path, "--version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=5
        )
        return result.returncode == 0 and "Inkscape" in result.stdout
    except Exception:
        return False

# Enforce hex structure
def validate_hex_input(value):
    if value == "":
        return True
    if not value.startswith("#"):
        value = "#" + value
    return bool(re.fullmatch(r"#([0-9a-fA-F]{0,6})", value))

# Ensure there is always a # in front of hex
def enforce_hash_prefix(event, preview=None):
    widget = event.widget
    val = widget.get()
    if val and not val.startswith("#"):
        widget.delete(0, tk.END)
        widget.insert(0, "#" + val)
    if preview:
        # Manually update preview color after modifying the entry text
        val = widget.get()
        if re.fullmatch(r"#([0-9a-fA-F]{6})", val):
            preview.config(bg=val)

# Ensure opacity can only be between 0 and 1
def validate_opacity(value):
    if value == "":
        return True  # Allow empty so user can delete
    try:
        val = float(value)
        return 0.0 <= val <= 1.0
    except ValueError:
        return False
    
# Check that hex and opacity inputs are valid when attempting to use them
def validate_all_inputs(input_ui_name, input_entries):
    invalid_fields = []

    # Validate hex fields (except Opacity)
    for label, entry in input_entries.items():
        val = entry.get().strip()
        if label == "Opacity":
            if val == "":
                invalid_fields.append(f"{label} (must be a number between 0 and 1)")
        else:
            if val == "":
                invalid_fields.append(f"{label} (cannot be blank)")
            elif not re.fullmatch(r"#([0-9a-fA-F]{6})", val):
                invalid_fields.append(f"{label} (invalid hex code)")

    # Validate UI Name
    ui_name = input_ui_name.get().strip()
    invalid_chars = r'<>:"/\\|?*'

    if any(char in ui_name for char in invalid_chars):
        invalid_fields.append(f'UI Name (contains invalid characters: {invalid_chars})')

    # Show error message if there are any invalid fields
    if invalid_fields:
        messagebox.showerror(
            "Invalid Input",
            "Please fix the following field(s):\n\n" + "\n".join(invalid_fields)
        )
        return False

    return True

# --------------------------------- #
# Recolouring tools
# --------------------------------- #

# Get width and height of a PNG image
def get_png_dimensions(file_path):
    with open(file_path, "rb") as f:
        f.read(8)  # Skip PNG header
        if f.read(4) != b'\x00\x00\x00\r':
            raise ValueError("Invalid PNG length")
        if f.read(4) != b'IHDR':
            raise ValueError("Invalid PNG: missing IHDR")
        width = unpack(">I", f.read(4))[0]
        height = unpack(">I", f.read(4))[0]
    return width, height

# Recolour SVG or LAYOUT files
def recolour_files(file_input_path, colour_replacements, file_output_path):
    # Read in file to recolour
    with open(file_input_path, "r", encoding="utf-8") as file:
        file_contents = file.read()

    # Replace HEX and/or RGB codes with desired colours
    regex_files = [(re.compile(old, re.IGNORECASE), new) for old, new in colour_replacements.items()]
    for pattern, new in regex_files:
        file_contents = pattern.sub(new, file_contents)        

    # Save recoloured file  
    with open(file_output_path, "w", encoding="utf-8") as file:
        file.write(file_contents)

# Export PNG from SVG
def export_png(inkscape_path, input_path, output_path):    
    subprocess.run([
                inkscape_path,
                str(input_path),
                "--export-type=png",
                f"--export-filename={output_path}"
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# Save input choices to file
def save_choices(choices, location):
    with open(location / "Colour_Selections.txt", "w") as f:
        for k, v in choices.items():
            print(f"{k}: {v}", file=f)
