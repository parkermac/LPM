#!/bin/bash
# Script to launch a sequence of particle tracking jobs for Nina Bednarsek.
# Requires a single command line argument, e.g. 100, for the "stay" depth.
#
# typical call:
# ./nina_driver.sh 70 &

# testing
#kwa0=" -3d True -clb True -stay "

# real version
kwa0=" -d 2021.04.15 -nsd 2 -dbs 139 -dtt 60 -3d True -clb True -stay "
kwa00=" -d 2021.04.15 -nsd 2 -dbs 139 -dtt 60 -3d True -clb True -sub_tag twopart -stay "

kwa1="../../LO/tracker/tracker.py -exp nina_jdfw"$kwa0$1
kwa2="../../LO/tracker/tracker.py -exp nina_jdfe"$kwa0$1
kwa3="../../LO/tracker/tracker.py -exp nina_aih"$kwa0$1
kwa11="../../LO/tracker/tracker.py -exp nina_jdfw"$kwa00$1
kwa22="../../LO/tracker/tracker.py -exp nina_jdfe"$kwa00$1
kwa33="../../LO/tracker/tracker.py -exp nina_aih"$kwa00$1

python $kwa1 > nina_jdfw.log &
python $kwa2 > nina_jdfe.log &
python $kwa3 > nina_aih.log &
python $kwa11 > nina_jdfw_2.log &
python $kwa22 > nina_jdfe_2.log &
python $kwa33 > nina_aih_2.log &
