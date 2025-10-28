"""
PyORBIT CSV Export for ESSP Submission
"""

# ============================================================================
# CONFIGURATION SECTION - CUSTOMIZE HERE
# ============================================================================

if 1: #Iara (multiple files ccf)
    dir_base = '/work2/lbuc/iara/GitHub/PyORBIT_examples/ESSP4/Results_combined/results_multiple_1022/DS2/DS2_2p/DS2_2p_ccfs/'
    dir_mods = 'DS2_2p_ccfs/'
    dir_plot = 'emcee_plot/model_files/'
    filename = 'DS2_2p_ccfs'

    datasets_list = ['RVdata_expres', 'RVdata_harps', 'RVdata_neid']
    datasets_labels = {'RVdata_expres':'EXPRES', 'RVdata_harps':'HARPS', 'RVdata_neid':'NEID'}

    activity_model = 'gp_multidimensional'

    activity_list = ['Contrastdata_expres', 'Contrastdata_harps', 'Contrastdata_neid', 'FWHMdata_expres', 'FWHMdata_harps', 'FWHMdata_neid']
    activity_labels = {'Contrastdata_expres':'EXPRES_Contrast', 'Contrastdata_harps':'HARPS_Contrast', 'Contrastdata_neid':'NEID_Contrast', 'FWHMdata_expres':'EXPRES_FWHM', 'FWHMdata_harps':'HARPS_FWHM', 'FWHMdata_neid':'NEID_FWHM'}

    full_dict = {
        'reference_planet': 'b',
    }


if 0: #Iara (multiple files)
    dir_base = '/work2/lbuc/iara/GitHub/PyORBIT_examples/ESSP4/Results_combined/results_multiple_1022/DS1/DS1_1p/DS1_1p_2_activity_indi/'
    dir_mods = 'DS1_1p_2_activity_indi/'
    dir_plot = 'emcee_plot/model_files/'
    filename = 'DS1_1p_2modes'

    datasets_list = ['RVdata_expres', 'RVdata_harps', 'RVdata_neid']
    datasets_labels = {'RVdata_expres':'EXPRES', 'RVdata_harps':'HARPS', 'RVdata_neid':'NEID'}

    activity_model = 'gp_multidimensional'

    activity_list = ['BISdata_expres', 'BISdata_harps', 'BISdata_neid', 'FWHMdata_expres', 'FWHMdata_harps', 'FWHMdata_neid']
    activity_labels = {'BISdata_expres':'EXPRES_BIS', 'BISdata_harps':'HARPS_BIS', 'BISdata_neid':'NEID_BIS', 'FWHMdata_expres':'EXPRES_FWHM', 'FWHMdata_harps':'HARPS_FWHM', 'FWHMdata_neid':'NEID_FWHM'}

    full_dict = {
        'reference_planet': 'b',
    }


if 0: #FIESTA
    dir_base = '/work2/lbuc/iara/GitHub/PyORBIT_examples/ESSP4/results_fiesta_more_steps_1022/DS2/DS2_1p_2modes/'
    dir_mods = 'DS2_1p_2modes/'
    dir_plot = 'emcee_plot/model_files/'
    filename = 'DS2_1p_2modes'

    datasets_list = ['RVdata_expres', 'RVdata_harps', 'RVdata_neid']
    datasets_labels = {'RVdata_expres':'EXPRES', 'RVdata_harps':'HARPS', 'RVdata_neid':'NEID'}

    activity_model = 'gp_multidimensional'

    activity_list = ['FIESTAdata_expres_mode1', 'FIESTAdata_expres_mode2', 'FIESTAdata_harps_mode1', 'FIESTAdata_harps_mode2', 'FIESTAdata_harpsn_mode1', 'FIESTAdata_harpsn_mode2', 'FIESTAdata_neid_mode1', 'FIESTAdata_neid_mode2']
    activity_labels = {'FIESTAdata_expres_mode1':'EXPRES_FIESTA1', 'FIESTAdata_expres_mode2':'EXPRES_FIESTA2', 'FIESTAdata_harps_mode1':'HARPS_FIESTA1', 'FIESTAdata_harps_mode2':'HARPS_FIESTA2', 'FIESTAdata_harpsn_mode1':'HARPSN_FIESTA1', 'FIESTAdata_harpsn_mode2':'HARPSN_FIESTA2', 'FIESTAdata_neid_mode1':'NEID_FIESTA1', 'FIESTAdata_neid_mode2':'NEID_FIESTA2'}

    full_dict = {
        'reference_planet': 'b',
    }


