# Delete all modules except for known faceplate modules
# 
# Todo: perhaps we could set an attribute of each module
# that tells what its faceplate equivlent is



# execfile("/Users/dann/Google Drive/4ms/kicad-pcb/_script/makefp/deletefootprints.py")
# execfile("/Users/design/gdrive/4ms/kicad-pcb/_script/makefp/deletefootprints.py")


footprint_convert = {
'ROTENC-12MM-BUT'					: 'FaceplateHole_Encoder_290',
'SPDT-SUB'							: 'FaceplateHole_SubMiniToggle',
'RGB_ROTARY_ENCODER'				: 'FaceplateHole_EncoderRGB_NoBushing',
'RGB-SPST-LED-TC002'				: 'FaceplateHole_RGBLEDButton',
'PJ301M-12'							: 'FaceplateHole_Jack_260',
'PJ366ST'							: 'FaceplateHole_Jack_260',
'LED-PLCC4'							: 'FaceplateHole_Lightpipe_WithMaskOpening',

'LED-C1-A2-3MM-VERT'				: 'FaceplateHole_LED3mm',
'LED_D3.0mm-3'						: 'FaceplateHole_LED3mm',
'LED-3MM-SQUARE-ANODE'				: 'FaceplateHole_LED3mm',

'POT-SLIDER-LED-ALPHA-RA2045F-20'	: 'FaceplateHole_Slider25mm_Slot',
'16MM-RV16AF-4A'					: 'FaceplateHole_Pot16mm',
'POT-9MM-ALPHA'						: 'FaceplateHole_Pot9mm',
'Slide_Switch_SS22D06-G6-H_Runrun'	: 'Slide_Switch_SS22D06-G6-H_Runrun_faceplate',
'SWITCHCRAFT-STEREO-SW_with_outline': 'FACEPLATE_HOLE_jack_quarter',

'FACEPLATE-Rail-mount-slot'			: 'FACEPLATE-Rail-mount-slot',
'FaceplateHole_SpacerMount_256'		: 'FaceplateHole_SpacerMount_256',
'FaceplateHole_FSR_slot'			: 'FaceplateHole_FSR_slot'
}

remove_footprints = ['R0603', 'C0603', 'PAD-06']

import os
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

def convert_and_delete_modules(midline, lib_uri, remove_layer=pcbnew.F_Cu):
    for m in board.GetModules():

		center = m.GetPosition()

		try:
			footpr = str(m.GetFPID().GetFootprintName())
		except:
			footpr = str(m.GetFPID().GetLibItemName())

		if footpr in footprint_convert:
			print "Found Back layer footprint: {} at {}mm,{}mm. Changing to {}".format(footpr, center.x/SCALE, center.y/SCALE, footprint_convert[footpr])
			faceplate_mod = io.FootprintLoad(lib_uri, footprint_convert[footpr])

			# Reflect over midline y-axis
			new_x = midline - (center.x - midline)
			center.x = new_x
			faceplate_mod.SetPosition(center)

			board.Add(faceplate_mod)
			board.Remove(m)
			continue

		if m.GetLayer() == remove_layer:
			board.Remove(m)
			continue

		if footpr in remove_footprints:
			board.Remove(m)
			continue

		print "Unknown Back layer footprint: {} at {}mm,{}mm. Moving 200mm down ".format(footpr, center.x/SCALE, center.y/SCALE)
		center.y = center.y + pcbnew.FromMM(2000)
		center.x = 0
		m.SetPosition(center)

def find_footprint_uri(libnickname):
	"""Attempts to find the uri of the given footprint library nickname 
		in the local and global fp-lib-table files.
		Returns the uri in the first occurance of (name "libnickname")
		by first searching the local, then the global fp-lib-table.
		Returns None if not found."""

	boardpath = os.path.dirname(board.GetFileName())
	start_of_uri_entry = "(uri \""
	end_of_uri_entry = "\")"

	#Search local fp-lib-table
	local_libtab_path = os.path.join(boardpath, "fp-lib-table")
	if os.path.exists(local_libtab_path):
		f = open(local_libtab_path,'r')
		for line in f:
			if line.find("(name {})".format(libnickname)) != -1:
				start = line.find(start_of_uri_entry) + len(start_of_uri_entry)
				end = line.find(end_of_uri_entry, start)
				uri = line[start:end]
				f.close()
				return uri
	f.close()

	#Search global fp-lib-table
	libtab_path = os.path.join(pcbnew.GetKicadConfigPath(), "fp-lib-table")
	if os.path.exists(libtab_path):
		f = open(libtab_path,'r')
		for line in f:
			if line.find("(name {})".format(libnickname)) != -1:
				start = line.find(start_of_uri_entry) + len(start_of_uri_entry)
				end = line.find(end_of_uri_entry, start)
				uri = line[start:end]
				found = True
				f.close()
				return uri

	f.close()
	return None #library not found


bbox = find_pcb_outline_bbox()
board_midline = bbox.Centre().x

lib_uri = find_footprint_uri("4ms_Faceplate")

convert_and_delete_modules(board_midline, lib_uri)


