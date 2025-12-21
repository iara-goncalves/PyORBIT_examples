#!/usr/bin/env python3
"""
PyORBIT dynesty model comparison for HD102365 using Bayesian evidence (logZ).

Usage:
    python compare_dynesty_models_HD102365.py [search_directory]

Example:
    python compare_dynesty_models_HD102365.py ../results_HD102365
"""

import re
import os
import sys
import glob
import pandas as pd
import numpy as np
from datetime import datetime


# =========================
# Utility functions
# =========================

def calculate_t0_from_mean_long(mean_long_deg, omega_deg, period_days, reference_epoch=0.0):
    """
    Calculate time of periastron (t0) from mean longitude.

    Formula: t0 = t_ref - (mean_long - omega) / n, n = 2π/P.
    """
    mean_long_rad = np.deg2rad(mean_long_deg)
    omega_rad = np.deg2rad(omega_deg)
    mean_anomaly_rad = mean_long_rad - omega_rad
    n = 2.0 * np.pi / period_days
    dt = mean_anomaly_rad / n
    return reference_epoch - dt


# =========================
# Export helpers
# =========================

def export_planet_fit_csv(datasets, df, group_name="DTU-Padova-PSU_dynesty",
                          reference_epoch=59334.700184, output_dir="."):
    """
    Export Best-Fit Planet Parameters CSV files for HD102365 dynesty runs.

    Filename:
        HD102365_DTU-Padova-PSU_dynesty_<config>_planetFit.csv

    Columns:
        K [m/s], P [d], t0 [eMJD], e, w [deg]

    Selection:
        Per (Dataset, Configuration) pick the model with highest log(Z).
    """
    exported_files = []

    for dataset in datasets:
        dataset_df = df[df['Dataset'] == dataset]
        grouped = dataset_df.groupby('Configuration')

        for config_name, group in grouped:
            # best by logZ
            group = group.copy()
            group['Planets'] = pd.Categorical(
                group['Planets'],
                categories=['0p', '1p', '2p', '3p'],
                ordered=True
            )
            group = group.sort_values('Planets')
            max_logz_idx = group['log(Z)'].idxmax()
            best_model_data = group.loc[max_logz_idx]
            orbital_params = best_model_data['Orbital Parameters']

            planet_rows = []
            planets = sorted(orbital_params.keys()) if orbital_params else []

            if planets:
                for planet in planets:
                    pp = orbital_params[planet]

                    # original strings (for ESSP‑like output)
                    K_str        = pp.get('K', {}).get('value_str')
                    P_str        = pp.get('P', {}).get('value_str')
                    e_str        = pp.get('e', {}).get('value_str')
                    omega_str    = pp.get('omega', {}).get('value_str')
                    mean_long_str = pp.get('mean_long', {}).get('value_str')

                    # float copies
                    K         = pp.get('K', {}).get('value')
                    P         = pp.get('P', {}).get('value')
                    e         = pp.get('e', {}).get('value')
                    omega     = pp.get('omega', {}).get('value')
                    mean_long = pp.get('mean_long', {}).get('value')

                    if K is None or P is None:
                        continue

                    # t0 from mean longitude
                    if mean_long is not None and omega is not None:
                        t0 = calculate_t0_from_mean_long(mean_long, omega, P, reference_epoch)
                    elif mean_long is not None:
                        t0 = calculate_t0_from_mean_long(mean_long, 0.0, P, reference_epoch)
                    else:
                        t0 = None

                    if e_str is None:
                        e_str = '0' if (e is not None and e == 0.0) else (str(e) if e is not None else '')
                    if omega_str is None:
                        omega_str = '0' if (omega is not None and omega == 0.0) else (str(omega) if omega is not None else '')

                    if t0 is not None:
                        t0_str = f"{t0:.10g}"
                    else:
                        t0_str = ''

                    row = {
                        'K [m/s]': K_str if K_str is not None else (str(K) if K is not None else ''),
                        'P [d]':   P_str if P_str is not None else (str(P) if P is not None else ''),
                        't0 [eMJD]': t0_str,
                        'e': e_str,
                        'w [deg]': omega_str
                    }
                    planet_rows.append(row)

            columns = ['K [m/s]', 'P [d]', 't0 [eMJD]', 'e', 'w [deg]']
            planet_df = pd.DataFrame(planet_rows) if planet_rows else pd.DataFrame(columns=columns)

            filename = f"{dataset}_{group_name}_{config_name}_planetFit.csv"
            filepath = os.path.join(output_dir, filename)
            planet_df.to_csv(filepath, index=False, encoding='utf-8')
            exported_files.append(filepath)

            npl = len(planet_rows)
            if npl == 0:
                print(f"  Exported: {filepath} (0-planet model, headers only)")
            else:
                print(f"  Exported: {filepath} ({npl} planet(s))")

    return exported_files


