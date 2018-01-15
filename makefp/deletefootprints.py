# Delete all modules except for known faceplate modules
# 
# Todo: perhaps we could set an attribute of each module
# that tells what its faceplate equivlent is
# Then delete everything without this attribute
#
# execfile("/Users/dann/Google Drive/4ms/kicad-pcb/_script/makefp/deletefootprints.py")
# execfile("/Users/design/gdrive/4ms/kicad-pcb/_script/makefp/deletefootprints.py")

#footprint_lib = "/Users/dann/Google Drive/4ms/kicad-pcb/_lib/lib-footprints/4ms_Faceplate.pretty"
footprint_lib = "/Users/design/gdrive/4ms/kicad-pcb/_lib/lib-footprints/4ms_Faceplate.pretty"

footprint_convert={
'ROTENC-12MM-BUT': 'FaceplateHole_Encoder_290',
'SPDT-SUB': 'FaceplateHole_SubMiniToggle',
'RGB_ROTARY_ENCODER': 'FaceplateHole_EncoderRGB_NoBushing',
'RGB-SPST-LED-TC002': 'FaceplateHole_RGBLEDButton',
'PJ301M-12': 'FaceplateHole_Jack_260',
'PJ366ST': 'FaceplateHole_Jack_260',
'LED-PLCC4': 'FaceplateHole_Lightpipe_WithMaskOpening',

'LED-C1-A2-3MM-VERT': 'FaceplateHole_LED3mm',
'LED_D3.0mm-3': 'FaceplateHole_LED3mm',
'LED-3MM-SQUARE-ANODE': 'FaceplateHole_LED3mm',

'POT-SLIDER-LED-ALPHA-RA2045F-20': 'FaceplateHole_Slider25mm_Slot',
'16MM-RV16AF-4A': 'FaceplateHole_Pot16mm',
'POT-9MM-ALPHA': 'FaceplateHole_Pot9mm',
'Slide_Switch_SS22D06-G6-H_Runrun': 'Slide_Switch_SS22D06-G6-H_Runrun_faceplate',
'SWITCHCRAFT-STEREO-SW_with_outline': 'FACEPLATE_HOLE_jack_quarter',

'FACEPLATE-Rail-mount-slot': 'FACEPLATE-Rail-mount-slot',
'FaceplateHole_SpacerMount_256': 'FaceplateHole_SpacerMount_256',
'FaceplateHole_FSR_slot': 'FaceplateHole_FSR_slot'
}

remove_fps = ['R0603', 'C0603', 'PAD-06']



import pcbnew
board = pcbnew.GetBoard()

io = pcbnew.PCB_IO()

SCALE = 1000000.0

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

# def find_net(netname_str):
# 	nets = board.GetNetsByName()
# 	found_neti = nets.find(netname_str)
# 	if (found_neti != nets.end()):
# 		found_net = found_neti.value()[1]
# 		return found_net
# 	else:
# 		print "Net name {} not found".format(netname_str)


def convert_and_delete_modules(midline, remove_layer=pcbnew.F_Cu):
    for m in board.GetModules():

		center = m.GetPosition()

		try:
			footpr = str(m.GetFPID().GetFootprintName())
		except:
			footpr = str(m.GetFPID().GetLibItemName())

		if footpr in footprint_convert:
			print "Found Back layer footprint: {} at {}mm,{}mm. Changing to {}".format(footpr, center.x/SCALE, center.y/SCALE, footprint_convert[footpr])
			faceplate_mod = io.FootprintLoad(footprint_lib, footprint_convert[footpr])

			# Reflect over midline y-axis
			new_x = midline - (center.x - midline)
			center.x = new_x
			faceplate_mod.SetPosition(center)

			# pads = faceplate_mod.Pads()
			# for pad in pads:
			# 	pad.SetNet(net)

			board.Add(faceplate_mod)


			board.Remove(m)
			continue

		if m.GetLayer() == remove_layer:
			board.Remove(m)
			continue

		if footpr in remove_fps:
			board.Remove(m)
			continue

		#print "Removing footprint: {} at {}mm,{}mm.".format(footpr, center.x/SCALE, center.y/SCALE)
		print "Unknown Back layer footprint: {} at {}mm,{}mm. Moving 200mm down ".format(footpr, center.x/SCALE, center.y/SCALE)
		center.y = center.y + int(2000.0*SCALE)
		center.x = 0
		m.SetPosition(center)


bbox = find_pcb_outline_bbox()
center = bbox.Centre()

# gndnet = find_net("GND")
#remove all other nets
#remove_all_nets_but("GND")

convert_and_delete_modules(center.x)


