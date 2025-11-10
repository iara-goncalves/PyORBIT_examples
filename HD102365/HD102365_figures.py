
import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from astropy.timeseries import LombScargle
from scipy.signal import find_peaks

def load_dat_files(data_dir):
    """Load data directly from .dat files created by the HD102365 processing script"""
    
    all_data = []
    
    # Look for all HD102365*.dat files
    dat_files = [f for f in os.listdir(data_dir) if f.startswith('HD102365') and f.endswith('.dat')]
    dat_files.sort()
    
    if not dat_files:
        raise FileNotFoundError(f"No HD102365*.dat files found in {data_dir}")
    
    print(f"Found {len(dat_files)} .dat files")
    
    # Group files by instrument and measurement type
    # File format: HD102365_{instrument}_{measurement}.dat
    file_groups = {}
    for filename in dat_files:
        parts = filename.replace('HD102365_', '').replace('.dat', '').split('_')
        
        if len(parts) == 2:
            instrument = parts[0]
            measurement = parts[1]
            
            if instrument not in file_groups:
                file_groups[instrument] = {}
            file_groups[instrument][measurement] = filename
    
    # Process each instrument
    for instrument in sorted(file_groups.keys()):
        print(f"Processing {instrument}...")
        inst_data = None
        
        for measurement, filename in sorted(file_groups[instrument].items()):
            filepath = os.path.join(data_dir, filename)
            
            try:
                # Read: time, value, error, jitter_flag, offset_flag, subset_flag
                data = np.loadtxt(filepath)
                
                # Create base DataFrame
                df = pd.DataFrame({
                    'Time [BJD]': data[:, 0],
                    'offset_flag': data[:, 4].astype(int),
                    'Instrument': instrument
                })
                
                # Add measurement-specific columns
                if measurement == 'RV':
                    df['RV [m/s]'] = data[:, 1]
                    df['RV Err. [m/s]'] = data[:, 2]
                elif measurement == 'BIS':
                    df['BIS [m/s]'] = data[:, 1]
                    df['BIS Err. [m/s]'] = data[:, 2]
                elif measurement == 'FWHM':
                    df['CCF FWHM [m/s]'] = data[:, 1]
                    df['CCF FWHM Err. [m/s]'] = data[:, 2]
                elif measurement == 'Contrast':
                    df['CCF Contrast'] = data[:, 1]
                    df['CCF Contrast Err.'] = data[:, 2]
                elif measurement == 'EWHa':
                    df['H-alpha Emission'] = data[:, 1]
                    df['H-alpha Err.'] = data[:, 2]
                elif measurement == 'SHK':
                    df['S_HK Index'] = data[:, 1]
                    df['S_HK Err.'] = data[:, 2]
                
                # Merge with existing instrument data
                if inst_data is None:
                    inst_data = df
                else:
                    inst_data = pd.merge(inst_data, df, on=['Time [BJD]', 'offset_flag', 'Instrument'], how='outer')
                
            except Exception as e:
                print(f"  Error loading {filepath}: {e}")
                continue
        
        if inst_data is not None:
            all_data.append(inst_data)
            print(f"  Loaded {len(inst_data)} points")
    
    # Combine all instruments
    if all_data:
        df_all = pd.concat(all_data, ignore_index=True)
        print(f"\nTotal: {len(df_all)} points from {len(all_data)} instruments")
        return df_all
    else:
        raise ValueError("No data loaded!")

