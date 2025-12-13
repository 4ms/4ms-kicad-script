import pcbnew
import os
import faceplate_footprint_lib

# --- Config ---
footprint_lib = faceplate_footprint_lib.get_lib_location()
SCALE = 1000000.0

# Map of original footprints → faceplate footprints
footprint_convert = {
    # POTS
    'TRIM-T73YE': 'Faceplate_Hole_Trim_3.175mm_With_Mask_Opening',
    'Potentiometer_Alps_RK09L_Double_Vertical': 'Faceplate_Hole_Pot_16mm',
    'Pot_16mm_21Det_RV16AF-4A': 'Faceplate_Hole_Pot_16mm',
    'Pot_16mm_NoDet_RV16AF-4A': 'Faceplate_Hole_Pot_16mm',
    'Pot_16mm_CtrDet_RV16AF-4A': 'Faceplate_Hole_Pot_16mm',
    'POT-9MM-ALPHA': 'Faceplate_Hole_Pot_9mm_Metal_Collar',
    'Pot_9mm_DShaft': 'Faceplate_Hole_Pot_9mm_Metal_Collar',
    'POT-9MM-SONGHUEI': 'Faceplate_Hole_Pot_9mm',
    'Pot_9mm_Knurl_Det': 'Faceplate_Hole_Pot_9mm',
    'Pot_9mm_Knurl_NoDet': 'Faceplate_Hole_Pot_9mm',
    '9mm_CtrDet_10k_DShaft': 'Faceplate_Hole_Pot_9mm',
    'Pot_9mm_Dshaft_Det': 'Faceplate_Hole_Pot_9mm',
    # SLIDERS
    'Pot_Slider_LED_20mm_RA2045F': 'Faceplate_Hole_Slider_25mm_Slot',
    'POT-SLIDER-LED-ALPHA-RA2045F-20': 'Faceplate_Hole_Slider_25mm_Slot',
    'POT-SLIDER-ALPHA-RA2045F-20': 'Faceplate_Hole_Slider_25mm_Slot',
    'Top-Up_60RFT2-B':'Faceplate_Hole_Top-Up_60RFT2-B',
    # ENCODERS
    'ENC_SPST_12mm': 'Faceplate_Hole_Encoder_290',
    'ENC_12mm_HollowShaft': 'Faceplate_Hole_Encoder_290',
    'ROTENC-12MM-BUT': 'Faceplate_Hole_Encoder_290',
    'RGB_ROTARY_ENCODER': 'Faceplate_Hole_Encoder_RGB_NoBushing',
    'ENC_RGB_SPST_12mm': 'Faceplate_Hole_Encoder_RGB_NoBushing',
    # JACKS
    'PJ301M-12': 'Faceplate_Hole_Jack_3.5mm',
    'PJ366ST': 'Faceplate_Hole_Jack_3.5mm',
    'EighthInch_PJ398SM': 'Faceplate_Hole_Jack_3.5mm',
    'EighthInch_Stereo_PJ366ST': 'Faceplate_Hole_Jack_3.5mm',
    'XLR-NCJ6FA-V-0': 'Faceplate_Hole_XLR_Quarter_Inch',
    # LEDS / LIGHTPIPES
    'LED-PLCC4': 'Faceplate_Hole_Lightpipe_With_Mask_Opening',
    'LED_PLCC-4': 'Faceplate_Hole_Lightpipe_With_Mask_Opening',
    'LED_0603_1608Metric': 'Faceplate_Hole_Lightpipe_With_Mask_Opening',
    'PLCC4': 'Faceplate_Hole_Lightpipe_With_Mask_Opening',
    'LED-C1-A2-3MM-VERT': 'Faceplate_Hole_LED_3mm',
    'LED_D3.0mm-3': 'Faceplate_Hole_LED_3mm',
    'LED-3MM-SQUARE-ANODE': 'Faceplate_Hole_LED_3mm',
    # BUTTONS / SWITCHES
    'SW_TH_Tactile_Omron_B3F-100x': 'Faceplate_Hole_ButtonTact_5mm',
    'Button_PB20B': 'Faceplate_Hole_Button_PB20',
    'Button_LED_PKS-01L-X': 'Faceplate_Hole_Button_PB20',
    'Switch_Toggle_SPDT_SubMini': 'Faceplate_Hole_SubMini_Toggle',
    'BUTTON-LED-PB61303': 'Faceplate_Hole_LED_Button_7mm_With_Mask_Opening',
    'RGB-SPST-LED-TC002': 'Faceplate_Hole_LED_Button_5.4mm_With_Mask_Opening',
    'Button_RgbLED_SPST_TC002': 'Faceplate_Hole_LED_Button_5.4mm_With_Mask_Opening'
}

