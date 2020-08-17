#!/bin/sh
for f in Symbols/*.lib; do kifield -x $f -i `echo $f | sed -e 's/\.lib/.csv/'`; done
for f in Symbols/*.csv; do sed -i.bk 's/,Specifications/,description/' $f; done
for f in Symbols/*.csv; do sed -i.bk 's/,datasheet/,docfile/' $f; done
for f in Symbols/*.csv; do sed -i.bk 's/,value/,keywords/' $f; done
for f in Symbols/*.csv; do kifield -x $f -i `echo $f | sed -e 's/\.csv/.dcm/'`; done
