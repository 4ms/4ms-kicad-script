# Run this 4th
#

#todo: set zone pad connections to "Solid" instead of "Thermal Relief"

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


def find_net(netname_str, brd):
    nets = brd.GetNetsByName()
    found_neti = nets.find(netname_str)
    if (found_neti != nets.end()):
        found_net = found_neti.value()[1]
        return found_net
    else:
        print "Net name {} not found".format(netname_str)


def set_all_pads_to_net(net, brd):
    for m in brd.GetModules():
        pads = m.Pads()
        for pad in pads:
            pad.SetNet(net)

def find_pcb_outline_bbox(brd):
    """Get the bounding box around all edge cuts drawings"""
    boundingbox = None
    for d in brd.GetDrawings():
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
        set_all_pads_to_net(gndnet, board)

        pcboutline = find_pcb_outline_bbox(board)

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

        msg+="\n"
        msg+="You may need to refresh the display now. Select Legacy mode, then Modern mode" + "\n"
        frame = displayDialog(None)
        frame.Center()
        frame.setMsg(msg)
        frame.ShowModal()
        frame.Destroy()

makefp_makegroundzone().register()


