# Run this 1st.
# 1st: removetracks.py
# 2nd: boundbox.py
# 3rd: deletefootprints.py
# 4th: makezone.py
#
# Delete all tracks and drawings on F.Cu and B.Cu layers

import pcbnew

def find_pcb_outline_bbox(board):
    """Get the bounding box around all edge cuts drawings, and list of edge cuts drawings"""
    edgecuts_dwgs = []
    boundingbox = None
    for d in board.GetDrawings():
        if (d.GetLayerName() != "Edge.Cuts"):
            continue
        edgecuts_dwgs.append(d)
        if (boundingbox == None):
            boundingbox = d.GetBoundingBox()
        else:
            boundingbox.Merge(d.GetBoundingBox())
    boundingbox.Inflate(-150000) #assume a 0.15mm line width
    return boundingbox, edgecuts_dwgs


def move_drawings(dwgs_list, dest_layernum):
    for d in dwgs_list:
        d.SetLayer(dest_layernum)


# Calculate the HP
def find_width_to_hp(pcbwidth):
    HPs = ((1, 5.00), 
    (1.5, 7.50), 
    (2, 9.80), 
    (3, 15.0),
    (4, 20.0),
    (6, 30.0),
    (8, 40.30),
    (10, 50.50),
    (12, 60.60),
    (14, 70.80),
    (16, 80.90),
    (18, 91.30),
    (20, 101.30),
    (21, 106.30),
    (22, 111.40),
    (24, 121.50),
    (26, 131.60),
    (28, 141.90),
    (42, 213.00))

    for hp, width in HPs:
        if width>pcbwidth:
            #print("HP={}".format(hp))
            return hp,width
            break;

def delete_tracks_on_layer(layernum, board):
    for d in board.GetTracks():
        if (d.GetLayer() == layernum):
            board.Remove(d)

def delete_graphics_on_layer(layernum, board):
    for d in board.GetDrawings():
        if (d.GetLayer() == layernum):
            board.Remove(d)


class makefp_removetracks( pcbnew.ActionPlugin ):
    def defaults( self ):
        self.name = "Make Faceplate Step 1 - Remove Tracks"
        self.category = "Make Faceplate 1"
        self.description = "Removes tracks and graphics"

    def Run( self ):
        msg="Loading Board"
        msg+="\n"
        board = pcbnew.GetBoard()

        #remove all tracks
        delete_tracks_on_layer(pcbnew.F_Cu, board)
        msg+="Removed tracks on F_Cu" + "\n"

        delete_tracks_on_layer(pcbnew.B_Cu, board)
        msg+="Removed tracks on B_Cu" + "\n"

        delete_tracks_on_layer(pcbnew.In1_Cu, board)
        msg+="Removed tracks on In1_Cu" + "\n"

        delete_tracks_on_layer(pcbnew.In2_Cu, board)
        msg+="Removed tracks on In2_Cu" + "\n"

        delete_graphics_on_layer(pcbnew.F_Cu, board)
        msg+="Removed graphics on F_Cu" + "\n"

        delete_graphics_on_layer(pcbnew.B_Cu, board)
        msg+="Removed graphics on B_Cu" + "\n"

        delete_graphics_on_layer(pcbnew.F_SilkS, board)
        msg+="Removed graphics on F_SilkS" + "\n"

        delete_graphics_on_layer(pcbnew.B_SilkS, board)
        msg+="Removed graphics on B_SilkS" + "\n"

        msg+="\n"
        msg+="You may need to refresh the display now. Select Legacy mode, then Modern mode" + "\n"
        # frame = displayDialog(None)
        # frame.Center()
        # frame.setMsg(msg)
        # frame.ShowModal()
        # frame.Destroy()


makefp_removetracks().register()
