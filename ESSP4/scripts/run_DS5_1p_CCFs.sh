#!/bin/sh 
### General options 
### -- specify queue -- 
#BSUB -q hpc
### -- set the job Name -- 
#BSUB -J DS5_1p_CCFs
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
#BSUB -u icogo@dtu.dk
### -- send notification at start -- 
#BSUB -B 
### -- send notification at completion -- 
#BSUB -N 
### -- Specify the output and error file. %J is the job-id -- 
#BSUB -o ../out/Output_DS5_1p_CCFs.out

# Change to activity directory
cd ../data/DS5/DS5_1p/DS5_1p_CCFs

# Clean up previous runs
rm -f configuration_file_emcee_run_DS5_1p_CCFs.log Output_DS5_1p_CCFs.out

# Activate PyORBIT environment
source /work2/lbuc/iara/anaconda3/etc/profile.d/conda.sh
conda activate pyorbit

# Run PyORBIT analysis
pyorbit_run emcee DS5_1p_CCFs.yaml > configuration_file_emcee_run_DS5_1p_CCFs.log
pyorbit_results emcee DS5_1p_CCFs.yaml -all >> configuration_file_emcee_run_DS5_1p_CCFs.log

# Create results directory and copy files
mkdir -p ./DS5_1p_CCFs
cp DS5_1p_CCFs.yaml ./DS5_1p_CCFs/
cp configuration_file_emcee_run_DS5_1p_CCFs.log ./DS5_1p_CCFs/

# Deactivate environment
conda deactivate

echo "Job DS5_1p_CCFs completed at: $(date)"
