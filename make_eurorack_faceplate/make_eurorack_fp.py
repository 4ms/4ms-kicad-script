import pcbnew
import faceplate_footprint_lib
footprint_lib = faceplate_footprint_lib.get_lib_location()

msg = ""
SCALE = 1000000.0

footprint_convert={
    # POTS
    'TRIM-T73YE': 'Faceplate_Hole_Trim_3.175mm_With_Mask_Opening',

    'Potentiometer_Alps_RK09L_Double_Vertical': 'Faceplate_Hole_Pot_16mm',

    'Potentiometer_Alpha_RV112_Dual_Vert': 'Faceplate_Hole_Pot_16mm',
    'Potentiometer_Alpha_RV112_Dual_Vert_Knurled': 'Faceplate_Hole_Pot_16mm',

    '16MM-RV16AF-4A': 'Faceplate_Hole_Pot_16mm',
    'Pot_16mm_21Det_RV16AF-4A': 'Faceplate_Hole_Pot_16mm',
    'Pot_16mm_NoDet_RV16AF-4A': 'Faceplate_Hole_Pot_16mm',
    'Pot_16mm_CtrDet_RV16AF-4A': 'Faceplate_Hole_Pot_16mm',

    'POT-9MM-ALPHA': 'Faceplate_Hole_Pot_9mm_Metal_Collar',
    'Pot_9mm_DShaft': 'Faceplate_Hole_Pot_9mm_Metal_Collar',
    'Pot_9mm_DShaft_Det': 'Faceplate_Hole_Pot_9mm_Metal_Collar',
    '9mm_CtrDet_10k_DShaft': 'Faceplate_Hole_Pot_9mm_Metal_Collar',

    'POT-9MM-SONGHUEI': 'Faceplate_Hole_Pot_9mm',
    'Pot_9mm_Knurl_Det': 'Faceplate_Hole_Pot_9mm',
    'Pot_9mm_Knurl_NoDet': 'Faceplate_Hole_Pot_9mm',
    '9mm_CtrDet_10k_DShaft': 'Faceplate_Hole_Pot_9mm',
    'Pot_9mm_Dshaft_Det': 'Faceplate_Hole_Pot_9mm',

    # SLIDERS:
    'Pot_Slider_LED_20mm_RA2045F': 'Faceplate_Hole_Slider_25mm_Slot',
    'POT-SLIDER-LED-ALPHA-RA2045F-20': 'Faceplate_Hole_Slider_25mm_Slot',
    'POT-SLIDER-ALPHA-RA2045F-20': 'Faceplate_Hole_Slider_25mm_Slot',
    'Top-Up_60RFT2-B':'Faceplate_Hole_Top-Up_60RFT2-B',

    # ENCODERS: 
    'ENC_SPST_12mm': 'Faceplate_Hole_Encoder_290',
    'ENC_12mm_HollowShaft': 'Faceplate_Hole_Encoder_290',
    'ENC_SPST_12mm_NUDGED': 'Faceplate_Hole_Encoder_290',
    # Alternative: 
    #'ENC_SPST_12mm_NUDGED': 'Faceplate_Hole_Encoder_KnurledShaft_Alpha'
    
    'ROTENC-12MM-BUT': 'Faceplate_Hole_Encoder_290',
    'RGB_ROTARY_ENCODER': 'Faceplate_Hole_Encoder_RGB_NoBushing',
    'ENC_RGB_SPST_12mm': 'Faceplate_Hole_Encoder_RGB_NoBushing',
    'ENC_RGB_SPST_12mm_NUDGED': 'Faceplate_Hole_Encoder_RGB_NoBushing',

    # JACKS:
    'PJ301M-12': 'Faceplate_Hole_Jack_3.5mm',
    'PJ366ST': 'Faceplate_Hole_Jack_3.5mm',
    'PJ301M-12-FIX': 'Faceplate_Hole_Jack_3.5mm',
    'EighthInch_PJ398SM': 'Faceplate_Hole_Jack_3.5mm',
    'EighthInch_Stereo_PJ366ST': 'Faceplate_Hole_Jack_3.5mm',
    'Barrel_Vert_PJ064': 'Faceplate_Hole_Jack_Barrel_315',
    'EighthInch_PJ398SM_Alt-GND': 'Faceplate_Hole_Jack_3.5mm',
    'XLR-NCJ6FA-V-0': 'Faceplate_Hole_XLR_Quarter_Inch',
    
    # LEDS AND LIGHTPIPES:
    'LED-PLCC4': 'Faceplate_Hole_Lightpipe_With_Mask_Opening',
    'LED_PLCC-4': 'Faceplate_Hole_Lightpipe_With_Mask_Opening',
    'LED_0603_1608Metric': 'Faceplate_Hole_Lightpipe_With_Mask_Opening',
    'PLCC4': 'Faceplate_Hole_Lightpipe_With_Mask_Opening',
    'LED-C1-A2-3MM-VERT': 'Faceplate_Hole_LED_3mm',
    'LED_D3.0mm-3': 'Faceplate_Hole_LED_3mm',
    'LED-3MM-SQUARE-ANODE': 'Faceplate_Hole_LED_3mm',
    'LED-T1X2': 'Faceplate_Hole_LED_3mm',
    'LED-T1': 'Faceplate_Hole_LED_3mm',
    'LED_3mm_C1A2': 'Faceplate_Hole_LED_3mm',
    'LED_3mm_C1A2_Polarity_Indicator': 'Faceplate_Hole_LED_3mm',

    # FLIP SWITCHES
    'Switch_Toggle_SPDT_Mini_SolderLug': 'Switch_Toggle_Mini_6.35mm_With_Mask_Opening',
    'SPDT-SUB': 'Faceplate_Hole_SubMini_Toggle',
    'Switch_Toggle_SPDT_SubMini': 'Faceplate_Hole_SubMini_Toggle',

    # BUTTONS:
    'Button_PB20B': 'Faceplate_Hole_Button_PB20',
    'Button_LED_PKS-01L-X': 'Faceplate_Hole_Button_PB20',
    'BUTTON-LED-PB61303': 'Faceplate_Hole_LED_Button_7mm_With_Mask_Opening',
    'RGB-SPST-LED-TC002': 'Faceplate_Hole_LED_Button_5.4mm_With_Mask_Opening',
    'Button_RgbLED_SPST_TC002': 'Faceplate_Hole_LED_Button_5.4mm_With_Mask_Opening',
    'Button_LED_PB61303_Adjusted+': 'Faceplate_Hole_LED_Button_7mm_With_Mask_Opening',
    'Button_LED_PB61303': 'Faceplate_Hole_LED_Button_7mm_With_Mask_Opening',
    'Button_RgbLED_SPST_PB615303HL-7mm': 'Faceplate_Hole_LED_Button_7mm_With_Mask_Opening',

    # SLIDE SWITCHES
    'Slide_Switch_SS22D06-G6-H_Runrun': 'Faceplate_Slide_Switch_SS22D06_Runrun',
    'Slide_Switch_Runrun_SS22D06': 'Faceplate_Slide_Switch_SS22D06_Runrun',
    'SWITCHCRAFT-STEREO-SW_with_outline': 'Faceplate_Hole_Jack_Quarter_Inch',

    # SPACERS/MOUNTS/SLOTS
    'Faceplate_Rail_Mount_Slot': 'Faceplate_Rail_Mount_Slot',
    'Faceplate_Hole_Spacer_Mount_256': 'Faceplate_Hole_Spacer_Mount_256',
    'Faceplate_Hole_FSR_slot': 'Faceplate_Hole_FSR_slot',
    'MountingHole_WurthElektronik_WA-SNTI':'Faceplate_Hole_Spacer_Mount_M3',

    'last_item': 'last_item'
}

