#!/bin/sh 
### General options 
### -- specify queue -- 
#BSUB -q hpc
### -- set the job Name -- 
#BSUB -J DS7_3p_CCFs
### -- ask for number of cores (default: 1) -- 
#BSUB -n 16
### -- specify that the cores must be on the same host -- 
#BSUB -R "span[hosts=1]"
### -- specify that we need 1GB of memory per core/slot -- 
#BSUB -R "rusage[mem=1GB]"
### -- specify that we want the job to get killed if it exceeds 2GB per core/slot -- 
#BSUB -M 2GB
### -- set walltime limit: hh:mm -- 
#BSUB -W 24:00
### -- set the email address -- 
#BSUB -u 
### -- send notification at start -- 
#BSUB -B 
### -- send notification at completion -- 
#BSUB -N 
### -- Specify the output and error file. %J is the job-id -- 
#BSUB -o ../out/Output_DS7_3p_CCFs.out

# Change to activity directory
cd ../results_jz/DS7/DS7_3p/DS7_3p_CCFs

# Clean up previous runs
rm -f configuration_file_emcee_run_DS7_3p_CCFs.log Output_DS7_3p_CCFs.out

# Activate PyORBIT environment
source /zhome/9d/b/207249/anaconda3/etc/profile.d/conda.sh
conda activate pyorbit

# Run PyORBIT analysis
pyorbit_run emcee DS7_3p_CCFs.yaml > configuration_file_emcee_run_DS7_3p_CCFs.log
pyorbit_results emcee DS7_3p_CCFs.yaml -all >> configuration_file_emcee_run_DS7_3p_CCFs.log

# Create results directory and copy files
mkdir -p ./DS7_3p_CCFs
cp DS7_3p_CCFs.yaml ./DS7_3p_CCFs/
cp configuration_file_emcee_run_DS7_3p_CCFs.log ./DS7_3p_CCFs/

# Deactivate environment
conda deactivate

echo "Job DS7_3p_CCFs completed at: $(date)"
