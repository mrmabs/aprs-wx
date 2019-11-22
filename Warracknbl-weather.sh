#!/bin/bash
#
# get current manglore weather and transmit it to aprs server
#

#wget --passive ftp://ftp.bom.gov.au/anon/gen/fwo/IDY03023.txt
#current=`grep -i "Eildon Fir" IDY03023.txt | cut -c13- | tr -s ' ' | tail -1`

cp1=`grep -i "Warracknbl" IDY03023.txt | cut -c13-47 | tr -s ' ' | tail -1`
cp2=`grep -i "Warracknbl" IDY03023.txt | cut -c49- | tr -s ' ' | tail -1`
current="$cp1 $cp2"

./packgen.py "Warracknbl" "$current"

