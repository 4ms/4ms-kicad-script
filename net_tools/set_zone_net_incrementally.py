import pcbnew
import wx
import re

from kicad_mmccoo.simpledialog import DialogUtils

#todo: automatically detect if zones or tracks are selected
#todo: display how many are selected in the dialog box

class DirectionPicker(DialogUtils.ScrolledPicker):
    def __init__(self, parent, singleton=True):
        DialogUtils.ScrolledPicker.__init__(self, parent, singleton=singleton, cols=2)

        self.AddSelector("Down")
        self.AddSelector("Up")
        self.AddSelector("Right")
        self.AddSelector("Left")

    def GetValuePtr(self):
        return self.value

class ElementTypePicker(DialogUtils.ScrolledPicker):
    def __init__(self, parent, singleton=True):
        DialogUtils.ScrolledPicker.__init__(self, parent, singleton=singleton, cols=2)

        self.AddSelector("Zones")
        self.AddSelector("Tracks and Vias")

    def GetValuePtr(self):
        return self.value


class SetZoneNetSeqDialog(DialogUtils.BaseDialog):
    def __init__(self):
        super(SetZoneNetSeqDialog, self).__init__("Set Zone Net Dialog")

        self.net = DialogUtils.NetPicker(self)
        self.AddLabeled(item=self.net,
                        label="First Net in Sequence",
                        proportion=4,
                        flag=wx.EXPAND|wx.ALL,
                        border=2)

        self.sortby = DirectionPicker(self)
        self.AddLabeled(item=self.sortby,
                label="Sequence direction",
                proportion=1,
                flag=wx.EXPAND|wx.ALL,
                border=2)

        self.elementtype = ElementTypePicker(self)
        self.AddLabeled(item=self.elementtype,
                label="Element type to modify",
                proportion=1,
                flag=wx.EXPAND|wx.ALL,
                border=2)

        numnets = self.net.board.GetNetsByName().size()
        self.IncSize(height=numnets/4 + 2, width=80)

class SetZoneNetSeq(pcbnew.ActionPlugin):
    def defaults(self):
        self.name = "Set Net of Selected Elements Sequentially"
        self.category = "Net Tools"
        self.description = "Sets each of the selected zones, tracks, or vias to a sequentially numbered net, sorted by X or Y position"

    def Run(self):
        dlg = SetZoneNetSeqDialog()
        res = dlg.ShowModal()

        if res == wx.ID_OK:
            print("ok")
            if (dlg.net.value == None):
                warndlg = wx.MessageDialog(self, "no net was selected", "Error", wx.OK | wx.ICON_WARNING)
                warndlg.ShowModal()
                warndlg.Destroy()
                return

            net = dlg.net.GetValuePtr()

            if (type(net) == list):
                warndlg = wx.MessageDialog(self, "Select only one net", "Error", wx.OK | wx.ICON_WARNING)
                warndlg.ShowModal()
                warndlg.Destroy()
                return


            board = pcbnew.GetBoard()

            if dlg.elementtype.value == "Zones":
                numzones = board.GetAreaCount()
                elements = [board.GetArea(zone_i) for zone_i in range(numzones)]

            if dlg.elementtype.value == "Tracks and Vias":
                elements = board.GetTracks()

            sortby = dlg.sortby.value
            if sortby == "Down":
                sorted_elements = sorted(elements, reverse=False, key=lambda z: z.GetBoundingBox().GetTop())
            elif sortby == "Up":
                sorted_elements = sorted(elements, reverse=True, key=lambda z: z.GetBoundingBox().GetTop())
            elif sortby == "Right":
                sorted_elements = sorted(elements, reverse=False, key=lambda z: z.GetBoundingBox().GetLeft())
            elif sortby == "Left":
                sorted_elements = sorted(elements, reverse=True, key=lambda z: z.GetBoundingBox().GetLeft())
            else:
                sorted_elements = sorted(elements, reverse=False, key=lambda z: z.GetBoundingBox().GetTop())

            nbn = board.GetNetsByName()

            last_num = re.compile(r'(?:[^\d]*(\d+)[^\d]*)+')

            for element in sorted_elements:
                if element.IsSelected():
                    element.SetNet(net)
                    netname = net.GetNetname()
                    print ("set element to net {}".format(netname))

                    netnum = last_num.search(netname)
                    if netnum:
                        nextnumstr = str(int(netnum.group(1))+1)
                        start, end = netnum.span(1)
                        netname = netname[:max(end-len(nextnumstr), start)] + nextnumstr + netname[end:]

                    try:
                        net = nbn[netname]
                    except:
                        return

        else:
            print("cancel")

SetZoneNetSeq().register()