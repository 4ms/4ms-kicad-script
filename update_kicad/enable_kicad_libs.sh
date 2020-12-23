cd ~/Library/Preferences/kicad

echo ""
echo "Enabling all libraries in the global lib-table files"
sed 's/(disabled))$/)/' fp-lib-table > fp-lib-table-tmp
sed 's/(disabled))$/)/' sym-lib-table > sym-lib-table-tmp

mv fp-lib-table fp-lib-table.before-enabled
mv sym-lib-table sym-lib-table.before-enabled

mv fp-lib-table-tmp fp-lib-table
mv sym-lib-table-tmp sym-lib-table

echo ""
echo "Unmodified lib-tables have been saved as fp-lib-table.before-enabled and sym-lib-table.before-enabled"
echo "You usually need to restart KiCAD to see the changes."
