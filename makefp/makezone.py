# execfile("/Users/dann/Google Drive/4ms/kicad-pcb/_script/makefp/makezone.py")

import pcbnew
board = pcbnew.GetBoard()

def find_net(netname_str):
	nets = board.GetNetsByName()
	found_neti = nets.find(netname_str)
	if (found_neti != nets.end()):
		found_net = found_neti.value()[1]
		return found_net
	else:
		print "Net name {} not found".format(netname_str)


def set_all_pads_to_net(net):
	for m in board.GetModules():
		pads = m.Pads()
		for pad in pads:
			pad.SetNet(net)

def find_pcb_outline_bbox():
    """Get the bounding box around all edge cuts drawings"""
    boundingbox = None
    for d in board.GetDrawings():
        if (d.GetLayerName() != "Edge.Cuts"):
            continue
        if (boundingbox == None):
            boundingbox = d.GetBoundingBox()
        else:
            boundingbox.Merge(d.GetBoundingBox())
    boundingbox.Inflate(-150000) #assume a 0.15mm line width
    return boundingbox


gndnet = find_net("GND")
set_all_pads_to_net(gndnet)

pcboutline = find_pcb_outline_bbox()
pcbwidth = pcboutline.GetWidth()

# Calculate the left and right edges of the faceplate
fpleft = pcbcenter.x - pcbwidth*SCALE/2.0
fpright = fpleft + pcbwidth*SCALE

# Calculate the top and bottom edges of the faceplate (128.5mm height)
fpbottom = pcbcenter.y + 128.5*SCALE/2.0
fptop = fpbottom - 128.5*SCALE

# Calculate the four corners
bottomleft = pcbnew.wxPoint(int(fpleft), int(fpbottom))
bottomright = pcbnew.wxPoint(int(fpright), int(fpbottom))
topleft = pcbnew.wxPoint(int(fpleft), int(fptop))
topright = pcbnew.wxPoint(int(fpright), int(fptop))


zone_container = board.InsertArea(gndnet.GetNet(), 0, pcbnew.B_Cu, topleft.x, topleft.y, pcbnew.CPolyLine.DIAGONAL_EDGE)
shape_poly_set = zone_container.Outline()
shape_poly_set.Append(topright.x, topright.y);
shape_poly_set.Append(bottomright.x, bottomright.y);
shape_poly_set.Append(bottomleft.x, bottomleft.y);
shape_poly_set.Append(topleft.x, topleft.y);
#shape_poly_set.CloseLastContour()
zone_container.Hatch()


