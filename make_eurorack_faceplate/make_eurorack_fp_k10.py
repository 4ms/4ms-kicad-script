import pcbnew
import os
import wx
import faceplate_footprint_lib

# --- Config ---
footprint_lib = faceplate_footprint_lib.get_lib_location()
SCALE = 1000000.0

# Map of original footprints → faceplate footprints
footprint_convert = {
    # POTS
    'TRIM-T73YE': 'Faceplate_Hole_Trim_3.175mm_With_Mask_Opening',
    'Potentiometer_Alps_RK09L_Double_Vertical': 'Faceplate_Hole_Pot_16mm',
    'Pot_16mm_21Det_RV16AF-4A': 'Faceplate_Hole_Pot_16mm',
    'Pot_16mm_NoDet_RV16AF-4A': 'Faceplate_Hole_Pot_16mm',
    'Pot_16mm_CtrDet_RV16AF-4A': 'Faceplate_Hole_Pot_16mm',
    'POT-9MM-ALPHA': 'Faceplate_Hole_Pot_9mm_Metal_Collar',
    'Pot_9mm_DShaft': 'Faceplate_Hole_Pot_9mm_Metal_Collar',
    'POT-9MM-SONGHUEI': 'Faceplate_Hole_Pot_9mm',
    'Pot_9mm_Knurl_Det': 'Faceplate_Hole_Pot_9mm',
    'Pot_9mm_Knurl_NoDet': 'Faceplate_Hole_Pot_9mm',
    '9mm_CtrDet_10k_DShaft': 'Faceplate_Hole_Pot_9mm',
    'Pot_9mm_Dshaft_Det': 'Faceplate_Hole_Pot_9mm',
    # SLIDERS
    'Pot_Slider_LED_20mm_RA2045F': 'Faceplate_Hole_Slider_25mm_Slot',
    'POT-SLIDER-LED-ALPHA-RA2045F-20': 'Faceplate_Hole_Slider_25mm_Slot',
    'POT-SLIDER-ALPHA-RA2045F-20': 'Faceplate_Hole_Slider_25mm_Slot',
    'Top-Up_60RFT2-B': 'Faceplate_Hole_Top-Up_60RFT2-B',
    # ENCODERS
    'ENC_SPST_12mm': 'Faceplate_Hole_Encoder_290',
    'ENC_12mm_HollowShaft': 'Faceplate_Hole_Encoder_290',
    'ROTENC-12MM-BUT': 'Faceplate_Hole_Encoder_290',
    'RGB_ROTARY_ENCODER': 'Faceplate_Hole_Encoder_RGB_NoBushing',
    'ENC_RGB_SPST_12mm': 'Faceplate_Hole_Encoder_RGB_NoBushing',
    # JACKS
    'PJ301M-12': 'Faceplate_Hole_Jack_3.5mm',
    'PJ366ST': 'Faceplate_Hole_Jack_3.5mm',
    'EighthInch_PJ398SM': 'Faceplate_Hole_Jack_3.5mm',
    'EighthInch_Stereo_PJ366ST': 'Faceplate_Hole_Jack_3.5mm',
    'XLR-NCJ6FA-V-0': 'Faceplate_Hole_XLR_Quarter_Inch',
    # MIDI
    'MIDI_DIN5_SameSky_SD-50BV': 'Faceplate_Hole_MIDI_DIN5_SD-50BV',
    # STANDOFFS / SPACERS
    'MountingHole_WurthElektronik_WA-SNTI_15mm': 'Faceplate_Hole_Spacer_Mount_M3',
    # LEDS / LIGHTPIPES
    'LED-PLCC4': 'Faceplate_Hole_Lightpipe_With_Mask_Opening',
    'LED_PLCC-4': 'Faceplate_Hole_Lightpipe_With_Mask_Opening',
    'LED_0603_1608Metric': 'Faceplate_Hole_Lightpipe_With_Mask_Opening',
    'PLCC4': 'Faceplate_Hole_Lightpipe_With_Mask_Opening',
    'LED-C1-A2-3MM-VERT': 'Faceplate_Hole_LED_3mm',
    'LED_D3.0mm-3': 'Faceplate_Hole_LED_3mm',
    'LED-3MM-SQUARE-ANODE': 'Faceplate_Hole_LED_3mm',
    # BUTTONS / SWITCHES
    'SW_TH_Tactile_Omron_B3F-100x': 'Faceplate_Hole_ButtonTact_5mm',
    'Button_PB20B': 'Faceplate_Hole_Button_PB20',
    'Button_LED_PKS-01L-X': 'Faceplate_Hole_Button_PB20',
    'Switch_Toggle_SPDT_SubMini': 'Faceplate_Hole_SubMini_Toggle',
    'BUTTON-LED-PB61303': 'Faceplate_Hole_LED_Button_7mm_With_Mask_Opening',
    'RGB-SPST-LED-TC002': 'Faceplate_Hole_LED_Button_5.4mm_With_Mask_Opening',
    'Button_RgbLED_SPST_TC002': 'Faceplate_Hole_LED_Button_5.4mm_With_Mask_Opening',
    'Slide_Switch_Runrun_SS22D06': 'Faceplate_Slide_Switch_SS22D06_Runrun',
}

