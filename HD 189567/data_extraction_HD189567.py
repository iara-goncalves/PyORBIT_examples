from glob import glob
import os
import numpy as np
import pandas as pd
from astropy.io import fits
import matplotlib.pyplot as plt
from astropy.timeseries import LombScargle
from scipy.signal import find_peaks

# Specify where all the data is - ESPRESSO
data_dir = "/work2/lbuc/iara/Data/Fits_ESPRESSO"

def extract_fits_data(fits_file):
    """
    Extract the required ESO QC parameters from a FITS file header
    """
    try:
        with fits.open(fits_file) as hdul:
            header = hdul[0].header
            
            # Extract the required parameters
            data = {
                'BJD': header.get('HIERARCH ESO QC BJD', np.nan),
                'RV': header.get('HIERARCH ESO QC CCF RV', np.nan),
                'RV_ERROR': header.get('HIERARCH ESO QC CCF RV ERROR', np.nan),
                'CCF_FWHM': header.get('HIERARCH ESO QC CCF FWHM', np.nan),
                'CCF_FWHM_ERROR': header.get('HIERARCH ESO QC CCF FWHM ERROR', np.nan),
                'CCF_CONTRAST': header.get('HIERARCH ESO QC CCF CONTRAST', np.nan),
                'CCF_CONTRAST_ERROR': header.get('HIERARCH ESO QC CCF CONTRAST ERROR', np.nan),
                'CCF_BIS': header.get('HIERARCH ESO QC CCF BIS SPAN', np.nan),
                'CCF_BIS_ERROR': header.get('HIERARCH ESO QC CCF BIS SPAN ERROR', np.nan)
            }
            
            # Convert km/s to m/s immediately after extraction
            km_to_m_columns = ['RV', 'RV_ERROR', 'CCF_FWHM', 'CCF_FWHM_ERROR', 'CCF_BIS', 'CCF_BIS_ERROR']
            for col in km_to_m_columns:
                if not np.isnan(data[col]):
                    data[col] = data[col] * 1000  # Convert km/s to m/s
            
        return data
    
    except Exception as e:
        print(f"Error reading {fits_file}: {e}")
        return None

def identify_outliers(data, sigma_threshold=4):
    """
    Identify outliers using sigma clipping
    """
    mean = np.nanmean(data)
    std = np.nanstd(data)
    outliers = np.abs(data - mean) > sigma_threshold * std
    return outliers