def export_best_model_directories(datasets, df, output_filename=None, output_dir="."):
    """
    Export directory names where best models (highest log(Z)) were found.
    """
    directory_names = []

    for dataset in datasets:
        dsub = df[df['Dataset'] == dataset]
        grouped = dsub.groupby('Configuration')

        for config_name, group in grouped:
            group = group.copy()
            group['Planets'] = pd.Categorical(
                group['Planets'],
                categories=['0p', '1p', '2p', '3p'],
                ordered=True
            )
            group = group.sort_values('Planets')
            max_logz_idx = group['log(Z)'].idxmax()
            best_model = group.loc[max_logz_idx]
            directory_names.append(best_model.get('Directory', ''))

    if not directory_names:
        return None

    dir_df = pd.DataFrame({'Directory': directory_names})
    if output_filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"best_model_directories_dynesty_{timestamp}.csv"
    else:
        filename = output_filename

    filepath = os.path.join(output_dir, filename)
    dir_df.to_csv(filepath, index=False, encoding='utf-8')
    print(f"  Exported: {filepath} ({len(directory_names)} directory name(s))")
    return filepath


# =========================
# Parsing dynesty logs (HD102365‑specific naming)
# =========================

def parse_dynesty_log_file(filepath):
    """
    Parse a PyORBIT dynesty log file (HD102365) to extract logZ, BIC, efficiency, and parameters.

    Expected filename pattern:
        configuration_file_dynesty_run_HD102365_<CONFIG>.log

    Returns a dict or None.
    """
    logz = None
    logz_err = None
    median_bic = None
    efficiency = None
    ncall = None
    niter = None
    orbital_parameters = {}
    activity_parameters = {}

    try:
        with open(filepath, 'r') as f:
            content = f.read()

        # log-evidence
        m = re.search(r'logz:\s*(-?[\d\.]+)\s*\+/-\s*([\d\.]+)', content)
        if m:
            logz = float(m.group(1))
            logz_err = float(m.group(2))

        # Median BIC
        m = re.search(r'Median BIC\s+\(using likelihood\)\s*=\s*(-?[\d\.]+)', content)
        if m:
            median_bic = float(m.group(1))

        # efficiency, ncall, niter
        m = re.search(r'eff\(%\):\s*([\d\.]+)', content)
        if m:
            efficiency = float(m.group(1))

        m = re.search(r'ncall:\s*(\d+)', content)
        if m:
            ncall = int(m.group(1))

        m = re.search(r'niter:\s*(\d+)', content)
        if m:
            niter = int(m.group(1))

        # Parameters: FIRST "Statistics on the model parameters" section
        lines = content.split('\n')
        first_stats_idx = -1
        for i, line in enumerate(lines):
            if "Statistics on the model parameters obtained from the posteriors samples" in line:
                first_stats_idx = i
                break

        if first_stats_idx != -1:
            current_planet = None
            in_activity_section = False

            for line in lines[first_stats_idx:]:
                if "Statistics on the derived parameters" in line or "Parameters corresponding to" in line:
                    break

                planet_match = re.search(r'----- common model:\s+([a-z])\s*$', line)
                if planet_match:
                    current_planet = planet_match.group(1)
                    in_activity_section = False
                    if current_planet not in orbital_parameters:
                        orbital_parameters[current_planet] = {}
                    continue

                if "----- common model:  activity" in line:
                    in_activity_section = True
                    current_planet = None
                    continue

                param_match = re.match(
                    r'^([A-Za-z_]+)\s+([-\d\.]+)\s+([-\d\.]+)\s+([\d\.]+).*\(15-84 p\)',
                    line.strip()
                )
                if param_match:
                    name = param_match.group(1)
                    median_str = param_match.group(2).strip()
                    low_str = param_match.group(3).strip()
                    up_str = param_match.group(4).strip()

                    median_val = float(median_str)
                    low_val = float(low_str)
                    up_val = float(up_str)

                    target = activity_parameters if in_activity_section else \
                             orbital_parameters.setdefault(current_planet, {})

                    target[name] = {
                        'value': median_val,
                        'value_str': median_str,
                        'lower_error': low_val,
                        'lower_error_str': low_str,
                        'upper_error': up_val,
                        'upper_error_str': up_str
                    }

    except FileNotFoundError:
        print(f"Error: File not found at {filepath}")
        return None
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return None

    if logz is None:
        return None

    basename = os.path.basename(filepath)
    # strip prefix/suffix
    cleaned = basename.replace('configuration_file_dynesty_run_', '').replace('.log', '')

    # HD102365_<CONFIG>
    if cleaned.startswith('HD102365_'):
        dataset = 'HD102365'
        config_name = cleaned[len('HD102365_'):]
    else:
        dataset = 'Unknown'
        config_name = cleaned

    # planets from config suffix: ..._0p_dynesty / _1p_dynesty / etc.
    pm = re.search(r'_(\dp)_dynesty', config_name)
    if pm:
        num_planets = pm.group(1)
    else:
        num_planets = 'N/A'

    directory_name = os.path.dirname(os.path.abspath(filepath))

    return {
        'Configuration': config_name,
        'Dataset': dataset,
        'Planets': num_planets,
        'log(Z)': logz,
        'log(Z) error': logz_err,
        'Median BIC': median_bic,
        'Efficiency %': efficiency,
        'N calls': ncall,
        'N iter': niter,
        'Orbital Parameters': orbital_parameters,
        'Activity Parameters': activity_parameters,
        'File': basename,
        'Directory': directory_name
    }