# Full list of parts to remove (substring match, case-insensitive)
remove_fps = [
    # Passives
    'R0603', 'R_0603', 'R_0402', 'R_0201',
    'C0603', 'C_0603', 'C_0402', 'C_0201', 'C_1206', 'C_0805', 'CP_Elec',
    'L_Wuerth', 'MAPI-2510', 'COIL',
    # ICs / packages
    'TSSOP', 'TSOT', 'SOT', 'SOP-', 'SOIC-', 'LQFP-', 'DFN-', 'QFN-',
    'PAD-06', 'mp153', 'Transistor',
    # Crystals / oscillators
    'FA-', 'Crystal',
    # Diodes
    'Diode', 'D_SOD-123', 'DFN-1006',
    # LEDs (non-panel)
    'LED',
    # Connectors (non-panel)
    'Pins', 'EighthInch', 'USB_C_Receptacle', 'SolderJumper', 'NetTie',
    # Switches (non-panel)
    'Button_SPST', 'Switch_SPST', 'SW_TH_',
]

# --- Helper Functions ---
def make_vec(x, y):
    return pcbnew.VECTOR2I(int(x), int(y))

def find_pcb_outline_bbox(board):
    edgecuts = []
    bbox = None
    for d in board.GetDrawings():
        if d.GetLayerName() != "Edge.Cuts":
            continue
        edgecuts.append(d)
        if bbox is None:
            bbox = d.GetBoundingBox()
        else:
            bbox.Merge(d.GetBoundingBox())
    if bbox:
        bbox.Inflate(-150000)
    return bbox, edgecuts

def move_drawings(dwgs, layernum):
    for d in dwgs:
        d.SetLayer(layernum)

def delete_tracks_on_layer(layernum, board):
    for t in list(board.GetTracks()):
        if t.GetLayer() == layernum:
            board.Remove(t)

def delete_graphics_on_layer(layernum, board):
    for d in list(board.GetDrawings()):
        if d.GetLayer() == layernum:
            board.Remove(d)

def delete_all_tracks_and_graphics(board):
    msg = ""
    layers = [pcbnew.F_Cu, pcbnew.B_Cu, pcbnew.In1_Cu, pcbnew.In2_Cu,
              pcbnew.F_SilkS, pcbnew.B_SilkS]
    for layer in layers:
        delete_tracks_on_layer(layer, board)
        delete_graphics_on_layer(layer, board)
        msg += f"Removed tracks/graphics on layer {layer}\n"
    return msg

