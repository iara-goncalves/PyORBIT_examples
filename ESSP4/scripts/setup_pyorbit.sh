#!/bin/bash

# PyORBIT Complete Setup Generator
# Creates directory structure, YAML configs, and job scripts
# Structure: ESSP4/scripts/ (this script) and ESSP4/data/ (data files)

# Define arrays
datasets=(DS1 DS2 DS3 DS4 DS5 DS6 DS7 DS8 DS9)
planets=(1p 2p 3p)
activities=(4activity_indi)  # Only one activity configuration

# Base directory - pointing from scripts/ to data/
base_dir="../data"

# LSF configuration
queue="hpc"
cores=16
mem_per_core="1GB"
mem_limit="2GB"
walltime="24:00"
email="icogo@dtu.dk"

echo "PyORBIT Complete Setup Generator"
echo "=================================="
echo "Datasets: ${#datasets[@]} (DS1-DS9)"
echo "Planets: ${#planets[@]} (1p, 2p, 3p)"
echo "Activities: 4 indicators (FWHM, Contrast, BIS, Halpha)"
echo "Base directory: $base_dir"
echo ""

# Counter for generated files
script_count=0
yaml_count=0
total_combinations=$((${#datasets[@]} * ${#planets[@]} * ${#activities[@]}))

echo "Creating complete directory structure and files..."
echo "Total combinations: $total_combinations"
echo ""

# Generate complete structure
for dataset in "${datasets[@]}"; do
    # Create main dataset directory (e.g., DS5/)
    dataset_dir="${base_dir}/${dataset}"
    mkdir -p "$dataset_dir"
    echo "Created main directory: $dataset_dir"
    
    for planet in "${planets[@]}"; do
        # Create planet directory inside dataset (e.g., DS5/DS5_1p)
        planet_dir="${dataset_dir}/${dataset}_${planet}"
        mkdir -p "$planet_dir"
        echo "  Created planet directory: $planet_dir"
        
        for activity in "${activities[@]}"; do
            # Create activity subdirectory (e.g., DS5/DS5_1p/DS5_1p_4activity_indi)
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
  RVdata:
    file: ../../../${dataset}_RV.dat
    kind: RV
    models:
      - radial_velocities
      - gp_multidimensional
EOF

            # Add activity indicator inputs
            for indicator in "${activity_indicators[@]}"; do
                cat >> "$yaml_file" << EOF
  ${indicator}data:
    file: ../../../${dataset}_${indicator}.dat
    kind: ${indicator}
    models:
      - gp_multidimensional
EOF
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
    RVdata:
      boundaries:
        rot_amp: [0.0, 10.0] #at least one must be positive definite
        con_amp: [-20.0, 20.0]
      derivative: True
EOF

            # Add activity indicator configurations for GP model
            for indicator in "${activity_indicators[@]}"; do
                cat >> "$yaml_file" << EOF
    ${indicator}data:
      boundaries:
        rot_amp: [-10.0, 10.0]
        con_amp: [-20.0, 20.0]
      derivative: True
EOF
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
#BSUB -o ../out/Output_${job_name}.out

# Change to activity directory
cd ${activity_dir}

# Clean up previous runs
rm -f configuration_file_emcee_run_${job_name}.log Output_${job_name}.out

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

echo "Submitting all PyORBIT jobs..."
echo "================================"

job_count=0
submitted_jobs=()

for script in run_*.sh; do
    if [ -f "$script" ]; then
        echo "Submitting: $script"
        job_id=$(bsub < "$script" | grep -oE '[0-9]+')
        if [ $? -eq 0 ]; then
            submitted_jobs+=("$job_id")
            ((job_count++))
            echo "   Job ID: $job_id"
        else
            echo "   Failed to submit: $script"
        fi
        sleep 1  # Small delay between submissions
    fi
done

echo ""
echo "Summary: $job_count jobs submitted"
echo "Job IDs: ${submitted_jobs[*]}"
echo ""
echo "Monitor with: ./monitor_jobs.sh"
EOF

cat > "monitor_jobs.sh" << 'EOF'
#!/bin/bash

echo "PyORBIT Job Monitor"
echo "==================="

echo "All your jobs:"
bjobs

echo ""
echo "PyORBIT jobs (4 activity indicators):"
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
echo "Refresh with: ./monitor_jobs.sh"
echo "Detailed job info: bjobs -l JOB_ID"
EOF

cat > "cancel_all_jobs.sh" << 'EOF'
#!/bin/bash

echo "Canceling all PyORBIT jobs..."
echo "============================="

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
echo "Directory structure created:"
for dataset in "${datasets[@]}"; do
    echo "  ${base_dir}/${dataset}/"
    for planet in "${planets[@]}"; do
        echo "    ├── ${dataset}_${planet}/"
        echo "    │   ├── ${dataset}_${planet}_4activity_indi/"
        echo "    │   │   └── ${dataset}_${planet}_4activity_indi.yaml"
    done
done

echo ""
echo "Configuration details:"
echo "- 4 Activity indicators: FWHM, Contrast, BIS, Halpha"
echo "- GP multidimensional model with rotation and convection"
echo "- MCMC: 500k steps, 150k burn-in, 150k save, thin=150"
echo ""
echo "Next steps:"
echo "1. Review YAML configurations if needed"
echo "2. Test with one job first: bsub < run_DS1_1p_4activity_indi.sh"
echo "3. Submit all jobs: ./submit_all_jobs.sh"
echo "4. Monitor progress: ./monitor_jobs.sh"
echo ""
echo "Total jobs: 27 (9 datasets × 3 planets × 1 configuration)"
