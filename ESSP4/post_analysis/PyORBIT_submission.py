"""
PyORBIT CSV Export for ESSP Submission
"""

# ============================================================================
# CONFIGURATION SECTION - CUSTOMIZE HERE
# ============================================================================

# Define activity indicator configurations
def get_activity_config(config_type):
    """Return activity indicators based on configuration type"""
    
    configs = {
        '2_activity_indi': ['BISdata', 'FWHMdata'],
        '4_activity_indi': ['BISdata', 'FWHMdata', 'Halphadata', 'CaIIdata'],
        '5_activity_indi': ['BISdata', 'FWHMdata', 'Contrastdata', 'Halphadata', 'CaIIdata'],
        'ccfs': ['FWHMdata', 'Contrastdata'],
        'white_noise': []  # No activity indicators
    }
    
    if config_type not in configs:
        raise ValueError(f"Unknown configuration: {config_type}")
    
    return configs[config_type]

# ============================================================================
# DATASET CONFIGURATIONS - CHOOSE ONE
# ============================================================================

if 1: #DS1
    dir_base = '/work2/lbuc/iara/GitHub/PyORBIT_examples/ESSP4/Results_combined/results_multiple_1022/DS1/DS1_1p/DS1_1p_5_activity_indi/'
    dir_mods = 'DS1_1p_5_activity_indi/'
    dir_plot = 'emcee_plot/model_files/'
    filename = 'DS1_1p_5_activity_indi'
    config_type = '5_activity_indi'
    reference_planet = 'b'

if 0: #DS2
    dir_base = '/work2/lbuc/iara/GitHub/PyORBIT_examples/ESSP4/Results_combined/results_multiple_1022/DS2/DS2_2p/DS2_2p_ccfs/'
    dir_mods = 'DS2_2p_ccfs/'
    dir_plot = 'emcee_plot/model_files/'
    filename = 'DS2_2p_ccfs'
    config_type = 'ccfs'
    reference_planet = 'b'

if 0: #DS3
    dir_base = '/work2/lbuc/iara/GitHub/PyORBIT_examples/ESSP4/Results_combined/results_multiple_1022/DS3/DS3_1p/DS3_1p_5_activity_indi/'
    dir_mods = 'DS3_1p_5_activity_indi/'
    dir_plot = 'emcee_plot/model_files/'
    filename = 'DS3_1p_5_activity_indi'
    config_type = '5_activity_indi'
    reference_planet = 'b'

if 0: #DS4
    dir_base = '/work2/lbuc/iara/GitHub/PyORBIT_examples/ESSP4/Results_combined/results_multiple_1022/DS4/DS4_2p/DS4_2p_4_activity_indi/'
    dir_mods = 'DS4_2p_4_activity_indi/'
    dir_plot = 'emcee_plot/model_files/'
    filename = 'DS4_2p_4_activity_indi'
    config_type = '4_activity_indi'
    reference_planet = 'b'

if 0: #DS5
    dir_base = '/work2/lbuc/iara/GitHub/PyORBIT_examples/ESSP4/Results_combined/results_multiple_1022/DS5/DS5_1p/DS5_1p_2_activity_indi/'
    dir_mods = 'DS5_1p_2_activity_indi/'
    dir_plot = 'emcee_plot/model_files/'
    filename = 'DS5_1p_2_activity_indi'
    config_type = '2_activity_indi'
    reference_planet = 'b'

# Common settings for all datasets
datasets_list = ['RVdata_expres', 'RVdata_harps', 'RVdata_neid']
instruments = ['expres', 'harps', 'neid']
activity_model = 'gp_multidimensional'

# Get activity indicators based on configuration
activity_indicators = get_activity_config(config_type)

print(f"Configuration: {config_type}")
print(f"Activity indicators: {activity_indicators}")

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
results_dir = '/work2/lbuc/iara/GitHub/PyORBIT_examples/ESSP4/submission_csv_files'
group_name = "DTUSpace"
method_name = "PyORBIT_GP"

if not os.path.exists(results_dir):
    os.makedirs(results_dir)

# Collect all data from all instruments
all_times = []
all_rv_data = {}
all_activity_data = {}

# Initialize activity data storage
for indicator in activity_indicators:
    all_activity_data[indicator] = {'times': [], 'values': [], 'errors': []}

