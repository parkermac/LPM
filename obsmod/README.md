# README for obsmod

#### This code is for making comparisons of observations and model output. I keep it out of the LO repo because this task often involves a lot of customization depending on the evaluation you are doing. Nonetheless, many of the tools here will be useful to others in the group.

---

## Bottles and CTD casts

### PROCESSING

`combine_obs_mod.py` Is the typical starting point for obsmod comparisons. It will combine all the bottle and cast extractions with observations for a given gtagex.

You have to edit it by hand to tell it which year, which data sources, and which model runs to consider.

In the code you can also set many filters and processing options, such as limiting the source list. But ingeneral this is better done at the plottnig step.

**NOTE**: You must first have run the cast extraction for each model run and year you want to consider. This is done using the tools in `LO/extract/cast`. See the shell script there called `multi_source_cast_extraction.sh` for an example.

The output is pickled dicts with names like:

- LPM_output/obsmod/combined_bottle\_[year]\_[gtagex].p
- LPM_output/obsmod/combined_ctd\_[year]\_[gtagex].p

Each pickled dict has one dict entry for "obs" and one for [gtagex], and each of these is a pandas DataFrame, for example:

```
{'obs':          cid        lon        lat                time           z  ...     DIC (uM)  DIN (uM)  DO (mg L-1)     Omega  pCO2 (uatm)
 0        0.0 -126.33400  48.624500 2017-02-07 14:50:45   -5.900000  ...          NaN       NaN     9.031470       NaN          NaN
 1        0.0 -126.33400  48.624500 2017-02-07 14:50:45 -101.000000  ...          NaN       NaN     7.276621       NaN          NaN
 2        0.0 -126.33400  48.624500 2017-02-07 14:50:45 -800.400024  ...          NaN       NaN     0.387267       NaN          NaN
 3        1.0 -126.66700  48.648499 2017-02-07 16:39:50 -200.300003  ...          NaN       NaN     4.458573       NaN          NaN
 4        1.0 -126.66700  48.648499 2017-02-07 16:39:50 -200.399994  ...          NaN       NaN     4.472864       NaN          NaN
 ...      ...        ...        ...                 ...         ...  ...          ...       ...          ...       ...          ...
 9400  1251.0 -124.00083  48.298500 2017-02-19 11:31:00  -74.256055  ...  2115.209138       NaN     7.609300  0.995072   676.014570
 9401  1251.0 -124.00083  48.298500 2017-02-19 11:31:00  -99.927107  ...  2127.296855       NaN     7.303080  1.107846   614.519091
 9402  1251.0 -124.00083  48.298500 2017-02-19 11:31:00 -124.504865  ...  2145.534459       NaN     6.760690  1.031623   678.994606
 9403  1251.0 -124.00083  48.298500 2017-02-19 11:31:00 -149.376930  ...  2158.478812       NaN     6.457381  1.014777   703.296361
 9404  1251.0 -124.00083  48.298500 2017-02-19 11:31:00 -180.289391  ...  2191.194650       NaN     5.636788  1.052859   712.222164
 
 [9405 rows x 23 columns],
 'cas7_t1_x10ab': similar entries to obs...}

```

A typical full list of columns in each DataFrame is:

```
['cid', 'lon', 'lat', 'time', 'z', 'SA', 'CT', 'DO (uM)', 'NO3 (uM)',
       'Chl (mg m-3)', 'name', 'cruise', 'source', 'NH4 (uM)', 'PO4 (uM)',
       'SiO4 (uM)', 'NO2 (uM)', 'TA (uM)', 'DIC (uM)', 'DIN (uM)',
       'DO (mg L-1)', 'Omega', 'pCO2 (uatm)']

```

---

### PLOTTING

`plot_val.py` This makes a number of property-property plots, and a map, comparing observed and modeled fields for a number of properties. It also can filter the output, e.g. only plotting coastal stations. And it can calculate derived quantities such as pCO2.

This also saves the figure as a png in LPM_output/obsmod_val_plots.

`plot_casts.py` This focuses on CTD casts at a single station, and plots observed and modeled vertical profiles, one for each month. Typically I only apply this to Ecology stations. It works for more than one gtagex, which is isefule for model-model-obs comparisons.


---

## Moorings

All the code with names starting with "mooring_". As yet undocumented.

---

## Tide height

All the code with names starting with "tide_". As yet undocumented.

---

