import xarray as xr
import os
import argparse

def process_netcdf_file(input_file, output_file, pressure_levels_pa):
    """
    Extracts multiple pressure levels from a NetCDF file, preserving metadata.

    Args:
        input_file (str): Path to the input NetCDF file.
        output_file (str): Path to the output NetCDF file.
        pressure_levels_pa (list): A list of pressure levels to extract (in Pa).
    """
    try:
        # Open the dataset without decoding times to preserve original time attributes.
        with xr.open_dataset(input_file, decode_times=False) as ds:
            print(f"Successfully opened {input_file}")

            # --- Auto-detect the main data variable ---
            main_var_name = None
            for var in ds.data_vars:
                if 'plev' in ds[var].dims:
                    main_var_name = var
                    break
            
            if not main_var_name:
                print("Error: Could not find a data variable with a 'plev' dimension.")
                return
            print(f"Detected main data variable: '{main_var_name}'")

            # --- Select the specified pressure levels ---
            print(f"Extracting data for pressure levels: {pressure_levels_pa} Pa...")
            ds_subset = ds.sel(plev=pressure_levels_pa, method='nearest')

            # --- Fix metadata and encoding to match original ---

            # Restore missing_value attribute if it exists in the original encoding
            if main_var_name in ds_subset.variables and 'missing_value' in ds[main_var_name].encoding:
                ds_subset[main_var_name].attrs['missing_value'] = ds[main_var_name].encoding['missing_value']
                print(f"Restored 'missing_value' attribute for {main_var_name}")

            # Remove incorrect 'coordinates' attribute from bounds variables
            for var_name in ['time_bnds', 'lat_bnds', 'lon_bnds']:
                if var_name in ds_subset.variables and 'coordinates' in ds_subset[var_name].attrs:
                    del ds_subset[var_name].attrs['coordinates']

            # Prepare encoding for each variable
            encoding = {}
            valid_encodings = {'_FillValue', 'dtype', 'scale_factor', 'add_offset', 'units', 'calendar', 
                               'zlib', 'complevel', 'shuffle', 'fletcher32', 'contiguous', 'chunksizes', 'least_significant_digit'}

            for var_name in ds_subset.variables:
                original_encoding = ds[var_name].encoding.copy()
                var_encoding = {k: v for k, v in original_encoding.items() if k in valid_encodings}

                if 'chunksizes' in var_encoding and var_encoding['chunksizes'] is not None:
                    new_chunks = []
                    var_shape = ds_subset[var_name].shape
                    if len(var_encoding['chunksizes']) == len(var_shape):
                        for i, dim_size in enumerate(var_shape):
                            new_chunks.append(min(var_encoding['chunksizes'][i], dim_size))
                        var_encoding['chunksizes'] = tuple(new_chunks)
                    else:
                        del var_encoding['chunksizes']

                # For all non-data variables, disable _FillValue creation
                if var_name != main_var_name:
                    var_encoding['_FillValue'] = None
                
                encoding[var_name] = var_encoding

            # --- Save the new file ---
            print(f"Saving to {output_file}...")
            ds_subset.to_netcdf(
                output_file,
                encoding=encoding,
                unlimited_dims=['time']
            )
            print(f"Successfully created output file: {output_file}")

    except FileNotFoundError:
        print(f"Error: Input file not found at {input_file}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    # --- Configuration ---
    # Define the pressure levels you want to extract in hPa
    PRESSURE_LEVELS_HPA = [1000, 850, 700, 500, 250, 100, 50]

    # --- Command-Line Argument Parsing ---
    parser = argparse.ArgumentParser(description='Extract specific pressure levels from a NetCDF file.')
    parser.add_argument('input_file', type=str, help='Path to the input NetCDF file.')
    args = parser.parse_args()

    # --- Execution ---
    # Convert pressure levels from hPa to Pascals
    pressure_levels_pa = [p * 100 for p in PRESSURE_LEVELS_HPA]

    # Define the output file path
    input_dir = os.path.dirname(args.input_file)
    input_filename_base = os.path.basename(args.input_file).replace('.nc', '')
    output_filename = f"{input_filename_base}_multi_plev.nc"
    output_file_path = os.path.join(input_dir, output_filename)

    print("--- Starting Multi-Level Pressure Extraction ---")
    process_netcdf_file(args.input_file, output_file_path, pressure_levels_pa)
    print("--- Script Finished ---")
