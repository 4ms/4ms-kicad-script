#!/usr/bin/env python3
import math

# -------------------------------
# Resistor Lists
# -------------------------------

# E24 (1%) base values
E24_BASE = [1.0, 1.1, 1.2, 1.3, 1.5, 1.6, 1.8, 2.0, 2.2, 2.4, 2.7, 3.0,
            3.3, 3.6, 3.9, 4.3, 4.7, 5.1, 5.6, 6.2, 6.8, 7.5, 8.2, 9.1]

# E96 (0.1%) base values
E96_BASE = [
    1.00, 1.02, 1.05, 1.07, 1.10, 1.13, 1.15, 1.18, 1.21, 1.24,
    1.27, 1.30, 1.33, 1.37, 1.40, 1.43, 1.47, 1.50, 1.54, 1.58,
    1.62, 1.65, 1.69, 1.74, 1.78, 1.82, 1.87, 1.91, 1.96, 2.00,
    2.05, 2.10, 2.15, 2.21, 2.26, 2.32, 2.37, 2.43, 2.49, 2.55,
    2.61, 2.67, 2.74, 2.80, 2.87, 2.94, 3.01, 3.09, 3.16, 3.24,
    3.32, 3.40, 3.48, 3.57, 3.65, 3.74, 3.83, 3.92, 4.02, 4.12,
    4.22, 4.32, 4.42, 4.53, 4.64, 4.75, 4.87, 4.99, 5.11, 5.23,
    5.36, 5.49, 5.62, 5.76, 5.90, 6.04, 6.19, 6.34, 6.49, 6.65,
    6.81, 6.98, 7.15, 7.32, 7.50, 7.68, 7.87, 8.06, 8.25, 8.45,
    8.66, 8.87, 9.09, 9.31, 9.53, 9.76
]

def generate_resistor_list(base_values, decades=range(0, 7)):
    """Generate full resistor list from base values scaled by decades (powers of 10)."""
    full_list = []
    for decade in decades:
        factor = 10 ** decade
        for val in base_values:
            full_list.append(val * factor)
    return full_list

# Full lists for calculations
E24_LIST = generate_resistor_list(E24_BASE)   # 1Ω → 10MΩ
E96_LIST = generate_resistor_list(E96_BASE)   # 1Ω → 10MΩ



# -------------------------------
# Resistor Formatting Function
# -------------------------------

def format_resistor(value_ohms):
    """Format resistor with proper units, removing unnecessary trailing zeros.
       For 1% resistors: max 1 decimal
       For 0.1% resistors: max 2 decimals
    """
    if value_ohms >= 1_000_000:
        val = value_ohms / 1_000_000
        s = f"{val:.2f}".rstrip('0').rstrip('.')
        return f"{s}MΩ"
    elif value_ohms >= 1_000:
        val = value_ohms / 1_000
        # If val is integer, show no decimals, else show max 1 decimal
        if val.is_integer():
            return f"{int(val)}kΩ"
        else:
            s = f"{val:.2f}".rstrip('0').rstrip('.')
            return f"{s}kΩ"
    else:
        # For values <1kΩ, same logic: max 1 decimal
        if value_ohms.is_integer():
            return f"{int(value_ohms)}Ω"
        else:
            s = f"{value_ohms:.2f}".rstrip('0').rstrip('.')
            return f"{s}Ω"



def calculate_current(vin, r1, r2):
    """Return the current through a voltage divider in amps."""
    return vin / (r1 + r2)
    
def format_current(current_amps):
    """Format current with up to 3 significant digits, rounded, switch to mA ≥1000 µA."""
    uA = current_amps * 1_000_000
    if uA < 1000:  # less than 1 mA
        if uA >= 100:
            val = round(uA)
        elif uA >= 10:
            val = round(uA, 1)
        else:
            val = round(uA, 2)
        return f"{val:g} µA"  # removes trailing zeros
    else:  # 1 mA or more
        mA = current_amps * 1_000
        if mA >= 100:
            val = round(mA)
        elif mA >= 10:
            val = round(mA, 1)
        else:
            val = round(mA, 2)
        return f"{val:g} mA"  # removes trailing zeros

