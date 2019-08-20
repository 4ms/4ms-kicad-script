#!/usr/bin/env bash
echo "****************"
echo "Before running this, download the latest Kicad nightly from here:"
echo "https://kicad-downloads.s3.cern.ch/index.html?prefix=osx/nightly/"
echo "This script supports the nightly and the unified dmg."
echo ""
echo "Then mount the dmg (double-click it in Finder). It should be at /Volumes/KiCad"
echo ""
echo "Then run this script, which will do the following:"
echo " - It will copy the files off of the disk image into /Applications/KiCad/ and /Library/Application Support/kicad/"
echo "   -- If the Kicad disk image doesn't have the kicad/modules/packages3d folder (because you downloaded the non-unified version), "
echo "      AND you have a folder called packages3d inside /Library/Application Support/kicad/modules/"
echo "      then the script will keep your current packages3d folder but overwrite everything else in /Library/Application Support/kicad/"
echo "   -- Otherwise, this script will simply overwrite the kicad folder." 
echo " - This script will pull out any lines containing \"4ms\" in the current fp/sym-lib-table files and merge these lines into the new installation's fp/sym-lib-table"
echo " - It will install the merged fp-lib-table and sym-lib-table"
echo "   -- All kicad libraries will be disabled by default."
echo ""
echo "Ready? Make sure KiCad is not running and the KiCad dmg is mounted."
echo ""
echo ""
echo "Also! You must have rsync version 3.1 or later installed. You have:"
echo "-------------------------------------------------------------------"
rsync --version
echo "-------------------------------------------------------------------"
echo ""
echo "If the above line doesn't say v3.1 or later, then run brew install rsync"
echo "Or brew upgrade rsync. You may have to open a new terminal window to get the new version to run."

read -n1 -rsp "Press space to continue or any other key to cancel" key
if [ "$key" = '' ]; then
	echo ""
	echo "Copying KiCad app..."
	rsync -ah --info=progress2 /Volumes/KiCad/KiCad /Applications

	echo ""
	if [ -d "/Volumes/KiCad/kicad/modules/packages3d" ] 
	then
	    echo "packages3d found on the disk image. If any packages3d folder is already installed, it will be overwritten." 
	    do_overwrite = 1
	else
	    echo "No packages3d found on the disk image."
	    if [ -d "/Library/Application\ Support/kicad/packages3d" ] 
		then
		    echo "...and packages3d is already installed. It will be kept."
		    do_overwrite = 0
		else
		    echo "...and no packages3d found already installed."
		    do_overwrite = 1
		fi
	fi

	if test $do_overwrite -eq 1
	then
		echo ""
		echo "Copying /Volumes/KiCad/kicad/template into Application Support/kicad..."
		rsync -ah --info=progress2 /Volumes/KiCad/kicad/template /Library/Application\ Support/kicad/

		echo ""
		echo "Copying /Volumes/KiCad/kicad/library into Application Support/kicad..."
		rsync -ah --info=progress2 /Volumes/KiCad/kicad/library /Library/Application\ Support/kicad/

		echo ""
		echo "Copying /Volumes/KiCad/kicad/share into Application Support/kicad..."
		rsync -ah --info=progress2 /Volumes/KiCad/kicad/share /Library/Application\ Support/kicad/

		echo ""
		echo "Copying /Volumes/KiCad/kicad/help into Application Support/kicad..."
		rsync -ah --info=progress2 /Volumes/KiCad/kicad/help /Library/Application\ Support/kicad/

		echo ""
		echo "Moving packages3d out of the way..."
		mv /Library/Application\ Support/kicad/modules/packages3d /Library/Application\ Support/kicad/packages3d

		echo ""
		echo "Copying /Volumes/KiCad/kicad/modules into Application Support/kicad..."
		rsync -ah --info=progress2 /Volumes/KiCad/kicad/modules /Library/Application\ Support/kicad/

		echo ""
		echo "Moving packages3d back into modules/..."
		mv /Library/Application\ Support/kicad/packages3d /Library/Application\ Support/kicad/modules/packages3d
	else
		echo ""
		echo "Copying /Volumes/KiCad/kicad into Application Support/kicad..."
		rsync -ah --info=progress2 /Volumes/KiCad/kicad /Library/Application\ Support/
	fi

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
	diff fp-lib-table fp-lib-table.bak

	echo ""
	echo "Difference between old and new sym-lib-table:"
	diff sym-lib-table sym-lib-table.bak

	echo ""
	echo "Done!"
	echo ""
else
	echo ""
	echo "Canceled."
fi
