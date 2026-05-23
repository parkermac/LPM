# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Purpose

This is a research/exploration repo for testing zarr and xarray access patterns for LiveOcean ROMS ocean model output. The experiments cover converting NetCDF history files to zarr, reading zarr from S3-compatible storage (Kopah), and comparing chunking strategies.

## Environment

Use the `loenv` conda environment (`/Users/parkermaccready/miniconda3/envs/loenv`). Core dependencies: `xarray`, `zarr`, `s3fs`, `h5netcdf`, `dask`, and `lo_tools` (LiveOcean utilities).

```bash
conda activate loenv
python test18.py         # run a script
jupyter notebook         # run notebooks interactively
```

## Storage & Credentials

- S3 endpoint: `https://s3.kopah.uw.edu`
- Bucket: `s3://liveocean-test/`
- Auth: `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` env vars (required; anonymous access is blocked for zarr stores)
- Public NetCDF files (`his_nc_files/`) support `anon=True` via `h5netcdf` engine
- After uploading a zarr store, run `zarr.consolidate_metadata(...)` then set ACL on `.zmetadata` with `s3cmd setacl ... --acl-public`

## Data Shape

ROMS history files have dimensions `(ocean_time, s_rho, eta_rho, xi_rho)` = roughly `(25, 30, 1302, 663)` per day. Auto-chunking via xarray produces chunks like `(1, 8, 434, 221)`. Each hourly `.nc` file is ~2 GB.

## LO Environment

`lo_tools.Lfun.Lstart()` returns `Ldir`, a dict of project paths. On this machine:
- `Ldir['LO']` → `/Users/parkermaccready/Documents/LO`
- `Ldir['roms_out']` → `/Users/parkermaccready/Documents/LO_roms`
- Output goes to `~/Documents/LPM_output/zarr_test/`

## Known Issues

- `anon=True` returns `AccessDenied` for zarr on Kopah even after `--acl public-read` — consolidated metadata must also be made public separately.
- Use `xr.set_options(use_new_combine_kwarg_defaults=True)` before `open_mfdataset` to suppress combine deprecation warnings.
- Zarr v3 warns that consolidated metadata is not part of the format spec; this is safe to ignore for now.