# -------------------------------
# Voltage Divider
# -------------------------------

def voltage_divider():
    vin = float(input("Enter Vin (V): "))
    vout_target = float(input("Enter desired Vout (V): "))

    # Make sure Vout < Vin
    while vout_target >= vin:
        print("Vout must be less than Vin. Please enter values again.")
        vin = float(input("Enter Vin (V): "))
        vout_target = float(input("Enter desired Vout (V): "))

    # Goldilocks current range
    GOLDILOCKS_MIN = 0.00001  # 10 µA
    GOLDILOCKS_MAX = 0.001    # 1 mA

    # Common resistor list for marking
    COMMON_VALUES = [1000, 2200, 3300, 4700, 5600, 6800, 8200,
                     10000, 22000, 33000, 47000, 56000, 68000, 82000, 100000]

    # --- Find closest 1% resistor combinations ---
    def find_closest_options(resistors, count=6):
        options = []
        for r1 in resistors:
            for r2 in resistors:
                vout = vin * r2 / (r1 + r2)
                error = abs(vout - vout_target)
                current = vin / (r1 + r2)
                if GOLDILOCKS_MIN <= current <= GOLDILOCKS_MAX:
                    note = "Common R" if (r1 in COMMON_VALUES or r2 in COMMON_VALUES) else ""
                    options.append((error, vout, r1, r2, current, note))
        options.sort(key=lambda x: x[0])
        seen = set()
        unique = []
        for opt in options:
            key = (round(opt[2]), round(opt[3]))
            if key not in seen:
                seen.add(key)
                unique.append(opt)
            if len(unique) >= count:
                break
        return unique

    # --- Find closest 0.1% resistor combinations ---
    def find_01pct_options(resistors, count=6):
        options = []
        for r1 in resistors:
            for r2 in resistors:
                vout = vin * r2 / (r1 + r2)
                error = abs(vout - vout_target)
                current = vin / (r1 + r2)
                if GOLDILOCKS_MIN <= current <= GOLDILOCKS_MAX:
                    options.append((error, vout, r1, r2, current))
        options.sort(key=lambda x: x[0])
        seen = set()
        unique = []
        for opt in options:
            key = (round(opt[2]), round(opt[3]))
            if key not in seen:
                seen.add(key)
                unique.append(opt)
            if len(unique) >= count:
                break
        return unique

    # --- Combined 1% + 0.1% combinations ---
    def find_combined_options(rlist_1pct, rlist_01pct, count=6):
        options = []
        for r1 in rlist_1pct:
            for r2 in rlist_01pct:
                vout = vin * r2 / (r1 + r2)
                error = abs(vout - vout_target)
                current = vin / (r1 + r2)
                if GOLDILOCKS_MIN <= current <= GOLDILOCKS_MAX:
                    options.append((error, vout, r1, r2, current))
        options.sort(key=lambda x: x[0])
        seen = set()
        unique = []
        for opt in options:
            key = (round(opt[2]), round(opt[3]))
            if key not in seen:
                seen.add(key)
                unique.append(opt)
            if len(unique) >= count:
                break
        return unique

    # Correctly scaled E96 list
    E96_LIST_CORRECTED = []
    for decade in range(-1, 7):  # 0.1Ω to 10MΩ
        factor = 10 ** decade
        for val in E96_LIST:
            E96_LIST_CORRECTED.append(val * factor)

    # --- Get results ---
    options_1pct = find_closest_options(E24_LIST, count=6)
    options_01pct = find_01pct_options(E96_LIST_CORRECTED, count=6)
    options_combined = find_combined_options(E24_LIST, E96_LIST_CORRECTED, count=6)

    # --- Display helper ---
    def display_options(options, title, combined=False, with_note=True):
        print(f"\n{title}")
        if combined:
            print("| Vout      | Error      | R1         | R2         | Current  |")
            print("|-----------|------------|------------|------------|----------|")
        else:
            print("| Vout      | Error      | R1      | R2      | Current  | Note       |")
            print("|-----------|------------|---------|---------|----------|------------|")

        for opt in options:
            error_mv = int(round((opt[1] - vout_target) * 1000))
            error_str = f"{error_mv:+d} mV"
            vout_str = f"{opt[1]:.3f}"
            if combined:
                r1_str = f"{format_resistor(opt[2])} (1%)"
                r2_str = f"{format_resistor(opt[3])} (0.1%)"
                print(f"| {vout_str:<8} | {error_str:<10} | {r1_str:<11} | {r2_str:<11} | {format_current(opt[4]):<8} |")
            else:
                note = opt[5] if with_note else ""
                print(f"| {vout_str:<8} | {error_str:<10} | {format_resistor(opt[2]):<7} | {format_resistor(opt[3]):<7} | {format_current(opt[4]):<8} | {note:<10} |")

    # --- Output all tables ---
    display_options(options_1pct, "1% OPTIONS (Closest, up to 6)")
    display_options(options_01pct, "0.1% OPTIONS (Closest, 0.1–1 mA)", with_note=False)
    display_options(options_combined, "COMBINED OPTIONS (1% + 0.1%, top 6)", combined=True)

