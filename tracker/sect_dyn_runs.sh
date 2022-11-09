#!/bin/bash
rundir='/dat1/parker/LO/tracker'
python $rundir/tracker.py -gtx cas6_v00_uu0mb -exp sect_AImid -3d True -dtt 2 -clb True -d 2021.07.25 -sh 20 -sub_tag SpringSBF > $rundir/SpringSBF.log
python $rundir/tracker.py -gtx cas6_v00_uu0mb -exp sect_AImid -3d True -dtt 2 -clb True -d 2021.07.26 -sh 14 -sub_tag SpringSBE > $rundir/SpringSBE.log
python $rundir/tracker.py -gtx cas6_v00_uu0mb -exp sect_AImid -3d True -dtt 2 -clb True -d 2021.08.01 -sh 14 -sub_tag NeapSBF > $rundir/NeapSBF.log
python $rundir/tracker.py -gtx cas6_v00_uu0mb -exp sect_AImid -3d True -dtt 2 -clb True -d 2021.08.02 -sh 8 -sub_tag NeapSBE > $rundir/NeapSBE.log