remove_fps = ['R0603', 'C0603', 'PAD-06', 'SOT-363_SC-70-6', 'SOT23-3_PO132', 'R_0402', 'R_0603', 'C_0402', 'C_0603', 'C_1206', 'C_0805','CP_Elec_5x5.3', 'R_0805_2012Metric',
              'TSSOP-8_4.4x3mm_Pitch0.65mm', 'TSSOP-14_4.4x5mm_P0.65mm', 'SSOP-10_3.9x4.9mm_P1.00mm','TSSOP-28_4.4x9.7mm_Pitch0.65mm','QFN-48-1EP_7x7mm_P0.5mm_EP5.6x5.6mm','TSSOP-20_4.4x6.5mm_P0.65mm','SOIC-8_3.9x4.9mm_Pitch1.27mm','SOT-23-THIN-16','QFN-32-1EP_4x4mm_P0.4mm_EP2.65x2.65mm',
              'D_SOD-323F', 'TSOT-23-5', 'D_SOD-123', 'D_SMA', 'FA-238', 'NetTie-2_SMD_Pad0.5mm', 'Button_Tact_PTS540', 'L_Taiyo-Yuden_NR-40xx', 
              'BGA-54_8.0x8.0mm_P0.8', 'BGA-144_07X07MM_P0.5', 'TSOT-23-6',
              'Pins_2x05_2.54mm_TH_EurorackPower','Pins_2x05_2.54mm_TH_Europower', 'Pins_2x04_2.54mm_TH', 'Pins_1x04_2.54mm_TH_SWD', 'Pins_1x03_2.54mm_TH_AudioOutsRGndL', 'Pins_1x03_2.54mm_TH_AudioInsRGndL', 'Pins_2x08_2.54mm_TH_EuroPower', 'Socket_2x05_2.54mm_TH', 'Pins_1x03_2.54mm_TH', 'Pins_1x02_2.54mm_TH',
              'DIP-8pin_TH', 'R_Axial_DIN0204_L3.6mm_D1.6mm_P5.08mm_Horizontal', 'C_Disc_P2.54mm', 'CP_Radial_P2.5mm', 'D_DO-35_P7.62mm_Horizontal', 'C_Disc_P5.08mm',
              '4msLogo_15.5x6.6mm', '4ms-logo-4', '4msLogo_3.8x1.7mm','NetTie-2_SMD_Pad0.16mm_6mil']


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
            return hp,width