if 0: # Iara (single file)
    dir_base = '/work2/lbuc/jzhao/PyORBIT_ESSP/ESSP/iaras/DS1/DS1_3p/DS1_3p_2activity_indi/'
    dir_mods = 'DS1_3p_2activity_indi/'
    dir_plot = 'emcee_plot/model_files/'
    filename = 'iaras_DS1_3p_2activity_indi'

    datasets_list = ['RVdata']
    datasets_labels = {'RVdata': 'RV'}

    activity_model = 'gp_multidimensional'

    activity_list = ['BISdata', 'FWHMdata']
    activity_labels = {'BISdata':'BIS', 'FWHMdata':'FWHM'}

    full_dict = {
        'reference_planet': 'b',
    }


if 0: # ESSP_gp_HARPSN_EXPRES_NEID_HARPS_poly_cpu
    dir_base = './'
    dir_mods = 'ESSP_gp_HARPSN_EXPRES_NEID_HARPS_poly_cpu/'
    dir_plot = 'emcee_plot/model_files/'
    filename = 'ESSP_gp_HARPSN_EXPRES_NEID_HARPS_poly_cpu'

    datasets_list = ['ESSP_HARPSN', 'ESSP_EXPRES', 'ESSP_NEID', 'ESSP_HARPS']
    datasets_labels = {'ESSP_HARPSN':'HARPSN', 'ESSP_EXPRES':'EXPRES', 'ESSP_NEID':'NEID', 'ESSP_HARPS':'HARPS'}

    activity_model = 'gp_multidimensional'

    activity_list = ['ESSP_BIS_HARPSN', 'ESSP_BIS_EXPRES', 'ESSP_BIS_NEID', 'ESSP_BIS_HARPS']
    activity_labels = {'ESSP_BIS_HARPSN':'BIS_HARPSN', 'ESSP_BIS_EXPRES':'BIS_EXPRES', 'ESSP_BIS_NEID':'BIS_NEID', 'ESSP_BIS_HARPS':'BIS_HARPS'}

    full_dict = {
        'reference_planet': 'b',
    }


if 0: # HD189567_3p_run7
    dir_base = './'
    dir_mods = 'HD189567_3p_run7/'
    dir_plot = 'emcee_plot/model_files/'
    filename = 'HD189567_3p_run7'

    datasets_list = ['RVdata']
    datasets_labels = {'RVdata':'RV'}

    activity_model = 'gp_multidimensional'
    activity_list = ['BISdata', 'FWHMdata']
    activity_labels = {
        'BISdata':'BIS',
        'FWHMdata':'FWHM',
    }

    full_dict = {
        'reference_planet': 'b',
    }

# CSV Export Configuration
results_dir = '/work2/lbuc/iara/GitHub/PyORBIT_examples/ESSP4/submission_csv_files'
group_name = "DTUSpace"
method_name = "PyORBIT_GP"

# ============================================================================
# END OF CONFIGURATION SECTION
# ============================================================================

# ============================================================================
# IMPORTS
# ============================================================================
import numpy as np
import pandas as pd
import os

# ============================================================================
# CSV FILE GENERATION
# ============================================================================

print("\n" + "="*60)
print("GENERATING CSV FILES FOR SUBMISSION")
print("="*60)

# Create results directory if it doesn't exist
if not os.path.exists(results_dir):
    os.makedirs(results_dir)

# Get reference planet
key_name = full_dict['reference_planet']

# Initialize lists to store all data
all_data = []

