"""
PyORBIT CSV Export for ESSP Submission - Multiple Configurations
"""

# ============================================================================
# IMPORTS
# ============================================================================
import numpy as np
import pandas as pd
import os
import matplotlib.pyplot as plt
import glob
import re

# ============================================================================
# CONFIGURATION SECTION
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

def parse_log_file(log_file_path):
    """Parse the log file to extract hyperparameters from the median parameter section"""
    
    try:
        with open(log_file_path, 'r') as f:
            content = f.read()
        
        # Find the "sample closest to the median values" section
        median_section_start = content.find("Parameters corresponding to the sample closest to the median values")
        
        if median_section_start == -1:
            print(f"Warning: No median parameters section found in {log_file_path}")
            return {}
        
        # Get the section from that point onwards
        median_content = content[median_section_start:]
        
        # Find the "Statistics on the model parameters" subsection within the median section
        model_params_start = median_content.find("Statistics on the model parameters obtained from the posteriors samples")
        
        if model_params_start == -1:
            print(f"Warning: No model parameters section found in median section of {log_file_path}")
            return {}
        
        # Get just the model parameters section
        model_section = median_content[model_params_start:]
        
        # Find the end of this section (next ====== line)
        end_marker = model_section.find("====================================================================================================", 100)  # Skip the opening marker
        if end_marker != -1:
            model_section = model_section[:end_marker]
        
        # Parse the hyperparameters
        hyperparams = {}
        
        lines = model_section.split('\n')
        current_dataset = None
        current_model = None
        
        for line in lines:
            line = line.strip()
            
            # Skip empty lines and headers
            if not line or '=====' in line or 'Statistics on' in line:
                continue
            
            # Check for dataset/model headers
            if line.startswith('----- dataset:') and 'model:' in line:
                # Extract both dataset and model
                parts = line.split('model:')
                dataset_part = parts[0].replace('----- dataset:', '').strip()
                model_part = parts[1].strip()
                current_dataset = dataset_part
                current_model = model_part
            elif line.startswith('----- dataset:'):
                current_dataset = line.replace('----- dataset:', '').strip()
                current_model = None
            elif line.startswith('----- common model:'):
                current_dataset = line.replace('----- common model:', '').strip()
                current_model = 'common'
            
            # Extract parameter values - look for lines with parameter name and single value
            elif current_dataset and len(line.split()) == 2:
                try:
                    parts = line.split()
                    param_name = parts[0]
                    param_value = float(parts[1])
                    
                    # Create unique key for parameter
                    if current_model == 'common':
                        key = f"{current_dataset}_{param_name}"
                    elif current_model:
                        key = f"{current_dataset}_{current_model}_{param_name}"
                    else:
                        key = f"{current_dataset}_{param_name}"
                    
                    hyperparams[key] = param_value
                    
                except (ValueError, IndexError):
                    continue
        
        # Debug: print found hyperparameters
        print(f"        DEBUG: Found {len(hyperparams)} hyperparameters")
        if hyperparams:
            for key, value in list(hyperparams.items())[:10]:  # Show first 10
                print(f"        DEBUG: {key} = {value}")
        
        return hyperparams
        
    except Exception as e:
        print(f"Error parsing log file {log_file_path}: {e}")
        return {}


# ============================================================================
# MAIN PROCESSING LOOP
# ============================================================================

# Base directories
base_results_dir = '/work2/lbuc/iara/GitHub/PyORBIT_examples/ESSP4/results_multiple'
output_base_dir = '/work2/lbuc/iara/GitHub/PyORBIT_examples/ESSP4/submission_csv_files/results_multiple'

# Common settings
datasets_list = ['RVdata_expres', 'RVdata_harps', 'RVdata_neid']
instruments = ['expres', 'harps', 'neid']
activity_model = 'gp_multidimensional'
reference_planet = 'b'
group_name = "DTUSpace"
method_name = "PyORBIT_GP"

# Create output base directory
if not os.path.exists(output_base_dir):
    os.makedirs(output_base_dir)

print("="*80)
print("PROCESSING ALL CONFIGURATIONS")
print("="*80)

# Find all dataset directories (DS1, DS2, DS3, DS4, DS5, etc.)
dataset_dirs = glob.glob(os.path.join(base_results_dir, 'DS*'))
dataset_dirs.sort()