# Process each dataset/instrument
for dataset in datasets_list:
    instrument = dataset.split('_')[1]
    print(f"Processing dataset: {dataset}")
    
    # Load RV data - from radial_velocities file
    RV_file = dir_base + dir_mods + dir_plot + dataset + '_radial_velocities_' + reference_planet + '.dat'
    print(f"  Loading RV data from: {RV_file}")
    RV_mod = np.genfromtxt(RV_file, skip_header=1)
    
    # Load activity RV data - from gp_multidimensional file  
    activity_file = dir_base + dir_mods + dir_plot + dataset + '_' + activity_model + '.dat'
    print(f"  Loading activity RV from: {activity_file}")
    activity_mod = np.genfromtxt(activity_file, skip_header=1)
    
    # Calculate values (all times are in eMJD)
    time_emjd = RV_mod[:, 0]  # Time in eMJD
    RV_full_model = RV_mod[:, 7]          # RV full model (column 7)
    RV_offset = RV_mod[:, 5]              # RV offset (column 5)
    RV_CA = RV_full_model - RV_offset     # RV with activity (full model - offset)
    RV_activity = activity_mod[:, 8]      # Activity RV component (column 8)
    RV_clean = RV_CA - RV_activity        # Clean RV (RV_CA - activity)
    
    # Calculate errors
    eRV_clean = np.sqrt(RV_mod[:, 9]**2 + RV_mod[:, 12]**2)  # Clean RV error
    eRV_activity = np.sqrt(activity_mod[:, 9]**2 + activity_mod[:, 12]**2)  # Activity RV error
    
    # Store RV data for this instrument
    for i in range(len(time_emjd)):
        all_times.append(time_emjd[i])
        all_rv_data[len(all_times)-1] = {
            'Time [eMJD]': time_emjd[i],
            'RV_C': RV_clean[i],
            'eRV_C': eRV_clean[i],
            'RV_A': RV_activity[i],
            'eRV_A': eRV_activity[i]
        }
    
    # Load activity indicators for this instrument
    for indicator in activity_indicators:
        try:
            activity_ind_file = dir_base + dir_mods + dir_plot + f"{indicator}_{instrument}_" + activity_model + '.dat'
            print(f"    Loading activity indicator from: {activity_ind_file}")
            activity_ind_mod = np.genfromtxt(activity_ind_file, skip_header=1)
            
            # Store activity indicator data
            for i in range(len(activity_ind_mod)):
                all_activity_data[indicator]['times'].append(activity_ind_mod[i, 0])
                all_activity_data[indicator]['values'].append(activity_ind_mod[i, 8])
                all_activity_data[indicator]['errors'].append(activity_ind_mod[i, 9])
                
        except Exception as e:
            print(f"    Warning: Could not load activity indicator {indicator}_{instrument}: {e}")
            continue

# Create final dataframe
final_data = []

for idx, rv_data in all_rv_data.items():
    row_data = rv_data.copy()
    
    # Add activity indicators by finding closest time match
    for indicator in activity_indicators:
        if all_activity_data[indicator]['times']:  # Check if we have data for this indicator
            times_array = np.array(all_activity_data[indicator]['times'])
            values_array = np.array(all_activity_data[indicator]['values'])
            errors_array = np.array(all_activity_data[indicator]['errors'])
            
            # Find closest time match
            time_match_idx = np.argmin(np.abs(times_array - rv_data['Time [eMJD]']))
            
            if np.abs(times_array[time_match_idx] - rv_data['Time [eMJD]']) < 0.001:  # Within 1.4 minutes
                # Determine units based on indicator type
                if 'BIS' in indicator:
                    unit = '[m/s]'
                elif 'FWHM' in indicator:
                    unit = '[m/s]'
                elif 'Contrast' in indicator:
                    unit = '[normalized]'
                elif 'CaII' in indicator:
                    unit = '[normalized]'
                elif 'Halpha' in indicator:
                    unit = '[normalized]'
                else:
                    unit = '[U]'  # Unknown units
                
                # Add indicator data
                row_data[f'{indicator} {unit}'] = values_array[time_match_idx]
                row_data[f'e{indicator} {unit}'] = errors_array[time_match_idx]
    
    final_data.append(row_data)

# Convert to DataFrame
df = pd.DataFrame(final_data)

# Sort by time
df = df.sort_values('Time [eMJD]').reset_index(drop=True)

# Generate file name according to specifications
dataset_name = filename.split('_')[0]  # e.g., 'DS1' from 'DS1_1p_5_activity_indi'

csv_filename = f"{dataset_name}_{group_name}_{method_name}_results.csv"
csv_filepath = os.path.join(results_dir, csv_filename)

# Reorder columns to match requirements with error columns next to data columns
required_columns = ['Time [eMJD]', 'RV_C', 'eRV_C', 'RV_A', 'eRV_A']

# Get all indicator columns and sort them to put error columns next to data columns
indicator_columns = [col for col in df.columns if col not in required_columns]

# Sort activity indicators to get data/error pairs together
activity_pairs = []
for indicator in sorted(activity_indicators):
    # Find columns for this indicator
    data_cols = [col for col in indicator_columns if col.startswith(f'{indicator} ') and not col.startswith(f'e{indicator} ')]
    error_cols = [col for col in indicator_columns if col.startswith(f'e{indicator} ')]
    
    # Add data column followed by error column
    for data_col in data_cols:
        activity_pairs.append(data_col)
        # Find corresponding error column
        error_col = data_col.replace(f'{indicator} ', f'e{indicator} ')
        if error_col in error_cols:
            activity_pairs.append(error_col)

# Final column order: required columns + activity pairs
final_columns = required_columns + activity_pairs
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