def make_vec(x, y):
    test = pcbnew.PCB_SHAPE(pcbnew.GetBoard())
    try:
        #Kicad 7
        vec = pcbnew.VECTOR2I(int(x), int(y))
        test.SetStart(vec)
    except:
        #Kicad 6
        vec = pcbnew.wxPoint(int(x), int(y))
        test.SetStart(vec)
    return vec


def find_pcb_outline_bbox(board):
    """Get the bounding box around all edge cuts drawings, and list of edge cuts drawings"""
    edgecuts_dwgs = []
    boundingbox = None

    for d in board.GetDrawings():
        if (d.GetLayerName() != "Edge.Cuts"):
            continue
        edgecuts_dwgs.append(d)

        if boundingbox is None:
            boundingbox = d.GetBoundingBox()
        else:
            boundingbox.Merge(d.GetBoundingBox())

    if boundingbox is not None:
        boundingbox.Inflate(-150000) #assume a 0.15mm line width

    return boundingbox, edgecuts_dwgs


def move_drawings(dwgs_list, dest_layernum):
    for d in dwgs_list:
        d.SetLayer(dest_layernum)


def delete_tracks_on_layer(layernum, board):
    for d in board.GetTracks():
        if (d.GetLayer() == layernum):
            board.Remove(d)


def delete_graphics_on_layer(layernum, board):
    for d in board.GetDrawings():
        if (d.GetLayer() == layernum):
            board.Remove(d)


def delete_all_tracks_and_graphics(board):
    global msg
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


