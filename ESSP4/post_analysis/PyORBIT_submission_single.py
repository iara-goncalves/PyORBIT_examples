"""
PyORBIT CSV Export for ESSP Submission - Single Instrument Configurations
"""

# ============================================================================
# IMPORTS
# ============================================================================
import numpy as np
import pandas as pd
import os
import glob

# ============================================================================
# CONFIGURATION SECTION
# ============================================================================

def get_activity_config(config_type):
    """Return activity indicators based on configuration type"""
    
    configs = {
        '2_activity_indi': ['BISdata', 'FWHMdata'],
        '4_activity_indi': ['BISdata', 'FWHMdata', 'Halphadata', 'CaIIdata'],
        '5_activity_indi': ['BISdata', 'FWHMdata', 'Contrastdata', 'Halphadata', 'CaIIdata'],
        'ccfs': ['FWHMdata', 'Contrastdata'],
        'white_noise': []
    }
    
    if config_type not in configs:
        raise ValueError(f"Unknown configuration: {config_type}")
    
    return configs[config_type]

def parse_log_file(log_file_path):
    """Parse the log file to extract hyperparameters from the LAST median parameter section"""
    
    try:
        with open(log_file_path, 'r') as f:
            content = f.read()
        
        model_params_marker = "Statistics on the model parameters obtained from the posteriors samples"
        
        positions = []
        start = 0
        while True:
            pos = content.find(model_params_marker, start)
            if pos == -1:
                break
            positions.append(pos)
            start = pos + 1
        
        if not positions:
            return {}
        
        last_position = positions[-1]
        model_section = content[last_position:]
        
        end_markers = [
            "Statistics on the derived parameters",
            "====================================================================================================\n\n\n",
            "Inclination fixed to 90 deg!"
        ]
        
        end_pos = len(model_section)
        for marker in end_markers:
            pos = model_section.find(marker, 200)
            if pos != -1 and pos < end_pos:
                end_pos = pos
        
        model_section = model_section[:end_pos]
        
        hyperparams = {}
        lines = model_section.split('\n')
        current_dataset = None
        current_model = None
        
        for line in lines:
            line_stripped = line.strip()
            
            if not line_stripped or '=====' in line_stripped or 'Statistics on' in line_stripped:
                continue
            
            if line_stripped.startswith('----- dataset:') and 'model:' in line_stripped:
                parts = line_stripped.split('-----')
                for part in parts:
                    if 'dataset:' in part:
                        current_dataset = part.replace('dataset:', '').strip()
                    elif 'model:' in part:
                        current_model = part.replace('model:', '').strip()
                        
            elif line_stripped.startswith('----- dataset:'):
                current_dataset = line_stripped.replace('----- dataset:', '').strip()
                current_model = None
                
            elif line_stripped.startswith('----- common model:'):
                current_dataset = line_stripped.replace('----- common model:', '').strip()
                current_model = 'common'
            
            elif current_dataset:
                parts = line_stripped.split()
                if len(parts) == 2:
                    try:
                        param_name = parts[0]
                        param_value = float(parts[1])
                        
                        if current_model == 'common':
                            key = f"{current_dataset}_{param_name}"
                        elif current_model:
                            key = f"{current_dataset}_{current_model}_{param_name}"
                        else:
                            key = f"{current_dataset}_{param_name}"
                        
                        hyperparams[key] = param_value
                        
                    except (ValueError, IndexError):
                        continue
        
        return hyperparams
        
    except Exception as e:
        print(f"        Error parsing log file: {e}")
        return {}

# ============================================================================
# MAIN PROCESSING LOOP
# ============================================================================

base_results_dir = '/work2/lbuc/iara/GitHub/PyORBIT_examples/ESSP4/results_single'
output_base_dir = '/work2/lbuc/iara/GitHub/PyORBIT_examples/ESSP4/submission_csv_files/results_single'

activity_model = 'gp_multidimensional'
reference_planet = 'b'
group_name = "DTUSpace"
method_name = "PyORBIT_GP"

if not os.path.exists(output_base_dir):
    os.makedirs(output_base_dir)

print("="*80)
print("PROCESSING ALL SINGLE INSTRUMENT CONFIGURATIONS")
print("="*80)

dataset_dirs = glob.glob(os.path.join(base_results_dir, 'DS*'))
dataset_dirs.sort()

