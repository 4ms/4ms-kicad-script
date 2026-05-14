import pcbnew

board = pcbnew.GetBoard()
for fp in board.GetFootprints():
    for pad in fp.Pads():
        if pad.GetAttribute() == pcbnew.PAD_ATTRIB_PTH:
            pos = pad.GetPosition()
            radius = pad.GetDrillSize().x // 2
            circle = pcbnew.PCB_SHAPE(board)
            circle.SetShape(pcbnew.SHAPE_T_CIRCLE)
            circle.SetLayer(pcbnew.Edge_Cuts)
            circle.SetCenter(pos)
            circle.SetEnd(pcbnew.VECTOR2I(pos.x + radius, pos.y))
            circle.SetWidth(pcbnew.FromMM(0.1))
            board.Add(circle)

pcbnew.Refresh()
print("Done.")