def make_faceplate_outline(board):
    msg = ""
    log_path = os.path.expanduser("~/makefp_debug.log")

    def dbg(s):
        with open(log_path, "a") as f:
            f.write(f"  {s}\n")

    dbg("checking footprint_lib path")
    if not os.path.exists(footprint_lib):
        raise FileNotFoundError(f"Invalid footprint library path: {footprint_lib}")

    railmount_fp = "Faceplate_Rail_Mount_Slot_Plated"
    dbg("finding pcb outline bbox")
    pcboutline, edgecuts = find_pcb_outline_bbox(board)
    if not pcboutline:
        return "No PCB outline found.\n"

    dbg("getting pcbcenter")
    pcbcenter = pcboutline.Centre()
    dbg(f"pcbcenter = {pcbcenter.x/1e6:.3f}, {pcbcenter.y/1e6:.3f}")
    dbg("moving edge cuts to Cmts_User")
    move_drawings(edgecuts, pcbnew.Cmts_User)

    # Standard HP sizing
    HPs = [(1,5.0),(1.5,7.5),(2,9.8),(3,15.0),(4,20.0),(6,30.0),(8,40.3),(10,50.5),
           (12,60.6),(14,70.8),(16,80.9),(18,91.3),(20,101.3),(21,106.3),(22,111.4),
           (24,121.5),(26,131.6),(28,141.9),(42,213.0)]
    pcbwidth = pcboutline.GetWidth() / SCALE
    fphp, fpwidth = next(((hp, w) for hp, w in HPs if w > pcbwidth), HPs[-1])
    msg += f"Faceplate is {fphp} HP wide by 128.5mm high\n"

    fpleft   = pcbcenter.x - fpwidth * SCALE / 2
    fpright  = fpleft + fpwidth * SCALE
    fpbottom = pcbcenter.y + 128.5 * SCALE / 2
    fptop    = fpbottom - 128.5 * SCALE

    corners = {
        'bl': make_vec(fpleft,  fpbottom),
        'br': make_vec(fpright, fpbottom),
        'tl': make_vec(fpleft,  fptop),
        'tr': make_vec(fpright, fptop),
    }

    dbg("drawing edge cuts lines")
    for start, end in [('bl','br'), ('tl','tr'), ('tl','bl'), ('tr','br')]:
        line = pcbnew.PCB_SHAPE(board)
        line.SetLayer(pcbnew.Edge_Cuts)
        line.SetStart(corners[start])
        line.SetEnd(corners[end])
        board.Add(line)
    dbg("edge cuts done")

    # Eurorack standard offsets (in inches, matching original makefp convention)
    slot_x_offset = 0.295 * 25.4 * SCALE  # 7.493mm inset from left/right edge
    slot_y_offset = 0.118 * 25.4 * SCALE  # 2.997mm inset from top/bottom edge
    slot_top_y    = corners['tl'].y + slot_y_offset
    slot_bot_y    = corners['bl'].y - slot_y_offset
    slot_left_x   = corners['tl'].x + slot_x_offset
    slot_right_x  = corners['tr'].x - slot_x_offset

    # ≤8HP: one slot per rail at left-side position (matches audio/button/pot/PI expanders)
    # ≥10HP: two slots per rail (left + right corners)
    if fphp <= 8:
        slot_positions = [
            make_vec(slot_left_x, slot_top_y),
            make_vec(slot_left_x, slot_bot_y),
        ]
    else:
        slot_positions = [
            make_vec(slot_left_x,  slot_top_y),
            make_vec(slot_right_x, slot_top_y),
            make_vec(slot_left_x,  slot_bot_y),
            make_vec(slot_right_x, slot_bot_y),
        ]
    dbg("loading rail mount slot footprints")
    for i, pos in enumerate(slot_positions):
        dbg(f"  slot {i}: FootprintLoad")
        mod = pcbnew.FootprintLoad(footprint_lib, railmount_fp)
        dbg(f"  slot {i}: SetPosition")
        mod.SetPosition(pos)
        dbg(f"  slot {i}: Add")
        board.Add(mod)
    dbg("rail mount slots done")

    # Rail connection (soldermask opening exposing B.Cu GND at rail contact points)
    rail_conn_map = {
        4: 'Rail_Connection_4HP',  5: 'Rail_Connection_5HP',
        6: 'Rail_Connection_6HP',  8: 'Rail_Connection_8HP',
        12: 'Rail_Connection_12HP', 14: 'Rail_Connection_14HP',
        16: 'Rail_Connection_16HP', 20: 'Rail_Connection_20HP',
        26: 'Rail_Connection_26HP', 28: 'Rail_Connection_28HP',
    }
    available = sorted(rail_conn_map.keys())
    rc_hp = max((h for h in available if h <= fphp), default=available[0])
    rail_conn_fp = rail_conn_map[rc_hp]
    rc_inset = 1.253 * SCALE
    rc_top_y = slot_top_y + rc_inset
    rc_bot_y = slot_bot_y - rc_inset
    dbg(f"loading rail connection footprints: {rail_conn_fp}")
    for i, y in enumerate([rc_top_y, rc_bot_y]):
        dbg(f"  rc {i}: FootprintLoad")
        mod = pcbnew.FootprintLoad(footprint_lib, rail_conn_fp)
        pos = make_vec(pcbcenter.x, y)
        dbg(f"  rc {i}: SetPosition")
        mod.SetPosition(pos)
        dbg(f"  rc {i}: Add")
        board.Add(mod)
        dbg(f"  rc {i}: SetLayer B.Cu")
        mod.SetLayer(pcbnew.B_Cu)
        # Set full layer set on all pads to B.Cu/B.Mask/B.Paste
        back_lset = pcbnew.LSET()
        back_lset.AddLayer(pcbnew.B_Cu)
        back_lset.AddLayer(pcbnew.B_Mask)
        back_lset.AddLayer(pcbnew.B_Paste)
        for pad in mod.Pads():
            pad.SetLayerSet(back_lset)
        dbg(f"  rc {i}: done")
    msg += f"Rail connections: {rail_conn_fp} on B.Cu (top + bottom)\n"

    return msg

