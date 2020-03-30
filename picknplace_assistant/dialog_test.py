from dialog.dialog_base import *

class TestApp(MainDialog):
    def __init__(self, parent):
        MainDialog.__init__(self, parent)

    def doCreatePDFs( self, event ):
            print("Create PDFs now")
            event.Skip()

    def doCancel( self, event ):
            print("cancelling")
            event.Skip()

app = wx.App(False)
frame = TestApp(None)
print("Showing Modal Dialog")
res = frame.ShowModal()
print("Shown")
if res == wx.ID_OK:
    print ("Clicked OK")
    print("Create PDF at: " + frame.m_textPath.GetValue())
else:
    print ("Clicked Cancel")

print("Done")
