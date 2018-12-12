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

class displayDialog(wx.Dialog):
    """
    The default frame
    http://stackoverflow.com/questions/3566603/how-do-i-make-wx-textctrl-multi-line-text-update-smoothly
    """

    #----------------------------------------------------------------------
    #def __init__(self):
    #    """Constructor"""
    #    wx.Frame.__init__(self, None, title="Display Frame", style=wx.DEFAULT_FRAME_STYLE, wx.ICON_INFORMATION)
    #    panel = wx.Panel(self)
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, id=-1, title="Plugin Output")#
        #, style=wx.DEFAULT_DIALOG_STYLE, wx.ICON_INFORMATION) 
        #, style=wx.DEFAULT_DIALOG_STYLE, wx.ICON_INFORMATION)
        #, pos=DefaultPosition, size=DefaultSize, style = wx.DEFAULT_FRAME_STYLE & (~wx.MAXIMIZE_BOX), name="fname")
        #, wx.ICON_INFORMATION) #, title="Annular Check", style=wx.DEFAULT_FRAME_STYLE, wx.ICON_INFORMATION)    
        #
        
        #self.SetIcon(PyEmbeddedImage(round_ico_b64_data).GetIcon())

        #wx.IconFromBitmap(wx.Bitmap("icon.ico", wx.BITMAP_TYPE_ANY)))
        self.panel = wx.Panel(self)     
        self.title = wx.StaticText(self.panel, label="Plugin Output:")
        #self.result = wx.StaticText(self.panel, label="")
        #self.result.SetForegroundColour('#FF0000')
        self.button = wx.Button(self.panel, label="Close")
        #self.lblname = wx.StaticText(self.panel, label="Your name:")
        #self.editname = wx.TextCtrl(self.panel, size=(140, -1))
        self.editname = wx.TextCtrl(self.panel, size = (1024, 500), style = wx.TE_MULTILINE|wx.TE_READONLY)


        # Set sizer for the frame, so we can change frame size to match widgets
        self.windowSizer = wx.BoxSizer()
        self.windowSizer.Add(self.panel, 1, wx.ALL | wx.EXPAND)        

        # Set sizer for the panel content
        self.sizer = wx.GridBagSizer(5, 0)
        self.sizer.Add(self.title, (0, 0))
        #self.sizer.Add(self.result, (1, 0))
        #self.sizer.Add(self.lblname, (1, 0))
        self.sizer.Add(self.editname, (1, 0))
        self.sizer.Add(self.button, (2, 0), (1, 2), flag=wx.EXPAND)

        # Set simple sizer for a nice border
        self.border = wx.BoxSizer()
        self.border.Add(self.sizer, 1, wx.ALL | wx.EXPAND, 5)
        
        # Use the sizers
        self.panel.SetSizerAndFit(self.border)  
        self.SetSizerAndFit(self.windowSizer)  
        #self.result.SetLabel(msg)
        # Set event handlers
        #self.Show()
        self.button.Bind(wx.EVT_BUTTON, self.OnClose)
        self.Bind(wx.EVT_CLOSE,self.OnClose)

    def OnClose(self,e):
        #wx.LogMessage("c")
        e.Skip()
        self.Close()

    #def OnButton(self, e):
    #    self.result.SetLabel(self.editname.GetValue())
    def setMsg(self, t_msg):
        self.editname.SetValue(t_msg)



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


def convert_and_delete_modules(midline, remove_layer, brd):

    import faceplate_footprint_lib
    footprint_lib = faceplate_footprint_lib.get_lib_location()

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

        'POT-9MM-SONGHUEI': 'Faceplate_Hole_Pot_9mm',
        'Pot_9mm_Knurl_Det': 'Faceplate_Hole_Pot_9mm',
        'Pot_9mm_Knurl_NoDet': 'Faceplate_Hole_Pot_9mm',

        # SLIDERS:
        'Pot_Slider_LED_20mm_RA2045F': 'Faceplate_Hole_Slider_25mm_Slot',
        'POT-SLIDER-LED-ALPHA-RA2045F-20': 'Faceplate_Hole_Slider_25mm_Slot',
        'POT-SLIDER-ALPHA-RA2045F-20': 'Faceplate_Hole_Slider_25mm_Slot',

        # ENCODERS:
        'RGB_ROTARY_ENCODER': 'Faceplate_Hole_Encoder_RGB_NoBushing',
        'ROTENC-12MM-BUT': 'Faceplate_Hole_Encoder_290',

        # JACKS:
        'PJ301M-12': 'Faceplate_Hole_Jack_3.5mm',
        'PJ366ST': 'Faceplate_Hole_Jack_3.5mm',
        'PJ301M-12-FIX': 'Faceplate_Hole_Jack_3.5mm',
        'EighthInch_PJ398SM': 'Faceplate_Hole_Jack_3.5mm',
        'EighthInch_Stereo_PJ366ST': 'Faceplate_Hole_Jack_3.5mm',
        'Barrel_Vert_PJ064': 'Faceplate_Hole_Jack_Barrel_315',
        
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
        'Button_RgbLED_SPST_TC002': 'Faceplate_Hole_LED_Button_7mm_With_Mask_Opening',
        
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
    remove_fps = ['R0603', 'C0603', 'PAD-06', 'SOT-363_SC-70-6', 'R_0603', 'C_0603']

    io = pcbnew.PCB_IO()
    SCALE = 1000000.0

    msg=""

    for m in brd.GetModules():
        center = m.GetPosition()
        try:
            footpr = str(m.GetFPID().GetFootprintName())
        except:
            footpr = str(m.GetFPID().GetLibItemName())

        if footpr in footprint_convert:
            msg+="Found Back layer footprint: {} at {}mm,{}mm. Changing to {}".format(footpr, center.x/SCALE, center.y/SCALE, footprint_convert[footpr])
            msg+="\n"
            faceplate_mod = io.FootprintLoad(footprint_lib, footprint_convert[footpr])

            # Reflect over midline y-axis
            new_x = midline - (center.x - midline)
            center.x = new_x
            faceplate_mod.SetPosition(center)

            # pads = faceplate_mod.Pads()
            # for pad in pads:
            #   pad.SetNet(net)

            brd.Add(faceplate_mod)

            brd.Remove(m)
            continue

        if m.GetLayer() == remove_layer:
            brd.Remove(m)
            continue

        if footpr in remove_fps:
            brd.Remove(m)
            continue

        msg+="Unknown Back layer footprint: {} at {}mm,{}mm. ".format(footpr, center.x/SCALE, center.y/SCALE)
        msg+="\n"

    return msg


class makefp_convertfootprints( pcbnew.ActionPlugin ):
    def defaults( self ):
        self.name = "Make Faceplate Step 3 - Convert Footprints"
        self.category = "Make Faceplate 3"
        self.description = "Converts footprints on back to faceplate footprints. Deletes all others"

    def Run( self ):
        msg="Loading Board\n"
        board = pcbnew.GetBoard()

        bbox = find_pcb_outline_bbox(board)
        center = bbox.Centre()

        # gndnet = find_net("GND")
        #remove all other nets
        #remove_all_nets_but("GND")

        msg+=convert_and_delete_modules(center.x, pcbnew.F_Cu, board)

        msg+="\n"
        msg+="You may need to refresh the display now. Select Legacy mode, then Modern mode" + "\n"
        # frame = displayDialog(None)
        # frame.Center()
        # frame.setMsg(msg)
        # frame.ShowModal()
        # frame.Destroy()

makefp_convertfootprints().register()