# Process each dataset
for n_dataset, dataset in enumerate(datasets_list):
    print(f"Processing dataset: {dataset}")
    
    # Load RV data
    RV_mod = np.genfromtxt(
        dir_base + dir_mods + dir_plot + dataset + '_radial_velocities_' + key_name + '.dat', 
        skip_header=1
    )
    
    # Load activity data
    activity_mod = np.genfromtxt(
        dir_base + dir_mods + dir_plot + dataset + '_' + activity_model + '.dat', 
        skip_header=1
    )
    
    # Calculate values
    time_mjd = RV_mod[:, 0]  # Time in MJD
    RV_CA = RV_mod[:, 7] - RV_mod[:, 5]  # RV with activity (full model - offset)
    RV_activity = activity_mod[:, 8]      # Activity RV component
    RV_clean = RV_CA - RV_activity        # Clean RV (RV_CA - activity)
    
    # Calculate errors
    eRV_clean = np.sqrt(RV_mod[:, 9]**2 + RV_mod[:, 12]**2)  # Clean RV error
    eRV_activity = np.sqrt(activity_mod[:, 9]**2 + activity_mod[:, 12]**2)  # Activity RV error
    
    # Get instrument name for labeling
    instrument = datasets_labels[dataset]
    
    # Create dataframe for this dataset
    for i in range(len(time_mjd)):
        row_data = {
            'Time [eMJD]': time_mjd[i],
            'RV_C': RV_clean[i],
            'eRV_C': eRV_clean[i],
            'RV_A': RV_activity[i],
            'eRV_A': eRV_activity[i],
            'Instrument': instrument,
            'Standard File Name': dataset
        }
        
        # Add activity indicators if available
        for activity_dataset in activity_list:
            if instrument.lower() in activity_dataset.lower():
                try:
                    activity_ind_mod = np.genfromtxt(
                        dir_base + dir_mods + dir_plot + activity_dataset + '_' + activity_model + '.dat', 
                        skip_header=1
                    )
                    
                    # Find matching time index
                    time_match_idx = np.argmin(np.abs(activity_ind_mod[:, 0] - time_mjd[i]))
                    
                    if np.abs(activity_ind_mod[time_match_idx, 0] - time_mjd[i]) < 0.001:  # Within 1.4 minutes
                        indicator_name = activity_labels[activity_dataset]
                        
                        # Determine units based on indicator type
                        if 'BIS' in indicator_name or 'bis' in indicator_name:
                            unit = '[m/s]'
                        elif 'FWHM' in indicator_name or 'fwhm' in indicator_name:
                            unit = '[m/s]'
                        elif 'Contrast' in indicator_name or 'contrast' in indicator_name:
                            unit = '[%]'
                        elif 'FIESTA' in indicator_name or 'fiesta' in indicator_name:
                            unit = '[normalized]'
                        else:
                            unit = '[U]'  # Unknown units
                        
                        row_data[f'{indicator_name} {unit}'] = activity_ind_mod[time_match_idx, 8]
                        row_data[f'e{indicator_name} {unit}'] = np.sqrt(
                            activity_ind_mod[time_match_idx, 9]**2 + 
                            activity_ind_mod[time_match_idx, 12]**2
                        )
                except:
                    print(f"Warning: Could not load activity indicator {activity_dataset}")
                    continue
        
        all_data.append(row_data)

# Convert to DataFrame
df = pd.DataFrame(all_data)

# Sort by time
df = df.sort_values('Time [eMJD]').reset_index(drop=True)

# Generate file name according to specifications
# Format: <<Data Set>>_<<Group Name>>_<<Method Name>>_results.csv
dataset_name = filename.split('_')[0]  # e.g., 'DS2' from 'DS2_2p_ccfs'

csv_filename = f"{dataset_name}_{group_name}_{method_name}_results.csv"
csv_filepath = os.path.join(results_dir, csv_filename)

# Reorder columns to match requirements
required_columns = ['Time [eMJD]', 'RV_C', 'eRV_C', 'RV_A', 'eRV_A']
optional_columns = ['Standard File Name', 'Instrument']

# Get all indicator columns
indicator_columns = [col for col in df.columns if col not in required_columns + optional_columns]

# Final column order
final_columns = required_columns + optional_columns + sorted(indicator_columns)
df = df[final_columns]

# Round numerical values for cleaner output
numerical_columns = df.select_dtypes(include=[np.number]).columns
df[numerical_columns] = df[numerical_columns].round(6)

# Save to CSV
df.to_csv(csv_filepath, index=False)

print(f"\nCSV file saved to: {csv_filepath}")
print(f"File contains {len(df)} observations")
print(f"Columns: {list(df.columns)}")

# Display first few rows
print("\nFirst 3 rows of the CSV file:")
print(df.head(3).to_string(index=False))

# Summary statistics
print(f"\nSummary Statistics:")
print(f"Time range: {df['Time [eMJD]'].min():.6f} to {df['Time [eMJD]'].max():.6f}")
print(f"RV_C range: {df['RV_C'].min():.3f} to {df['RV_C'].max():.3f} m/s")
print(f"RV_A range: {df['RV_A'].min():.3f} to {df['RV_A'].max():.3f} m/s")
print(f"Mean eRV_C: {df['eRV_C'].mean():.3f} m/s")
print(f"Mean eRV_A: {df['eRV_A'].mean():.3f} m/s")

print("\n" + "="*60)
print("CSV FILE GENERATION COMPLETED!")
print("="*60)
