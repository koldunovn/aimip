This directory contains the scripts I used for data preparation for AIMIP, and that you can modify to your needs.

Most interesting probably is a function `cmorize_data_with_template` from `cmor_utils.py`, that allows you to use existing CMORized files as templates for your own data.   

The simplest way to use it is:
```python

import xarray as xr
from data_preparation.cmor_utils import cmorize_data_with_template

my_interpolated_data = "/work/ab0995/a270088/AIMIP/MPI-M/MPI-ESM1-2-LR/aimip/r1i1p1f1/Amon/tas/gr/v20190815/tas_Amon_MPI-ESM1-2-LR_amip_r1i1p1f1_gr_197901-199812.nc"
template_for_this_variable = "/work/ab0995/a270088/AIMIP/MPI-M/MPI-ESM1-2-LR/aimip/r1i1p1f1/Amon/tas/gr/v20190815/tas_Amon_MPI-ESM1-2-LR_amip_r1i1p1f1_gr_197901-199812.nc"
my_data_in_numpy = xr.open_dataset(my_interpolated_data)['tas'].to_numpy() + 5
metadata_overrides = {
        'source_id': 'MyNewModelFromArray',}
cmorize_data_with_template(
            user_data_array=my_data_in_numpy,
            template_path=template_for_this_variable,
            output_path='./t.nc',
            metadata_overrides=metadata_overrides
        )
```

The scripts are:

- cmor_utils.py: Utility functions for CMORizing data.
- native_to_1degree.py: Interpolates native data to a 1 degree grid and create CMOR files.
- extract_plevels_multi.py: Extracts pressure levels and create CMOR files.
- example_template_usage.py: Example usage of `cmorize_data_with_template` from `cmor_utils.py`.

Limitations:
- `cmorize_data_with_template` assumes the number of time steps is the same in the template and the user data.




