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

    # Common 1% resistor values
    COMMON_VALUES = [1000, 2200, 3300, 4700, 5600, 6800, 8200,
                     10000, 22000, 33000, 47000, 56000, 68000, 82000, 100000]

    # Helper: Calculate current
    def calculate_current(vin, r1, r2):
        return vin / (r1 + r2)

    # Helper: Format resistor (remove unnecessary 0s)
    def format_resistor(r):
        if r >= 1000:
            r_k = r / 1000
            if r_k.is_integer():
                return f"{int(r_k)}kΩ"
            return f"{r_k:.1f}kΩ"
        else:
            if r.is_integer():
                return f"{int(r)}Ω"
            return f"{r:.1f}Ω"

    # Helper: Format current nicely
    def format_current(curr):
        if curr >= 0.001:
            return f"{curr*1000:.1f} mA"
        return f"{curr*1e6:.1f} µA"

    # Find the 6 closest 1% options, noting if using common resistor
    def find_closest_options(resistors, count=6):
        options = []
        for r1 in resistors:
            for r2 in resistors:
                if r1 + r2 == 0:
                    continue
                vout = vin * r2 / (r1 + r2)
                error = abs(vout - vout_target)
                current = calculate_current(vin, r1, r2)
                if GOLDILOCKS_MIN <= current <= GOLDILOCKS_MAX:
                    note = "Common R" if r1 in COMMON_VALUES or r2 in COMMON_VALUES else ""
                    options.append((error, vout, r1, r2, current, note))
        options.sort(key=lambda x: x[0])
        return options[:count]

    # Find the 0.1% closest options with current filter
    def find_01pct_options(resistors, count=3):
        options = []
        for r1 in resistors:
            for r2 in resistors:
                if r1 + r2 == 0:
                    continue
                vout = vin * r2 / (r1 + r2)
                error = abs(vout - vout_target)
                current = calculate_current(vin, r1, r2)
                if GOLDILOCKS_MIN <= current <= GOLDILOCKS_MAX:
                    options.append((error, vout, r1, r2, current, ""))
        options.sort(key=lambda x: x[0])
        return options[:count]

    # Find combined options (top 3 from both lists)
    def find_combined_options(resistors1, resistors2, count=3):
        options = []

        # 1% options
        for r1 in resistors1:
            for r2 in resistors1:
                if r1 + r2 == 0:
                    continue
                vout = vin * r2 / (r1 + r2)
                error = abs(vout - vout_target)
                current = calculate_current(vin, r1, r2)
                if GOLDILOCKS_MIN <= current <= GOLDILOCKS_MAX:
                    note = "1%"
                    options.append((error, vout, r1, r2, current, note))

        # 0.1% options
        for r1 in resistors2:
            for r2 in resistors2:
                if r1 + r2 == 0:
                    continue
                vout = vin * r2 / (r1 + r2)
                error = abs(vout - vout_target)
                current = calculate_current(vin, r1, r2)
                if GOLDILOCKS_MIN <= current <= GOLDILOCKS_MAX:
                    note = "0.1%"
                    options.append((error, vout, r1, r2, current, note))

        # Sort by error
        options.sort(key=lambda x: x[0])
        return options[:count]

    # Display function with error in mV and optional Note
    def display_options(options, title):
        print(f"\n{title}")
        print("| Vout      | Error      | R1      | R2      | Current  | Note       |")
        print("|----------|------------|---------|---------|----------|------------|")
        for _, vout, r1, r2, current, note in options:
            error_mv = int(round((vout - vout_target) * 1000))  # mV
            error_str = f"{error_mv:+d} mV"
            print(f"| {vout:.3f}    | {error_str:<10} | {format_resistor(r1):<7} | {format_resistor(r2):<7} | {format_current(current):<8} | {note:<10} |")

    # Correct E96 list scaling (1Ω → 10MΩ)
    E96_LIST_CORRECTED = []
    for decade in range(-1, 7):  # 0.1Ω to 10MΩ
        factor = 10 ** decade
        for val in E96_LIST:
            E96_LIST_CORRECTED.append(val * factor)

    # Get options
    options_1pct = find_closest_options(E24_LIST, count=6)
    options_01pct = find_01pct_options(E96_LIST_CORRECTED)
    options_combined = find_combined_options(E24_LIST, E96_LIST_CORRECTED, count=3)

    # Display results
    display_options(options_1pct, "1% OPTIONS (Closest, up to 6)")
    display_options(options_01pct, "0.1% OPTIONS (Closest, 0.1–1 mA)")
    display_options(options_combined, "COMBINED OPTIONS (1% + 0.1%, top 3)")



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
            print("Inverting Op Amp function not implemented yet.")
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