def get_fp_name(fp):
    try:
        return str(fp.GetFPID().GetLibItemName())
    except:
        try:
            return str(fp.GetFPID().GetFootprintName())
        except:
            return None

def remove_nonfp_footprints(board):
    msg = ""
    for m in list(board.GetFootprints()):
        footpr = get_fp_name(m)
        if footpr and any(rem.lower() in footpr.lower() for rem in remove_fps):
            board.Remove(m)
            msg += f"Removed footprint: {footpr}\n"
    return msg

def add_fp(center, footpr, board):
    msg = f"Found footprint {footpr}, adding {footprint_convert[footpr]}\n"
    faceplate_mod = pcbnew.FootprintLoad(footprint_lib, footprint_convert[footpr])
    faceplate_mod.SetPosition(center)
    board.Add(faceplate_mod)
    return msg

def convert_faceplate_footprints(board):
    msg = ""
    pcboutline, _ = find_pcb_outline_bbox(board)
    if pcboutline:
        midline = pcboutline.Centre().x
        for m in list(board.GetFootprints()):
            footpr = get_fp_name(m)
            if footpr in footprint_convert:
                center = m.GetPosition()
                center = pcbnew.VECTOR2I(
                    int(midline - (center.x - midline)),
                    center.y
                )
                msg += add_fp(center, footpr, board)
    return msg

def remove_faceplate_footprints(board):
    msg = ""
    for m in list(board.GetFootprints()):
        footpr = get_fp_name(m)
        if footpr in footprint_convert:
            board.Remove(m)
            msg += f"Removed faceplate footprint: {footpr}\n"
    return msg

