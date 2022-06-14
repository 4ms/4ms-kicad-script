## XY-pos-file-convert

Converts a Kicad pos file to the format JLCPCB expects. Rotates components, and re-arranges the CSV file columns.

To run:

```
python3 pos_file_convery.py path/to/MyProject-all-pos.csv path/to/MyProject-JLCPCB-cpl.csv
```

The second argument is optional. If missing, the output file will be in the same folder as the input.

`python3` may need to be just `python` for your system.
