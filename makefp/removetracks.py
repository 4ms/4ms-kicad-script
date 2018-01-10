import pcbnew
board = pcbnew.GetBoard()

SCALE = 1000000.0

	

def delete_tracks_on_layer(layernum):
    for d in board.GetTracks():
        if (d.GetLayer() != layernum):
            continue
        board.Remove(d)

def create_layer_table():
    laytab={}
    numlayers = pcbnew.PCB_LAYER_ID_COUNT
    for i in range(numlayers):
        laytab[board.GetLayerName(i)] = i
    return laytab

layertable = create_layer_table()

#remove all tracks
delete_tracks_on_layer(layertable["F.Cu"])
delete_tracks_on_layer(layertable["B.Cu"])


