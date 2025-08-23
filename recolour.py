import os
import re
import shutil
import time
from concurrent.futures import ThreadPoolExecutor
from itertools import repeat
from tkinter import messagebox
from utils import recolour_files, export_png, get_png_dimensions, save_choices
from dbpf_writer_lib import create_dbpf_package, read_resources

def run_recolour(ui_path, ui_name, replacements_layout, replacements_svg, inkscape_path, colour_values, run_logos, run_patches, run_processing):
    print("# ----- Starting recolour.py script ----- #")

    start = time.time()

    # Required file paths
    input_path = ui_path / "Base UI"
    ui_folder = ui_path / "Creations" / ui_name
    processing_folder = ui_folder / "Processing"
    svg_path = processing_folder / "SVG Files"
    output_path = processing_folder / "Output Files"
    language_logos = processing_folder / "Language Logos"
    language_custom_svg = language_logos / "SVG Custom Replacements"
    language_english_svg = language_logos / "SVG English Replacements"
    language_png = language_logos / "PNG"
    logo_packages = ui_folder / "Non English Logo Packages"
    patches_input = input_path / "Patches"
    patches_processing = processing_folder / "Patches"
    patches_output = ui_folder / "Patches"

    # Remove folder if it already exists
    if ui_folder.exists() and ui_folder.is_dir():
        shutil.rmtree(ui_folder)

    # Create missing folders
    for p in [ui_folder, processing_folder, svg_path, output_path, language_logos, language_custom_svg, language_english_svg, language_png, patches_processing]:
        p.mkdir(parents=True, exist_ok=True)

    # Save colour choices to output file
    print("- Saving Colour_Selections.txt")
    save_choices(choices=colour_values, location=ui_folder)
    
    # --------------------------------- #
    # MAIN UI
    # --------------------------------- #

    if True:
        print("# ----- Running main UI section ----- #")
        # Grab all .layo, .xml, .stbl and .svg file paths
        text_files = list(input_path.rglob("*.xml")) + list(input_path.rglob("*.stbl"))
        layout_files = [f for f in input_path.rglob("*.layout") if "Logos - All languages" not in f.parts and "Patches" not in f.parts] 
        svg_files = [f for f in input_path.rglob("*.svg") if "Logos - All languages" not in f.parts and "Patches" not in f.parts]   

        # Grab the Base UI version number
        print("- Loading base UI verison number")
        cloudUI_version_path = input_path / "CLOUD UI VERSION.txt"
        if cloudUI_version_path.is_file():
            cloudUI_version = cloudUI_version_path.read_text(encoding="utf-8").strip()
        else:
            print("Version file not found")
            cloudUI_version = ""

        # Copy XML/STBL if needed
        print("- Copying .xml and .stbl files")
        for f in text_files:
            dest = output_path / f.name
            if not dest.exists() or f.stat().st_mtime > dest.stat().st_mtime:
                shutil.copy(f, dest)   
        
        # Recolour and copy .layout files
        print("- Recolouring .layout files")
        for layout in layout_files:
            recolour_files(layout, replacements_layout, output_path / layout.name)     

        # Recolour svg and store them in svg folder
        print("- Recolouring .svg files")
        for svg in svg_files:
            recolour_files(svg, replacements_svg, svg_path / svg.name) 
        
        # Export svg to png
        print("- Exporting .png files")
        svg_files = list(svg_path.glob("*.svg"))
        png_paths = [output_path / svg.with_suffix(".png").name for svg in svg_files]

        with ThreadPoolExecutor() as executor:
            executor.map(export_png, repeat(inkscape_path), svg_files, png_paths)    

        # Occasionally an export from svg to png can fail
        # Identify missing .pngs and export them again
        input_svg_files = [f for f in svg_path.rglob("*.svg") if "Logos - All languages" not in f.parts and "Patches" not in f.parts]   
        input_svg_files = [f.stem for f in input_svg_files]

        output_png_files = [f for f in output_path.rglob("*.png") if "Language Logos" not in f.parts]   
        output_png_files = [f.stem for f in output_png_files]

        # Missing png files
        for filename in input_svg_files:
            if filename not in output_png_files:
                print("- Error exporting " + filename + " from .svg to .png. Attempting to re-export.")
                missing_input = svg_path / (filename + ".svg")
                missing_output = output_path / (filename + ".png")
                export_png(inkscape_path, missing_input, missing_output)

        output_png_files = [f for f in output_path.rglob("*.png") if "Language Logos" not in f.parts]   
        output_png_files = [f.stem for f in output_png_files]

        # Notify user if there are still missing images even after re-exporting
        missing_files = [f for f in input_svg_files if f not in output_png_files]
        if len(missing_files)>0:
            missing_str = "\n".join(missing_files)
            messagebox.showerror("Error", f"Missing files:\n{missing_str}")
        else:
            print("- No missing output files identified")

        # Create .package file
        print("- Generating UI .package file")
        resource_data = read_resources(output_path)
        output_package_file = ui_folder / f"{ui_name.replace(" ", "")}_CloudUI{cloudUI_version}.package"

        try:    
            create_dbpf_package(output_package_file, resource_data)
        except Exception as e:    
            print(f"\n!!! An error occurred during package creation: {e}")

    # --------------------------------- #
    # LANGUAGE LOGOS
    # Used in the startup loading screen in non-English games
    # --------------------------------- #

    if run_logos==True:

        print("# ----- Running language logos section ----- #")

        # Create missing folders
        for p in [logo_packages]:
            p.mkdir(parents=True, exist_ok=True)

        # Logos: Non-English Replacements
        customReplacements_path = input_path / "Loading Screen - Startup/Logos - All languages/Non English Replacements"
        svg_files_customReplacements = list(customReplacements_path.rglob("*.svg"))

        # Logos: English Replacements - png files
        englishReplacements_path = input_path / "Loading Screen - Startup/Logos - All languages/English Replacements"
        englishReplacements = list(englishReplacements_path.rglob("*.png"))

        # Logos: English Replacements - svg template files
        englishReplacementsTemplates_path = input_path / "Loading Screen - Startup/Logos - All languages"
        englishReplacementsTemplates = list(englishReplacementsTemplates_path.glob("*.svg"))

        # Recolour english replacement templates
        print("- Recolouring english replacement language logos")
        englishReplacements_path_outputs = language_english_svg
        for svg in englishReplacementsTemplates:
            recolour_files(svg, replacements_svg, englishReplacements_path_outputs / svg.name) 

        # Export templates to png
        print("- Exporting to .png")
        png_output_path = language_png
        svg_files = list(englishReplacements_path_outputs.glob("*.svg"))
        png_paths = [englishReplacements_path_outputs / svg.with_suffix(".png").name for svg in svg_files]

        with ThreadPoolExecutor() as executor:
            executor.map(export_png, repeat(inkscape_path), svg_files, png_paths)  

        # Match english logos to correct png size and copy with new file name
        print("- Recolouring english language logos")
        for original_logo in englishReplacements:
            w, h = get_png_dimensions(original_logo)
            match_name = f"Logo_{w}x{h}.png"
            match_path = englishReplacements_path_outputs / match_name
            if match_path.exists():
                shutil.copy(match_path, png_output_path / original_logo.name)

        # Recolour all Non English replacements
        print("- Recoluring custom language logos")
        customReplacements_path_outputs = language_custom_svg
        for svg in svg_files_customReplacements:
            recolour_files(svg, replacements_svg, customReplacements_path_outputs / svg.name) 

        # Export svg to png
        print("- Exporting custom language logos to .png")
        png_output_path = language_png
        svg_files = list(customReplacements_path_outputs.glob("*.svg"))
        png_paths = [png_output_path / svg.with_suffix(".png").name for svg in svg_files]

        with ThreadPoolExecutor() as executor:
            executor.map(export_png, repeat(inkscape_path), svg_files, png_paths)  

        # Create .package files
        print("- Generating langauge logo .package files")

        # Collect all language codes, e.g. de_de
        pattern = re.compile(r"_([a-z]{2}_[a-z]{2})%%\+IMAG\.png$", re.IGNORECASE)
        language_codes = set()
        for file in language_png.glob("*.png"):
            match = pattern.search(file.name)
            if match:
                language_codes.add(match.group(1).lower())

        # Create a package file for each language
        for lang_code in sorted(language_codes):
            images = [f for f in language_png.iterdir() if f.is_file() and lang_code in f.name]

            # create temp folder to store images in
            p = processing_folder / "temp"
            p.mkdir(parents=True, exist_ok=True)

            # copy files into temp folder
            for image_file in images:
                shutil.copy(image_file, p)
            
            resource_data = read_resources(p)
            output_package_file = logo_packages / f"{ui_name.replace(" ", "")}_languageLogos_{lang_code}.package"

            try:    
                create_dbpf_package(output_package_file, resource_data)
            except Exception as e:    
                print(f"\n!!! An error occurred during package creation: {e}")

            shutil.rmtree(p) # delete folder when done

    # --------------------------------- #
    # COMPATIBILITY PATCHES
    # Optional patches to add/remove elements from cloud UI
    # --------------------------------- #

    if run_patches==True:

        print("# ----- Running compatibility patches section ----- #")

        # Create missing folders
        for p in [patches_output]:
            p.mkdir(parents=True, exist_ok=True)

        # For each patch in the Base UI/Patches folder, copy and recolour everything and generate a .package
        available_patches = [p for p in patches_input.iterdir() if p.is_dir()]
        for patch in available_patches:   

            # create matching folders in Processing/Patches/Patch Name AND Creations/UI Name/Patches/Patch Name
            folder_name = patch.name
            print("- Creating patch for: " + folder_name)
            folder_processing = patches_processing / folder_name
            folder_output = patches_output / folder_name
            folder_processing.mkdir(parents=True, exist_ok=True)
            folder_output.mkdir(parents=True, exist_ok=True)

            # Copy readme file to output folder if it exists
            print("- Copying readme file if it exists")
            patch_readme = patch / "Read me.txt"
            if patch_readme.exists():
                destination_folder = folder_output / "Read me.txt"
                shutil.copy(patch_readme, destination_folder)

            # Copy other files to processing folder if any exist
            print("- Copying other files if they exist, e.g. not .svg or .layout")
            patch_other_files = [
                f for f in patch.iterdir()    
                if f.is_file() and f.suffix not in [".svg", ".layout"] and f.name != "Read me.txt"]
            
            for file in patch_other_files:
                if file.exists():
                    destination_folder = folder_processing / file.name
                    shutil.copy(file, destination_folder)

            # Recolour the layo files
            print("- Recolouring .layout files")
            patch_layo_files = [f for f in patch.glob("*.layout")]
            for layout in patch_layo_files:
                recolour_files(layout, replacements_layout, folder_processing / layout.name) 

            # Recolour and export the svg files
            print("- Recolouring and exporting .svg files")
            patch_svg_files = [f for f in patch.glob("*.svg")]
            for svg in patch_svg_files:
                patch_svg_path = folder_processing / svg.name
                recolour_files(svg, replacements_svg, patch_svg_path) 
                export_png(inkscape_path, patch_svg_path, patch_svg_path.with_suffix(".png"))
                patch_svg_path.unlink(missing_ok=True)

            # Grab all the patch files in processing and export package
            print("- Generate patch .package")
            resource_data = read_resources(folder_processing)
            output_package_file = folder_output / f"addon_{ui_name.replace(" ", "")}_{folder_name.replace(" ", "")}.package"

            try:    
                create_dbpf_package(output_package_file, resource_data)
            except Exception as e:    
                print(f"\n!!! An error occurred during package creation: {e}")

    print("# ----- Export(s) completed ----- #")
    if run_processing==True:
        shutil.rmtree(processing_folder) # delete folder when done
    
    # Popup window to notify about completion
    elapsed = time.time() - start
    minutes, seconds = divmod(elapsed, 60)

    if minutes >= 1:
        elapsed_str = f"{int(minutes)} min {int(seconds)} sec"
    else:
        elapsed_str = f"{int(seconds)} sec"

    os.startfile(ui_folder) # open UI folder

    messagebox.showinfo(
        "Done!",
        f"A folder containing your custom UI and other helpful files has been opened for you. "
        f"Copy the relevant .package files from this folder into your Mods folder.\n\n"
        f"You can find all the custom UIs you've created by navigating to Cloud UI Recolour Tool > Creations.\n\n"
        f"UI export completed in {elapsed_str}."
    )
