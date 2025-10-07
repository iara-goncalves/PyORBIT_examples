#!/bin/bash

# PyORBIT Complete Setup Generator - Multi-Instrument Version
# Creates directory structure, YAML configs, and job scripts
# Structure: ESSP4/scripts/ (this script) and ESSP4/results_multiple/ (results)
# Data files: ESSP4/data/ (instrument-specific .dat files)
# Each analysis uses ALL three instruments (expres, harps, neid) simultaneously

# Define arrays
datasets=(DS1 DS2 DS3 DS4 DS5 DS6 DS7 DS8 DS9)
planets=(1p 2p 3p)
instruments=(expres harps neid)
activities=(4activity_indi)  # Only one activity configuration

# Base directories
data_dir="/work2/lbuc/iara/GitHub/PyORBIT_examples/ESSP4/data"
results_dir="/work2/lbuc/iara/GitHub/PyORBIT_examples/ESSP4/results_multiple"
out_dir="/work2/lbuc/iara/GitHub/PyORBIT_examples/ESSP4/out_multiple"

# LSF configuration
queue="hpc"
cores=16
mem_per_core="1GB"
mem_limit="2GB"
walltime="24:00"
email="icogo@dtu.dk"

echo "PyORBIT Complete Setup Generator - Multi-Instrument Version"
echo "============================================================"
echo "Datasets: ${#datasets[@]} (DS1-DS9)"
echo "Planets: ${#planets[@]} (1p, 2p, 3p)"
echo "Instruments: ALL 3 instruments per analysis (expres, harps, neid)"
echo "Activities: 4 indicators (FWHM, Contrast, BIS, Halpha)"
echo "Data directory: $data_dir"
echo "Results directory: $results_dir"
echo "Output directory: $out_dir"
echo ""

# Create base directories
mkdir -p "$results_dir"
mkdir -p "$out_dir"

# Counter for generated files
script_count=0
yaml_count=0
total_combinations=$((${#datasets[@]} * ${#planets[@]} * ${#activities[@]}))

echo "Creating complete directory structure and files..."
echo "Total combinations: $total_combinations"
echo ""

# Generate complete structure
for dataset in "${datasets[@]}"; do
    # Create main dataset directory in results_multiple
    dataset_dir="${results_dir}/${dataset}"
    mkdir -p "$dataset_dir"
    echo "Created main directory: $dataset_dir"
    
    for planet in "${planets[@]}"; do
        # Create planet directory inside dataset
        planet_dir="${dataset_dir}/${dataset}_${planet}"
        mkdir -p "$planet_dir"
        echo "  Created planet directory: $planet_dir"
        
        for activity in "${activities[@]}"; do
            # Create activity subdirectory (no instrument in name since we use all)
            activity_dir="${planet_dir}/${dataset}_${planet}_${activity}"
            mkdir -p "$activity_dir"
            echo "    Created activity directory: $activity_dir"
            
            # Generate YAML configuration file
            yaml_file="${activity_dir}/${dataset}_${planet}_${activity}.yaml"
            
            # Determine number of planets for configuration
            case $planet in
                "1p") num_planets=1 ;;
                "2p") num_planets=2 ;;
                "3p") num_planets=3 ;;
            esac
            
            # Activity indicators: FWHM, Contrast, BIS, Halpha
            activity_indicators=("FWHM" "Contrast" "BIS" "Halpha")
            
            # Generate YAML configuration
            cat > "$yaml_file" << EOF
inputs:
EOF

            # Add RV data for each instrument
            for instrument in "${instruments[@]}"; do
                cat >> "$yaml_file" << EOF
  RVdata_${instrument}:
    file: ${data_dir}/${dataset}_${instrument}_RV.dat
    kind: RV
    models:
      - radial_velocities
      - gp_multidimensional
