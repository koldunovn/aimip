import os
import xarray as xr
import uuid
from cmor_utils import cmorize_data_with_template

def generate_tracking_id():
    """Generates a new CMIP-compliant tracking_id."""
    return f"hdl:21.14100/{uuid.uuid4()}"

def main():
    """
    Example script to demonstrate the use of the cmorize_data_with_template function
    with an in-memory NumPy array.
    """
    # Define file paths
    base_dir = "/work/ab0995/a270088/AIMIP/MPI-M/MPI-ESM1-2-LR/aimip/r1i1p1f1/Amon/tas/gr/v20190815/"
    template_filename = "tas_Amon_MPI-ESM1-2-LR_amip_r1i1p1f1_gr_197901-199812.nc"
    template_path = os.path.join(base_dir, template_filename)

    # Check if template file exists before we proceed
    if not os.path.exists(template_path):
        print(f"Error: Template file not found at {template_path}")
        print("Please run cmorize_from_template.py to generate it first.")
        return

    # 1. Simulate a user's workflow: load data into an in-memory array.
    # For this example, we load data from the template itself.
    print(f"--- Loading user data into memory from {template_path} ---")
    with xr.open_dataset(template_path) as ds:
        # Identify the main variable and load its data into a NumPy array
        main_var_name = ds.attrs.get('variable_id', 'tas')
        #load data and modify it a bit to pretend it's a different data
        user_data_array = ds[main_var_name].to_numpy()+5
    print(f"Successfully loaded '{main_var_name}' data into array of shape {user_data_array.shape}")

    # 2. Define the output path and metadata for the new file
    output_filename = "tas_Amon_MyNewModelFromArray_amip_r1i1p1f1_gr_197901-199812.nc"
    output_path = os.path.join(base_dir, output_filename)
    
    new_tracking_id = generate_tracking_id()
    print(f"\nGenerated new tracking_id: {new_tracking_id}")
    
    metadata_overrides = {
        'source_id': 'MyNewModelFromArray',
        'institution': 'My Other Institution',
        'contact': 'me-again@example.com',
        'title': 'MyNewModel output prepared from in-memory data',
        'tracking_id': new_tracking_id,
        'experiment': 'AIMIP',
        'experiment_id': 'aimip',
        'further_info_url': '',
        'institution_id': 'MOI',
        'nominal_resolution': '100 km',
        'license': 'Whatever license'
    }

    # 3. Call the CMORization function with the in-memory data
    print("\n--- Running CMORization with In-Memory Data ---")
    try:
        cmorize_data_with_template(
            user_data_array=user_data_array,
            template_path=template_path,
            output_path=output_path,
            metadata_overrides=metadata_overrides
        )
        print(f"\nExample script finished successfully.")
        print(f"Check the new file at: {output_path}")
        print(f"You can inspect it with: ncdump -h {output_path}")
    except (ValueError, FileNotFoundError) as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    main()
