# Create a EdgeCuts box centered around existing EdgeCuts
#     Height=5.059in
#     Width = smallest HP size possible (from A-100 tech specs lookup table)
# Then delete the existing EdgeCuts

import pcbnew
board = pcbnew.GetBoard()

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


def create_layer_table():
    numlayers = pcbnew.PCB_LAYER_ID_COUNT
    for i in range(numlayers):
        layertable[board.GetLayerName(i)] = i
    return layertable


# Get the bounding box around the edge cuts
def find_pcb_outline_bbox():
    rect = None
    for d in board.GetDrawings():
        if (d.GetLayerName() != "Edge.Cuts"):
            continue
        if (rect == None):
            rect = d.GetBoundingBox()
        else:
            rect.Merge(d.GetBoundingBox())
    rect.Inflate(-150000) #assume a 0.15mm line width
    return rect


# Calculate the HP
def find_width_to_hp(pcbwidth):
    for hp, width in HPs:
        if width>pcbwidth:
            #print("HP={}".format(hp))
            return width
            break;

#def remove_inner_edgecuts(bottomleft, topright):

#Create the layer table
layertable=create_layer_table()

# Find the center of the pcb outline
pcboutline = find_pcb_outline_bbox()
pcbcenter = pcboutline.Centre()


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
bottomline.SetLayer(layertable['Edge.Cuts'])
bottomline.SetStart(bottomleft)
bottomline.SetEnd(bottomright)

topline = pcbnew.DRAWSEGMENT(board)
board.Add(topline)
topline.SetLayer(layertable['Edge.Cuts'])
topline.SetStart(topleft)
topline.SetEnd(topright)

leftline = pcbnew.DRAWSEGMENT(board)
board.Add(leftline)
leftline.SetLayer(layertable['Edge.Cuts'])
leftline.SetStart(topleft)
leftline.SetEnd(bottomleft)

rightline = pcbnew.DRAWSEGMENT(board)
board.Add(rightline)
rightline.SetLayer(layertable['Edge.Cuts'])
rightline.SetStart(topright)
rightline.SetEnd(bottomright)
