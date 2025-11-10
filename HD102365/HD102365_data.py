# HD102365_data.py

from glob import glob
import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.pyplot import errorbar

def load_dat_file(dat_file, star_name="HD102365"):
    """Load the .dat file and extract data for the specified star.
    
    Format understanding based on actual data:
    - UCLES: has EWHa only (S_HK columns empty) → 8 columns after split
    - HIRES-Post, HARPS-Pre, PFS-Pre, PFS-Post: have S_HK only → 8 columns after split
    - Other instruments: RV only → 6 columns after split
    
    The challenge: both "S_HK only" and "EWHa only" result in 8 columns!
    Solution: Use instrument name to determine which one it is.
    """
    
    # Define which instruments have which activity indicators
    EWHA_INSTRUMENTS = {'UCLES'}
    SHK_INSTRUMENTS = {'HIRES-Post', 'HARPS-Pre', 'PFS-Pre', 'PFS-Post', 'HARPS-Post'}
    
    data = []
    with open(dat_file, 'r') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
                
            parts = line.split()
            
            # Check if this line is for our star
            if len(parts) > 0 and parts[0] == star_name:
                try:
                    star = parts[0]
                    bjd = float(parts[1])
                    rv = float(parts[2])
                    e_rv = float(parts[3])
                    inst = parts[4]
                    
                    # Initialize optional values
                    shk = np.nan
                    e_shk = np.nan
                    ewha = np.nan
                    e_ewha = np.nan
                    run_id = ''
                    
                    # Parse based on number of columns after .split()
                    if len(parts) == 6:
                        # Only RV data: star bjd rv e_rv instrument run_id
                        run_id = parts[5]
                        
                    elif len(parts) == 8:
                        # Could be either S_HK only OR EWHa only
                        # Use instrument name to determine which
                        if inst in EWHA_INSTRUMENTS:
                            # EWHa only (S_HK columns were empty)
                            ewha = float(parts[5])
                            e_ewha = float(parts[6])
                            run_id = parts[7]
                        elif inst in SHK_INSTRUMENTS:
                            # S_HK only (EWHa columns were empty)
                            shk = float(parts[5])
                            e_shk = float(parts[6])
                            run_id = parts[7]
                        else:
                            # Unknown instrument with 8 columns - try to guess
                            print(f"Warning: Unknown instrument '{inst}' with 8 columns at line {line_num}")
                            run_id = parts[7]
                        
                    elif len(parts) == 10:
                        # Both S_HK and EWHa present
                        shk = float(parts[5])
                        e_shk = float(parts[6])
                        ewha = float(parts[7])
                        e_ewha = float(parts[8])
                        run_id = parts[9]
                    
                    else:
                        print(f"Warning: Unexpected format at line {line_num} ({len(parts)} columns)")
                        print(f"  Content: {line[:100]}")
                        continue
                    
                    data.append({
                        'Star': star,
                        'BJD': bjd,
                        'RV': rv,
                        'e_RV': e_rv,
                        'Instrument': inst,
                        'SHK': shk,
                        'e_SHK': e_shk,
                        'EWHa': ewha,
                        'e_EWHa': e_ewha,
                        'File': run_id
                    })
                    
                except (ValueError, IndexError) as e:
                    print(f"Warning: Could not parse line {line_num}: {e}")
                    print(f"  Content: {line[:100]}")
                    continue
    
    df = pd.DataFrame(data)
    print(f"\nLoaded {len(df)} observations for {star_name}")
    if len(df) > 0:
        print(f"Date range: {df['BJD'].min():.2f} to {df['BJD'].max():.2f}")
        print(f"Instruments: {sorted(df['Instrument'].unique())}")
        print(f"\nActivity indicators by instrument:")
        for inst in sorted(df['Instrument'].unique()):
            inst_data = df[df['Instrument'] == inst]
            n_shk = inst_data['SHK'].notna().sum()
            n_ewha = inst_data['EWHa'].notna().sum()
            print(f"  {inst}: {len(inst_data)} obs, S_HK: {n_shk}, EWHa: {n_ewha}")
    return df