def plot_activity_with_periodograms(instrument, inst_df, fig_dir):
    """
    Plot activity indicators with Lomb-Scargle periodograms.
    Left column: Activity data, Right column: Periodograms
    Only includes rows where data exists.
    """
    
    # Define plot information: (column_name, error_column, y_label)
    plot_info = [
        ("RV [m/s]", "RV Err. [m/s]", "RV [m/s]"),
        ("CCF Contrast", "CCF Contrast Err.", "CCF Contrast"),
        ("CCF FWHM [m/s]", "CCF FWHM Err. [m/s]", "CCF FWHM [m/s]"),
        ("BIS [m/s]", "BIS Err. [m/s]", "BIS [m/s]"),
        ("H-alpha Emission", "H-alpha Err.", "H-alpha Emission"),
        ("S_HK Index", "S_HK Err.", "S_HK Index"),
    ]
    
    # Filter to only include indicators with data
    valid_plots = []
    for col, err_col, ylabel in plot_info:
        if col in inst_df.columns and not inst_df[col].isna().all():
            valid_data = inst_df[inst_df[col].notna()]
            if len(valid_data) > 0:
                valid_plots.append((col, err_col, ylabel))
                print(f"  {col}: {len(valid_data)} points")
    
    if len(valid_plots) == 0:
        print(f"No valid data for {instrument}, skipping plot.")
        return
    
    # Create figure with only the necessary rows
    n_rows = len(valid_plots)
    fig, axes = plt.subplots(n_rows, 2, figsize=(18, 3*n_rows))
    
    # Handle case where there's only one row (axes won't be 2D)
    if n_rows == 1:
        axes = axes.reshape(1, -1)
    
    # Use skyblue color for data points
    data_color = "skyblue"
    
    for i, (col, err_col, ylabel) in enumerate(valid_plots):
        ax_data = axes[i, 0]      # Left column for data
        ax_period = axes[i, 1]    # Right column for periodogram
        
        # Filter valid data
        valid_data = inst_df[inst_df[col].notna()].copy()
        
        # === LEFT SIDE: DATA PLOT ===
        # Center data by median
        median_val = valid_data[col].median()
        y_centered = valid_data[col] - median_val
        
        # Handle error bars
        if err_col in valid_data.columns:
            error_values = valid_data[err_col]
        else:
            error_values = None
        
        ax_data.errorbar(valid_data["Time [BJD]"], y_centered, 
                       yerr=error_values, fmt="o", 
                       color=data_color, label=instrument, 
                       alpha=0.7, markersize=5)
        
        ax_data.set_ylabel(f"{ylabel} - median")
        ax_data.grid(True, alpha=0.3)
        ax_data.legend(loc='best', fontsize=8)
        
        # === RIGHT SIDE: LOMB-SCARGLE PERIODOGRAM ===
        try:
            # Prepare data for periodogram
            time_data = valid_data["Time [BJD]"].values
            y_data = valid_data[col].values
            
            # Handle error values
            if err_col in valid_data.columns:
                dy_data = valid_data[err_col].values
            else:
                dy_data = np.ones_like(y_data)
            
            # Remove NaN values
            mask = ~(np.isnan(time_data) | np.isnan(y_data) | np.isnan(dy_data))
            t = time_data[mask]
            y = y_data[mask]
            dy = dy_data[mask]
            
            if len(t) > 5:  # Need sufficient points for periodogram
                # Fix non-positive errors
                m = dy > 0
                if not m.all():
                    repl = np.median(dy[m]) if m.any() else 1.0
                    dy[~m] = repl
                
                span = t.max() - t.min()
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
                    ls = LombScargle(t, y, dy)
                    power = ls.power(freq)
                    
                    # === FALSE ALARM PROBABILITY LEVELS ===
                    fap_levels = [0.001, 0.01, 0.1]  # 0.1%, 1%, 10%
                    fap_colors = ['red', 'orange', 'green']
                    fap_labels = ['0.1%', '1%', '10%']
                    fap_powers = []
                    
                    try:
                        for fap in fap_levels:
                            fap_power = ls.false_alarm_level(fap, method='baluev')
                            fap_powers.append(fap_power)
                        print(f"    FAP levels: 0.1%={fap_powers[0]:.3f}, 1%={fap_powers[1]:.3f}, 10%={fap_powers[2]:.3f}")
                    except Exception as fap_error:
                        print(f"    Warning: Could not compute FAP levels: {fap_error}")
                        fap_powers = []
                    
                    # === PEAK DETECTION ===
                    power_threshold = np.percentile(power, 85)
                    max_power = np.max(power)
                    
                    if power_threshold > 0.8 * max_power:
                        power_threshold = 0.5 * max_power
                    
                    min_period_separation = 0.01
                    min_freq_separation = int(len(freq) * min_period_separation / np.log10(f_max/f_min))
                    
                    try:
                        peak_indices, peak_properties = find_peaks(
                            power, 
                            height=float(power_threshold),
                            distance=max(1, min_freq_separation),
                            prominence=float(power_threshold) * 0.1
                        )
                        
                        if len(peak_indices) == 0:
                            lower_threshold = np.percentile(power, 70)
                            peak_indices, peak_properties = find_peaks(
                                power, 
                                height=float(lower_threshold),
                                distance=max(1, min_freq_separation),
                                prominence=float(lower_threshold) * 0.05
                            )
                            
                    except Exception as peak_error:
                        print(f"    Peak detection error: {peak_error}")
                        peak_indices = [np.argmax(power)] if len(power) > 0 else []
                        peak_indices = np.array(peak_indices)
                    
                    # === PROCESS DETECTED PEAKS ===
                    if len(peak_indices) > 0:
                        peak_periods = 1.0 / freq[peak_indices]
                        peak_powers_raw = power[peak_indices]
                        
                        # Sort by power (highest first)
                        sorted_indices = np.argsort(peak_powers_raw)[::-1]
                        peak_periods = peak_periods[sorted_indices][:3]  # Top 3 peaks
                        peak_powers_sorted = peak_powers_raw[sorted_indices][:3]
                        
                        # Calculate FAP for each detected peak
                        peak_faps = []
                        peak_significance = []
                        
                        for peak_power in peak_powers_sorted:
                            try:
                                peak_fap = ls.false_alarm_probability(peak_power, method='baluev')
                                peak_faps.append(peak_fap)
                                
                                if len(fap_powers) >= 3:
                                    if peak_power >= fap_powers[0]:
                                        significance = "highly significant"
                                    elif peak_power >= fap_powers[1]:
                                        significance = "significant"
                                    elif peak_power >= fap_powers[2]:
                                        significance = "marginally significant"
                                    else:
                                        significance = "not significant"
                                else:
                                    significance = "unknown"
                                peak_significance.append(significance)
                                
                            except Exception as e:
                                peak_faps.append(np.nan)
                                peak_significance.append("unknown")
                        
                        print(f"    Detected peaks:")
                        for j, (period, power_val, fap, sig) in enumerate(zip(peak_periods, peak_powers_sorted, peak_faps, peak_significance)):
                            ordinal = ['1st', '2nd', '3rd'][j]
                            if not np.isnan(fap):
                                print(f"      {ordinal}: {period:.2f}d, Power={power_val:.4f}, FAP={fap:.2e} ({sig})")
                            else:
                                print(f"      {ordinal}: {period:.2f}d, Power={power_val:.4f}")
                                
                    else:
                        peak_periods = []
                        peak_powers_sorted = []
                        peak_faps = []
                        peak_significance = []
                    
                    # Convert to periods for plotting
                    periods = 1.0 / freq
                    
                    # Plot periodogram
                    ax_period.semilogx(periods, power, 'k-', linewidth=1)
                    
                    # Plot FALSE ALARM PROBABILITY reference lines
                    for fap_power, fap_color, fap_label in zip(fap_powers, fap_colors, fap_labels):
                        ax_period.axhline(fap_power, color=fap_color, linestyle='--', 
                                        alpha=0.7, linewidth=1.5, 
                                        label=f'{fap_label} FAP')
                    
                    # Plot detected peaks with their FAP values
                    peak_colors = ['purple', 'blue', 'cyan']
                    peak_styles = ['-', '--', ':']
                    
                    for j, (peak_period, peak_power, peak_fap, significance) in enumerate(zip(peak_periods, peak_powers_sorted, peak_faps, peak_significance)):
                        if j < len(peak_colors):
                            ordinal = ['1st', '2nd', '3rd'][j]
                            if not np.isnan(peak_fap):
                                label = f'{ordinal}: {peak_period:.1f}d (FAP={peak_fap:.1e})'
                            else:
                                label = f'{ordinal}: {peak_period:.1f}d'
                            
                            ax_period.axvline(peak_period, color=peak_colors[j], 
                                            ls=peak_styles[j], lw=2, alpha=0.8,
                                            label=label)
                    
                    # Add reference lines for common periods
                    reference_periods = [1, 7, 14, 28, 100, 365]
                    for ref_period in reference_periods:
                        if min_period <= ref_period <= max_period:
                            ax_period.axvline(ref_period, color='blue', alpha=0.3, 
                                            linestyle=':', linewidth=1)
                            ax_period.text(ref_period, ax_period.get_ylim()[1]*0.85, 
                                         f'{ref_period}d', rotation=90, ha='right', 
                                         va='top', fontsize=8, alpha=0.6, color='blue')
                    
                    ax_period.set_xlabel("Period [days]")
                    ax_period.set_ylabel("LS Power")
                    ax_period.set_title(f"{ylabel} Periodogram", fontsize=10)
                    ax_period.grid(True, alpha=0.3)
                    
                    # Add legend (FAP lines + peaks)
                    ax_period.legend(fontsize=7, loc='upper right')
                    
                    # Add statistics text
                    if len(peak_periods) > 0:
                        peak_info = []
                        for j, (p, pow, fap) in enumerate(zip(peak_periods, peak_powers_sorted, peak_faps)):
                            if not np.isnan(fap):
                                peak_info.append(f'Peak {j+1}: {p:.1f}d (FAP={fap:.1e})')
                            else:
                                peak_info.append(f'Peak {j+1}: {p:.1f}d (P={pow:.3f})')
                        peak_text = '\n'.join(peak_info)
                        stats_text = f'N={len(t)} points\nSpan={span:.1f}d\n{peak_text}'
                    else:
                        stats_text = f'N={len(t)} points\nSpan={span:.1f}d\nNo significant peaks'
                    
                    ax_period.text(0.02, 0.75, stats_text, 
                                 transform=ax_period.transAxes, fontsize=7, 
                                 verticalalignment='top', alpha=0.9,
                                 bbox=dict(boxstyle="round,pad=0.4", facecolor="white", 
                                         alpha=0.9, edgecolor='gray', linewidth=0.5))
                    
                else:
                    ax_period.text(0.5, 0.5, f"Insufficient time span\n({span:.1f} days)", 
                                 ha='center', va='center', transform=ax_period.transAxes)
            else:
                ax_period.text(0.5, 0.5, f"Insufficient data\n({len(t)} points)", 
                             ha='center', va='center', transform=ax_period.transAxes)
                
        except Exception as e:
            ax_period.text(0.5, 0.5, f"Error computing\nperiodogram:\n{str(e)[:50]}...", 
                         ha='center', va='center', transform=ax_period.transAxes, fontsize=8)
            print(f"    Error: {str(e)}")
    
    # Set x-labels for bottom row
    axes[-1, 0].set_xlabel("Time [BJD]")
    axes[-1, 1].set_xlabel("Period [days]")
    
    # Set overall title
    fig.suptitle(f"HD102365 - {instrument} - Activity Indicators & Lomb-Scargle Periodograms", 
                 fontsize=16)
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    
    # Save figure
    fig_path = os.path.join(fig_dir, f"HD102365_{instrument}_activity_LS_periodograms.png")
    plt.savefig(fig_path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f"  Saved: {fig_path}")

def main():
    """Main function"""
    
    data_dir = "/work2/lbuc/iara/GitHub/PyORBIT_examples/HD102365/processed_data"
    fig_dir = "/work2/lbuc/iara/GitHub/PyORBIT_examples/HD102365/figures"
    
    os.makedirs(fig_dir, exist_ok=True)
    
    # Load data and create plots
    df_all = load_dat_files(data_dir)
    
    print("\nCreating periodogram plots...")
    for instrument, inst_df in df_all.groupby("Instrument"):
        print(f"\n{instrument}:")
        plot_activity_with_periodograms(instrument, inst_df, fig_dir)
    
    print("\nDone!")

if __name__ == "__main__":
    main()
