#!/bin/bash
if [ -f ../data/*.glade.h ]
then
  rm ../data/*.glade.h
fi
intltool-extract --type=gettext/glade ../data/bluewho.glade

if ! [ -f bluewho.pot ]
then
  touch bluewho.pot
fi
xgettext --language=Python --keyword=_ --keyword=N_ --output bluewho.pot ../data/*.glade.h ../src/*.py
rm ../data/*.glade.h
read