def make_ground_zone(board):
    msg = ""
    gnd_net = board.FindNet("GND")
    if not gnd_net:
        return "No GND net found.\n"

    # Remove any existing zones before creating new ones
    existing = list(board.Zones())
    for z in existing:
        board.Remove(z)
    msg += f"Removed {len(existing)} existing zone(s).\n"

    # Assign GND to all pads
    for fp in board.GetFootprints():
        for pad in fp.Pads():
            pad.SetNet(gnd_net)

    pcboutline, _ = find_pcb_outline_bbox(board)
    if not pcboutline:
        return "No PCB outline for GND zone.\n"

    margin = pcbnew.FromMils(10)
    pcboutline.Inflate(-margin)

    corners = [
        (pcboutline.GetLeft(),  pcboutline.GetTop()),
        (pcboutline.GetRight(), pcboutline.GetTop()),
        (pcboutline.GetRight(), pcboutline.GetBottom()),
        (pcboutline.GetLeft(),  pcboutline.GetBottom()),
    ]

    # GND pour on both F.Cu and B.Cu — solid connection, no thermal relief
    for layer in [pcbnew.F_Cu, pcbnew.B_Cu]:
        zone = pcbnew.ZONE(board)
        zone.SetLayer(layer)
        zone.SetNet(gnd_net)
        zone.SetLocalClearance(pcbnew.FromMM(0.12))
        zone.SetMinThickness(pcbnew.FromMM(0.25))
        zone.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL)
        outline = zone.Outline()
        outline.NewOutline()
        for corner in corners:
            outline.Append(corner[0], corner[1])
        board.Add(zone)

    msg += f"GND zones created on F.Cu and B.Cu (solid, no thermal relief).\n"

    # Build connectivity before filling — required in KiCad 10 for correct net resolution
    board.BuildConnectivity()
    try:
        filler = pcbnew.ZONE_FILLER(board)
        filler.Fill(board.Zones())
        msg += "Zones filled automatically.\n"
    except Exception as e:
        msg += f"Auto-fill failed ({e}) — press B in KiCad to fill manually.\n"

    return msg

# --- Plugin ---
class make_eurorack_fp_k10(pcbnew.ActionPlugin):
    def defaults(self):
        self.name = "Make Eurorack Faceplate (KiCad 10)"
        self.category = "Eurorack"
        self.description = "Creates a Eurorack faceplate using 4ms faceplate library (KiCad 10)"

    def Run(self):
        log_path = os.path.expanduser("~/makefp_debug.log")

        def step(name, fn):
            with open(log_path, "a") as f:
                f.write(f">>> START: {name}\n")
            result = fn()
            with open(log_path, "a") as f:
                f.write(result if result else "")
                f.write(f">>> DONE: {name}\n")
            return result or ""

        # Clear log
        with open(log_path, "w") as f:
            f.write("makefp_k10 started\n")

        try:
            board = pcbnew.GetBoard()
            log = ""
            log += step("delete_all_tracks_and_graphics", lambda: delete_all_tracks_and_graphics(board))
            log += step("make_faceplate_outline",         lambda: make_faceplate_outline(board))
            log += step("convert_faceplate_footprints",   lambda: convert_faceplate_footprints(board))
            log += step("remove_faceplate_footprints",    lambda: remove_faceplate_footprints(board))
            log += step("remove_nonfp_footprints",        lambda: remove_nonfp_footprints(board))
            log += step("make_ground_zone",               lambda: make_ground_zone(board))
            log += step("Refresh",                        lambda: (pcbnew.Refresh(), "Refresh OK\n")[1])

            converted = log.count("Found footprint")
            removed   = log.count("Removed footprint:")
            hp_line   = next((l for l in log.splitlines() if "HP wide" in l), "")
            rc_line   = next((l for l in log.splitlines() if "Rail connections:" in l), "")

            summary = (
                f"{hp_line}\n"
                f"{rc_line}\n"
                f"Panel footprints converted: {converted}\n"
                f"Components removed: {removed}\n"
                f"GND zones: {'created' if 'GND zones created' in log else 'skipped'}\n"
                f"(Press B to fill zones)\n\n"
                f"Debug log: {log_path}"
            )
            wx.MessageBox(summary, "Eurorack Faceplate (KiCad 10)", wx.OK | wx.ICON_INFORMATION)

        except Exception as e:
            import traceback
            err = traceback.format_exc()
            with open(log_path, "a") as f:
                f.write(f"\nEXCEPTION:\n{err}")
            wx.MessageBox(f"Script error — see {log_path}\n\n{e}", "Error", wx.OK | wx.ICON_ERROR)

make_eurorack_fp_k10().register()