def load_rdb_files(rdb_dir, file_pattern="HD102365_ESPRESSO*.rdb", exclude_files=None):
    """Load all .rdb files and concatenate them with proper flags.
    
    Parameters:
    -----------
    rdb_dir : str
        Directory containing the RDB files
    file_pattern : str
        Glob pattern for RDB files
    exclude_files : list of str, optional
        List of filenames to exclude (e.g., ['HD102365_ESPRESSO19_2.rdb'])
    """
    
    if exclude_files is None:
        exclude_files = []
    
    rdb_files = sorted(glob(os.path.join(rdb_dir, file_pattern)))
    
    # Filter out excluded files
    rdb_files = [f for f in rdb_files if os.path.basename(f) not in exclude_files]
    
    print(f"Found {len(rdb_files)} .rdb files (after exclusions)")
    if exclude_files:
        print(f"Excluded files: {', '.join(exclude_files)}")
    
    df_list = []
    
    for i, rdb_file in enumerate(rdb_files):
        print(f"Loading {os.path.basename(rdb_file)}...")
        
        # Read RDB file (skip first 2 lines: header and dashes)
        df_tmp = pd.read_csv(rdb_file, sep='\t', skiprows=2, 
                            names=['rjd', 'vrad', 'svrad', 'fwhm', 'sig_fwhm', 
                                   'bis_span', 'sig_bis_span', 'contrast', 'sig_contrast',
                                   's_mw', 'sig_s', 'ha', 'sig_ha', 'na', 'sig_na',
                                   'ca', 'sig_ca', 'rhk', 'sig_rhk', 'berv', 'weight'])
        
        # Convert RJD to BJD
        # RJD = MJD - 50000, and BJD ≈ MJD + 2400000.5
        # So BJD = RJD + 2450000
        df_tmp['bjd'] = df_tmp['rjd'] + 2450000.0
        
        print(f"  Converted RJD to BJD: {df_tmp['rjd'].min():.2f} → {df_tmp['bjd'].min():.2f}")
        
        # Add dataset identifier
        df_tmp['Dataset'] = os.path.basename(rdb_file).replace('.rdb', '')
        df_tmp['offset_flag'] = i  # Different offset for each file
        df_tmp['jitter_flag'] = i  # Different jitter for each file
        
        df_list.append(df_tmp)
    
    # Concatenate all dataframes
    df_all = pd.concat(df_list, ignore_index=True)
    print(f"Total ESPRESSO observations: {len(df_all)}")
    print(f"BJD range: {df_all['bjd'].min():.2f} to {df_all['bjd'].max():.2f}")
    
    return df_all

def detect_outliers_dat(df, sigma_threshold=4):
    """Detect outliers in .dat file data per instrument."""
    
    df['is_outlier'] = False
    
    for inst in df['Instrument'].unique():
        idx = df[df['Instrument'] == inst].index
        
        # Check RV outliers
        rv_data = df.loc[idx, 'RV'].dropna()
        if len(rv_data) > 0:
            median = rv_data.median()
            std = rv_data.std(ddof=1)
            if std > 0 and not np.isnan(std):
                outliers = np.abs(df.loc[idx, 'RV'] - median) > (sigma_threshold * std)
                df.loc[idx[outliers], 'is_outlier'] = True
    
    n_out = df['is_outlier'].sum()
    print(f"Outliers flagged in .dat data: {n_out} ({n_out/len(df)*100:.2f}%)")
    
    return df

def detect_outliers_rdb(df, sigma_threshold=4):
    """Detect outliers in .rdb file data per dataset."""
    
    df['is_outlier'] = False
    cols_to_check = ['vrad', 'bis_span', 'fwhm']
    
    for dataset in df['Dataset'].unique():
        idx = df[df['Dataset'] == dataset].index
        out_mask = np.zeros(len(idx), dtype=bool)
        
        for col in cols_to_check:
            data = df.loc[idx, col].dropna()
            if len(data) > 0:
                median = data.median()
                std = data.std(ddof=1)
                if std > 0 and not np.isnan(std):
                    col_outliers = np.abs(df.loc[idx, col] - median) > (sigma_threshold * std)
                    out_mask |= col_outliers.fillna(False).values
        
        df.loc[idx, 'is_outlier'] = out_mask
    
    n_out = df['is_outlier'].sum()
    print(f"Outliers flagged in .rdb data: {n_out} ({n_out/len(df)*100:.2f}%)")
    
    return df

