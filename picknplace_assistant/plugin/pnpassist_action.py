import pcbnew
import re
import os
import errno
import numpy as np

import sys
sys.path.append('/System/Library/Frameworks/Python.framework/Versions/2.7/Extras/lib/python')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, Ellipse, FancyBboxPatch
from matplotlib.backends.backend_pdf import PdfPages
import wx

import textwrap

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
        wx.Dialog.__init__(self, parent, id=-1, title="PNP Assist output")#
        #, style=wx.DEFAULT_DIALOG_STYLE, wx.ICON_INFORMATION) 
        #, style=wx.DEFAULT_DIALOG_STYLE, wx.ICON_INFORMATION)
        #, pos=DefaultPosition, size=DefaultSize, style = wx.DEFAULT_FRAME_STYLE & (~wx.MAXIMIZE_BOX), name="fname")
        #, wx.ICON_INFORMATION) #, title="Annular Check", style=wx.DEFAULT_FRAME_STYLE, wx.ICON_INFORMATION)    
        #
        
        #self.SetIcon(PyEmbeddedImage(round_ico_b64_data).GetIcon())

        #wx.IconFromBitmap(wx.Bitmap("icon.ico", wx.BITMAP_TYPE_ANY)))
        self.panel = wx.Panel(self)     
        self.title = wx.StaticText(self.panel, label="PNP Assist debug:")
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


def create_board_figure(pcb, bom_row, layer=pcbnew.F_Cu):
    msg = ""
    unsupported_pads = []
    qty, value, footpr, highlight_refs = bom_row
    # global ax

    plt.figure(figsize=(5.8, 8.2))
    ax = plt.subplot("111", aspect="equal")

    color_pad1 = "lightgray"
    color_pad2 = "#AA0000"
    color_pad3 = "#CC4444"
    color_bbox1 = "None"
    color_bbox2 = "#E9AFAF"

    # get board edges (assuming rectangular, axis aligned pcb)
    edge_coords = []
    for d in pcb.GetDrawings():
        if (d.GetLayer() == pcbnew.Edge_Cuts):
            edge_coords.append(d.GetStart())
            edge_coords.append(d.GetEnd())
    edge_coords = np.asarray(edge_coords) * 1e-6
    board_xmin, board_ymin = edge_coords.min(axis=0)
    board_xmax, board_ymax = edge_coords.max(axis=0)

    # draw board edges
    rct = Rectangle((board_xmin, board_ymin), board_xmax - board_xmin, board_ymax - board_ymin, angle=0)
    rct.set_color("None")
    rct.set_edgecolor("black")
    rct.set_linewidth(3)
    ax.add_patch(rct)

    # add title
    ax.text(board_xmin + .5 * (board_xmax - board_xmin), board_ymin - 0.5,
            "%dx %s, %s" % (qty, value, footpr), 
            horizontalalignment='center', verticalalignment='bottom')

    # add ref list
    ax.text((board_xmax + board_xmin)*0.5, board_ymax + 0.5,
            textwrap.fill(", ".join(highlight_refs), 60), 
            horizontalalignment='center', verticalalignment='top')

    # draw parts
    for m in pcb.GetModules():
        if m.GetLayer() != layer:
            continue
        ref, center = m.GetReference(), np.asarray(m.GetCenter()) * 1e-6
        highlight = ref in highlight_refs

        # bounding box
        mrect = m.GetFootprintRect()
        mrect_pos = np.asarray(mrect.GetPosition()) * 1e-6
        mrect_size = np.asarray(mrect.GetSize()) * 1e-6
        rct = Rectangle(mrect_pos, mrect_size[0], mrect_size[1])
        rct.set_color(color_bbox2 if highlight else color_bbox1)
        rct.set_zorder(-1)
        if highlight:
            rct.set_linewidth(.1)
            rct.set_edgecolor(color_pad2)
        ax.add_patch(rct)

        # center marker
        if highlight:
            plt.plot(center[0], center[1], ".", markersize=mrect_size.min(), color=color_pad2)

        # plot pads
        for p in m.Pads():
            pos = np.asarray(p.GetPosition()) * 1e-6
            size = np.asarray(p.GetSize()) * 1e-6 * .9

            is_pin1 = p.GetPadName() == "1" or p.GetPadName() == "A1"
            shape = p.GetShape()
            offset = p.GetOffset()  # TODO: check offset

            # pad rect
            angle = p.GetOrientation() * 0.1
            cos, sin = np.cos(np.pi / 180. * angle), np.sin(np.pi / 180. * angle)
            dpos = np.dot([[cos, -sin], [sin, cos]], -.5 * size)

            if shape == 1:
                rct = Rectangle(pos + dpos, size[0], size[1], angle=angle)
            elif shape == 2:
                rct = Rectangle(pos + dpos, size[0], size[1], angle=angle)
            elif shape == 0:
                rct = Ellipse(pos, size[0], size[1], angle=angle)
            else:
                #todo: check if already printed this error
                #already_found_unsupported_shape = ref+p.GetPadName() in unsupported_pads
                #if !already_found_unsupported_shape:
                #    unsupported_pads.append(ref+p.GetPadName())
                print("Unsupported pad shape", shape)
                msg+="Unsupported pad shape " + str(shape) + " for " + ref + " at " + str(p.GetPosition().x) + ", " + str(p.GetPosition().y)+"\n"
                continue
            rct.set_linewidth(0)
            rct.set_color(color_pad2 if highlight else color_pad1)
            rct.set_zorder(1)
            # highlight pin1
            if highlight and is_pin1:
                rct.set_color(color_pad3)
                rct.set_linewidth(.1)
                rct.set_edgecolor(color_pad2)
            ax.add_patch(rct)

    plt.xlim(board_xmin, board_xmax)
    plt.ylim(board_ymax, board_ymin)

    plt.axis('off')
    return msg