def make_faceplate_outline(board):
    global msg
    global SCALE

    railmount_fp = "Faceplate_Rail_Mount_Slot_Plated"

    # Find the pcb outline and a list of the drawings on the edgecuts layer
    pcboutline, edgecuts_dwgs = find_pcb_outline_bbox(board)

    # Find the center of the pcb outline
    pcbcenter = pcboutline.Centre()

    # Move the previous edge cuts to comments layer
    move_drawings(edgecuts_dwgs, pcbnew.Cmts_User)

    # Set the fp width to the smallest standard HP size that's larger than the pcb width
    pcbwidth = pcboutline.GetWidth()
    fphp, fpwidth = find_width_to_hp(pcbwidth/SCALE)

    msg+="Faceplate is %d HP wide by 128.5mm high\n" % fphp

    # Calculate the left and right edges of the faceplate
    fpleft = pcbcenter.x - fpwidth*SCALE/2.0
    fpright = fpleft + fpwidth*SCALE

    # Calculate the top and bottom edges of the faceplate (128.5mm height)
    fpbottom = pcbcenter.y + 128.5*SCALE/2.0
    fptop = fpbottom - 128.5*SCALE

    # Calculate the four corners
    bottomleft = make_vec(int(fpleft), int(fpbottom))
    bottomright = make_vec(int(fpright), int(fpbottom))
    topleft = make_vec(int(fpleft), int(fptop))
    topright = make_vec(int(fpright), int(fptop))

    # Draw the board outline segments
    bottomline = pcbnew.PCB_SHAPE(board)
    board.Add(bottomline)
    bottomline.SetLayer(pcbnew.Edge_Cuts)
    bottomline.SetStart(bottomleft)
    bottomline.SetEnd(bottomright)

    topline = pcbnew.PCB_SHAPE(board)
    board.Add(topline)
    topline.SetLayer(pcbnew.Edge_Cuts)
    topline.SetStart(topleft)
    topline.SetEnd(topright)

    leftline = pcbnew.PCB_SHAPE(board)
    board.Add(leftline)
    leftline.SetLayer(pcbnew.Edge_Cuts)
    leftline.SetStart(topleft)
    leftline.SetEnd(bottomleft)

    rightline = pcbnew.PCB_SHAPE(board)
    board.Add(rightline)
    rightline.SetLayer(pcbnew.Edge_Cuts)
    rightline.SetStart(topright)
    rightline.SetEnd(bottomright)

    #add rail mount slots
    railmount_topleft = make_vec(int(topleft.x + 0.295*25.4*SCALE), int(topleft.y + 0.118*25.4*SCALE))
    railmount_topright = make_vec(int(topright.x - 0.295*25.4*SCALE), int(topright.y + 0.118*25.4*SCALE))
    railmount_bottomleft = make_vec(int(bottomleft.x + 0.295*25.4*SCALE), int(bottomleft.y - 0.118*25.4*SCALE))
    railmount_bottomright = make_vec(int(bottomright.x - 0.295*25.4*SCALE), int(bottomright.y - 0.118*25.4*SCALE))

    mod = pcbnew.FootprintLoad(footprint_lib, railmount_fp)
    mod.SetPosition(railmount_topleft)
    board.Add(mod)

    mod = pcbnew.FootprintLoad(footprint_lib, railmount_fp)
    mod.SetPosition(railmount_topright)
    board.Add(mod)

    mod = pcbnew.FootprintLoad(footprint_lib, railmount_fp)
    mod.SetPosition(railmount_bottomleft)
    board.Add(mod)

    mod = pcbnew.FootprintLoad(footprint_lib, railmount_fp)
    mod.SetPosition(railmount_bottomright)
    board.Add(mod)

def get_fp_name(fp):
    try:
        footpr = str(fp.GetFPID().GetLibItemName())
    except:
        try:
            footpr = str(fp.GetFPID().GetFootprintName())
        except:
            footpr = None
    return footpr


def remove_all_footprints_on_layer(layername, brd):
    msg=""
    fps = brd.GetFootprints()
    for m in fps:
        if m.GetLayerName() == layername:
            if get_fp_name(m).startswith("Faceplate_"):
                continue
            result = brd.Remove(m)
            msg+="Removed {}, ".format(result)
    return msg


