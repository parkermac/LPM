# README for LPM

#### This repo is for Parker MacCready's analysis code.  It it meant to be an updated version of ptools.  Code here may often assume it is being run in the (loenv) python environment, and has access to things like the modules in the lo_tools package.

#### Some of the directory structure may mimic that in LO, as needed, and may write to LO_output or LPM_output as convenient.

---

#### TEF (not up to date)

`test_freshwater.py` is a simple test of the sensitivity of freshwater transport to the value of Socn.

`allSect_[*].py` are several plotting codes use the two-layer properties averaged over some time period, and plotted for all sections on one plot.

`threeTide_[*].py` are several plotting codes that are customized to plot the results of three tidal manipulation experiments at once,

`Qprism_series.py` plots time series of the results of bulk_calc.py, focusing on dynamical response to Qprism for a single section.