EOF
            done

            # Add activity indicator inputs for each instrument
            for indicator in "${activity_indicators[@]}"; do
                for instrument in "${instruments[@]}"; do
                    cat >> "$yaml_file" << EOF
  ${indicator}data_${instrument}:
    file: ${data_dir}/${dataset}_${instrument}_${indicator}.dat
    kind: ${indicator}
    models:
      - gp_multidimensional
EOF
                done
            done

            # Add common section
            cat >> "$yaml_file" << EOF

common:
  planets:
EOF

            # Add planet configurations
            planet_letters=("b" "c" "d")  # Standard planet naming
            for ((p=0; p<num_planets; p++)); do
                planet_letter=${planet_letters[$p]}
                cat >> "$yaml_file" << EOF
    ${planet_letter}:
      orbit: keplerian
      parametrization: Eastman2013
      boundaries:
        P: [1.3, 100.0]
        K: [0.001, 10.0]
        e: [0.00, 0.70]
      priors:
        e: ['Gaussian', 0.00, 0.098]
EOF
            done

            # Add activity section
            cat >> "$yaml_file" << EOF
  activity:
    boundaries:
      Prot: [20.0, 35.0]
      Pdec: [30.0, 1000.0]
      Oamp: [0.01, 1.0]
    priors:
      Prot: ['Gaussian', 28.00, 0.50]
      Oamp: ['Gaussian', 0.35, 0.035]
  star:
    star_parameters:
      priors:
        mass: ['Gaussian', 1, 0.000001]
        radius: ['Gaussian', 1, 0.000001]
        density: ['Gaussian', 1, 0.000001]

models:
  radial_velocities:
    planets:
EOF

            # Add planet list for radial_velocities model
            for ((p=0; p<num_planets; p++)); do
                planet_letter=${planet_letters[$p]}
                cat >> "$yaml_file" << EOF
      - ${planet_letter}
EOF
            done

            # Add GP multidimensional model
            cat >> "$yaml_file" << EOF
  gp_multidimensional:
    model: spleaf_multidimensional_esp
    common: activity
    n_harmonics: 4
    hyperparameters_condition: True
    rotation_decay_condition: True
EOF

            # Add RV data configurations for GP model (all instruments)
            for instrument in "${instruments[@]}"; do
                cat >> "$yaml_file" << EOF
    RVdata_${instrument}:
      boundaries:
        rot_amp: [0.0, 10.0] #at least one must be positive definite
        con_amp: [-20.0, 20.0]
      derivative: True
EOF
            done

            # Add activity indicator configurations for GP model (all instruments)
            for indicator in "${activity_indicators[@]}"; do
                for instrument in "${instruments[@]}"; do
                    cat >> "$yaml_file" << EOF
    ${indicator}data_${instrument}:
      boundaries:
        rot_amp: [-10.0, 10.0]
        con_amp: [-20.0, 20.0]
      derivative: True
EOF
                done
            done

            # Add parameters and solver sections
            cat >> "$yaml_file" << EOF

parameters:
  Tref: 59334.700184
  low_ram_plot: True
  plot_split_threshold: 1000
  cpu_threads: 16

solver:
  pyde:
    ngen: 50000
    npop_mult: 4
  emcee:
    npop_mult: 4
    nsteps: 500000
    nburn: 150000
    nsave: 150000
    thin: 150
    #use_threading_pool: False
  nested_sampling:
    nlive: 1000
    sampling_efficiency: 0.30
  recenter_bounds: True
EOF

            ((yaml_count++))
            echo "      Created YAML: $yaml_file"
            
            # Generate LSF job script
            job_name="${dataset}_${planet}_${activity}"
            script_name="run_${job_name}.sh"
            
            cat > "$script_name" << EOF