def save_dat_files_per_instrument(df, outdir, exclude_outliers=True):
    """Save .dat file data split by instrument."""
    
    os.makedirs(outdir, exist_ok=True)
    
    if exclude_outliers:
        df_export = df[~df.is_outlier].copy()
        print("Writing .dat files using INLIERS only.")
    else:
        df_export = df.copy()
        print("Writing .dat files using ALL points.")
    
    # Get all unique instruments
    instruments = sorted(df_export['Instrument'].unique())
    
    for inst in instruments:
        inst_data = df_export[df_export['Instrument'] == inst].copy()
        
        if len(inst_data) == 0:
            continue
        
        print(f"\n{inst}: {len(inst_data)} observations")
        
        # Prepare data - ALL FLAGS SET TO 0 for single instrument files
        time = inst_data['BJD'].values
        rv = inst_data['RV'].values
        rv_err = inst_data['e_RV'].values
        jitter_flag = np.zeros(len(inst_data), dtype=int)
        offset_flag = np.zeros(len(inst_data), dtype=int)  # SET TO 0
        subset_flag = -1 * np.ones(len(inst_data), dtype=int)
        
        # Save RV data
        rv_data = np.column_stack([time, rv, rv_err, jitter_flag, offset_flag, subset_flag])
        rv_outfile = os.path.join(outdir, f"HD102365_{inst}_RV.dat")
        np.savetxt(rv_outfile, rv_data, fmt=["%.6f", "%.6f", "%.6f", "%d", "%d", "%d"])
        print(f"  ✓ RV: {rv_outfile}")
        
        # Save SHK data if available
        if inst_data['SHK'].notna().any():
            shk_data_filtered = inst_data[inst_data['SHK'].notna()].copy()
            n_shk = len(shk_data_filtered)
            
            time_shk = shk_data_filtered['BJD'].values
            shk = shk_data_filtered['SHK'].values
            e_shk = shk_data_filtered['e_SHK'].values
            
            # Use a default error if e_SHK is NaN
            e_shk = np.where(np.isnan(e_shk), 0.01, e_shk)
            
            jitter_shk = np.zeros(n_shk, dtype=int)
            offset_shk = np.zeros(n_shk, dtype=int)  # SET TO 0
            subset_shk = -1 * np.ones(n_shk, dtype=int)
            
            shk_data = np.column_stack([time_shk, shk, e_shk, jitter_shk, offset_shk, subset_shk])
            shk_outfile = os.path.join(outdir, f"HD102365_{inst}_SHK.dat")
            np.savetxt(shk_outfile, shk_data, fmt=["%.6f", "%.6f", "%.6f", "%d", "%d", "%d"])
            print(f"  ✓ SHK: {shk_outfile} ({n_shk} points)")
        
        # Save EWHa data if available
        if inst_data['EWHa'].notna().any():
            ewha_data_filtered = inst_data[inst_data['EWHa'].notna()].copy()
            n_ewha = len(ewha_data_filtered)
            
            time_ewha = ewha_data_filtered['BJD'].values
            ewha = ewha_data_filtered['EWHa'].values
            e_ewha = ewha_data_filtered['e_EWHa'].values
            
            # Use a default error if e_EWHa is NaN
            e_ewha = np.where(np.isnan(e_ewha), 0.001, e_ewha)
            
            jitter_ewha = np.zeros(n_ewha, dtype=int)
            offset_ewha = np.zeros(n_ewha, dtype=int)  # SET TO 0
            subset_ewha = -1 * np.ones(n_ewha, dtype=int)
            
            ewha_data = np.column_stack([time_ewha, ewha, e_ewha, jitter_ewha, offset_ewha, subset_ewha])
            ewha_outfile = os.path.join(outdir, f"HD102365_{inst}_EWHa.dat")
            np.savetxt(ewha_outfile, ewha_data, fmt=["%.6f", "%.6f", "%.6f", "%d", "%d", "%d"])
            print(f"  ✓ EWHa: {ewha_outfile} ({n_ewha} points)")