# Full list of parts to remove
remove_fps = [
    'R0603', 'C0603', 'PAD-06', 'COIL', 'TSSOP', 'TSOT', 'SOT',
    'R_0402', 'C_0402', 'C_0603', 'C_1206', 'C_0805', 
    'CP_Elec_5x5.3', 'Pins', 'EighthInch', 'Button_SPST', 
    'Switch_SPST', 'NetTie', 'D_SOD-123', 'SW_TH_',
    'LED', 'Diode', 'Transistor', 'mp153'
]

# --- Helper Functions ---
def make_vec(x, y):
    try:
        return pcbnew.VECTOR2I(int(x), int(y))
    except:
        return pcbnew.wxPoint(int(x), int(y))

def find_pcb_outline_bbox(board):
    edgecuts = []
    bbox = None
    for d in board.GetDrawings():
        if d.GetLayerName() != "Edge.Cuts":
            continue
        edgecuts.append(d)
        if bbox is None:
            bbox = d.GetBoundingBox()
        else:
            bbox.Merge(d.GetBoundingBox())
    if bbox:
        bbox.Inflate(-150000)
    return bbox, edgecuts

def move_drawings(dwgs, layernum):
    for d in dwgs:
        d.SetLayer(layernum)

def delete_tracks_on_layer(layernum, board):
    for t in list(board.GetTracks()):
        if t.GetLayer() == layernum:
            board.Remove(t)

def delete_graphics_on_layer(layernum, board):
    for d in list(board.GetDrawings()):
        if d.GetLayer() == layernum:
            board.Remove(d)

def delete_all_tracks_and_graphics(board):
    msg = ""
    layers = [pcbnew.F_Cu, pcbnew.B_Cu, pcbnew.In1_Cu, pcbnew.In2_Cu,
              pcbnew.F_SilkS, pcbnew.B_SilkS]
    for layer in layers:
        delete_tracks_on_layer(layer, board)
        delete_graphics_on_layer(layer, board)
        msg += f"Removed tracks/graphics on layer {layer}\n"
    return msg

def make_faceplate_outline(board):
    msg = ""
    if not os.path.exists(footprint_lib):
        raise FileNotFoundError(f"Invalid footprint library path: {footprint_lib}")

    railmount_fp = "Faceplate_Rail_Mount_Slot_Plated"
    pcboutline, edgecuts = find_pcb_outline_bbox(board)
    if not pcboutline:
        return "No PCB outline found.\n"

    pcbcenter = pcboutline.Centre()
    move_drawings(edgecuts, pcbnew.Cmts_User)

    # Standard HP sizing
    HPs = [(1,5.0),(1.5,7.5),(2,9.8),(3,15.0),(4,20.0),(6,30.0),(8,40.3),(10,50.5),
           (12,60.6),(14,70.8),(16,80.9),(18,91.3),(20,101.3),(21,106.3),(22,111.4),
           (24,121.5),(26,131.6),(28,141.9),(42,213.0)]
    pcbwidth = pcboutline.GetWidth()/SCALE
    fphp, fpwidth = next(((hp,w) for hp,w in HPs if w>pcbwidth), HPs[-1])
    msg += f"Faceplate is {fphp} HP wide by 128.5mm high\n"

    fpleft = pcbcenter.x - fpwidth*SCALE/2
    fpright = fpleft + fpwidth*SCALE
    fpbottom = pcbcenter.y + 128.5*SCALE/2
    fptop = fpbottom - 128.5*SCALE

    corners = {
        'bl': make_vec(fpleft, fpbottom),
        'br': make_vec(fpright, fpbottom),
        'tl': make_vec(fpleft, fptop),
        'tr': make_vec(fpright, fptop)
    }

    for start,end in [('bl','br'),('tl','tr'),('tl','bl'),('tr','br')]:
        line = pcbnew.PCB_SHAPE(board)
        line.SetLayer(pcbnew.Edge_Cuts)
        line.SetStart(corners[start])
        line.SetEnd(corners[end])
        board.Add(line)

    # Railmount positions
    offsets = [(0.295,0.118),(-0.295,0.118),(0.295,-0.118),(-0.295,-0.118)]
    positions = [
        make_vec(corners['tl'].x + offsets[0][0]*25.4*SCALE, corners['tl'].y + offsets[0][1]*25.4*SCALE),
        make_vec(corners['tr'].x + offsets[1][0]*25.4*SCALE, corners['tr'].y + offsets[1][1]*25.4*SCALE),
        make_vec(corners['bl'].x + offsets[2][0]*25.4*SCALE, corners['bl'].y + offsets[2][1]*25.4*SCALE),
        make_vec(corners['br'].x + offsets[3][0]*25.4*SCALE, corners['br'].y + offsets[3][1]*25.4*SCALE)
    ]
    for pos in positions:
        mod = pcbnew.FootprintLoad(footprint_lib, railmount_fp)
        mod.SetPosition(pos)
        board.Add(mod)

    return msg

