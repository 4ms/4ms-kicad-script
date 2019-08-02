import pcbnew
import wx
#import os
#import sys
#import inspect
#import pdb

from kicad_mmccoo.simpledialog import DialogUtils

class SetZoneNetDialog(DialogUtils.BaseDialog):
    def __init__(self):
        super(SetZoneNetDialog, self).__init__("Set Zone Net Dialog")

        self.net = DialogUtils.NetPicker(self)
        self.AddLabeled(item=self.net,
                        label="Target Net",
                        proportion=1,
                        flag=wx.EXPAND|wx.ALL,
                        border=2)

        numnets = self.net.board.GetNetsByName().size()
        self.IncSize(height=numnets/4 + 2, width=80)

class SetZoneNet(pcbnew.ActionPlugin):
    def defaults(self):
        self.name = "Set Net of Selected Zones"
        self.category = "A descriptive category name"
        self.description = "Sets the net of all selected zones"

    def Run(self):
        dlg = SetZoneNetDialog()
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
            numzones = board.GetAreaCount()

            for zone_i in range(numzones):
                zone = board.GetArea(zone_i)
                if zone.IsSelected():
                    zone.SetNet(net)

        else:
            print("cancel")

SetZoneNet().register()