# -------------------------------
# Inverting Op Amp + Offset (combined table, % error)
# -------------------------------
def basic_inverting_with_offset():
    print("\n--- Inverting Op Amp + Offset Calculator ---")

    # 1️⃣ Get user inputs
    vin_min = float(input("Enter Vin(min) (V): "))
    vin_max = float(input("Enter Vin(max) (V): "))
    vout_min = float(input("Enter Vout(min) (V): "))
    vout_max = float(input("Enter Vout(max) (V): "))

    # Validate input order
    while vin_min >= vin_max or vout_min >= vout_max:
        print("Error: Ensure Vin_min < Vin_max and Vout_min < Vout_max.")
        vin_min = float(input("Enter Vin(min) (V): "))
        vin_max = float(input("Enter Vin(max) (V): "))
        vout_min = float(input("Enter Vout(min) (V): "))
        vout_max = float(input("Enter Vout(max) (V): "))

    # 2️⃣ Compute gain and offset
    ΔVin = vin_max - vin_min
    ΔVout = vout_max - vout_min
    if ΔVin == 0:
        print("Error: ΔVin = 0, cannot continue.")
        return

    A = ΔVout / ΔVin        # Rfb/Rin
    gain = -A                # inverting
    Vplus = (vout_min + A * vin_max) / (1 + A)
    need_offset = abs(Vplus) > 1e-9

    if need_offset:
        Vref = float(input("Enter available Vref for offset divider (V): "))
    else:
        Vref = 0

    print("\n--- Pseudocode / Summary ---")
    print(f"  Vin(min) = {vin_min:.3f} V, Vin(max) = {vin_max:.3f} V")
    print(f"  Vout(min) = {vout_min:.3f} V, Vout(max) = {vout_max:.3f} V")
    print(f"  Gain = {gain:.4f}")
    print(f"  Vplus = {Vplus:.4f} V")
    if need_offset:
        print(f"  Offset divider → from Vref = {Vref:.3f} V to Vplus = {Vplus:.3f} V")
    else:
        print("  No offset required (Vplus ≈ 0 V)")

    # 3️⃣ Search for resistor combinations
    GOLDILOCKS_MIN, GOLDILOCKS_MAX = 0.0001, 0.001  # 0.1–1 mA
    worst_vin = max(abs(vin_min), abs(vin_max))

    E96_LIST_CORRECTED = [v * (10 ** d) for d in range(0, 7) for v in E96_BASE]

    def ratio_error(rfb, rin): return abs((rfb / rin) - A)
    def input_current(rin): return worst_vin / rin if rin else float('inf')

    # Combine all options (1%/0.1%/mixed) in priority order
    def find_best_pairs(list_rfb, list_rin, tag_rfb, tag_rin):
        out = []
        for rfb in list_rfb:
            for rin in list_rin:
                if rin == 0: continue
                err = ratio_error(rfb, rin)
                curr = input_current(rin)
                if GOLDILOCKS_MIN <= curr <= GOLDILOCKS_MAX:
                    out.append((err, rfb, rin, curr, tag_rfb, tag_rin))
        return out

    all_results = []
    all_results += find_best_pairs(E24_LIST, E24_LIST, "1%", "1%")          # 1% only
    all_results += find_best_pairs(E96_LIST_CORRECTED, E96_LIST_CORRECTED, "0.1%", "0.1%")  # 0.1% only
    all_results += find_best_pairs(E24_LIST, E96_LIST_CORRECTED, "1%", "0.1%") + \
                   find_best_pairs(E96_LIST_CORRECTED, E24_LIST, "0.1%", "1%")                # mixed

    # Sort by closest gain, then current
    all_results.sort(key=lambda x: (x[0], x[3]))

    # Keep unique combinations
    seen, unique_results = set(), []
    for err, rfb, rin, curr, tag_rfb, tag_rin in all_results:
        key = (round(rin, 5), round(rfb, 5))
        if key not in seen:
            seen.add(key)
            unique_results.append((err, rfb, rin, curr, tag_rfb, tag_rin))
        if len(unique_results) >= 12:
            break

    # 4️⃣ Display combined table
    print("\n--- Combined Gain Options ---")
    print("| Gain    | Error % | Rin        | Rfb        | Current | Types       |")
    print("|---------|---------|------------|------------|---------|-------------|")
    for err, rfb, rin, curr, tag_rfb, tag_rin in unique_results:
        g = -(rfb / rin)
        err_pct = ((g - gain) / gain * 100) if gain != 0 else 0.0
        print(f"| {g:7.3f} | {err_pct:7.2f}% | {format_resistor(rin):10} | {format_resistor(rfb):10} | {format_current(curr):8} | Rin:{tag_rin},Rfb:{tag_rfb} |")

    # 5️⃣ Offset divider (unchanged)
    if need_offset:
        print("\n--- Offset Divider Options ---")
        print("Target equation:  Vplus = Vref * (Rbot / (Rtop + Rbot))")
        print(f"→ Need Vplus = {Vplus:.4f} V from Vref = {Vref:.4f} V\n")

        ratio_target = Vplus / Vref
        if ratio_target <= 0 or ratio_target >= 1:
            print("⚠️  Invalid ratio — check Vref and Vplus.")
            return

        pairs = []
        for rtop in E24_LIST:
            for rbot in E24_LIST:
                if rtop + rbot == 0: continue
                v = Vref * (rbot / (rtop + rbot))
                err = abs(v - Vplus)
                i_div = Vref / (rtop + rbot)
                if i_div > 1e-6:
                    pairs.append((err, rtop, rbot, i_div))
        pairs.sort(key=lambda x: (x[0], x[3]))
        print("| V+      | Error % | Rtop      | Rbot      | Idiv     |")
        print("|---------|---------|-----------|-----------|----------|")
        for err, rtop, rbot, i_div in pairs[:6]:
            v_ach = Vref * (rbot / (rtop + rbot))
            err_pct = ((v_ach - Vplus) / Vplus * 100) if Vplus != 0 else 0.0
            print(f"| {v_ach:7.3f} | {err_pct:+7.2f}% | {format_resistor(rtop):9} | {format_resistor(rbot):9} | {format_current(i_div):8} |")

    print("\n✅ Done.\n")



# -------------------------------
# Main Menu
# -------------------------------

def main():
    while True:
        print("\n--- Circuit Math Tool ---")
        print("1. Voltage Divider")
        print("2. Inverting Op Amp (with optional offset)")
        print("3. Summing Inverting Op Amp")
        print("4. Non-Inverting Op Amp")
        print("5. Exit")
        choice = input("Select a function (1-5): ")
        if choice == "1":
            voltage_divider()
        elif choice == "2":
            basic_inverting_with_offset()
        elif choice == "3":
            print("Summing Inverting Op Amp function not implemented yet.")
        elif choice == "4":
            print("Non-Inverting Op Amp function not implemented yet.")
        elif choice == "5":
            print("Exiting...")
            break
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    main()