def natural_sort(l):
    """
    Natural sort for strings containing numbers
    """
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
    return sorted(l, key=alphanum_key)


def generate_bom(pcb, filter_layer=None):
    """
    Generate BOM from pcb layout.
    :param filter_layer: include only parts for given layer
    :return: BOM table (qty, value, footprint, refs)
    """

    # build grouped part list
    part_groups = {}
    for m in pcb.GetModules():
        # filter part by layer
        if filter_layer is not None and filter_layer != m.GetLayer():
            continue
        # group part refs by value and footprint
        value = m.GetValue()
        try:
            footpr = str(m.GetFPID().GetFootprintName())
        except:
            footpr = str(m.GetFPID().GetLibItemName())
        group_key = (value, footpr)
        refs = part_groups.setdefault(group_key, [])
        refs.append(m.GetReference())

    # build bom table, sort refs
    # bom_table is a list of lines
    #    line is a tuple of (qty-int, value-string, fp-string, refs-[list])
    #    refs is a list of references
    bom_table = []
    for (value, footpr), refs in part_groups.items():
        line = (len(refs), value, footpr, natural_sort(refs))
        bom_table.append(line)

    # sort table by reference prefix and quantity
    def sort_func(row):
        qty, _, _, rf = row
        ref_ord = {"R": 3, "C": 3, "L": 1, "D": 1, "J": -1, "P": -1}.get(rf[0][0], 0)
        return -ref_ord, -qty
    bom_table = sorted(bom_table, key=sort_func)

    return bom_table

class pnpassist( pcbnew.ActionPlugin ):
    def defaults( self ):
        self.name = "PNP Assistant"
        self.category = "PNP"
        self.description = "Create a PDF showing which parts go where"

    def Run( self ):
        # build BOM
        msg="Loading Board..."
        msg+="\n"
        pcb = pcbnew.GetBoard()

        pcbfilename, kicadpcb_ext = os.path.splitext(pcb.GetFileName())
        pathname = os.path.dirname(pcbfilename)

        # Front side PDF
        filename = os.path.basename(pcbfilename) + "_front_picknplace.pdf"
        fname_out = pathname + "/bom/" + filename

        # make the ./bom directory
        if not os.path.exists(os.path.dirname(fname_out)):
            try:
                os.makedirs(os.path.dirname(fname_out))
            except OSError as exc: # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise

        frame = displayDialog(None)
        frame.Center()
        frame.setMsg("This will take a moment, click \"Close\" and please wait...")
        frame.ShowModal()
        frame.Destroy()

        bom_table = generate_bom(pcb, filter_layer=pcbnew.F_Cu)
        with PdfPages(fname_out) as pdf:
            for i, bom_row in enumerate(bom_table):
                msg+="Plotting page (%d/%d)" % (i+1, len(bom_table))
                msg+="\n"
                msg+=create_board_figure(pcb, bom_row, layer=pcbnew.F_Cu)
                pdf.savefig()
                #plt.close('') # This throws an error with wx when run interactively

        msg+="Front side written to %s" % fname_out
        msg+="\n"

        # Back side PDF
        filename = os.path.basename(pcbfilename) + "_back_picknplace.pdf"
        fname_out = pathname + "/bom/" + filename

        # make the ./bom directory
        if not os.path.exists(os.path.dirname(fname_out)):
            try:
                os.makedirs(os.path.dirname(fname_out))
            except OSError as exc: # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise

        bom_table = generate_bom(pcb, filter_layer=pcbnew.B_Cu)
        with PdfPages(fname_out) as pdf:
            for i, bom_row in enumerate(bom_table):
                msg+="Plotting page (%d/%d)" % (i+1, len(bom_table))
                msg+="\n"
                msg+=create_board_figure(pcb, bom_row, layer=pcbnew.B_Cu)
                pdf.savefig()
                #plt.close('') # This throws an error with wx when run interactively

        msg+="Back side written to %s" % fname_out
        msg+="\n"

        frame = displayDialog(None)
        frame.Center()
        frame.setMsg(msg)
        frame.ShowModal()
        frame.Destroy()


pnpassist().register()
