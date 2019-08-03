import pcbnew

##convert vias to modules

footprint_lib = "/Users/design/4ms/kicad-pcb/_lib/lib-footprints/4ms_LED.pretty"
footprint_name = "LED_PLCC-4"

io = pcbnew.PCB_IO()

board = pcbnew.GetBoard()
tracks = board.GetTracks()
vias = []
for e in tracks:
    if e.GetLength()==0:
        vias.append(e)

for via in vias:
	pos = via.GetPosition()
	fp = io.FootprintLoad(footprint_lib, footprint_name)
	fp.SetPosition(pos)
	board.Add(fp)
	#board.Remove(via)