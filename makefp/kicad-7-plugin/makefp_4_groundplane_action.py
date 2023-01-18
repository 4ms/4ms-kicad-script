# Run this 4th

#todo: set zone pad connections to "Solid" instead of "Thermal Relief"

import pcbnew

def find_net(netname_str, brd):
    nets = brd.GetNetsByName()
    try:
        found_neti = nets.find(netname_str)
        if (found_neti != nets.end()):
            found_net = found_neti.value()[1]
            return found_net
    except:
        return None


def set_all_pads_to_net(net, brd):
    ms = brd.GetFootprints()
    for m in ms:
        pads = m.Pads()
        for pad in pads:
            pad.SetNet(net)

def find_pcb_outline_bbox(brd):
    """Get the bounding box around all edge cuts drawings"""
    boundingbox = None
    ds = brd.GetDrawings()
    for d in ds:
        if (d.GetLayerName() != "Edge.Cuts"):
            continue
        if (boundingbox == None):
            boundingbox = d.GetBoundingBox()
        else:
            boundingbox.Merge(d.GetBoundingBox())
    boundingbox.Inflate(-150000) #assume a 0.15mm line width
    return boundingbox


class makefp_makegroundzone( pcbnew.ActionPlugin ):
    def defaults( self ):
        self.name = "Make Faceplate Step 4 - Make Ground Plane"
        self.category = "Make Faceplate 4"
        self.description = "Create a ground plane on the back and connect all pads to it"

    def Run( self ):
        SCALE = 1000000.0

        msg="Loading Board\n"
        board = pcbnew.GetBoard()

        gndnet = find_net("GND", board)
        if gndnet == None:
            return
            #TODO: create a new net

        set_all_pads_to_net(gndnet, board)

        pcboutline = find_pcb_outline_bbox(board)

        pcboutline.Inflate(-1 * pcbnew.FromMils(10))
        leftside = pcboutline.GetLeft()
        rightside = pcboutline.GetRight()
        bottomside = pcboutline.GetBottom()
        topside = pcboutline.GetTop()

        msg+="Creating copper pour on GND: top={} bottom={} left={} right={}".format(topside/SCALE, bottomside/SCALE, leftside/SCALE, rightside/SCALE)

        zone_container = board.AddArea(None, gndnet.GetNetCode(), pcbnew.B_Cu, pcbnew.VECTOR2I(leftside, topside), pcbnew.ZONE_FILL_MODE_POLYGONS)
        shape_poly_set = zone_container.Outline()
        shape_poly_set.Append(leftside, bottomside)
        shape_poly_set.Append(rightside, bottomside)
        shape_poly_set.Append(rightside, topside)
        zone_container.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL)


makefp_makegroundzone().register()