def get_fp_name(fp):
    try:
        return str(fp.GetFPID().GetLibItemName())
    except:
        try:
            return str(fp.GetFPID().GetFootprintName())
        except:
            return None

def remove_nonfp_footprints(board):
    msg = ""
    fps = list(board.GetFootprints())  # convert to list to safely remove
    for m in fps:
        footpr = get_fp_name(m)
        if footpr and any(rem.lower() in footpr.lower() for rem in remove_fps):
            board.Remove(m)
            msg += f"Removed footprint: {footpr}\n"
    return msg

def add_fp(center, footpr, board):
    msg = f"Found footprint {footpr}, adding {footprint_convert[footpr]}\n"
    faceplate_mod = pcbnew.FootprintLoad(footprint_lib, footprint_convert[footpr])
    faceplate_mod.SetPosition(center)
    board.Add(faceplate_mod)
    return msg

def convert_faceplate_footprints(board):
    msg = ""
    pcboutline,_ = find_pcb_outline_bbox(board)
    if pcboutline:
        midline = pcboutline.Centre().x
        for m in list(board.GetFootprints()):
            footpr = get_fp_name(m)
            if footpr in footprint_convert:
                center = m.GetPosition()
                center.x = midline - (center.x - midline)
                msg += add_fp(center, footpr, board)
    return msg

def remove_faceplate_footprints(board):
    msg = ""
    for m in list(board.GetFootprints()):
        footpr = get_fp_name(m)
        if footpr in footprint_convert:
            board.Remove(m)
            msg += f"Removed faceplate footprint: {footpr}\n"
    return msg

def make_ground_zone(board):
    msg = ""
    gnd_net = board.FindNet("GND")
    if not gnd_net:
        return "No GND net found.\n"

    # Assign all pads to GND
    for fp in board.GetFootprints():
        for pad in fp.Pads():
            pad.SetNet(gnd_net)

    # Get PCB outline
    pcboutline,_ = find_pcb_outline_bbox(board)
    if pcboutline:
        # Slight margin inside edge
        margin = pcbnew.FromMils(10)
        pcboutline.Inflate(-margin)

        # Create zone container
        zone = pcbnew.ZONE_CONTAINER(board)
        zone.SetLayer(pcbnew.B_Cu)
        zone.SetNet(gnd_net)
        zone.SetZoneClearance(pcbnew.FromMM(0.2))
        zone.SetMinThickness(pcbnew.FromMM(0.2))

        # Add outline points
        outline = pcbnew.SHAPE_POLY_SET()
        for corner in [(pcboutline.GetLeft(), pcboutline.GetTop()),
                       (pcboutline.GetRight(), pcboutline.GetTop()),
                       (pcboutline.GetRight(), pcboutline.GetBottom()),
                       (pcboutline.GetLeft(), pcboutline.GetBottom())]:
            outline.NewOutline()
            outline.Append(pcbnew.VECTOR2I(*corner))
        zone.Outline().Add(outline)

        board.Add(zone)

        # Fill zone
        filler = pcbnew.ZONE_FILLER(board)
        filler.Fill(zone)

        msg += "GND zone created and all pads assigned.\n"

    return msg

# --- Plugin ---
class make_eurorack_fp(pcbnew.ActionPlugin):
    def defaults(self):
        self.name = "Make Eurorack Faceplate"
        self.category = "Eurorack"
        self.description = "Creates a eurorack faceplate using 4ms faceplate library"

    def Run(self):
        board = pcbnew.GetBoard()
        msg = ""
        msg += delete_all_tracks_and_graphics(board)
        msg += make_faceplate_outline(board)
        msg += convert_faceplate_footprints(board)
        msg += remove_faceplate_footprints(board)
        msg += remove_nonfp_footprints(board)
        msg += make_ground_zone(board)
        pcbnew.Refresh()
        pcbnew.MessageBox(msg, "Eurorack Faceplate Info")

make_eurorack_fp().register()