# Store all hyperparameters for final combined CSV
all_hyperparams = []

for dataset_dir in dataset_dirs:
    dataset_name = os.path.basename(dataset_dir)  # e.g., 'DS1'
    print(f"\nProcessing dataset: {dataset_name}")
    
    # Create output directory for this dataset
    dataset_output_dir = os.path.join(output_base_dir, dataset_name)
    if not os.path.exists(dataset_output_dir):
        os.makedirs(dataset_output_dir)
    
    # Find all configuration directories for this dataset (DS1_0p, DS1_1p, etc.)
    config_dirs = glob.glob(os.path.join(dataset_dir, f'{dataset_name}_*'))
    config_dirs.sort()
    
    for config_dir in config_dirs:
        config_name = os.path.basename(config_dir)  # e.g., 'DS1_1p'
        print(f"  Processing configuration: {config_name}")
        
        # Look for subdirectories inside this configuration that contain the actual analysis
        # The structure is: DS1_1p/DS1_1p_2_activity_indi/DS1_1p_2_activity_indi/emcee_plot/model_files
        subdirs = glob.glob(os.path.join(config_dir, f'{config_name}_*'))
        
        if not subdirs:
            print(f"    Warning: No subdirectories found in {config_dir}")
            continue
        
        # Process each subdirectory (there might be multiple analyses per configuration)
        for subdir in subdirs:
            subdir_name = os.path.basename(subdir)  # e.g., 'DS1_1p_2_activity_indi'
            print(f"    Processing subdirectory: {subdir_name}")
            
            # Extract configuration type from subdirectory name
            if 'white_noise' in subdir_name:
                config_type = 'white_noise'
            elif '5_activity_indi' in subdir_name:
                config_type = '5_activity_indi'
            elif '4_activity_indi' in subdir_name:
                config_type = '4_activity_indi'
            elif '2_activity_indi' in subdir_name:
                config_type = '2_activity_indi'
            elif 'ccfs' in subdir_name:
                config_type = 'ccfs'
            else:
                print(f"      Warning: Unknown configuration type for {subdir_name}")
                continue
            
            # Get activity indicators
            activity_indicators = get_activity_config(config_type)
            
            # Build paths - NOTE THE DOUBLE NESTING!
            # Path: DS1_1p/DS1_1p_2_activity_indi/DS1_1p_2_activity_indi/emcee_plot/model_files
            model_files_dir = os.path.join(subdir, subdir_name, 'emcee_plot', 'model_files')
            
            if not os.path.exists(model_files_dir):
                print(f"      Warning: Model files directory not found: {model_files_dir}")
                continue
            
            # ============================================================================
            # CHECK FOR RADIAL VELOCITIES FILES - SKIP 0p CONFIGURATIONS
            # ============================================================================
            
            # Check if radial_velocities_b.dat files exist for any instrument
            rv_files_exist = False
            for dataset in datasets_list:
                RV_file = os.path.join(model_files_dir, f'{dataset}_radial_velocities_{reference_planet}.dat')
                if os.path.exists(RV_file):
                    rv_files_exist = True
                    break
            
            if not rv_files_exist:
                print(f"      Skipping {subdir_name}: No radial_velocities_b.dat files found (likely 0p configuration)")
                continue
            
            # ============================================================================
            # PROCESS RV DATA
            # ============================================================================
            
            try:
                # Collect all data from all instruments
                all_data = []
                
                # Process each dataset/instrument
                for dataset in datasets_list:
                    instrument = dataset.split('_')[1]
                    
                    # Load RV data - from radial_velocities file
                    RV_file = os.path.join(model_files_dir, f'{dataset}_radial_velocities_{reference_planet}.dat')
                    if not os.path.exists(RV_file):
                        print(f"      Warning: RV file not found: {RV_file}")
                        continue
                    
                    RV_mod = np.genfromtxt(RV_file, skip_header=1)
                    
                    # Load activity RV data - from gp_multidimensional file  
                    activity_file = os.path.join(model_files_dir, f'{dataset}_{activity_model}.dat')
                    if not os.path.exists(activity_file):
                        print(f"      Warning: Activity file not found: {activity_file}")
                        continue
                    
                    activity_mod = np.genfromtxt(activity_file, skip_header=1)
                    
                    # Calculate values (all times are in eMJD)
                    time_emjd = RV_mod[:, 0]  # Time in eMJD
                    RV_full_model = RV_mod[:, 3]          # RV original data (column 4)
                    RV_offset = RV_mod[:, 5]              # RV offset (column 5)
                    RV_CA = RV_full_model - RV_offset     # RV with activity (full model - offset)
                    RV_activity = activity_mod[:, 8]      # Activity RV component (column 8)
                    RV_clean = RV_CA - RV_activity        # Clean RV (RV_CA - activity)
                    
                    # Calculate errors
                    eRV_clean = np.sqrt(RV_mod[:, 9]**2 + RV_mod[:, 12]**2)  # Clean RV error
                    eRV_activity = np.sqrt(activity_mod[:, 9]**2 + activity_mod[:, 12]**2)  # Activity RV error
                    
                    # Load activity indicators for this instrument
                    activity_data = {}
                    for indicator in activity_indicators:
                        try:
                            activity_ind_file = os.path.join(model_files_dir, f"{indicator}_{instrument}_{activity_model}.dat")
                            if os.path.exists(activity_ind_file):
                                activity_ind_mod = np.genfromtxt(activity_ind_file, skip_header=1)
                                
                                # Store activity indicator data (same length and order as RV data)
                                activity_data[indicator] = {
                                    'values': activity_ind_mod[:, 8],  # Activity indicator values
                                    'errors': activity_ind_mod[:, 9]   # Activity indicator errors
                                }
                                    
                        except Exception as e:
                            print(f"        Warning: Could not load activity indicator {indicator}_{instrument}: {e}")
                            continue
                    
                    # Create data rows for this instrument
                    for i in range(len(time_emjd)):
                        row_data = {
                            'Time [eMJD]': time_emjd[i],
                            'RV_C': RV_clean[i],
                            'eRV_C': eRV_clean[i],
                            'RV_A': RV_activity[i],
                            'eRV_A': eRV_activity[i]
                        }
                        
                        # Add activity indicators for this time point
                        for indicator in activity_indicators:
                            if indicator in activity_data:
                                # Determine units based on indicator type
                                if 'BIS' in indicator:
                                    unit = '[m/s]'
                                elif 'FWHM' in indicator:
                                    unit = '[m/s]'
                                elif 'Contrast' in indicator:
                                    unit = '[U]'
                                elif 'CaII' in indicator:
                                    unit = '[U]'
                                elif 'Halpha' in indicator:
                                    unit = '[U]'
                                else:
                                    unit = '[U]'  # Unknown units
                                
                                # Add indicator data (same index as RV data)
                                row_data[f'{indicator} {unit}'] = activity_data[indicator]['values'][i]
                                row_data[f'e{indicator} {unit}'] = activity_data[indicator]['errors'][i]
                        
                        all_data.append(row_data)
                
                if not all_data:
                    print(f"      Warning: No data found for configuration {subdir_name}")
                    continue
                
                # Convert to DataFrame
                df = pd.DataFrame(all_data)
                
                # Sort by time
                df = df.sort_values('Time [eMJD]').reset_index(drop=True)
                
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
                csv_filename = f"{subdir_name}_{group_name}_{method_name}_results.csv"
                csv_filepath = os.path.join(dataset_output_dir, csv_filename)
                df.to_csv(csv_filepath, index=False)
                
                print(f"      CSV saved: {csv_filename} ({len(df)} observations)")
                
            except Exception as e:
                print(f"      Error processing RV data for {subdir_name}: {e}")
                continue
            
            # ============================================================================
            # PROCESS HYPERPARAMETERS FOR THIS CONFIGURATION
            # ============================================================================

            # Find log file - it's in the first level of the subdirectory
            log_file = os.path.join(subdir, f'configuration_file_emcee_run_{subdir_name}.log')

            if os.path.exists(log_file):
                print(f"      Processing hyperparameters from: {os.path.basename(log_file)}")
                hyperparams = parse_log_file(log_file)
                
                if hyperparams:
                    # Create hyperparameters for this specific configuration
                    config_hyperparams = []
                    
                    # Extract common activity parameters (these are the same for all instruments)
                    common_prot = hyperparams.get('activity_Prot', np.nan)
                    common_pdec = hyperparams.get('activity_Pdec', np.nan)
                    common_oamp = hyperparams.get('activity_Oamp', np.nan)
                    
                    # Extract relevant parameters for each instrument/dataset combination
                    for instrument in instruments:
                        # Create hyperparameter row for each activity indicator + instrument combination
                        for indicator in activity_indicators:
                            param_row = {
                                'name': f"{indicator}_{instrument}",
                                'Prot': common_prot,
                                'Pdec': common_pdec,
                                'Oamp': common_oamp
                            }
                            
                            # Extract instrument-specific parameters (rot_amp, con_amp)
                            # Try different possible key formats
                            possible_keys = [
                                f'{indicator}data_{instrument}_gp_multidimensional_rot_amp',
                                f'{indicator}_{instrument}_gp_multidimensional_rot_amp'
                            ]
                            
                            param_row['rot_amp'] = np.nan
                            param_row['con_amp'] = np.nan
                            
                            for key_format in possible_keys:
                                if key_format in hyperparams:
                                    param_row['rot_amp'] = hyperparams[key_format]
                                    break
                            
                            for key_format in possible_keys:
                                con_key = key_format.replace('rot_amp', 'con_amp')
                                if con_key in hyperparams:
                                    param_row['con_amp'] = hyperparams[con_key]
                                    break
                            
                            config_hyperparams.append(param_row)
                            
                            # Also add to global list for combined CSV
                            global_param_row = param_row.copy()
                            global_param_row['configuration'] = subdir_name
                            global_param_row['dataset'] = dataset_name
                            all_hyperparams.append(global_param_row)
                    
                    # Debug: show what we're about to save
                    print(f"        DEBUG: Creating {len(config_hyperparams)} hyperparameter rows")
                    print(f"        DEBUG: Common activity params - Prot: {common_prot}, Pdec: {common_pdec}, Oamp: {common_oamp}")
                    
                    # Save individual hyperparameters CSV for this configuration
                    if config_hyperparams:
                        config_hyperparams_df = pd.DataFrame(config_hyperparams)
                        
                        # Round numerical values
                        numerical_cols = ['Prot', 'Pdec', 'Oamp', 'rot_amp', 'con_amp']
                        for col in numerical_cols:
                            if col in config_hyperparams_df.columns:
                                config_hyperparams_df[col] = config_hyperparams_df[col].round(6)
                        
                        # Save individual configuration hyperparameters CSV
                        hyperparams_filename = f"{subdir_name}_{group_name}_{method_name}_hyperparameters.csv"
                        hyperparams_filepath = os.path.join(dataset_output_dir, hyperparams_filename)
                        config_hyperparams_df.to_csv(hyperparams_filepath, index=False)
                        
                        print(f"      Hyperparameters CSV saved: {hyperparams_filename}")
                    else:
                        print(f"      DEBUG: No hyperparameter rows created for {subdir_name}")
                else:
                    print(f"      DEBUG: No hyperparameters parsed from {log_file}")
            else:
                print(f"      Warning: Log file not found: {log_file}")

# ============================================================================
# SAVE COMBINED HYPERPARAMETERS CSV
# ============================================================================

if all_hyperparams:
    hyperparams_df = pd.DataFrame(all_hyperparams)
    
    # Round numerical values
    numerical_cols = ['Prot', 'Pdec', 'Oamp', 'rot_amp', 'con_amp']
    for col in numerical_cols:
        if col in hyperparams_df.columns:
            hyperparams_df[col] = hyperparams_df[col].round(6)
    
    # Save combined hyperparameters CSV
    combined_hyperparams_csv = os.path.join(output_base_dir, f"{group_name}_{method_name}_all_hyperparameters.csv")
    hyperparams_df.to_csv(combined_hyperparams_csv, index=False)
    
    print(f"\nCombined hyperparameters CSV saved: {combined_hyperparams_csv}")
    print(f"Contains {len(hyperparams_df)} parameter sets")
    
    # Display first few rows
    print("\nFirst 5 rows of combined hyperparameters:")
    print(hyperparams_df.head().to_string(index=False))

print("\n" + "="*80)
print("ALL CONFIGURATIONS PROCESSED!")
print("="*80)
print(f"Results saved in: {output_base_dir}")
