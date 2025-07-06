import xarray as xr
import os
from datetime import datetime
import pytz
import numpy as np

def cmorize_data_with_template(user_data_array, template_path, output_path, metadata_overrides):
    """
    Replaces the data of the main variable in a template NetCDF file with data from a user's
    in-memory NumPy array, updates metadata, and saves a new CMOR-compliant file.

    Args:
        user_data_array (np.ndarray): The user's n-dimensional data array.
        template_path (str): Path to the CMOR-compliant template NetCDF file.
        output_path (str): Path for the new output NetCDF file.
        metadata_overrides (dict): Dictionary of global attributes to update (e.g., {'source_id': 'NewModel'}).
    """
    print(f"--- Starting CMORization Process ---")
    print(f"User data: In-memory NumPy array of shape {user_data_array.shape}")
    print(f"Template: {template_path}")
    print(f"Output: {output_path}")

    with xr.open_dataset(template_path, decode_times=False) as template_ds:

        # 1. Determine the main variable name from the template
        main_var_name = template_ds.attrs.get('variable_id')
        if not main_var_name or main_var_name not in template_ds.data_vars:
            raise ValueError("Cannot determine main variable from 'variable_id' in template.")
        print(f"\nIdentified main data variable: '{main_var_name}'")

        # 2. Start with a deep copy of the template to preserve all metadata
        cmor_ds = template_ds.copy(deep=True)

        # 3. Replace the data array
        print("Replacing data with user-provided array.")
        # Ensure dimensions match before replacing data
        template_shape = cmor_ds[main_var_name].shape
        if user_data_array.shape != template_shape:
            raise ValueError(f"Shape of user data array {user_data_array.shape} does not match shape of template data {template_shape}.")
        cmor_ds[main_var_name].data = user_data_array

        # 4. Apply metadata overrides
        print("\nApplying metadata overrides...")
        for key, value in metadata_overrides.items():
            if key in cmor_ds.attrs:
                print(f"  - Overriding global attribute '{key}': '{cmor_ds.attrs.get(key)}' -> '{value}'")
                cmor_ds.attrs[key] = value
            else:
                print(f"  - Adding new global attribute '{key}': '{value}'")
                cmor_ds.attrs[key] = value

        # 5. Update history
        history_update = f"{datetime.now(pytz.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}: Data replaced with user-provided in-memory data."
        cmor_ds.attrs['history'] = f"{history_update} ; {template_ds.attrs.get('history', '')}"
        print("\nUpdated history attribute.")

        # 6. Prepare encodings and perform final cleanup (lessons learned)
        print("\nPreparing encodings and performing final cleanup...")
        encoding = {}
        valid_keys = {'_FillValue', 'dtype', 'scale_factor', 'add_offset', 'units', 'calendar', 'zlib', 'complevel', 'shuffle', 'fletcher32', 'contiguous', 'chunksizes', 'least_significant_digit'}

        # Demote 'height' to prevent attribute propagation issues
        if 'height' in cmor_ds.coords:
            cmor_ds = cmor_ds.reset_coords(['height'])
            print("  - Demoted 'height' from coordinate to data variable.")

        for var_name in cmor_ds.variables:
            da = cmor_ds[var_name]
            var_encoding = template_ds[var_name].encoding.copy() if var_name in template_ds else {}

            # Disable _FillValue for coordinates, bounds, and our special 'height' case
            if var_name in cmor_ds.coords or '_bnds' in var_name or var_name == 'height':
                var_encoding['_FillValue'] = None
            
            # Clean up rogue 'coordinates' attributes
            if 'coordinates' in da.attrs and var_name != main_var_name:
                 del da.attrs['coordinates']

            encoding[var_name] = {k: v for k, v in var_encoding.items() if k in valid_keys}

        # 7. Save the final file
        print("\nSaving to NetCDF...")
        cmor_ds.to_netcdf(output_path, encoding=encoding, unlimited_dims=['time'])
        print(f"\nSuccessfully created {output_path}")

    return
