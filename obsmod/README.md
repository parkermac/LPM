# README for obsmod

#### This code is for making comparisons of observations and model output. I keep it out of the LO repo because this task often involves a lot of customization depending on the evaluation you are doing. Nonetheless, many of the tools here will be useful to others in the group.

---

`process_multi_bottle.py` works on bottle observations from multiple sources and lines them up with cast extractions from multiple model runs, for one year.

You have to edit it by hand to tell it which year, which data sources, and which model runs to consider.

The output is a pickled dict with a name like:

LPM_output/obsmod/multi_bottle_2017.p

NOTE: I may want a more informative system for output naming, because this overwrites any old versions. However, the simple name makes it (somewhat) easier to do the subsequent plotting. Also this code is fast - just takes a few minutes no my mac for four sources and three model runs.

The dict keys are, for example:

['obs', 'cas6_v0_live', 'cas6_traps2_x2b', 'cas7_trapsV00_meV00']

And then each dict entry is a pandas DataFrame that looks like:

```
         cid                time        lat         lon    name  ...  cruise       source  Chl (mg m-3)      TA (uM)     DIC (uM)
0        0.0 2017-01-11 00:00:00  47.092040 -122.918197  BUD005  ...    None      ecology           NaN          NaN          NaN
1        0.0 2017-01-11 00:00:00  47.092040 -122.918197  BUD005  ...    None      ecology           NaN          NaN          NaN
2        0.0 2017-01-11 00:00:00  47.092040 -122.918197  BUD005  ...    None      ecology           NaN          NaN          NaN
3        1.0 2017-01-11 00:00:00  47.276485 -122.709575  CRR001  ...    None      ecology           NaN          NaN          NaN
4        1.0 2017-01-11 00:00:00  47.276485 -122.709575  CRR001  ...    None      ecology           NaN          NaN          NaN
...      ...                 ...        ...         ...     ...  ...     ...          ...           ...          ...          ...
9116  1140.0 2017-09-28 16:24:39  44.198200 -124.982000    HB07  ...  SH1709  nceiCoastal           NaN          NaN          NaN
9117  1140.0 2017-09-28 16:24:39  44.198200 -124.982000    HB07  ...  SH1709  nceiCoastal           NaN  2240.237304  2046.707343
9118  1140.0 2017-09-28 16:24:39  44.198200 -124.982000    HB07  ...  SH1709  nceiCoastal           NaN  2238.971453  2036.033628
9119  1140.0 2017-09-28 16:24:39  44.198200 -124.982000    HB07  ...  SH1709  nceiCoastal           NaN  2239.328260  2035.576111
9120  1140.0 2017-09-28 16:24:39  44.198200 -124.982000    HB07  ...  SH1709  nceiCoastal           NaN          NaN          NaN
```

The full list of columns in the DataFrame is:

```
['cid', 'time', 'lat', 'lon', 'name', 'z', 'CT', 'SA', 'DO (uM)',
       'NO3 (uM)', 'NO2 (uM)', 'NH4 (uM)', 'PO4 (uM)', 'SiO4 (uM)', 'cruise',
       'source', 'Chl (mg m-3)', 'TA (uM)', 'DIC (uM)']
```

**The main feature of this collection of DataFrames is that they all have exactly the same entries, which facilitates subsequent comparisons.**

"cid" is a cast identifier, which is unique for each cast and uniform across the different DataFrames.

---

`process_multi_ctd.py` is just like `process_multi_bottle.py` except it works on CTD casts, which are separate extracts in the LO/extract/cast system.

___

`plot_multi.py` is good for making property-property plots for model-model-obs comparisons. This is useful for when you are evaluating a new model to see if it is an improvement over a previous run.

By editing flags in the code you can make choices about the plots that are generated, e.g. does one plot have all the data sources, or is it a separate plot for each source.

The plots are put in `LPM_output/obsmod_plots` with names like `bottle_2017_all_deep.png` that reflect to choices you made.

---

`plot_val.py` makes a single plot of property-property panels focused on a single run, comparing it to observations. It puts everything on one plot. You can make a lot of choices to allow interesting exploration of the results, like what would happen if there was complete nitrification (NH4 => NO3)?

The output ends up in `LPM_output/obsmod_val_plots` with a name like `bottle_2017_cas7_trapsV00_meV00_all.png`.

`plot_val_fewer_panels.py` was a custom version of `plot_val.py` to make a simpler plot for a proposal.

---

`plot_casts.py` makes property vs. depth plots for individual casts. It is mainly only useful for observations like Ecology stations where we have monthly casts at one station for a year.

By default it has lines for all the runs in the df_dict, and of course for the observations. It makes one panel for each cast at a given station. Currently just plots to the screen.

---
