cd ~/Library/Preferences/kicad

echo ""
echo "Disabling all libraries in the global lib-table files"
sed 's/\([^d]\)))$/\1)(disabled))/' fp-lib-table > fp-lib-table-tmp
sed 's/\([^d]\)))$/\1)(disabled))/' sym-lib-table > sym-lib-table-tmp

mv fp-lib-table fp-lib-table.before-disabled
mv sym-lib-table sym-lib-table.before-disabled

mv fp-lib-table-tmp fp-lib-table
mv sym-lib-table-tmp sym-lib-table

echo ""
echo "Unmodified lib-tables have been saved as fp-lib-table.before-disabled and sym-lib-table.before-disabled"
echo "You usually need to restart KiCAD to see the changes."
