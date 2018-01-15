# Create a EdgeCuts box centered around existing EdgeCuts
#     Height=5.059in
#     Width = smallest HP size possible (from A-100 tech specs lookup table)
# Then move the existing EdgeCuts to Cmts.User
#
# execfile("/Users/dann/Google Drive/4ms/kicad-pcb/_script/makefp/boundbox.py")
# execfile("/Users/design/gdrive/4ms/kicad-pcb/_script/makefp/boundbox.py")

#footprint_lib = "/Users/dann/Google Drive/4ms/kicad-pcb/_lib/lib-footprints/4ms_Faceplate.pretty"
footprint_lib = "/Users/design/gdrive/4ms/kicad-pcb/_lib/lib-footprints/4ms_Faceplate.pretty"
railmount_fp = "FACEPLATE-Rail-mount-slot"

import pcbnew
board = pcbnew.GetBoard()
io = pcbnew.PCB_IO()

SCALE = 1000000.0

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


def find_pcb_outline_bbox():
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
    for hp, width in HPs:
        if width>pcbwidth:
            #print("HP={}".format(hp))
            return width
            break;

# Find the pcb outline and a list of the drawings on the edgecuts layer
pcboutline, edgecuts_dwgs = find_pcb_outline_bbox()

# Find the center of the pcb outline
pcbcenter = pcboutline.Centre()

# Move the previous edge cuts to comments layer
move_drawings(edgecuts_dwgs, pcbnew.Cmts_User)


# Set the fp width to the smallest standard HP size that's larger than the pcb width
pcbwidth = pcboutline.GetWidth()
fpwidth = find_width_to_hp(pcbwidth/SCALE)

# Calculate the left and right edges of the faceplate
fpleft = pcbcenter.x - fpwidth*SCALE/2.0
fpright = fpleft + fpwidth*SCALE

# Calculate the top and bottom edges of the faceplate (128.5mm height)
fpbottom = pcbcenter.y + 128.5*SCALE/2.0
fptop = fpbottom - 128.5*SCALE

# Calculate the four corners
bottomleft = pcbnew.wxPoint(int(fpleft), int(fpbottom))
bottomright = pcbnew.wxPoint(int(fpright), int(fpbottom))
topleft = pcbnew.wxPoint(int(fpleft), int(fptop))
topright = pcbnew.wxPoint(int(fpright), int(fptop))

# Draw the board outline segments
bottomline = pcbnew.DRAWSEGMENT(board)
board.Add(bottomline)
bottomline.SetLayer(pcbnew.Edge_Cuts)
bottomline.SetStart(bottomleft)
bottomline.SetEnd(bottomright)

topline = pcbnew.DRAWSEGMENT(board)
board.Add(topline)
topline.SetLayer(pcbnew.Edge_Cuts)
topline.SetStart(topleft)
topline.SetEnd(topright)

leftline = pcbnew.DRAWSEGMENT(board)
board.Add(leftline)
leftline.SetLayer(pcbnew.Edge_Cuts)
leftline.SetStart(topleft)
leftline.SetEnd(bottomleft)

rightline = pcbnew.DRAWSEGMENT(board)
board.Add(rightline)
rightline.SetLayer(pcbnew.Edge_Cuts)
rightline.SetStart(topright)
rightline.SetEnd(bottomright)

#add rail mount slots
railmount_topleft = pcbnew.wxPoint(topleft.x + 0.295*25.4*SCALE, topleft.y + 0.118*25.4*SCALE)
railmount_topright = pcbnew.wxPoint(topright.x - 0.295*25.4*SCALE, topright.y + 0.118*25.4*SCALE)
railmount_bottomleft = pcbnew.wxPoint(bottomleft.x + 0.295*25.4*SCALE, bottomleft.y - 0.118*25.4*SCALE)
railmount_bottomright = pcbnew.wxPoint(bottomright.x - 0.295*25.4*SCALE, bottomright.y - 0.118*25.4*SCALE)

mod = io.FootprintLoad(footprint_lib, railmount_fp)
mod.SetPosition(railmount_topleft)
board.Add(mod)

mod = io.FootprintLoad(footprint_lib, railmount_fp)
mod.SetPosition(railmount_topright)
board.Add(mod)

mod = io.FootprintLoad(footprint_lib, railmount_fp)
mod.SetPosition(railmount_bottomleft)
board.Add(mod)

mod = io.FootprintLoad(footprint_lib, railmount_fp)
mod.SetPosition(railmount_bottomright)
board.Add(mod)
