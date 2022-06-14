## Resistor Generator

This python script generates a Kicad 6 symbol library containing an entry for all E24 and E96 resistor values for a given SMT package size and tolerance.
By default it generates all values for which resistor manufacturer Yageo has in their [RC series](https://www.mouser.com/datasheet/2/447/Yageo_03_18_2021_PYu_RC_Group_51_RoHS_L_11-2199992.pdf).

Ranges:
  * 1% 0201 to 2512: 1Ω to 10M
  * 0.1% 0402: 4.7Ω to 240k
  * 0.1% 0603 to 2512: 1Ω to 1MΩ

A Yageo part number is generated for each symbol and stored in the `Part Number` field. Yageo RC-series is used for 1% and RT-series for 0.1%. Also, most symbols will have a JLCPCB ID if found in the JLCPCB component database.

The `4ms_Resistor_*.kicad_sym` symbols libraries were generated with this script.

Note that the algorithm to figure out the JLCPCB part number is not guaranteed to be perfect. I welcome improvements, (ideas, tips or PRs). 
All values for 0402, 0603, 0805 for 1% and 0.1% tolerance have been manually checked and are (very likely) accurate.

Number of JLCPCB IDs missing:

  * 0402 1%: missing 50 of 798
  * 0603 1%: missing 49 of 798
  * 0805 1%: missing 47 of 798
  * 0402 0.1%: missing 276 of 536
  * 0603 0.1%: missing 120 of 685
  * 0805 0.1%: missing 295 of 703
 
 Some of these may not exist in JLCPCB's component database (i.e. very high or low values).
