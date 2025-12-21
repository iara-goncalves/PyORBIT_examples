# compare_emcee_models_HD102365.py

#!/usr/bin/env python3
"""
PyORBIT Log File Parser and Analyzer for HD102365 (emcee runs)
Extracts BIC, convergence statistics, orbital parameters, and activity parameters
from PyORBIT MCMC log files.

This is a lightly adapted version of compare_emcee_models.py:
- Same logic and tables
- HD102365-specific filename parsing and outputs
"""

import re
import os
import sys
import glob
import pandas as pd
import numpy as np
from datetime import datetime


def calculate_t0_from_mean_long(mean_long_deg, omega_deg, period_days, reference_epoch=0.0):
    """
    Calculate time of periastron (t0) from mean longitude.

    Formula: t0 = t_ref - (mean_long - omega) / n, n = 2π/P
    """
    mean_long_rad = np.deg2rad(mean_long_deg)
    omega_rad = np.deg2rad(omega_deg)
    mean_anomaly_rad = mean_long_rad - omega_rad
    n = 2.0 * np.pi / period_days
    dt = mean_anomaly_rad / n
    return reference_epoch - dt


def export_planet_fit_csv(datasets, df, group_name="DTU-Padova-PSU_emcee",
                          reference_epoch=59334.700184, fit_type="multiple",
                          output_dir="."):
    """
    Export Best-Fit Planet Parameters CSV files for ESSP submission (emcee, HD102365).

    Files:
        HD102365_DTU-Padova-PSU_emcee_<fit_type>_<config>_planetFit.csv

    Columns:
        K [m/s], P [d], t0 [eMJD], e, w [deg]

    Selection:
        per (Dataset, Configuration) choose the model with **lowest Median BIC**.
    """
    exported_files = []

    for dataset in datasets:
        dataset_df = df[df['Dataset'] == dataset]
        grouped = dataset_df.groupby('Configuration')

        for config_name, group in grouped:
            # best by BIC
            group = group.copy()
            group['Planets'] = pd.Categorical(
                group['Planets'],
                categories=['0p', '1p', '2p', '3p'],
                ordered=True
            )
            group = group.sort_values('Planets')
            min_bic_idx = group['Median BIC'].idxmin()
            best_model = group.loc[min_bic_idx]
            orbital_params = best_model['Orbital Parameters']

            planet_rows = []
            planets = sorted(orbital_params.keys()) if orbital_params else []

            if planets:
                for planet in planets:
                    pp = orbital_params[planet]

                    K = pp.get('K', {}).get('value')
                    P = pp.get('P', {}).get('value')
                    e = pp.get('e', {}).get('value')
                    omega = pp.get('omega', {}).get('value')
                    mean_long = pp.get('mean_long', {}).get('value')

                    if K is None or P is None:
                        continue

                    if mean_long is not None and omega is not None:
                        t0 = calculate_t0_from_mean_long(mean_long, omega, P, reference_epoch)
                    elif mean_long is not None:
                        t0 = calculate_t0_from_mean_long(mean_long, 0.0, P, reference_epoch)
                    else:
                        t0 = None

                    if e is None:
                        e = 0.0
                    if omega is None:
                        omega = 0.0

                    row = {
                        'K [m/s]': K,
                        'P [d]': P,
                        't0 [eMJD]': t0 if t0 is not None else np.nan,
                        'e': e,
                        'w [deg]': omega
                    }
                    planet_rows.append(row)

            columns = ['K [m/s]', 'P [d]', 't0 [eMJD]', 'e', 'w [deg]']
            planet_df = pd.DataFrame(planet_rows) if planet_rows else pd.DataFrame(columns=columns)

            clean_config_name = config_name
            if fit_type == 'single' and config_name.endswith('_single'):
                clean_config_name = config_name[:-7]

            filename = f"{dataset}_{group_name}_{fit_type}_{clean_config_name}_planetFit.csv"
            filepath = os.path.join(output_dir, filename)
            planet_df.to_csv(filepath, index=False, encoding='utf-8', float_format='%.6f')
            exported_files.append(filepath)

            npl = len(planet_rows)
            if npl == 0:
                print(f"  Exported: {filepath} (0-planet model, headers only)")
            else:
                print(f"  Exported: {filepath} ({npl} planet(s))")

    return exported_files