def save_rdb_concatenated(df, outdir, exclude_outliers=True):
    """Save concatenated .rdb data for PyORBIT (using BJD timestamps)."""
    
    os.makedirs(outdir, exist_ok=True)
    
    if exclude_outliers:
        df_export = df[~df.is_outlier].copy()
        print("Writing ESPRESSO files using INLIERS only.")
    else:
        df_export = df.copy()
        print("Writing ESPRESSO files using ALL points.")
    
    # Prepare data - USE BJD INSTEAD OF RJD
    time = df_export['bjd'].values  # Changed from 'rjd' to 'bjd'
    rv = df_export['vrad'].values
    rv_err = df_export['svrad'].values
    jitter_flag = df_export['jitter_flag'].values
    offset_flag = df_export['offset_flag'].values
    subset_flag = -1 * np.ones(len(df_export), dtype=int)
    
    # Save RV data
    rv_data = np.column_stack([time, rv, rv_err, jitter_flag, offset_flag, subset_flag])
    rv_outfile = os.path.join(outdir, "HD102365_ESPRESSO_RV.dat")
    np.savetxt(rv_outfile, rv_data, fmt=["%.6f", "%.6f", "%.6f", "%d", "%d", "%d"])
    print(f"Saved: {rv_outfile} ({len(rv_data)} points)")
    print(f"  BJD range: {time.min():.2f} to {time.max():.2f}")
    
    # Save BIS data
    bis = df_export['bis_span'].values
    bis_err = df_export['sig_bis_span'].values
    bis_data = np.column_stack([time, bis, bis_err, jitter_flag, offset_flag, subset_flag])
    bis_outfile = os.path.join(outdir, "HD102365_ESPRESSO_BIS.dat")
    np.savetxt(bis_outfile, bis_data, fmt=["%.6f", "%.6f", "%.6f", "%d", "%d", "%d"])
    print(f"Saved: {bis_outfile}")
    
    # Save FWHM data
    fwhm = df_export['fwhm'].values
    fwhm_err = df_export['sig_fwhm'].values
    fwhm_data = np.column_stack([time, fwhm, fwhm_err, jitter_flag, offset_flag, subset_flag])
    fwhm_outfile = os.path.join(outdir, "HD102365_ESPRESSO_FWHM.dat")
    np.savetxt(fwhm_outfile, fwhm_data, fmt=["%.6f", "%.6f", "%.6f", "%d", "%d", "%d"])
    print(f"Saved: {fwhm_outfile}")

def plot_all_instruments_timeseries(df_dat, fig_dir):
    """Plot time series of RV data for all instruments."""
    
    fig, ax = plt.subplots(figsize=(14, 6))
    
    # Get unique instruments
    instruments = sorted(df_dat['Instrument'].unique())
    
    # Define colors for different instruments
    colors = plt.cm.tab10(np.linspace(0, 1, len(instruments)))
    
    # Plot each instrument
    for idx, inst in enumerate(instruments):
        inst_data = df_dat[df_dat['Instrument'] == inst].copy()
        inst_data = inst_data.sort_values('BJD')
        
        # Split into inliers and outliers
        inliers = inst_data[~inst_data['is_outlier']]
        outliers = inst_data[inst_data['is_outlier']]
        
        # Plot inliers
        if not inliers.empty:
            ax.errorbar(inliers['BJD'], inliers['RV'], 
                       yerr=inliers['e_RV'],
                       fmt='o', markersize=4, capsize=2, 
                       label=inst, color=colors[idx], alpha=0.7)
        
        # Plot outliers (in black with red edge)
        if not outliers.empty:
            ax.errorbar(outliers['BJD'], outliers['RV'], 
                       yerr=outliers['e_RV'],
                       fmt='o', markersize=6, capsize=2, 
                       color='black', markeredgecolor='red', 
                       markeredgewidth=1.5, alpha=0.7)
    
    ax.set_xlabel('BJD', fontsize=12)
    ax.set_ylabel('RV (m/s)', fontsize=12)
    ax.set_title('Radial Velocity Time Series - All Instruments', fontsize=14, fontweight='bold')
    ax.legend(loc='best', fontsize=10, ncol=2)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    fig_path = os.path.join(fig_dir, "HD102365_all_instruments_timeseries.png")
    plt.savefig(fig_path, dpi=150, bbox_inches='tight')
    print(f"Saved figure: {fig_path}")
    plt.close()

