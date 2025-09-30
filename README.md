AIMIP data preparation
==

The easiest way to start converting your data into CMORized files is to download the example files we’ve prepared and use them as templates for your own data.

Accessing the data
===

The data are stored in an S3 bucket at DKRZ. Here’s an example of how to access them:

```python
import xarray as xr
import s3fs

fs = s3fs.S3FileSystem(client_kwargs={'endpoint_url': 'https://s3.eu-dkrz-1.dkrz.cloud'},anon=True)

# We only list files interpolated on regular grid (gr)
files = fs.glob('ai-mip/MPI-M/MPI-ESM1-2-LR/aimip/r1i1p1f1/Amon/*/gr/*/*')
# Variables you want to analyse
selected_vars = ['tas', 'pr', 'ps']
selected_files = [f for f in files if any(f"/{var}/" in f for var in selected_vars)]
open_files = [fs.open(f) for f in selected_files]

# Open files with Xarray
ds = xr.open_mfdataset(
    open_files,
    engine='h5netcdf',
    combine='by_coords'
)
```

If you want to download all data and preserve the folder structure (which is required by some CMIP analysis software), use:

```python
fs.get('ai-mip/', './AMPI-local/', recursive=True)
```

More examples in `data_read` directory.

**NOTE!** Before the core AIMIP-1 paper is published, the authors of any paper, arxiv or conference preprint based on AIMIP-1 outputs must offer coauthorship to all the AIMIP-1 contributing modeling groups before that paper/arxiv/preprint is submitted.

Example files
===
We have prepared example files for all variables listed in the [AMIP proposal](https://docs.google.com/document/d/1-NqmXTrEGolzzUdQdMQER43sluNvqeJIiRZeYjE2jKY/edit?tab=t.0#heading=h.agwogvnn8ud) (currently only `Amon` frequency) using `MPI-ESM1-2-LR` model AMIP simulations. These files are located at `/ai-mip/MPI-M/MPI-ESM1-2-LR/` as shown above. Versions are available both on the native grid (`gn`) and interpolated to a 1° regular grid (`gr`).

Uploading Your Data
===
We expect the data to be CMORized (i.e., converted to the standard CMIP6 format). If you have experience with CMORization and can provide fully CMOR-compliant files, great! However, to simplify the process, we provide example files to use as templates. The closer your data are to the example format, the more likely your model will be included in every analysis. If you plan to publish your data on ESGF later, full CMOR compliance is the only option 🤷.

There are some [minimum requirements for ESMValTool compatibility](https://gist.github.com/schlunma/fb7fb96f8a41c476bb1e1d99be321097#absolutely-mandatory-criteria), but in general: the closer your data are to true CMOR compliance, the better 😊.

You can find example on how to use example data as a template for your own data in `data_preparation/example_template_usage.py`.

Folder and File Naming Conventions
====
We expect you to follow the same folder structure as used in the example files. While there’s a [detailed specification document](https://docs.google.com/document/d/1h0r8RZr_f3-8egBMMh7aqLwy3snpD6_MrDz1q8n5XUk/edit?tab=t.0), here’s a brief summary of the most relevant elements:

Folder structure:
`MPI-M/MPI-ESM1-2-LR/aimip/r1i1p1f1/Amon/pr/gr/v20190815/`

- `MPI-M`: Institute name
- `MPI-ESM1-2-LR`: Model name
- `aimip`: Activity name
- `r1i1p1f1`: Realization (ensemble member)
- `Amon` Output frequency
- `pr` Variable name
- `gr` Grid type
- `v20190815` Data version

File name:
`pr_Amon_MPI-ESM1-2-LR_amip_r1i1p1f1_gr_197901-199812.nc`

- `pr` Variable
- `Amon` Frequency
- `MPI-ESM1-2-LR` Model
- `amip` Activity (in our case we rename to `aimip`, but I keep `amip` in the example files to avoid confusion)
- `r1i1p1f1` Realization
- `gr` Grid type (we use gr for regular 1 degree grid; gn can be used for native grid)
- `197901-199812` Time period

More details is available in the [AMIP Specification](https://docs.google.com/document/d/1-NqmXTrEGolzzUdQdMQER43sluNvqeJIiRZeYjE2jKY/edit?tab=t.0#heading=h.agwogvnn8ud).

At a minimum, you must define:
- Name of the institute e.g. `RTE-RRTMGP-Consortium` (use only dashes, no underscores)
- Name of the model e.g. `MPI-ESM1-2-LR` (use only dashes, no underscores)

Use these consistently across all your data. If your institute already participates in CMIP, [check this list](https://github.com/WCRP-CMIP/CMIP6_CVs/blob/main/CMIP6_institution_id.json), and use the official name.

When your data are ready, contact Nikolay Koldunov (nikolay.koldunov@awi.de,  use “AIMIP” in the subject line), and we will upload it to the bucket. In the future, we plan to allow direct uploads to institute-specific folders.

TODO
===
- Add daily data examples
- Add catalog (intake, maybe STAC later)
- Make zarr version (at least for monthly data)