for dataset_dir in dataset_dirs:
    dataset_name = os.path.basename(dataset_dir)
    print(f"\nProcessing dataset: {dataset_name}")
    
    dataset_output_dir = os.path.join(output_base_dir, dataset_name)
    if not os.path.exists(dataset_output_dir):
        os.makedirs(dataset_output_dir)
    
    config_dirs = glob.glob(os.path.join(dataset_dir, f'{dataset_name}_*'))
    config_dirs.sort()
    
    for config_dir in config_dirs:
        config_name = os.path.basename(config_dir)
        print(f"  Processing configuration: {config_name}")
        
        subdirs = glob.glob(os.path.join(config_dir, f'{config_name}_*'))
        
        if not subdirs:
            continue
        
        for subdir in subdirs:
            subdir_name = os.path.basename(subdir)
            print(f"    Processing: {subdir_name}")
            
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
                continue
            
            activity_indicators = get_activity_config(config_type)
            
            model_files_dir = os.path.join(subdir, subdir_name, 'emcee_plot', 'model_files')
            
            if not os.path.exists(model_files_dir):
                continue
            
            is_0p_config = '0p' in config_name
            
            # ============================================================================
            # PROCESS RV DATA
            # ============================================================================
            
            try:
                all_data = []
                
                # For single instrument, use the generic names without instrument suffix
                if is_0p_config:
                    # Only activity data for 0p configurations
                    activity_file = os.path.join(model_files_dir, f'RVdata_{activity_model}.dat')
                    if not os.path.exists(activity_file):
                        continue
                    
                    activity_mod = np.genfromtxt(activity_file, skip_header=1)
                    
                    time_emjd = activity_mod[:, 0]
                    RV_activity = activity_mod[:, 6]
                    eRV_activity = np.sqrt(activity_mod[:, 9]**2 + activity_mod[:, 12]**2)
                    
                    # Load activity indicators
                    activity_data = {}
                    for indicator in activity_indicators:
                        try:
                            activity_ind_file = os.path.join(model_files_dir, f"{indicator}_{activity_model}.dat")
                            if os.path.exists(activity_ind_file):
                                activity_ind_mod = np.genfromtxt(activity_ind_file, skip_header=1)
                                
                                activity_data[indicator] = {
                                    'values': activity_ind_mod[:, 8],
                                    'errors': activity_ind_mod[:, 9]
                                }
                        except:
                            continue
                    
                    # Create rows with NaN for RV_C and eRV_C
                    for i in range(len(time_emjd)):
                        row_data = {
                            'Time [eMJD]': time_emjd[i],
                            'RV_C': np.nan,
                            'eRV_C': np.nan,
                            'RV_A': RV_activity[i],
                            'eRV_A': eRV_activity[i]
                        }
                        
                        for indicator in activity_indicators:
                            if indicator in activity_data:
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
                                    unit = '[U]'
                                
                                row_data[f'{indicator} {unit}'] = activity_data[indicator]['values'][i]
                                row_data[f'e{indicator} {unit}'] = activity_data[indicator]['errors'][i]
                        
                        all_data.append(row_data)
                
                else:
                    # For non-0p configurations
                    RV_file = os.path.join(model_files_dir, f'RVdata_radial_velocities_{reference_planet}.dat')
                    if not os.path.exists(RV_file):
                        continue
                    
                    RV_mod = np.genfromtxt(RV_file, skip_header=1)
                    
                    activity_file = os.path.join(model_files_dir, f'RVdata_{activity_model}.dat')
                    if not os.path.exists(activity_file):
                        continue
                    
                    activity_mod = np.genfromtxt(activity_file, skip_header=1)
                    
                    time_emjd = RV_mod[:, 0]
                    RV_full_model = RV_mod[:, 3]
                    RV_offset = RV_mod[:, 5]
                    RV_CA = RV_full_model - RV_offset
                    RV_activity = activity_mod[:, 6]
                    RV_clean = RV_CA - RV_activity
                    
                    eRV_clean = np.sqrt(RV_mod[:, 9]**2 + RV_mod[:, 12]**2)
                    eRV_activity = np.sqrt(activity_mod[:, 9]**2 + activity_mod[:, 12]**2)
                    
                    activity_data = {}
                    for indicator in activity_indicators:
                        try:
                            activity_ind_file = os.path.join(model_files_dir, f"{indicator}_{activity_model}.dat")
                            if os.path.exists(activity_ind_file):
                                activity_ind_mod = np.genfromtxt(activity_ind_file, skip_header=1)
                                
                                activity_data[indicator] = {
                                    'values': activity_ind_mod[:, 8],
                                    'errors': activity_ind_mod[:, 9]
                                }
                        except:
                            continue
                    
                    for i in range(len(time_emjd)):
                        row_data = {
                            'Time [eMJD]': time_emjd[i],
                            'RV_C': RV_clean[i],
                            'eRV_C': eRV_clean[i],
                            'RV_A': RV_activity[i],
                            'eRV_A': eRV_activity[i]
                        }
                        
                        for indicator in activity_indicators:
                            if indicator in activity_data:
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
                                    unit = '[U]'
                                
                                row_data[f'{indicator} {unit}'] = activity_data[indicator]['values'][i]
                                row_data[f'e{indicator} {unit}'] = activity_data[indicator]['errors'][i]
                        
                        all_data.append(row_data)
                
                if not all_data:
                    continue
                
                df = pd.DataFrame(all_data)
                df = df.sort_values('Time [eMJD]').reset_index(drop=True)
                
                required_columns = ['Time [eMJD]', 'RV_C', 'eRV_C', 'RV_A', 'eRV_A']
                indicator_columns = [col for col in df.columns if col not in required_columns]
                
                activity_pairs = []
                for indicator in sorted(activity_indicators):
                    data_cols = [col for col in indicator_columns if col.startswith(f'{indicator} ') and not col.startswith(f'e{indicator} ')]
                    error_cols = [col for col in indicator_columns if col.startswith(f'e{indicator} ')]
                    
                    for data_col in data_cols:
                        activity_pairs.append(data_col)
                        error_col = data_col.replace(f'{indicator} ', f'e{indicator} ')
                        if error_col in error_cols:
                            activity_pairs.append(error_col)
                
                final_columns = required_columns + activity_pairs
                df = df[final_columns]
                
                numerical_columns = df.select_dtypes(include=[np.number]).columns
                df[numerical_columns] = df[numerical_columns].round(6)
                
                csv_filename = f"{subdir_name}_{group_name}_{method_name}_results.csv"
                csv_filepath = os.path.join(dataset_output_dir, csv_filename)
                df.to_csv(csv_filepath, index=False)
                
                print(f"      ✓ Results CSV saved ({len(df)} observations)")
                
            except Exception as e:
                print(f"      ✗ Error processing RV data: {e}")
                continue
            
            # ============================================================================
            # PROCESS HYPERPARAMETERS
            # ============================================================================

            log_file = os.path.join(subdir, f'configuration_file_emcee_run_{subdir_name}_single.log')

            if os.path.exists(log_file):
                hyperparams = parse_log_file(log_file)
                
                if hyperparams:
                    config_hyperparams = []
                    
                    common_prot = hyperparams.get('activity_Prot', np.nan)
                    common_pdec = hyperparams.get('activity_Pdec', np.nan)
                    common_oamp = hyperparams.get('activity_Oamp', np.nan)
                    
                    common_row = {
                        'name': 'common_model_activity',
                        'Prot': common_prot,
                        'Pdec': common_pdec,
                        'Oamp': common_oamp,
                        'rot_amp': np.nan,
                        'con_amp': np.nan
                    }
                    config_hyperparams.append(common_row)
                    
                    # For single instrument, extract parameters without instrument suffix
                    for indicator in ['RVdata'] + activity_indicators:
                        param_row = {
                            'name': indicator,
                            'Prot': common_prot,
                            'Pdec': common_pdec,
                            'Oamp': common_oamp
                        }
                        
                        rot_amp_key = f"{indicator}_gp_multidimensional_rot_amp"
                        con_amp_key = f"{indicator}_gp_multidimensional_con_amp"
                        
                        param_row['rot_amp'] = hyperparams.get(rot_amp_key, np.nan)
                        param_row['con_amp'] = hyperparams.get(con_amp_key, np.nan)
                        
                        config_hyperparams.append(param_row)
                    
                    if config_hyperparams:
                        config_hyperparams_df = pd.DataFrame(config_hyperparams)
                        
                        numerical_cols = ['Prot', 'Pdec', 'Oamp', 'rot_amp', 'con_amp']
                        for col in numerical_cols:
                            if col in config_hyperparams_df.columns:
                                config_hyperparams_df[col] = config_hyperparams_df[col].round(6)
                        
                        hyperparams_filename = f"{subdir_name}_{group_name}_{method_name}_hyperparameters.csv"
                        hyperparams_filepath = os.path.join(dataset_output_dir, hyperparams_filename)
                        config_hyperparams_df.to_csv(hyperparams_filepath, index=False)
                        
                        print(f"      ✓ Hyperparameters CSV saved")

print("\n" + "="*80)
print("ALL SINGLE INSTRUMENT CONFIGURATIONS PROCESSED!")
print("="*80)
print(f"Results saved in: {output_base_dir}")