#!/bin/bash

python tracker.py -gtx cas6_v00_uu0mb -exp sect_AImid -3d True -dtt 2 -clb True -d 2021.07.25 -sh 20 -sub_tag SpringSBF > SpringSBF.log
python tracker.py -gtx cas6_v00_uu0mb -exp sect_AImid -3d True -dtt 2 -clb True -d 2021.07.26 -sh 14 -sub_tag SpringSBE > SpringSBE.log
python tracker.py -gtx cas6_v00_uu0mb -exp sect_AImid -3d True -dtt 2 -clb True -d 2021.08.01 -sh 14 -sub_tag NeapSBF > NeapSBF.log
python tracker.py -gtx cas6_v00_uu0mb -exp sect_AImid -3d True -dtt 2 -clb True -d 2021.08.02 -sh 8 -sub_tag NeapSBE > NeapSBE.log

