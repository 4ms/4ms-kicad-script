# Run this 2nd
#
# Create a EdgeCuts box centered around existing EdgeCuts
#     Height=5.059in
#     Width = smallest HP size possible (from A-100 tech specs lookup table)
# Then move the existing EdgeCuts to Cmts.User

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
        self.editname = wx.TextCtrl(self.panel, size = (600, 500), style = wx.TE_MULTILINE|wx.TE_READONLY)


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
    """Get the bounding box around all edge cuts drawings, and list of edge cuts drawings"""
    edgecuts_dwgs = []
    boundingbox = None
    for d in board.GetDrawings():
        if (d.GetLayerName() != "Edge.Cuts"):
            continue
        edgecuts_dwgs.append(d)
        if (boundingbox == None):
            boundingbox = d.GetBoundingBox()
        else:
            boundingbox.Merge(d.GetBoundingBox())
    boundingbox.Inflate(-150000) #assume a 0.15mm line width
    return boundingbox, edgecuts_dwgs


def move_drawings(dwgs_list, dest_layernum):
    for d in dwgs_list:
        d.SetLayer(dest_layernum)


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
            #print("HP={}".format(hp))
            return hp,width
            break;

class makefp_boundbox( pcbnew.ActionPlugin ):
    def defaults( self ):
        self.name = "Make Faceplate Step 2 - Create outline"
        self.category = "Make Faceplate 2"
        self.description = "Create standard HP width bounding box on Edge_Cuts layer"

    def Run( self ):
        #Dan's home computer:
        #footprint_lib = "/Users/dann/Google Drive/4ms/kicad-pcb/_lib/lib-footprints/4ms_Faceplate.pretty"

        #Dan's work comptuer:
        footprint_lib = "/Users/design/4ms/kicad-pcb/_lib/lib-footprints/4ms_Faceplate.pretty"

        #Zach's computer:
        # footprint_lib = "/Users/dag/Desktop/kicad/_lib/lib-footprints/4ms_Faceplate.pretty"

        railmount_fp = "Faceplate_Rail_Mount_Slot"

        SCALE = 1000000.0
        msg=""

        board = pcbnew.GetBoard()
        io = pcbnew.PCB_IO()

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
        bottomleft = pcbnew.wxPoint(int(fpleft), int(fpbottom))
        bottomright = pcbnew.wxPoint(int(fpright), int(fpbottom))
        topleft = pcbnew.wxPoint(int(fpleft), int(fptop))
        topright = pcbnew.wxPoint(int(fpright), int(fptop))

        # Draw the board outline segments
        bottomline = pcbnew.DRAWSEGMENT(board)
        board.Add(bottomline)
        bottomline.SetLayer(pcbnew.Edge_Cuts)
        bottomline.SetStart(bottomleft)
        bottomline.SetEnd(bottomright)

        topline = pcbnew.DRAWSEGMENT(board)
        board.Add(topline)
        topline.SetLayer(pcbnew.Edge_Cuts)
        topline.SetStart(topleft)
        topline.SetEnd(topright)

        leftline = pcbnew.DRAWSEGMENT(board)
        board.Add(leftline)
        leftline.SetLayer(pcbnew.Edge_Cuts)
        leftline.SetStart(topleft)
        leftline.SetEnd(bottomleft)

        rightline = pcbnew.DRAWSEGMENT(board)
        board.Add(rightline)
        rightline.SetLayer(pcbnew.Edge_Cuts)
        rightline.SetStart(topright)
        rightline.SetEnd(bottomright)

        #add rail mount slots
        railmount_topleft = pcbnew.wxPoint(topleft.x + 0.295*25.4*SCALE, topleft.y + 0.118*25.4*SCALE)
        railmount_topright = pcbnew.wxPoint(topright.x - 0.295*25.4*SCALE, topright.y + 0.118*25.4*SCALE)
        railmount_bottomleft = pcbnew.wxPoint(bottomleft.x + 0.295*25.4*SCALE, bottomleft.y - 0.118*25.4*SCALE)
        railmount_bottomright = pcbnew.wxPoint(bottomright.x - 0.295*25.4*SCALE, bottomright.y - 0.118*25.4*SCALE)

        mod = io.FootprintLoad(footprint_lib, railmount_fp)
        mod.SetPosition(railmount_topleft)
        board.Add(mod)

        mod = io.FootprintLoad(footprint_lib, railmount_fp)
        mod.SetPosition(railmount_topright)
        board.Add(mod)

        mod = io.FootprintLoad(footprint_lib, railmount_fp)
        mod.SetPosition(railmount_bottomleft)
        board.Add(mod)

        mod = io.FootprintLoad(footprint_lib, railmount_fp)
        mod.SetPosition(railmount_bottomright)
        board.Add(mod)

        msg+="Creating four rail mount slots (for 8HP and smaller faceplates, delete two of these)" + "\n"
        msg+="You may need to refresh the display now. Select Legacy mode, then Modern mode" + "\n"
        # frame = displayDialog(None)
        # frame.Center()
        # frame.setMsg(msg)
        # frame.ShowModal()
        # frame.Destroy()


makefp_boundbox().register()
