# Run this 4th
#

#Dan's Home exe:
# execfile("/Users/dann/Google Drive/4ms/kicad-pcb/_script/makefp/makezone.py")

#Dan's Work exe:
# execfile("/Users/design/4ms/kicad-pcb/_script/makefp/makezone.py")

#Zach's exe:
# execfile("/Users/dag/Desktop/kicad/4ms-kicad-script/makefp/makezone.py")

#Darcy's exe:
# execfile("/XXXXXXXXXXXXXXX/makefp/makezone.py")

#todo: set zone pad connections to "Solid" instead of "Thermal Relief"

import pcbnew
board = pcbnew.GetBoard()
SCALE = 1000000.0

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

pcboutline.Inflate(-1 * pcbnew.FromMils(10))
leftside = pcboutline.GetLeft()
rightside = pcboutline.GetRight()
bottomside = pcboutline.GetBottom()
topside = pcboutline.GetTop()

print "Creating copper pour on GND: top={} bottom={} left={} right={}".format(topside/SCALE, bottomside/SCALE, leftside/SCALE, rightside/SCALE)

zone_container = board.InsertArea(gndnet.GetNet(), 0, pcbnew.B_Cu, leftside, topside, pcbnew.CPolyLine.DIAGONAL_EDGE)
shape_poly_set = zone_container.Outline()
shape_poly_set.Append(leftside, bottomside);
shape_poly_set.Append(rightside, bottomside);
shape_poly_set.Append(rightside, topside);
zone_container.SetPadConnection(pcbnew.PAD_ZONE_CONN_FULL);
zone_container.Hatch()