def export_best_model_directories(datasets, df, output_filename=None, output_dir="."):
    """
    Export a simple list of directory names where best models (lowest BIC) were found.
    """
    directory_names = []

    for dataset in datasets:
        dataset_df = df[df['Dataset'] == dataset]
        grouped = dataset_df.groupby('Configuration')

        for config_name, group in grouped:
            group = group.copy()
            group['Planets'] = pd.Categorical(
                group['Planets'],
                categories=['0p', '1p', '2p', '3p'],
                ordered=True
            )
            group = group.sort_values('Planets')
            min_bic_idx = group['Median BIC'].idxmin()
            best_model = group.loc[min_bic_idx]
            directory_names.append(best_model.get('Directory', ''))

    if not directory_names:
        return None

    dir_df = pd.DataFrame({'Directory': directory_names})
    if output_filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"best_model_directories_emcee_{timestamp}.csv"
    else:
        filename = output_filename

    filepath = os.path.join(output_dir, filename)
    dir_df.to_csv(filepath, index=False, encoding='utf-8')
    print(f"  Exported: {filepath} ({len(directory_names)} directory name(s))")
    return filepath


def parse_log_file(filepath):
    """
    Parse a PyORBIT emcee log file (HD102365) to extract Median BIC,
    convergence status, orbital and activity parameters.

    Expected filename:
        configuration_file_emcee_run_HD102365_<CONFIG>.log
    """
    median_bic = None
    gelman_rubin_values = []
    orbital_parameters = {}
    activity_parameters = {}

    try:
        with open(filepath, 'r') as f:
            content = f.read()

        # Median BIC
        m = re.search(r'Median BIC\s+\(using likelihood\)\s*=\s*(-?[\d\.]+)', content)
        if m:
            median_bic = float(m.group(1))

        # Gelman–Rubin entries
        gr_pattern = (
            r'Gelman-Rubin:\s+(\d+)\s+([\d\.]+)\s+'
            r'([a-zA-Z_][a-zA-Z_0-9]*(?:_[a-zA-Z_][a-zA-Z_0-9]*)*)\s*$'
        )
        gr_matches = re.findall(gr_pattern, content, re.MULTILINE)
        gr_dict = {}
        for match in gr_matches:
            param_name = match[2]
            gr_value = float(match[1])
            gr_dict[param_name] = gr_value
            gelman_rubin_values.append(gr_value)

        # Parameters: LAST stats block
        lines = content.split('\n')
        last_stats_idx = -1
        for i, line in enumerate(lines):
            if "Statistics on the model parameters obtained from the posteriors samples" in line:
                last_stats_idx = i

        if last_stats_idx != -1:
            current_planet = None
            in_activity = False

            for line in lines[last_stats_idx:]:
                planet_match = re.search(r'----- common model:\s+([a-z])\s*$', line)
                if planet_match:
                    current_planet = planet_match.group(1)
                    in_activity = False
                    orbital_parameters.setdefault(current_planet, {})
                    continue

                if "----- common model:  activity" in line:
                    in_activity = True
                    current_planet = None
                    continue

                param_match = re.match(r'^([A-Za-z_]+)\s+([-\d\.]+)\s*$', line.strip())
                if param_match:
                    pname = param_match.group(1)
                    pval = float(param_match.group(2))

                    if in_activity:
                        full_name = f'activity_{pname}'
                        gr = gr_dict.get(full_name)
                        activity_parameters[pname] = {
                            'value': pval,
                            'gelman_rubin': gr
                        }
                    elif current_planet:
                        full_name = f'{current_planet}_{pname}'
                        gr = gr_dict.get(full_name)
                        orbital_parameters[current_planet][pname] = {
                            'value': pval,
                            'gelman_rubin': gr
                        }

            # add sre_coso / sre_sino GR entries (no value in stats section)
            for planet in orbital_parameters.keys():
                coso_key = f'{planet}_sre_coso'
                if coso_key in gr_dict:
                    orbital_parameters[planet].setdefault('sre_coso', {})
                    orbital_parameters[planet]['sre_coso']['gelman_rubin'] = gr_dict[coso_key]

                sino_key = f'{planet}_sre_sino'
                if sino_key in gr_dict:
                    orbital_parameters[planet].setdefault('sre_sino', {})
                    orbital_parameters[planet]['sre_sino']['gelman_rubin'] = gr_dict[sino_key]

    except FileNotFoundError:
        print(f"Error: File not found at {filepath}")
        return None
    except Exception as e:
        print(f"An error occurred while reading {filepath}: {e}")
        return None

    if median_bic is None:
        return None

    # Convergence stats
    if gelman_rubin_values:
        converged_count = sum(1 for gr in gelman_rubin_values if gr < 1.1)
        total_count = len(gelman_rubin_values)
        convergence_pct = (converged_count / total_count * 100.0) if total_count > 0 else 0.0
        max_gr = max(gelman_rubin_values)
    else:
        convergence_pct = 0.0
        max_gr = None

    basename = os.path.basename(filepath)
    cleaned_name = basename.replace('configuration_file_emcee_run_', '').replace('.log', '')

    # For HD102365 we expect: HD102365_<CONFIG>
    if cleaned_name.startswith('HD102365_'):
        dataset = 'HD102365'
        config_name = cleaned_name[len('HD102365_'):]
    else:
        dataset = 'Unknown'
        config_name = cleaned_name

    # Planets from config suffix: ..._0p_emcee, ..._1p_emcee, etc.
    pm = re.search(r'_(\dp)_emcee', config_name)
    if pm:
        num_planets = pm.group(1)
    else:
        num_planets = 'N/A'

    directory_name = os.path.dirname(os.path.abspath(filepath))

    return {
        'Configuration': config_name,
        'Dataset': dataset,
        'Planets': num_planets,
        'Median BIC': median_bic,
        'Convergence %': convergence_pct,
        'Max GR': max_gr,
        'Orbital Parameters': orbital_parameters,
        'Activity Parameters': activity_parameters,
        'File': basename,
        'Directory': directory_name
    }