def plot_activity_with_periodograms_espresso(df, output_dir, sigma_threshold=4):
    """
    Plot ESPRESSO activity indicators with Lomb-Scargle periodograms using only inliers.
    Left column: Activity data, Right column: Periodograms
    """
    # Remove outliers for periodogram analysis
    df_clean = df.copy()
    
    # Identify and mark outliers for each indicator
    indicators_for_outliers = ['RV', 'CCF_FWHM', 'CCF_CONTRAST', 'CCF_BIS']
    df_clean['is_outlier'] = False
    
    for indicator in indicators_for_outliers:
        if indicator in df_clean.columns:
            mask = ~np.isnan(df_clean[indicator])
            if mask.sum() > 0:
                outliers = identify_outliers(df_clean.loc[mask, indicator].values, sigma_threshold)
                df_clean.loc[mask, 'is_outlier'] |= outliers
    
    # Use only inliers for periodograms
    inliers = df_clean[~df_clean.is_outlier].copy()
    
    fig, axes = plt.subplots(4, 2, figsize=(18, 16))
    
    # Define plot information: (column_name, error_column, y_label, units)
    plot_info = [
        ("RV", "RV_ERROR", "RV [m/s]", "m/s"),
        ("CCF_CONTRAST", "CCF_CONTRAST_ERROR", "CCF Contrast", "%"),
        ("CCF_FWHM", "CCF_FWHM_ERROR", "CCF FWHM [m/s]", "m/s"),
        ("CCF_BIS", "CCF_BIS_ERROR", "BIS [m/s]", "m/s"),
    ]
    
    for i, (col, err_col, ylabel, units) in enumerate(plot_info):
        ax_data = axes[i, 0]      # Left column for data
        ax_period = axes[i, 1]    # Right column for periodogram
        
        if col not in df.columns:
            ax_data.text(0.5, 0.5, f"Column '{col}' not found", 
                        ha='center', va='center', transform=ax_data.transAxes)
            ax_period.text(0.5, 0.5, f"No data for '{col}'", 
                          ha='center', va='center', transform=ax_period.transAxes)
            ax_data.set_ylabel(ylabel)
            continue
        
        # === LEFT SIDE: DATA PLOT ===
        # Get data without NaN values for both value and error
        mask = ~(np.isnan(df[col]) | np.isnan(df[err_col]))
        bjd_clean = df.loc[mask, 'BJD']
        data_clean = df.loc[mask, col]
        error_clean = df.loc[mask, err_col]
        
        if len(data_clean) > 0:
            # Calculate mean for centering
            data_mean = np.nanmean(data_clean)
            y_centered = data_clean - data_mean
            
            # Identify outliers for plotting
            outliers = identify_outliers(data_clean.values, sigma_threshold)
            
            # Plot inliers with error bars
            ax_data.errorbar(bjd_clean[~outliers], y_centered[~outliers], 
                           yerr=error_clean[~outliers], fmt=".", 
                           color='blue', alpha=0.7, markersize=6, label='ESPRESSO')
            
            # Plot outliers with error bars
            if np.any(outliers):
                ax_data.errorbar(bjd_clean[outliers], y_centered[outliers], 
                               yerr=error_clean[outliers], fmt="o", 
                               color="black", alpha=0.7, markersize=8,
                               markeredgecolor="red", markeredgewidth=1.5,
                               label=f'Outliers (>{sigma_threshold}σ)')
        
        ax_data.set_ylabel(f"{ylabel} - mean")
        ax_data.grid(True, alpha=0.3)
        if i == 0:  # Add legend only to first plot
            ax_data.legend(fontsize=8)
        
        # === RIGHT SIDE: LOMB-SCARGLE PERIODOGRAM ===
        try:
            if not inliers.empty and col in inliers.columns:
                # Prepare data for periodogram (inliers only)
                mask_inliers = ~(np.isnan(inliers[col]) | np.isnan(inliers[err_col]))
                time_data = inliers.loc[mask_inliers, 'BJD'].values
                y_data = inliers.loc[mask_inliers, col].values
                dy_data = inliers.loc[mask_inliers, err_col].values
                
                if len(time_data) > 5:  # Need sufficient points for periodogram
                    # Fix non-positive errors
                    m = dy_data > 0
                    if not m.all():
                        repl = np.median(dy_data[m]) if m.any() else 1.0
                        dy_data[~m] = repl
                        print(f"Warning: Fixed {(~m).sum()} non-positive errors in {col}")
                    
                    span = time_data.max() - time_data.min()
                    if span > 1:  # Need reasonable time span
                        # Define period range
                        min_period = 1.1
                        max_period = max(2.0, 0.8 * span)
                        f_min = 1.0 / max_period
                        f_max = 1.0 / min_period
                        
                        # Create frequency grid
                        N = 15000
                        freq = np.linspace(f_min, f_max, N)
                        
                        # Compute Lomb-Scargle periodogram
                        ls = LombScargle(time_data, y_data, dy_data)
                        power = ls.power(freq)
                        
                        # === PEAK DETECTION ===
                        power_threshold = np.percentile(power, 90)
                        min_period_separation = 0.01
                        min_freq_separation = int(len(freq) * min_period_separation / np.log10(f_max/f_min))
                        
                        # Find peaks
                        peak_indices, peak_properties = find_peaks(
                            power, 
                            height=power_threshold,
                            distance=max(1, min_freq_separation),
                            prominence=power_threshold * 0.1
                        )
                        
                        # Sort peaks by power and take top 3
                        if len(peak_indices) > 0:
                            peak_powers = power[peak_indices]
                            sorted_peak_order = np.argsort(peak_powers)[::-1]
                            
                            top_peak_indices = peak_indices[sorted_peak_order[:3]]
                            top_peak_powers = peak_powers[sorted_peak_order[:3]]
                            top_peak_periods = 1.0 / freq[top_peak_indices]
                            
                            # Sort by period for consistent display
                            period_sort_order = np.argsort(top_peak_periods)
                            peak_periods = top_peak_periods[period_sort_order]
                            peak_powers_sorted = top_peak_powers[period_sort_order]
                        else:
                            peak_periods = []
                            peak_powers_sorted = []
                        
                        # Convert to periods for plotting
                        periods = 1.0 / freq
                        
                        # Plot periodogram
                        ax_period.semilogx(periods, power, 'k-', linewidth=1)
                        
                        # Plot the top 3 peaks
                        peak_colors = ['red', 'orange', 'purple']
                        peak_styles = ['--', '-.', ':']
                        
                        for j, (peak_period, peak_power) in enumerate(zip(peak_periods, peak_powers_sorted)):
                            if j < len(peak_colors):
                                ordinal = ['1st', '2nd', '3rd'][j]
                                ax_period.axvline(peak_period, color=peak_colors[j], 
                                                ls=peak_styles[j], lw=2, 
                                                label=f'{ordinal} Peak: {peak_period:.1f}d')
                        
                        # Add reference lines for common periods
                        reference_periods = [1, 7, 14, 28]
                        for ref_period in reference_periods:
                            if min_period <= ref_period <= max_period:
                                ax_period.axvline(ref_period, color='blue', alpha=0.4, 
                                                linestyle=':', linewidth=1)
                                ax_period.text(ref_period, ax_period.get_ylim()[1]*0.85, 
                                             f'{ref_period}d', rotation=90, ha='right', 
                                             va='top', fontsize=8, alpha=0.7, color='blue')
                        
                        ax_period.set_xlabel("Period [days]")
                        ax_period.set_ylabel("LS Power")
                        ax_period.set_title(f"{ylabel} Periodogram", fontsize=10)
                        ax_period.grid(True, alpha=0.3)
                        
                        # Only add legend if there are peaks
                        if len(peak_periods) > 0:
                            ax_period.legend(fontsize=8)
                        
                        # Add statistics text
                        if len(peak_periods) > 0:
                            peak_info = '\n'.join([f'Peak {j+1}: {p:.1f}d (P={pow:.3f})' 
                                                 for j, (p, pow) in enumerate(zip(peak_periods, peak_powers_sorted))])
                            stats_text = f'N={len(time_data)} points\nSpan={span:.1f}d\n{peak_info}'
                        else:
                            stats_text = f'N={len(time_data)} points\nSpan={span:.1f}d\nNo significant peaks'
                        
                        ax_period.text(0.02, 0.75, stats_text, 
                                     transform=ax_period.transAxes, fontsize=7, 
                                     verticalalignment='top', alpha=0.9,
                                     bbox=dict(boxstyle="round,pad=0.4", facecolor="white", 
                                             alpha=0.9, edgecolor='gray', linewidth=0.5))
                        
                        # Print results
                        if len(peak_periods) > 0:
                            peak_str = ', '.join([f'{p:.2f}d' for p in peak_periods])
                            print(f"ESPRESSO - {col}: Top periods = {peak_str}")
                        else:
                            print(f"ESPRESSO - {col}: No significant peaks found")
                        
                    else:
                        ax_period.text(0.5, 0.5, f"Insufficient time span\n({span:.1f} days)", 
                                     ha='center', va='center', transform=ax_period.transAxes)
                else:
                    ax_period.text(0.5, 0.5, f"Insufficient data\n({len(time_data)} points)", 
                                 ha='center', va='center', transform=ax_period.transAxes)
            else:
                ax_period.text(0.5, 0.5, "No data available", 
                             ha='center', va='center', transform=ax_period.transAxes)
                
        except Exception as e:
            ax_period.text(0.5, 0.5, f"Error computing\nperiodogram:\n{str(e)[:50]}...", 
                         ha='center', va='center', transform=ax_period.transAxes, fontsize=8)
            print(f"Error in ESPRESSO - {col}: {str(e)}")
    
    # Set x-labels for bottom row
    axes[-1, 0].set_xlabel("Time [eMJD]")
    axes[-1, 1].set_xlabel("Period [days]")
    
    # Set overall title
    fig.suptitle("ESPRESSO - Activity Indicators & Lomb-Scargle Periodograms (Inliers Only)", 
                 fontsize=16)
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    
    # Save figure
    fig_path = os.path.join(output_dir, 'ESPRESSO_activity_LS_periodograms.png')
    plt.savefig(fig_path, dpi=150, bbox_inches='tight')
    plt.show()
    print(f"Saved figure: {fig_path}")

