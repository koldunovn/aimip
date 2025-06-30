import xarray as xr
import os

def extract_pressure_level(input_file, output_file, pressure_level):
    """
    Extracts a single pressure level from a NetCDF file and saves it to a new file,
    preserving metadata and dimensions as closely as possible.

    Args:
        input_file (str): Path to the input NetCDF file.
        output_file (str): Path to the output NetCDF file.
        pressure_level (float): The pressure level to extract (in Pa).
    """
    try:
        # Open the dataset without decoding times to preserve original time attributes.
        with xr.open_dataset(input_file, decode_times=False) as ds:
            print(f"Successfully opened {input_file}")

            pressure_coord = 'plev'

            if pressure_coord not in ds.coords:
                print(f"Error: Pressure coordinate '{pressure_coord}' not found in the dataset.")
                print(f"Available coordinates are: {list(ds.coords.keys())}")
                return

            # Select the specified pressure level using a slice `[pressure_level]`
            # to ensure the 'plev' dimension is kept.
            print(f"Extracting data for pressure level {pressure_level} Pa...")
            ds_subset = ds.sel({pressure_coord: [pressure_level]}, method='nearest')

            # --- Fix metadata discrepancies ---

            # Restore missing_value attribute for the data variable if it exists in the original encoding
            if 'zg' in ds_subset.variables and 'missing_value' in ds['zg'].encoding:
                ds_subset['zg'].attrs['missing_value'] = ds['zg'].encoding['missing_value']
                print("Restored 'missing_value' attribute for zg")

            # Remove incorrect 'coordinates' attribute from bounds variables if present
            for var_name in ['time_bnds', 'lat_bnds', 'lon_bnds']:
                if var_name in ds_subset.variables and 'coordinates' in ds_subset[var_name].attrs:
                    del ds_subset[var_name].attrs['coordinates']
                    print(f"Removed 'coordinates' attribute from {var_name}")

            # Prepare encoding to prevent unwanted attributes and match original file structure.
            encoding = {}
            # List of valid encoding keys for the netCDF4 backend.
            valid_encodings = {'_FillValue', 'dtype', 'scale_factor', 'add_offset',
                               'units', 'calendar', 'zlib', 'complevel', 'shuffle',
                               'fletcher32', 'contiguous', 'chunksizes', 'least_significant_digit'}

            for var_name in ds_subset.variables:
                # Start with a copy of the original encoding
                original_encoding = ds[var_name].encoding.copy()

                # Filter to only include valid encoding keys
                var_encoding = {k: v for k, v in original_encoding.items() if k in valid_encodings}

                # Adjust chunk sizes to not exceed dimension sizes
                if 'chunksizes' in var_encoding and var_encoding['chunksizes'] is not None:
                    new_chunks = []
                    var_shape = ds_subset[var_name].shape
                    if len(var_encoding['chunksizes']) == len(var_shape):
                        for i, dim_size in enumerate(var_shape):
                            original_chunk = var_encoding['chunksizes'][i]
                            new_chunks.append(min(original_chunk, dim_size))
                        var_encoding['chunksizes'] = tuple(new_chunks)
                        print(f"Adjusted chunksizes for {var_name} to {var_encoding['chunksizes']}")
                    else:
                        del var_encoding['chunksizes']
                        print(f"Removed mismatched chunksizes for {var_name}")

                # For coordinate/bounds variables, disable _FillValue creation.
                # For the data variable 'zg', allow its original _FillValue to be used.
                if var_name != 'zg':
                    var_encoding['_FillValue'] = None
                
                encoding[var_name] = var_encoding

            # Save the subset to a new NetCDF file with the specified encoding.
            print(f"Saving to {output_file}...")
            ds_subset.to_netcdf(
                output_file,
                encoding=encoding,
                unlimited_dims=['time']  # Ensure time remains an unlimited dimension
            )
            print(f"Successfully created output file: {output_file}")

    except FileNotFoundError:
        print(f"Error: Input file not found at {input_file}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    # --- Configuration ---
    # Path to the input NetCDF file
    INPUT_NC_FILE = '/work/ab0995/a270088/AIMIP/MPI-M/MPI-ESM1-2-LR/aimip/r1i1p1f1/Amon/zg/gn/v20190815/zg_Amon_MPI-ESM1-2-LR_amip_r1i1p1f1_gn_199901-201412.nc'

    # Desired pressure level in Pascals (e.g., 50000 Pa for 500 hPa)
    PRESSURE_LEVEL_PA = 50000

    # --- Execution ---
    # Define the output file path
    input_dir = os.path.dirname(INPUT_NC_FILE)
    input_filename_base = os.path.basename(INPUT_NC_FILE).replace('.nc', '')
    output_filename = f"{input_filename_base}_plev{int(PRESSURE_LEVEL_PA/100)}.nc"
    OUTPUT_NC_FILE = os.path.join(input_dir, output_filename)

    print("--- Starting Pressure Level Extraction (Improved Version) ---")
    extract_pressure_level(INPUT_NC_FILE, OUTPUT_NC_FILE, PRESSURE_LEVEL_PA)
    print("--- Script Finished ---")
