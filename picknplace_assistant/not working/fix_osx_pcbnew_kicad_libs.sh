#!/bin/bash
# Inspired on: https://www.bountysource.com/issues/31269729-libwx_osx_cocoau-3-1-dylib-not-found

KICAD_LIBS_TOFIX="libwx_osx_cocoau_gl-3.0.0 libwx_osx_cocoau_adv-3.0.0 libwx_osx_cocoau_aui-3.0.0 libwx_osx_cocoau_adv-3.0.0 libwx_osx_cocoau_html-3.0.0 libwx_osx_cocoau_core-3.0.0 libwx_osx_cocoau_stc-3.0.0 libkicad_3dsg.2.0.0 libGLEW.2.0.0 libcairo.2 libpixman-1.0 libwx_baseu_net-3.0.0 libwx_baseu-3.0.0 libwx_baseu_xml-3.0.0"

#KICAD_LIBS_TOFIX=`find /Applications/Kicad/kicad.app/Contents/Frameworks/ -iname *.dylib | xargs otool -L | grep executable_path | awk '{print $1}' | awk -F'/' '{print $4}'`

for kicadlib in $KICAD_LIBS_TOFIX;
do
	echo "Fixing ${kicadlib} broken path on pcbnew..."
	install_name_tool -change @executable_path/../Frameworks/${kicadlib}.dylib /Applications/Kicad/kicad.app/Contents/Frameworks/${kicadlib}.dylib /Applications/Kicad/pcbnew.app/Contents/Frameworks/python/site-packages/_pcbnew.so
done

echo "Done! All paths should be absolute now, no @executable_path in:"
otool -L /Applications/Kicad/kicad.app/Contents/Frameworks/python/site-packages/_pcbnew.so


# Brute force step
echo "Forcing absolute paths on all the dylibs and dependencies on KiCAD, this might take a while..."
for kicadlib in $KICAD_LIBS_TOFIX;
do
	for kicaddep in $KICAD_LIBS_TOFIX;
	do
		echo "Fixing ${kicadlib} referenced by ${kicaddep}..."
		install_name_tool -change @executable_path/../Frameworks/${kicadlib}.dylib /Applications/Kicad/kicad.app/Contents/Frameworks/${kicadlib}.dylib /Applications/Kicad/pcbnew.app/Contents/Frameworks/${kicaddep}.dylib
	done
done