# =========================
# Main analysis
# =========================

def analyze_and_display_dynesty(log_files, search_directory=None):
    """
    Analyze HD102365 dynesty log files, print Bayesian comparison,
    and export CSV/HTML/planet‑fit/best‑dir outputs.
    """
    # Output directory: based on search_directory basename
    output_dir = "."
    if search_directory:
        folder_name = os.path.basename(os.path.normpath(search_directory))
        output_dir = folder_name
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            print(f"Created output directory: {output_dir}\n")

    all_data = []
    failed = []

    print(f"Processing {len(log_files)} dynesty log files...")
    for lf in log_files:
        d = parse_dynesty_log_file(lf)
        if d:
            all_data.append(d)
        else:
            failed.append(lf)

    if failed:
        print(f"\nWarning: {len(failed)} files could not be parsed (missing logZ or wrong format):")
        for f in failed:
            print("  -", f)
        print()

    if not all_data:
        print("No usable dynesty log files.")
        return

    df = pd.DataFrame(all_data)
    datasets = sorted(df['Dataset'].unique())

    print("=" * 100)
    print("HD102365 – DYNESTY MODEL COMPARISON (Bayesian evidence)")
    print("=" * 100)
    print("\nInterpretation:")
    print("  Δlog(Z) > 5   → Decisive evidence")
    print("  Δlog(Z) > 2.5 → Strong evidence")
    print("  Δlog(Z) > 1   → Moderate evidence")
    print("  Δlog(Z) < 1   → Weak / inconclusive")
    print("  Lower BIC is better; ΔBIC > 10 is strong.")
    print("=" * 100)

    export_groups = []

    for dataset in datasets:
        dsub = df[df['Dataset'] == dataset]
        grouped = dsub.groupby('Configuration')

        print(f"\n{'='*100}")
        print(f"DATASET: {dataset}")
        print(f"{'='*100}\n")

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

            max_logz_idx = group['log(Z)'].idxmax()
            max_logz_value = group.loc[max_logz_idx, 'log(Z)']

            min_bic_idx = group['Median BIC'].idxmin()
            min_bic_value = group.loc[min_bic_idx, 'Median BIC']

            display = group[['Planets', 'log(Z)', 'log(Z) error',
                             'Median BIC', 'Efficiency %', 'N calls']].copy()
            display['Δlog(Z)'] = group['log(Z)'] - max_logz_value
            display['ΔBIC'] = group['Median BIC'] - min_bic_value
            display['Bayes Factor'] = display['Δlog(Z)'].apply(lambda x: f"{np.exp(x):.2e}")

            group_copy = group.copy()
            group_copy['Preferred_logZ'] = group_copy.index == max_logz_idx
            group_copy['Preferred_BIC'] = group_copy.index == min_bic_idx
            group_copy['Δlog(Z)'] = group_copy['log(Z)'] - max_logz_value
            group_copy['ΔBIC'] = group_copy['Median BIC'] - min_bic_value
            group_copy['Dataset'] = dataset
            group_copy['Configuration'] = config_name

            export_group = group_copy[['Dataset', 'Configuration', 'Planets',
                                       'log(Z)', 'log(Z) error', 'Δlog(Z)',
                                       'Median BIC', 'ΔBIC',
                                       'Efficiency %', 'N calls', 'N iter',
                                       'Preferred_logZ', 'Preferred_BIC',
                                       'File', 'Directory']]
            export_groups.append(export_group)

            print(display[['Planets', 'log(Z)', 'Δlog(Z)',
                           'Median BIC', 'ΔBIC', 'Efficiency %']].to_string(index=False))

            print(f"\nBest by log(Z): {group.loc[max_logz_idx, 'Planets']} "
                  f"(log(Z) = {max_logz_value:.2f} ± {group.loc[max_logz_idx, 'log(Z) error']:.2f})")
            print(f"Best by BIC:    {group.loc[min_bic_idx, 'Planets']} "
                  f"(BIC = {min_bic_value:.2f})")

            if len(group) > 1:
                print("\nEvidence vs best model:")
                for idx, row in group.iterrows():
                    if idx == max_logz_idx:
                        continue
                    delta_logz = row['log(Z)'] - max_logz_value
                    bf = np.exp(-delta_logz)
                    if delta_logz > -1.0:
                        strength = "Weak"
                    elif delta_logz > -2.5:
                        strength = "Moderate"
                    elif delta_logz > -5.0:
                        strength = "Strong"
                    else:
                        strength = "Decisive"
                    print(f"  {row['Planets']} vs {group.loc[max_logz_idx, 'Planets']}: "
                          f"Δlog(Z) = {delta_logz:.2f}, BF = {bf:.2e} → {strength}")

            print("\n" + "-"*100 + "\n")

            best_models_info.append({
                'Configuration': config_name,
                'Best Model': group.loc[max_logz_idx, 'Planets'],
                'log(Z)': max_logz_value,
                'BIC': group.loc[max_logz_idx, 'Median BIC'],
                'Orbital Parameters': group.loc[max_logz_idx, 'Orbital Parameters'],
                'Activity Parameters': group.loc[max_logz_idx, 'Activity Parameters']
            })

        # parameter summary tables to stdout (like your generic script)
        if best_models_info:
            print(f"\n{'='*140}")
            print(f"PARAMETERS SUMMARY FOR {dataset} (best by log(Z))")
            print(f"{'='*140}\n")

            print("TABLE 1: ORBITAL PARAMETERS\n")
            print(f"{'Config':<22} {'Model':<6} {'Planet':<8} "
                  f"{'P (days)':<12} {'K (m/s)':<10} {'mean_long (°)':<14} "
                  f"{'e':<10} {'ω (deg)':<10}")
            print("-" * 140)

            for info in best_models_info:
                cfg = info['Configuration']
                model = info['Best Model']
                op = info['Orbital Parameters']
                planets = sorted(op.keys()) if op else []

                if not planets:
                    print(f"{cfg:<22} {model:<6} {'-':<8} "
                          f"{'-':<12} {'-':<10} {'-':<14} {'-':<10} {'-':<10}")
                else:
                    for p in planets:
                        pp = op[p]
                        P_str = pp.get('P', {}).get('value_str', '-') if 'P' in pp else '-'
                        K_str = pp.get('K', {}).get('value_str', '-') if 'K' in pp else '-'
                        ml_str = pp.get('mean_long', {}).get('value_str', '-') if 'mean_long' in pp else '-'
                        e_str = pp.get('e', {}).get('value_str', '-') if 'e' in pp else '-'
                        w_str = pp.get('omega', {}).get('value_str', '-') if 'omega' in pp else '-'

                        print(f"{cfg:<22} {model:<6} {p:<8} "
                              f"{P_str:<12} {K_str:<10} {ml_str:<14} "
                              f"{e_str:<10} {w_str:<10}")

            print("\nTABLE 2: ACTIVITY PARAMETERS\n")
            print(f"{'Config':<22} {'Model':<6} "
                  f"{'Prot (days)':<15} {'Pdec (days)':<15} {'Oamp':<10}")
            print("-" * 80)

            for info in best_models_info:
                cfg = info['Configuration']
                model = info['Best Model']
                ap = info['Activity Parameters']

                Prot_str = ap.get('Prot', {}).get('value_str', '-') if 'Prot' in ap else '-'
                Pdec_str = ap.get('Pdec', {}).get('value_str', '-') if 'Pdec' in ap else '-'
                Oamp_str = ap.get('Oamp', {}).get('value_str', '-') if 'Oamp' in ap else '-'

                print(f"{cfg:<22} {model:<6} "
                      f"{Prot_str:<15} {Pdec_str:<15} {Oamp_str:<10}")

            print("\n" + "="*140 + "\n")

    # ========= CSV + HTML export =========
    if export_groups:
        combined = pd.concat(export_groups, ignore_index=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_name = f"HD102365_dynesty_model_comparison_{timestamp}.csv"
        csv_path = os.path.join(output_dir, csv_name)
        combined.to_csv(csv_path, index=False, encoding='utf-8')
        print(f"Exported Bayesian comparison CSV: {csv_path}")

        # Simple HTML wrapper pointing to CSV (you already have a fancy HTML from generic script;
        # here we keep it minimal to avoid duplication)
        html_name = f"HD102365_dynesty_model_comparison_{timestamp}.html"
        html_path = os.path.join(output_dir, html_name)
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8">
<title>HD102365 dynesty model comparison</title></head>
<body>
<h1>HD102365 dynesty model comparison</h1>
<p>See CSV file <code>{os.path.basename(csv_name)}</code> for full log(Z) / BIC table.</p>
</body></html>""")
        print(f"Exported HTML pointer:         {html_path}")

        print("\nExporting planet‑fit CSVs (best logZ per configuration)...")
        planet_files = export_planet_fit_csv(datasets, df,
                                             group_name="DTU-Padova-PSU_dynesty",
                                             reference_epoch=59334.700184,
                                             output_dir=output_dir)

        print("\nExporting best‑model directory list...")
        if search_directory:
            folder_name = os.path.basename(os.path.normpath(search_directory))
            out_name = f"{folder_name}_dynesty_best_dirs.csv"
        else:
            out_name = None
        dir_file = export_best_model_directories(datasets, df,
                                                 output_filename=out_name,
                                                 output_dir=output_dir)

        print("\nDone.")
        print("  Preferred_logZ = True → highest evidence model within that configuration.")
        print("  Preferred_BIC  = True → lowest BIC within that configuration.")
        if planet_files:
            print(f"  Planet‑fit files: {len(planet_files)}")
        if dir_file:
            print(f"  Best‑dir file:   {dir_file}")


# =========================
# CLI entry point
# =========================

if __name__ == "__main__":
    if len(sys.argv) > 1:
        search_directory = sys.argv[1]
    else:
        search_directory = "."

    if not os.path.isdir(search_directory):
        print(f"Error: Directory '{search_directory}' does not exist or is not a directory.")
        sys.exit(1)

    print(f"Searching for dynesty log files in: {os.path.abspath(search_directory)}")
    all_logs = glob.glob(os.path.join(search_directory, "**/*.log"), recursive=True)

    # Keep only dynesty HD102365 logs
    all_logs = [
        f for f in all_logs
        if os.path.basename(f).startswith("configuration_file_dynesty_run_")
        and "HD102365" in os.path.basename(f)
    ]

    if not all_logs:
        print("No matching dynesty HD102365 log files found.")
        sys.exit(1)

    # Deduplicate by basename, prefer shallower path
    groups = {}
    for lf in all_logs:
        base = os.path.basename(lf)
        groups.setdefault(base, []).append(lf)

    log_files = []
    for base, files in groups.items():
        best = min(files, key=lambda p: p.count(os.sep))
        log_files.append(best)

    print(f"Found {len(log_files)} unique dynesty log files.\n")
    analyze_and_display_dynesty(log_files, search_directory=search_directory)
