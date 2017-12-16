#Also need to do this, so it doesn't link against the System Python.
# See https://stackoverflow.com/questions/15678153/homebrew-python-on-mac-os-x-10-8-fatal-python-error-pythreadstate-get-no-cu
install_name_tool -change /System/Library/Frameworks/Python.framework/Versions/2.7/Python /usr/local/Cellar/python/2.7.13/Frameworks/Python.framework/Versions/2.7/lib/libpython2.7.dylib /Applications/Kicadnightly/kicad.app/Contents/Frameworks/python/site-packages/_pcbnew.so

#install matplotlib
#python2 -mpip install matplotlib