def remove_nonfp_footprints(brd):
    msg=""
    fps = brd.GetFootprints()
    for m in fps:
        footpr = get_fp_name(m)
        if footpr is None:
            continue

        if footpr in remove_fps:
            brd.Remove(m) 
            msg+="Removed footprint on Remove List: {}".format(footpr)
    return msg
    

def add_fp(center, footpr, brd):
    msg="Found Back layer footprint: {} at {}mm,{}mm. Changing to {}".format(footpr, center.x/SCALE, center.y/SCALE, footprint_convert[footpr])
    msg+="\n"
    faceplate_mod = pcbnew.FootprintLoad(footprint_lib, footprint_convert[footpr])
    faceplate_mod.SetPosition(center)
    brd.Add(faceplate_mod)
    return msg


def convert_faceplate_footprints(brd):
    msg=""

    # Find the pcb outline and a list of the drawings on the edgecuts layer
    pcboutline, _ = find_pcb_outline_bbox(brd)
    midline = pcboutline.Centre().x

    fps = brd.GetFootprints()
    for m in fps:
        footpr = get_fp_name(m)
        # try:
        #     footpr = str(m.GetFPID().GetLibItemName())
        # except:
        #     footpr = str(m.GetFPID().GetFootprintName())

        if footpr in footprint_convert:
            # Reflect over midline y-axis
            center = m.GetPosition()
            new_x = midline - (center.x - midline)
            center.x = new_x
            msg+=add_fp(center, footpr, brd)
            #brd.Remove(m)
            continue
        
        msg+="Footprint not in list: {}".format(footpr)+"\n"

    return msg


def remove_faceplate_footprints(brd):
    msg=""
    fps = brd.GetFootprints()
    for m in fps:
        footpr = get_fp_name(m)
        # try:
        #     footpr = str(m.GetFPID().GetLibItemName())
        # except:
        #     footpr = str(m.GetFPID().GetFootprintName())

        if footpr in footprint_convert:
            brd.Remove(m)
            continue
        
        msg+="Footprint Removed: {}".format(footpr)+"\n"

    return msg


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


def make_ground_zone(board):
    global msg

    gndnet = find_net("GND", board)
    if gndnet is None:
        return
        #TODO: create a new net

    set_all_pads_to_net(gndnet, board)

    pcboutline, _ = find_pcb_outline_bbox(board)

    pcboutline.Inflate(-1 * pcbnew.FromMils(10))
    leftside = pcboutline.GetLeft()
    rightside = pcboutline.GetRight()
    bottomside = pcboutline.GetBottom()
    topside = pcboutline.GetTop()

    msg+="Creating copper pour on GND: top={} bottom={} left={} right={}".format(topside/SCALE, bottomside/SCALE, leftside/SCALE, rightside/SCALE)

    zone_container = board.AddArea(None, gndnet.GetNetCode(), pcbnew.B_Cu, make_vec(leftside, topside), pcbnew.ZONE_FILL_MODE_POLYGONS)
    shape_poly_set = zone_container.Outline()
    shape_poly_set.Append(leftside, bottomside)
    shape_poly_set.Append(rightside, bottomside)
    shape_poly_set.Append(rightside, topside)
    zone_container.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL)


class make_eurorack_fp( pcbnew.ActionPlugin ):
    def defaults( self ):
        self.name = "Make Eurorack Faceplate"
        self.category = "Make Eurorack Faceplate"
        self.description = "Creates a eurorack faceplate using 4ms faceplate library"

    def Run( self ):
        msg="Loading Board"
        msg+="\n"
        board = pcbnew.GetBoard()

        delete_all_tracks_and_graphics(board)
        make_faceplate_outline(board)
        msg+=convert_faceplate_footprints(board)
        msg+=remove_faceplate_footprints(board)
        msg+=remove_nonfp_footprints(board)
        make_ground_zone(board)

make_eurorack_fp().register()