def main():
    # Get all FITS files in the directory
    fits_files = glob(os.path.join(data_dir, "*.fits"))
    
    if not fits_files:
        print(f"No FITS files found in {data_dir}")
        return
    
    print(f"Found {len(fits_files)} FITS files")
    
    # Extract data from all files (units already converted to m/s)
    all_data = []
    for fits_file in fits_files:
        print(f"Processing: {os.path.basename(fits_file)}")
        data = extract_fits_data(fits_file)
        if data is not None:
            data['filename'] = os.path.basename(fits_file)
            all_data.append(data)
    
    if not all_data:
        print("No data extracted from any files")
        return
    
    # Create DataFrame (already in m/s units)
    df = pd.DataFrame(all_data)
    
    # Sort by BJD
    df = df.sort_values('BJD').reset_index(drop=True)
    
    # Display the DataFrame
    print("\nExtracted data (all units in m/s):")
    print(df.head())
    print(f"\nTotal records: {len(df)}")
    
    # Create output directory for .dat files
    output_dir = os.path.join(data_dir, "data_files_espresso")
    os.makedirs(output_dir, exist_ok=True)
    
    # Save individual .dat files for each activity indicator with new names
    indicators = {
        'RV_ESPRESSO': {
            'columns': ['BJD', 'RV', 'RV_ERROR']
        },
        'CCF_FWHM_ESPRESSO': {
            'columns': ['BJD', 'CCF_FWHM', 'CCF_FWHM_ERROR']
        },
        'CCF_CONTRAST_ESPRESSO': {
            'columns': ['BJD', 'CCF_CONTRAST', 'CCF_CONTRAST_ERROR']
        },
        'CCF_BIS_ESPRESSO': {
            'columns': ['BJD', 'CCF_BIS', 'CCF_BIS_ERROR']
        }
    }
    
    # Set sigma threshold for outlier detection
    sigma_threshold = 4  # Changed from 3 to 4
    
    for indicator, info in indicators.items():
        # Create subset DataFrame
        subset_df = df[info['columns']].copy()
        
        # Remove rows with NaN values
        subset_df = subset_df.dropna()
        
        if len(subset_df) > 0:
            # Identify outliers for the main parameter (not BJD or errors)
            main_param = info['columns'][1]  # Second column is the main parameter
            outliers = identify_outliers(subset_df[main_param].values, sigma_threshold)
            
            # Save as .dat file
            output_file = os.path.join(output_dir, f"{indicator}.dat")
            
            # Save with tab separation, no header
            np.savetxt(output_file, subset_df.values, 
                      delimiter='\t', 
                      fmt='%g')
            
            print(f"Saved {indicator}.dat with {len(subset_df)} records")
            print(f"  - {np.sum(outliers)} outliers detected (>{sigma_threshold}σ)")
        else:
            print(f"Warning: No valid data for {indicator}")
    
    # Create activity indicators + periodograms plot
    print(f"\nCreating activity indicators + periodograms plot (σ threshold = {sigma_threshold})...")
    plot_activity_with_periodograms_espresso(df, output_dir, sigma_threshold)
    
    # Display summary statistics
    print("\nSummary Statistics (all in m/s units):")
    numeric_columns = ['BJD', 'RV', 'RV_ERROR', 'CCF_FWHM', 'CCF_FWHM_ERROR', 
                      'CCF_CONTRAST', 'CCF_CONTRAST_ERROR', 'CCF_BIS', 'CCF_BIS_ERROR']
    print(df[numeric_columns].describe())
    
    return df

# Run the extraction
if __name__ == "__main__":
    extracted_df = main()
