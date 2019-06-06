##Installing the 4ms scripts as python plugins##

You can add these scripts to the PCB editor in KiCad 5 or higher.


1. Quit Kicad

2. Find the file which ends in the name “XXX_action.py”
This is a script that has been modified to work as a plug-in.

3. Copy this plugin file to the plugin directory:
   * **macOS/OSX:**  /User/[your username]/Library/Preferences/kicad/scripting/plugins/
   * **Windows:** C:\Users[your username]\AppData\Roaming\kicad\scripting\
   * **Linux:**  /usr/share/kicad/scripting/plugins/ or ~/.kicad-plugins

###Running a script:###

Open PCBnew and run the script by selecting it from the Tools > External Plugins… menu

Or in the latest versions you can go to PCBnew Preferences and enable plugins to show on the toolbar