def plot_instrument_timeseries(inst, inst_df, fig_dir):
    """Plot time series for a single instrument."""
    
    fig, axes = plt.subplots(3, 1, figsize=(12, 10), sharex=True)
    
    plot_info = [
        ('RV', 'e_RV', 'RV [m/s]'),
        ('SHK', 'e_SHK', 'S_HK Index'),
        ('EWHa', 'e_EWHa', 'EW H-alpha [0.1 Å]')
    ]
    
    for ax, (col, err_col, ylabel) in zip(axes, plot_info):
        if col not in inst_df.columns or inst_df[col].isna().all():
            ax.text(0.5, 0.5, f"No {col} data", 
                   ha='center', va='center', transform=ax.transAxes)
            ax.set_ylabel(ylabel)
            continue
        
        # Filter out NaN values
        valid_data = inst_df[inst_df[col].notna()].copy()
        
        if len(valid_data) == 0:
            ax.text(0.5, 0.5, f"No valid {col} data", 
                   ha='center', va='center', transform=ax.transAxes)
            ax.set_ylabel(ylabel)
            continue
        
        # Split into inliers and outliers
        inliers = valid_data[~valid_data['is_outlier']]
        outliers = valid_data[valid_data['is_outlier']]
        
        # Get errors
        if err_col in valid_data.columns:
            yerr_in = inliers[err_col].values
            yerr_out = outliers[err_col].values if len(outliers) > 0 else None
        else:
            yerr_in = None
            yerr_out = None
        
        # Plot inliers
        if not inliers.empty:
            ax.errorbar(inliers['BJD'], inliers[col], yerr=yerr_in,
                       fmt="o", color="skyblue", label="Data", 
                       alpha=0.7, markersize=5)
        
        # Plot outliers
        if not outliers.empty:
            ax.errorbar(outliers['BJD'], outliers[col], yerr=yerr_out,
                       fmt="o", color="black", alpha=0.7, markersize=7,
                       markeredgecolor="red", markeredgewidth=1.5,
                       label="Outliers")
        
        ax.set_ylabel(ylabel)
        ax.grid(True, alpha=0.3)
        ax.legend(loc='best')
    
    axes[-1].set_xlabel("BJD")
    fig.suptitle(f"HD102365 - {inst}", fontsize=16)
    plt.tight_layout(rect=[0, 0, 1, 0.97])
    
    fig_path = os.path.join(fig_dir, f"HD102365_{inst}_timeseries.png")
    plt.savefig(fig_path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f"Saved figure: {fig_path}")