def analyze_and_display(log_files, search_directory=None, fit_type="multiple"):
    """
    Analyze HD102365 emcee log files and print formatted comparison tables.
    Export results to CSV/HTML, planet-fit CSVs and best-dir list.
    """
    # Output dir from search_directory
    output_dir = "."
    if search_directory:
        folder_name = os.path.basename(os.path.normpath(search_directory))
        output_dir = folder_name
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            print(f"Created output directory: {output_dir}\n")

    all_data = []
    failed_files = []

    print(f"Processing {len(log_files)} log files...")
    for log_file in log_files:
        data = parse_log_file(log_file)
        if data:
            all_data.append(data)
        else:
            failed_files.append(log_file)

    if failed_files:
        print(f"\nWarning: {len(failed_files)} files could not be parsed (missing Median BIC data or wrong format):")
        for f in failed_files:
            print("  -", f)
        print()

    if not all_data:
        print("No data could be extracted from any log files.")
        return

    df = pd.DataFrame(all_data)
    datasets = sorted(df['Dataset'].unique())

    print("--- Model Comparison by Dataset and Configuration (HD102365 emcee) ---\n")

    export_data = []

    for dataset in datasets:
        dataset_df = df[df['Dataset'] == dataset]
        grouped = dataset_df.groupby('Configuration')

        print(f"\n{'='*80}")
        print(f"DATASET: {dataset}")
        print(f"{'='*80}\n")

        best_models_info = []

        for config_name, group in grouped:
            print(f"--- Configuration: {config_name} ---\n")

            group = group.copy()
            group['Planets'] = pd.Categorical(
                group['Planets'],
                categories=['0p', '1p', '2p', '3p'],
                ordered=True
            )
            group = group.sort_values('Planets')

            min_bic_idx = group['Median BIC'].idxmin()
            min_bic_value = group.loc[min_bic_idx, 'Median BIC']

            display_group = group[['Planets', 'Median BIC', 'Convergence %', 'Max GR']].copy()
            display_group['ΔBIC'] = group['Median BIC'] - min_bic_value

            group_copy = group.copy()
            group_copy['Preferred_BIC'] = group_copy.index == min_bic_idx
            group_copy['ΔBIC'] = group_copy['Median BIC'] - min_bic_value
            group_copy['Dataset'] = dataset
            group_copy['Configuration'] = config_name

            export_group = group_copy[['Dataset', 'Configuration', 'Planets',
                                       'Median BIC', 'ΔBIC',
                                       'Convergence %', 'Max GR',
                                       'Preferred_BIC', 'File', 'Directory']]
            export_data.append(export_group)

            print(display_group.to_string(index=False))
            print(f"\nBest BIC: {group.loc[min_bic_idx, 'Planets']} model "
                  f"(BIC = {min_bic_value:.2f})")
            print("\n" + "-"*80 + "\n")

            best_models_info.append({
                'Configuration': config_name,
                'Best Model': group.loc[min_bic_idx, 'Planets'],
                'BIC': min_bic_value,
                'Convergence %': group.loc[min_bic_idx, 'Convergence %'],
                'Max GR': group.loc[min_bic_idx, 'Max GR'],
                'Orbital Parameters': group.loc[min_bic_idx, 'Orbital Parameters'],
                'Activity Parameters': group.loc[min_bic_idx, 'Activity Parameters']
            })

        # Parameter summary tables (same as your base script)
        if best_models_info:
            print(f"\n{'='*160}")
            print(f"ORBITAL & ACTIVITY PARAMETERS SUMMARY FOR {dataset}")
            print(f"{'='*160}\n")

            # Orbital parameters table
            print("TABLE 1: ORBITAL PARAMETERS\n")
            print(f"{'Config':<20} {'Model':<8} {'Planet':<8} {'P (days)':<12} {'P_GR':<8} "
                  f"{'K (m/s)':<10} {'K_GR':<8} {'mean_long':<12} {'ml_GR':<8} "
                  f"{'e':<10} {'ω (deg)':<10} {'coso_GR':<10} {'sino_GR':<10}")
            print("-" * 160)

            for info in best_models_info:
                config_name = info['Configuration']
                best_model = info['Best Model']
                op = info['Orbital Parameters']

                planets = sorted(op.keys()) if op else []

                if not planets:
                    print(f"{config_name:<20} {best_model:<8} {'-':<8} "
                          f"{'-':<12} {'-':<8} {'-':<10} {'-':<8} "
                          f"{'-':<12} {'-':<8} {'-':<10} {'-':<10} "
                          f"{'-':<10} {'-':<10}")
                else:
                    for planet in planets:
                        pp = op[planet]

                        p_val = f"{pp.get('P', {}).get('value', 0):.4f}" if 'P' in pp else '-'
                        p_gr = pp.get('P', {}).get('gelman_rubin')
                        p_gr_str = f"{p_gr:.3f}" if p_gr is not None else '-'

                        k_val = f"{pp.get('K', {}).get('value', 0):.4f}" if 'K' in pp else '-'
                        k_gr = pp.get('K', {}).get('gelman_rubin')
                        k_gr_str = f"{k_gr:.3f}" if k_gr is not None else '-'

                        ml_val = f"{pp.get('mean_long', {}).get('value', 0):.2f}" if 'mean_long' in pp else '-'
                        ml_gr = pp.get('mean_long', {}).get('gelman_rubin')
                        ml_gr_str = f"{ml_gr:.3f}" if ml_gr is not None else '-'

                        e_val = pp.get('e', {}).get('value') if 'e' in pp else None
                        w_val = pp.get('omega', {}).get('value') if 'omega' in pp else None
                        e_str = f"{e_val:.4f}" if e_val is not None else '-'
                        w_str = f"{w_val:.2f}" if w_val is not None else '-'

                        coso_gr = pp.get('sre_coso', {}).get('gelman_rubin')
                        sino_gr = pp.get('sre_sino', {}).get('gelman_rubin')
                        coso_str = f"{coso_gr:.3f}" if coso_gr is not None else '-'
                        sino_str = f"{sino_gr:.3f}" if sino_gr is not None else '-'

                        print(f"{config_name:<20} {best_model:<8} {planet:<8} "
                              f"{p_val:<12} {p_gr_str:<8} {k_val:<10} {k_gr_str:<8} "
                              f"{ml_val:<12} {ml_gr_str:<8} {e_str:<10} {w_str:<10} "
                              f"{coso_str:<10} {sino_str:<10}")

            print()
            # Activity parameters table
            print("TABLE 2: ACTIVITY PARAMETERS\n")
            print(f"{'Config':<20} {'Model':<8} {'Prot (days)':<15} {'Prot_GR':<10} "
                  f"{'Pdec (days)':<15} {'Pdec_GR':<10} {'Oamp':<10} {'Oamp_GR':<10}")
            print("-" * 120)

            for info in best_models_info:
                config_name = info['Configuration']
                best_model = info['Best Model']
                ap = info['Activity Parameters']

                prot_val = f"{ap.get('Prot', {}).get('value', 0):.4f}" if 'Prot' in ap else '-'
                prot_gr = ap.get('Prot', {}).get('gelman_rubin')
                prot_gr_str = f"{prot_gr:.3f}" if prot_gr is not None else '-'

                pdec_val = f"{ap.get('Pdec', {}).get('value', 0):.4f}" if 'Pdec' in ap else '-'
                pdec_gr = ap.get('Pdec', {}).get('gelman_rubin')
                pdec_gr_str = f"{pdec_gr:.3f}" if pdec_gr is not None else '-'

                oamp_val = f"{ap.get('Oamp', {}).get('value', 0):.4f}" if 'Oamp' in ap else '-'
                oamp_gr = ap.get('Oamp', {}).get('gelman_rubin')
                oamp_gr_str = f"{oamp_gr:.3f}" if oamp_gr is not None else '-'

                print(f"{config_name:<20} {best_model:<8} {prot_val:<15} {prot_gr_str:<10} "
                      f"{pdec_val:<15} {pdec_gr_str:<10} {oamp_val:<10} {oamp_gr_str:<10}")

            print("\n" + "="*160 + "\n")

    # Export CSV + HTML + planetFit + best-dir
    if export_data:
        combined_df = pd.concat(export_data, ignore_index=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        csv_filename = f"HD102365_emcee_model_comparison_{timestamp}.csv"
        csv_filepath = os.path.join(output_dir, csv_filename)
        combined_df.to_csv(csv_filepath, index=False, encoding='utf-8')

        html_filename = f"HD102365_emcee_model_comparison_{timestamp}.html"
        html_filepath = os.path.join(output_dir, html_filename)

        # Reuse your HTML layout but with HD102365‑specific title & CSV name
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>HD102365 emcee Model Comparison</title>
</head>
<body>
    <h1>HD102365 emcee Model Comparison</h1>
    <p>Full table exported to CSV file: <code>{os.path.basename(csv_filename)}</code></p>
</body>
</html>
"""
        with open(html_filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)

        print(f"\n{'='*80}")
        print("Exporting Best-Fit Planet Parameters CSV files (emcee)...")
        planet_fit_files = export_planet_fit_csv(datasets, df,
                                                 group_name="DTU-Padova-PSU_emcee",
                                                 reference_epoch=59334.700184,
                                                 fit_type=fit_type,
                                                 output_dir=output_dir)

        print(f"\nExporting best model directory names (emcee)...")
        if search_directory:
            folder_name = os.path.basename(os.path.normpath(search_directory))
            output_filename = f"{folder_name}_emcee_best_dirs.csv"
        else:
            output_filename = None
        dir_file = export_best_model_directories(datasets, df,
                                                 output_filename=output_filename,
                                                 output_dir=output_dir)

        print(f"\n{'='*80}")
        print("Results exported to:")
        print(f"  - CSV:  {csv_filepath}")
        print(f"  - HTML: {html_filepath}")
        if planet_fit_files:
            print(f"  - Planet Fit CSVs: {len(planet_fit_files)}")
            print("    Format: HD102365_DTU-Padova-PSU_emcee_<fit_type>_<config>_planetFit.csv")
        if dir_file:
            print(f"  - Best-directory list: {dir_file}")
        print("Notes:")
        print("  - Preferred_BIC=True → lowest BIC in that configuration.")
        print("  - Convergence % = fraction of parameters with GR < 1.1.")
        print("  - Planet Fit CSVs use t0 reference_epoch=59334.700184.")
        print(f"{'='*80}\n")


def main():
    """
    Main function to run the HD102365 emcee analyzer.

    Usage:
        python compare_emcee_models_HD102365.py [directory] [fit_type]

    directory: root folder containing emcee logs
    fit_type:  'multiple' (default) or 'single'
    """
    if len(sys.argv) > 1:
        search_directory = sys.argv[1]
    else:
        search_directory = "."

    fit_type = "multiple"
    if len(sys.argv) > 2:
        fit_type_arg = sys.argv[2].lower()
        if fit_type_arg in ['multiple', 'single']:
            fit_type = fit_type_arg
        else:
            print(f"Warning: Invalid fit_type '{sys.argv[2]}'. Using default 'multiple'.")

    if not os.path.isdir(search_directory):
        print(f"Error: Directory '{search_directory}' does not exist.")
        sys.exit(1)

    print(f"Searching for emcee log files in: {os.path.abspath(search_directory)}\n")

    all_log_files = glob.glob(os.path.join(search_directory, '**/*.log'), recursive=True)

    # Only emcee HD102365 logs
    all_log_files = [
        f for f in all_log_files
        if os.path.basename(f).startswith('configuration_file_emcee_run_')
        and 'HD102365' in os.path.basename(f)
    ]

    file_groups = {}
    for log_file in all_log_files:
        basename = os.path.basename(log_file)
        file_groups.setdefault(basename, []).append(log_file)

    log_files = []
    for basename, files in file_groups.items():
        if len(files) == 1:
            log_files.append(files[0])
        else:
            best_file = min(files, key=lambda f: f.count(os.sep))
            log_files.append(best_file)
            print(f"Note: Found {len(files)} copies of '{basename}', using: {best_file}")

    if not log_files:
        print("No emcee log files found matching 'configuration_file_emcee_run_HD102365_*.log'")
        sys.exit(1)

    print(f"\nFound {len(log_files)} unique emcee log files to analyze (filtered from {len(all_log_files)} total).")
    print(f"Using fit_type: {fit_type}\n")

    analyze_and_display(log_files, search_directory=search_directory, fit_type=fit_type)


if __name__ == "__main__":
    main()
