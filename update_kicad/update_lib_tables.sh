cd ~/Library/Preferences/kicad

#Backup the old tables
echo ""
echo "Backing up the existing fp-lib-table and sym-lib-table as fp-lib-table.bak and sym-lib-table.bak"
cp fp-lib-table fp-lib-table.bak
cp sym-lib-table sym-lib-table.bak

#Copy the lib tables to the User directory
echo ""
echo "Copying the new fp-lib-table and sym-lib-table files into ~/Library/Preferences/kicad/"
cp /Library/Application\ Support/kicad/template/fp-lib-table ~/Library/Preferences/kicad/fp-lib-table-new
cp /Library/Application\ Support/kicad/template/sym-lib-table ~/Library/Preferences/kicad/sym-lib-table-new

#Extract the 4ms libs 
echo ""
echo "Extracting all lines containing '4ms' from the existing lib-tables"
cat fp-lib-table | grep 4ms > fp-lib-table-4ms
cat sym-lib-table | grep 4ms > sym-lib-table-4ms

#Disable all kicad libraries (we only want the 4ms libraries enabled)
echo ""
echo "Disabling all kicad official libraries"
sed 's/))$/)(disabled))/' fp-lib-table-new > fp-lib-table-tmp
sed 's/))$/)(disabled))/' sym-lib-table-new > sym-lib-table-tmp

#Merge the 4ms library lines after the first line --- first line starts with '(fp_lib_table'
echo ""
echo "Merging the 4ms library lines and the new fp-lib-table"
rm fp-lib-table
sed -e '/(fp_lib_table/rfp-lib-table-4ms' fp-lib-table-tmp > fp-lib-table

#Merge the 4ms library lines after the first line --- first line starts with '(sym_lib_table'
echo ""
echo "Merging the 4ms library lines and the new sym-lib-table"
rm sym-lib-table
sed -e '/(sym_lib_table/rsym-lib-table-4ms' sym-lib-table-tmp > sym-lib-table

#Display difference in tables
echo ""
echo "Difference between old and new fp-lib-table:"
diff <(sed -e "s/\"//g" fp-lib-table) <(sed -e "s/\"//g" fp-lib-table.bak)

echo ""
echo "Difference between old and new sym-lib-table:"
diff <(sed -e "s/\"//g" sym-lib-table) <(sed -e "s/\"//g" sym-lib-table.bak)

echo ""
echo "Removing temp files"
rm fp-lib-table-tmp fp-lib-table-new fp-lib-table-4ms
rm sym-lib-table-tmp sym-lib-table-new sym-lib-table-4ms

echo ""
echo "Done!"
echo ""