#!/bin/sh 
### General options 
### -- specify queue -- 
#BSUB -q ${queue}
### -- set the job Name -- 
#BSUB -J ${job_name}
### -- ask for number of cores (default: 1) -- 
#BSUB -n ${cores}
### -- specify that the cores must be on the same host -- 
#BSUB -R "span[hosts=1]"
### -- specify that we need ${mem_per_core} of memory per core/slot -- 
#BSUB -R "rusage[mem=${mem_per_core}]"
### -- specify that we want the job to get killed if it exceeds ${mem_limit} per core/slot -- 
#BSUB -M ${mem_limit}
### -- set walltime limit: hh:mm -- 
#BSUB -W ${walltime}
### -- set the email address -- 
#BSUB -u ${email}
### -- send notification at start -- 
#BSUB -B 
### -- send notification at completion -- 
#BSUB -N 
### -- Specify the output and error file. %J is the job-id -- 
#BSUB -o ${out_dir}/Output_${job_name}.out

# Change to activity directory
cd ${activity_dir}

# Clean up previous runs
rm -f configuration_file_emcee_run_${job_name}.log

# Activate PyORBIT environment
source /work2/lbuc/iara/anaconda3/etc/profile.d/conda.sh
conda activate pyorbit

# Run PyORBIT analysis
pyorbit_run emcee ${dataset}_${planet}_${activity}.yaml > configuration_file_emcee_run_${job_name}.log
pyorbit_results emcee ${dataset}_${planet}_${activity}.yaml -all >> configuration_file_emcee_run_${job_name}.log

# Create results directory and copy files
mkdir -p ./${job_name}
cp ${dataset}_${planet}_${activity}.yaml ./${job_name}/
cp configuration_file_emcee_run_${job_name}.log ./${job_name}/

# Deactivate environment
conda deactivate

echo "Job ${job_name} completed at: \$(date)"
EOF

            chmod +x "$script_name"
            ((script_count++))
            echo "      Created job script: $script_name"
        done
        echo ""
    done
    echo ""
done

# Generate management scripts
echo "Creating job management scripts..."

cat > "submit_all_jobs.sh" << 'EOF'
#!/bin/bash

echo "Submitting all PyORBIT jobs (multi-instrument)..."
echo "=================================================="

job_count=0
submitted_jobs=()
failed_jobs=()

for script in run_*.sh; do
    if [ -f "$script" ]; then
        echo "Submitting: $script"
        output=$(bsub < "$script" 2>&1)
        job_id=$(echo "$output" | grep -oE '[0-9]+' | head -1)
        
        if [ $? -eq 0 ] && [ -n "$job_id" ]; then
            submitted_jobs+=("$job_id")
            ((job_count++))
            echo "   ✓ Job ID: $job_id"
        else
            failed_jobs+=("$script")
            echo "   ✗ Failed to submit: $script"
            echo "     Error: $output"
        fi
        sleep 1  # Small delay between submissions
    fi
done

echo ""
echo "=========================================="
echo "Submission Summary"
echo "=========================================="
echo "Successfully submitted: $job_count jobs"
echo "Failed submissions: ${#failed_jobs[@]}"

