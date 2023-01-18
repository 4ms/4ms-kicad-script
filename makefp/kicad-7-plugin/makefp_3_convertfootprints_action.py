# Run this 3rd
# 
#
# Delete all modules except for known faceplate modules
# 
# Todo: perhaps we could set an attribute of each module
# that tells what its faceplate equivlent is
# Then delete everything without this attribute

import pcbnew
import wx

import faceplate_footprint_lib
footprint_lib = faceplate_footprint_lib.get_lib_location()

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

    # ENCODERS: 
    'ENC_SPST_12mm': 'Faceplate_Hole_Encoder_290',
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

    # FLIP SWITCHES
    'Switch_Toggle_SPDT_Mini_SolderLug': 'Switch_Toggle_Mini_6.35mm_With_Mask_Opening',
    'SPDT-SUB': 'Faceplate_Hole_SubMini_Toggle',
    'Switch_Toggle_SPDT_SubMini': 'Faceplate_Hole_SubMini_Toggle',

    # BUTTONS:
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

    'last_item': 'last_item'
}
remove_fps = ['R0603', 'C0603', 'PAD-06', 'SOT-363_SC-70-6', 'SOT23-3_PO132', 'R_0603', 'C_0603', 'C_1206', 'C_0805']

def find_pcb_outline_bbox(board):
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
#   nets = board.GetNetsByName()
#   found_neti = nets.find(netname_str)
#   if (found_neti != nets.end()):
#       found_net = found_neti.value()[1]
#       return found_net
#   else:
#       print "Net name {} not found".format(netname_str)

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
            brd.Remove(m) #<<< this causes a crash!
            msg+="Removed footprint on Exclude List: {}".format(footpr)
    return msg
    
def add_fp(center, footpr, brd):
        msg="Found Back layer footprint: {} at {}mm,{}mm. Changing to {}".format(footpr, center.x/SCALE, center.y/SCALE, footprint_convert[footpr])
        msg+="\n"
        faceplate_mod = pcbnew.FootprintLoad(footprint_lib, footprint_convert[footpr])
        faceplate_mod.SetPosition(center)
        # pads = faceplate_mod.Pads()
        # for pad in pads:
        #   pad.SetNet(net)
        brd.Add(faceplate_mod)
        print(msg)
        return msg

def convert_faceplate_footprints(brd):
    msg=""

    midline = find_pcb_outline_bbox(brd).Centre().x

    fps = brd.GetFootprints()
    for m in fps:
        center = m.GetPosition()
        try:
            footpr = str(m.GetFPID().GetLibItemName())
        except:
            footpr = str(m.GetFPID().GetFootprintName())

        if footpr in footprint_convert:
            # Reflect over midline y-axis
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
        try:
            footpr = str(m.GetFPID().GetLibItemName())
        except:
            footpr = str(m.GetFPID().GetFootprintName())

        if footpr in footprint_convert:
            brd.Remove(m)
            continue
        
        msg+="Footprint Removed: {}".format(footpr)+"\n"

    return msg


class makefp_convertfootprints( pcbnew.ActionPlugin ):
    def defaults( self ):
        self.name = "Make Faceplate Step 3 - Convert Footprints"
        self.category = "Make Faceplate 3"
        self.description = "Converts footprints on back to faceplate footprints. Deletes all others"

    def Run( self ):
        msg="Loading Board\n"
        board = pcbnew.GetBoard()

        # gndnet = find_net("GND")
        #remove all other nets
        #remove_all_nets_but("GND")

        #TODO: repeat this until it returns ''
        #Workaround: use kicad's filter selection tool to select all tracks and vias and zones
        #also delete all graphics and text
        #msg+=remove_all_footprints_on_layer("F.Cu", board)

        #Crashes, but doesn't crash if you do board.Remove(m) one at a time from console
        #Workaround: hide back footprints in Kicad, then select all and delete
        #then one-by-one select any remaining back layer components (caps, resistors, etc)
        #msg+=remove_nonfp_footprints(board)


        msg+=convert_faceplate_footprints(board)

        msg+=remove_faceplate_footprints(board)

        msg+="\n"
        msg+="You may need to refresh the display now. Select Legacy mode, then Modern mode" + "\n"

makefp_convertfootprints().register()
