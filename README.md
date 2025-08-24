# Cloud UI Recolour Tool

## **What is this?**

Cloud UI Recolour Tool is a small program for The Sims 3 that lets you customise the colours (and opacity to some extent) of Cloud UI and generate your own package files to drop into your Mods folder. It works by replacing colour values in the original recolourable files used to create Cloud Pink UI.

You can select a preset theme (Light, Colourful or Dark mode) and a main colour to go along with it and see a preview of what it will look like in game. You can also customise individual colours even further in the Detailed Customisation section to tweak it exactly how you want it.

Once you’re happy with how it’s looking you can generate:

- The main UI package file
- Language logo package files (used for the startup loading screen if your game is not in English)
- Patches for various mods

## Requirements & Setup

- Windows only, sorry
- You need [Inkscape](https://inkscape.org/release/) installed for this to work (it’s free and used for exporting recoloured images)
- Download and unzip the Cloud UI Recolour Tool folder and the Base UI folder. Place the Base UI folder inside the Cloud UI Recolour Tool folder. I recommend placing the Cloud UI Recolour Tool folder on your desktop.
- Download [refpack_pipe.exe](https://github.com/p182/refpack-pipe/releases/tag/refpack-rust-5.0-optimal) and place it in the Cloud UI Recolour Tool folder. This is optional but highly recommended - it compresses the generated package file sizes. 

The Cloud UI Recolour Tool folder contains:

- **Cloud UI Recolour Tool.exe**: The program itself
- **PinkPlumbob.ico**: The icon used for the program
- **UI_Preview.svg**: The tool uses this to generate a preview of the UI using the currently selected colours
- **Credits - For Sharing**: Containing credits for this tool & the UI, helpful if you're uploading and sharing your custom UI

## **How to use**

#### Inkscape setup

1. Double click on Cloud UI Recolour Tool.exe to open the program
2. The first time you load it up you might see a window asking for the location of inkscape.exe. This will only appear if the tool was unable to locate it automatically. You will need to install Inkscape if you haven’t already, or click the ‘Browse…’ button to locate it on your computer. It is usually in C:/Program Files/Inkscape/bin/inkscape.exe, but this will vary depending on your computer.
3. Once Inkscape is located you will be taken to the main app window where you can start playing around with the UI colours.

### Main recolour window

#### Section 1:
Enter a name for your custom UI. This will be used to name your .package files when you click ‘Create UI’.

#### Section 2:
Select a preset (Light, Colourful or Dark) and a main accent colour. These will be used to generate a colour palette for your UI, and you can change them as many times as you want.

#### Section 3:
This step is optional, but if you want more control over specific parts of the UI you can click the ‘Show Detailed Controls’ button to see additional colours that you can edit. There is also an Opacity control at the bottom.

- **Main Font**: The main text colour in the UI
- **Darkest Accent, Dark Accent, Main Accent, Light Accent**: Accent colours used throughout the UI (e.g. the Pink shades used in Cloud Pink UI), I recommend keeping this in a Dark to Light colour gradient, but you can experiment with any colours
- **Background Light & Background Dark**: Colours used for the loading screens. Use the same colour in each if you don’t want a gradient effect.
- **HUD Background 1:** The background colour of the main sections of the UI, like the bottom left panel, dialog boxes etc.
- **HUD Background 2:** The puck colour (the control panel at the bottom left where the map view, walls up/down etc buttons are)
- **HUD Accent Light:** Generally used in places where text or images appear on top, e.g. wishes panel, notification text area.
- **HUD Accent Dark**: Generally used for buttons that are not selected, e.g. if you are in Live mode, the Build & Buy buttons will be this colour.
- **MISC**: Used for deselected tabs and other small miscellaneous items
- **Opacity**: Controls how transparent certain sections appear. Usually works in the same places as HUD Background 1, but not always.

#### Section 4:
The ‘Show Preview’ button generates an image preview of the UI using your currently selected colours. The image will appear on the right hand side of the tool. You can change colours and click ‘Show Preview’ as many times as you like.

Once you’ve settled on colours you can check or uncheck the checkboxes above ‘Create UI’.

- If ‘Generate language logos’ is checked, the tool will generate package files for each available language so that games not in english will show the recoloured The Sims 3 logo when the game is starting.
- If ‘Generate patches’ is selected, the tool will recolour any available patches in the Base UI/Patches folder. You will be able to pick and choose which ones to install once they’re created.
- If ‘Delete processing files’ is selected, the tool will automatically remove any temporary files used to create the UI. Only leave this unchecked if you want to make manual adjustments to the recoloured UI.

When you’re ready you can click ‘Create UI’ to generate your custom recoloured UI!

Please note that once ‘Create UI’ is clicked, the tool will freeze while it generates the UI. This is normal, and you will see a window pop up when it is finished. It takes around ~2 minutes on my higher-end PC, and ~12 minutes on my older PC - it may take longer or shorter depending on your computer, please be patient 🙂

## **How to install your custom UI mods**

When the tool is finished running, you will see a folder with your UI name on it inside Cloud UI Recolour Tool > Creations. This contains:

- {Your UI Name}_CloudUIv1.3.0.package: Your main UI mod, this can go straight into your Mods folder (either Packages or Overrides is fine).
- Colour_Selections.txt: A reference file with the colours you chose for the UI so you can re-create it later or send to someone else.
- A folder called Non English Logo Packages (if you checked the Generate language logos checkbox): If your game is not in English, locate the file with your language code on the end and put it in your Mods folder
- A folder called Patches (if you checked the ‘Generate patches’ checkbox): Locate the patches you want in your game and copy the package files into your Overrides folder. Please check the Read me.txt files for each mod before installing - some patches have special instructions, and some patches require the original mod for the patch to work. Information and links to the original mod is included in the Read me file. Not all patches are compatible with each other!

## **Known/Potential Issues**

**The tool might be flagged by antivirus or Microsoft Defender.** If this is the case you will need to add an exception and/or adjust your settings to allow the tool to run. If a popup comes up that says "Windows protected your PC", click the "More info" text and then "Run anyway".

**Some packages are not generating.** There is a file path character limit in Windows that can cause issues for this tool, because the UI elements for TS3 have very long names. Try moving the entire Cloud UI Recolour Tool folder to your Desktop - if you’re still missing packages after this then the issue is likely caused by something else.

**The UIs exported are not perfect!** I have tried my best to resolve as many issues as I could with the exported UIs, but this tool lets you choose any colours you like, and some colours might work better than others. There are also many many files to replace, so there are probably going to be mistakes in my original edits. Feel free to reach out if you find something particularly annoying! I will be occasionally updating the Base UI files when I make improvements or fix issues, so make sure you keep your Colour_Selections.txt file for your favourite generated UIs if you want to be able to update it later!

## **Information for modders/developers**

I will be writing up some info/tutorials when I get a chance, but if you’re a mod creator and would like to make a recolourable patch for your mod that works with this tool, feel free to reach out! I’m also happy to give you some details if you’re interested in building your own recolourable UI as well :)

## **Credits**

- [cowplantcartel](https://cowplantcartel.tumblr.com/) (me!) for building this tool and Cloud Pink UI which is used as a base for recolouring
- [p182](https://github.com/p182) provided the code in dbpf_writer_lib.py for this project, and also built [**refpack_pipe.exe**](https://github.com/p182/refpack-pipe) which compresses the package files. Thank you so much p182, I couldn't have done this without you!
- David_mtv, coregirl, momomomomoi, sidereus23 and sims3loveforlife for translations used in the loading screen text
- Arro, Butterbot, Cmar, xFairyExterminatorx, LazyDuchess and gamefreak130 for creating the original mods used to create the Patches in this tool
- emelie.ikj for the loading screen text base files
- Everyone who used the previous iterations of Cloud UI and sent feedback. This really just started with me wanting to build myself a cute pink UI, but you all inspired me to keep it going 💕

## Final Notes

You are welcome to upload and share your creations from the tool (and tag me if you want to - I’d love to see what you make!), but please don’t stick it behind a paywall, and remember to credit those whose work has gone into this tool. There is a Credits file inside the Cloud UI Recolour Tool folder that you can copy and paste :)