if [ ${#failed_jobs[@]} -gt 0 ]; then
    echo ""
    echo "Failed jobs:"
    for failed in "${failed_jobs[@]}"; do
        echo "  - $failed"
    done
fi

if [ $job_count -gt 0 ]; then
    echo ""
    echo "Submitted Job IDs: ${submitted_jobs[*]}"
    echo ""
    echo "Monitor with: ./monitor_jobs.sh"
    echo "Cancel all with: ./cancel_all_jobs.sh"
fi
EOF

cat > "monitor_jobs.sh" << 'EOF'
#!/bin/bash

echo "PyORBIT Job Monitor (Multi-Instrument)"
echo "======================================="

echo "All your jobs:"
bjobs

echo ""
echo "PyORBIT jobs (multi-instrument, 4 activity indicators):"
bjobs | grep -E "(DS[1-9]_[1-3]p_4activity_indi)"

echo ""
echo "Job summary:"
total_jobs=$(bjobs | grep -c -E "(DS[1-9]_[1-3]p_4activity_indi)")
running_jobs=$(bjobs | grep RUN | grep -c -E "(DS[1-9]_[1-3]p_4activity_indi)")
pending_jobs=$(bjobs | grep PEND | grep -c -E "(DS[1-9]_[1-3]p_4activity_indi)")

echo "Total PyORBIT jobs: $total_jobs"
echo "Running: $running_jobs"
echo "Pending: $pending_jobs"

echo ""
echo "Jobs by dataset:"
for ds in DS1 DS2 DS3 DS4 DS5 DS6 DS7 DS8 DS9; do
    ds_count=$(bjobs | grep -c -E "(${ds}_[1-3]p_4activity_indi)")
    if [ $ds_count -gt 0 ]; then
        echo "  $ds: $ds_count jobs"
    fi
done

echo ""
echo "Jobs by planet configuration:"
for planet in 1p 2p 3p; do
    planet_count=$(bjobs | grep -c -E "(DS[1-9]_${planet}_4activity_indi)")
    if [ $planet_count -gt 0 ]; then
        echo "  $planet: $planet_count jobs"
    fi
done

echo ""
echo "Refresh with: ./monitor_jobs.sh"
echo "Detailed job info: bjobs -l JOB_ID"
EOF

cat > "cancel_all_jobs.sh" << 'EOF'
#!/bin/bash

echo "Canceling all PyORBIT jobs (multi-instrument)..."
echo "================================================="

job_ids=$(bjobs | grep -E "(DS[1-9]_[1-3]p_4activity_indi)" | awk '{print $1}')

if [ -z "$job_ids" ]; then
    echo "No PyORBIT jobs found to cancel."
    exit 0
fi

echo "Found PyORBIT jobs to cancel:"
echo "$job_ids"
echo ""

read -p "Are you sure you want to cancel all these jobs? (y/N): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    for job_id in $job_ids; do
        echo "Canceling job: $job_id"
        bkill $job_id
    done
    echo "All PyORBIT jobs canceled."
else
    echo "Operation canceled."
fi
EOF

chmod +x submit_all_jobs.sh
chmod +x monitor_jobs.sh
chmod +x cancel_all_jobs.sh

echo "Setup Complete!"
echo "==============="
echo "Created $yaml_count YAML configuration files"
echo "Created $script_count job scripts"
echo "Created job management scripts"
echo ""
echo "Directory structure created in: $results_dir"
echo "Output files will be saved in: $out_dir"
echo ""
echo "Structure example:"
echo "  ${results_dir}/DS5/"
echo "    ├── DS5_1p/"
echo "    │   └── DS5_1p_4activity_indi/"
echo "    │       └── DS5_1p_4activity_indi.yaml"
echo "    ├── DS5_2p/"
echo "    │   └── DS5_2p_4activity_indi/"
echo "    │       └── DS5_2p_4activity_indi.yaml"
echo "    └── DS5_3p/"
echo "        └── DS5_3p_4activity_indi/"
echo "            └── DS5_3p_4activity_indi.yaml"
echo ""
echo "Configuration details:"
echo "- Data files: ALL 3 instruments used simultaneously"
echo "  * expres: DS5_expres_RV.dat, DS5_expres_FWHM.dat, etc."
echo "  * harps: DS5_harps_RV.dat, DS5_harps_FWHM.dat, etc."
echo "  * neid: DS5_neid_RV.dat, DS5_neid_FWHM.dat, etc."
echo "- 4 Activity indicators per instrument: FWHM, Contrast, BIS, Halpha"
echo "- Total: 15 datasets per analysis (3 RV + 12 activity indicators)"
echo "- GP multidimensional model with rotation and convection"
echo "- MCMC: 500k steps, 150k burn-in, 150k save, thin=150"
echo ""
echo "Next steps:"
echo "1. Review YAML configurations if needed"
echo "2. Test with one job first: bsub < run_DS1_1p_4activity_indi.sh"
echo "3. Submit all jobs: ./submit_all_jobs.sh"
echo "4. Monitor progress: ./monitor_jobs.sh"
echo ""
echo "Total jobs: 27 (9 datasets × 3 planets × 1 configuration with all instruments)"