# Run this 1st.
# 1st: removetracks.py
# 2nd: boundbox.py
# 3rd: deletefootprints.py
# 4th: makezone.py
#
# Delete all tracks and drawings on F.Cu and B.Cu layers

#Dan's Home exe:
# execfile("/Users/dann/Google Drive/4ms/kicad-pcb/_script/makefp/removetracks.py")

#Dan's Work exe:
# execfile("/Users/design/4ms/kicad-pcb/_script/makefp/removetracks.py")

#Zach's exe:
# execfile("/Users/dag/Desktop/kicad/4ms-kicad-script/makefp/removetracks.py")

#Darcy's exe:
# execfile("/XXXXXXXXXXXXXXXXX/makefp/removetracks.py")

import pcbnew
board = pcbnew.GetBoard()

def delete_tracks_on_layer(layernum):
    for d in board.GetTracks():
        if (d.GetLayer() == layernum):
        	board.Remove(d)

def delete_graphics_on_layer(layernum):
    for d in board.GetDrawings():
        if (d.GetLayer() == layernum):
        	board.Remove(d)



#remove all tracks
delete_tracks_on_layer(pcbnew.F_Cu)
delete_tracks_on_layer(pcbnew.B_Cu)

delete_graphics_on_layer(pcbnew.F_Cu)
delete_graphics_on_layer(pcbnew.B_Cu)
delete_graphics_on_layer(pcbnew.F_SilkS)
delete_graphics_on_layer(pcbnew.B_SilkS)