def plot_espresso_timeseries(df, fig_dir):
    """Plot ESPRESSO time series with different datasets colored."""
    
    fig, axes = plt.subplots(3, 1, figsize=(12, 10), sharex=True)
    
    plot_info = [
        ('vrad', 'svrad', 'RV [m/s]'),
        ('bis_span', 'sig_bis_span', 'BIS [m/s]'),
        ('fwhm', 'sig_fwhm', 'FWHM [m/s]')
    ]
    
    # Get unique datasets and assign colors
    datasets = sorted(df['Dataset'].unique())
    colors = plt.cm.tab10(np.linspace(0, 1, len(datasets)))
    color_map = dict(zip(datasets, colors))
    
    for ax, (col, err_col, ylabel) in zip(axes, plot_info):
        for dataset in datasets:
            ds_data = df[df['Dataset'] == dataset].copy()
            
            # Split into inliers and outliers
            inliers = ds_data[~ds_data['is_outlier']]
            outliers = ds_data[ds_data['is_outlier']]
            
            # Plot inliers - USE BJD INSTEAD OF RJD
            if not inliers.empty:
                ax.errorbar(inliers['bjd'], inliers[col], yerr=inliers[err_col],
                           fmt="o", color=color_map[dataset], label=dataset,
                           alpha=0.7, markersize=5)
            
            # Plot outliers
            if not outliers.empty:
                ax.errorbar(outliers['bjd'], outliers[col], yerr=outliers[err_col],
                           fmt="o", color="black", alpha=0.7, markersize=7,
                           markeredgecolor="red", markeredgewidth=1.5)
        
        ax.set_ylabel(ylabel)
        ax.grid(True, alpha=0.3)
    
    # Add legend and outlier marker
    handles, labels = axes[0].get_legend_handles_labels()
    if df['is_outlier'].any():
        from matplotlib.lines import Line2D
        outlier_marker = Line2D([0], [0], marker='o', color='w', 
                               markerfacecolor='black', markeredgecolor='red',
                               markeredgewidth=1.5, markersize=7, label='Outliers')
        handles.append(outlier_marker)
        labels.append('Outliers')
    axes[0].legend(handles, labels, loc='best')
    
    axes[-1].set_xlabel("BJD")
    fig.suptitle("HD102365 - ESPRESSO", fontsize=16)
    plt.tight_layout(rect=[0, 0, 1, 0.97])
    
    fig_path = os.path.join(fig_dir, "HD102365_ESPRESSO_timeseries.png")
    plt.savefig(fig_path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f"Saved figure: {fig_path}")

def main():
    """Main function to process HD102365 data."""
    
    # Configuration
    data_dir = "/work2/lbuc/iara/GitHub/PyORBIT_examples/HD102365"
    dat_file = os.path.join(data_dir, "table3.dat")
    outdir = os.path.join(data_dir, "processed_data")
    fig_dir = os.path.join(data_dir, "figures")
    
    os.makedirs(outdir, exist_ok=True)
    os.makedirs(fig_dir, exist_ok=True)
    
    # Process .dat file
    print("=" * 60)
    print("Processing table3.dat file...")
    print("=" * 60)
    df_dat = load_dat_file(dat_file, star_name="HD102365")
    df_dat = detect_outliers_dat(df_dat, sigma_threshold=4)
    save_dat_files_per_instrument(df_dat, outdir, exclude_outliers=True)
    
    # Create plots for each instrument
    print("\nCreating time series plots for each instrument...")
    for inst in df_dat['Instrument'].unique():
        inst_data = df_dat[df_dat['Instrument'] == inst]
        plot_instrument_timeseries(inst, inst_data, fig_dir)
    
    # Create all instruments combined plot
    print("\nCreating all instruments combined time series plot...")
    plot_all_instruments_timeseries(df_dat, fig_dir)
    
    # Process .rdb files
    print("\n" + "=" * 60)
    print("Processing ESPRESSO .rdb files...")
    print("=" * 60)
    
    # Exclude the problematic file
    exclude_files = ['HD102365_ESPRESSO19_2.rdb', 'HD102365_ESPRESSO19_3.rdb']
    
    df_rdb = load_rdb_files(data_dir, 
                           file_pattern="HD102365_ESPRESSO*.rdb",
                           exclude_files=exclude_files)
    df_rdb = detect_outliers_rdb(df_rdb, sigma_threshold=4)
    save_rdb_concatenated(df_rdb, outdir, exclude_outliers=True)
    
    # Create ESPRESSO plot
    print("\nCreating ESPRESSO time series plot...")
    plot_espresso_timeseries(df_rdb, fig_dir)
    
    print("\n" + "=" * 60)
    print("Processing complete!")
    print("=" * 60)
    print(f"\nOutput files saved to:")
    print(f"  Data: {outdir}")
    print(f"  Figures: {fig_dir}")

if __name__ == "__main__":
    main()
