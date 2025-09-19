from astropy.io import fits
import glob
import os

data_dir = '/work2/lbuc/iara/Data/HD189567/HD189567_SCIENCE.SPECTRUM'
fits_files = glob.glob(os.path.join(data_dir, '*.fits'))

print(f'Searching for RV measurements in first file: {os.path.basename(fits_files[0])}')

with fits.open(fits_files[0]) as hdul:
    print('\n=== SEARCHING FOR CCF AND RV KEYWORDS ===')
    
    # Look specifically for CCF-related keywords (Cross-Correlation Function)
    ccf_keywords = []
    rv_keywords = []
    
    for key in hdul[0].header.keys():
        if 'CCF' in key.upper():
            ccf_keywords.append((key, hdul[0].header[key]))
        elif 'RV' in key.upper() and 'BERV' not in key.upper():  # Exclude BERV
            rv_keywords.append((key, hdul[0].header[key]))
    
    if ccf_keywords:
        print("CCF-related keywords:")
        for key, value in ccf_keywords:
            print(f"  {key}: {value}")
    
    if rv_keywords:
        print("\nRV-related keywords (excluding BERV):")
        for key, value in rv_keywords:
            print(f"  {key}: {value}")
    
    # Also check for DRS keywords that might contain stellar RV
    print('\n=== CHECKING FOR DRS RV KEYWORDS ===')
    drs_rv_keywords = []
    for key in hdul[0].header.keys():
        if key.startswith('ESO DRS') and any(word in key.upper() for word in ['RV', 'RADVEL', 'VELOCITY']) and 'BERV' not in key.upper():
            drs_rv_keywords.append((key, hdul[0].header[key]))
    
    if drs_rv_keywords:
        print("DRS RV keywords:")
        for key, value in drs_rv_keywords:
            print(f"  {key}: {value}")
    else:
        print("No DRS RV keywords found")
        
    # Let's also check if there are any other keywords with 'RADIAL' or 'VELOCITY'
    print('\n=== CHECKING FOR RADIAL VELOCITY KEYWORDS ===')
    vel_keywords = []
    for key in hdul[0].header.keys():
        if any(word in key.upper() for word in ['RADIAL', 'VELOCITY']) and 'BERV' not in key.upper():
            vel_keywords.append((key, hdul[0].header[key]))
    
    if vel_keywords:
        print("Velocity-related keywords:")
        for key, value in vel_keywords:
            print(f"  {key}: {value}")


# Add this to check the SPECTRUM extension
print('\n=== CHECKING SPECTRUM EXTENSION ===')
spectrum_hdu = hdul[1]
print(f"Columns in SPECTRUM extension: {spectrum_hdu.columns.names}")

# Check if any column names suggest RV data
for col_name in spectrum_hdu.columns.names:
    print(f"Column '{col_name}': {spectrum_hdu.columns[col_name]}")
