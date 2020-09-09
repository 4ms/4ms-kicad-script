# Run this 1st.
# 1st: removetracks.py
# 2nd: boundbox.py
# 3rd: deletefootprints.py
# 4th: makezone.py
#
# Delete all tracks and drawings on F.Cu and B.Cu layers

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

def delete_tracks_on_layer(layernum, board):
    for d in board.GetTracks():
        if (d.GetLayer() == layernum):
            board.Remove(d)

def delete_graphics_on_layer(layernum, board):
    for d in board.GetDrawings():
        if (d.GetLayer() == layernum):
            board.Remove(d)


class makefp_removetracks( pcbnew.ActionPlugin ):
    def defaults( self ):
        self.name = "Make Faceplate Step 1 - Remove Tracks"
        self.category = "Make Faceplate 1"
        self.description = "Removes tracks and graphics"

    def Run( self ):
        msg="Loading Board"
        msg+="\n"
        board = pcbnew.GetBoard()

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

        msg+="\n"
        msg+="You may need to refresh the display now. Select Legacy mode, then Modern mode" + "\n"
        # frame = displayDialog(None)
        # frame.Center()
        # frame.setMsg(msg)
        # frame.ShowModal()
        # frame.Destroy()


makefp_removetracks().register()
