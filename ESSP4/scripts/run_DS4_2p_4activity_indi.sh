#!/bin/sh 
### General options 
### -- specify queue -- 
#BSUB -q hpc
### -- set the job Name -- 
#BSUB -J DS4_2p_4activity_indi
### -- ask for number of cores (default: 1) -- 
#BSUB -n 16
### -- specify that the cores must be on the same host -- 
#BSUB -R "span[hosts=1]"
### -- specify that we need 4GB of memory per core/slot -- 
#BSUB -R "rusage[mem=4GB]"
### -- specify that we want the job to get killed if it exceeds 5GB per core/slot -- 
#BSUB -M 5GB
### -- set walltime limit: hh:mm -- 
#BSUB -W 24:00
### -- set the email address -- 
#BSUB -u icogo@dtu.dk
### -- send notification at start -- 
#BSUB -B 
### -- send notification at completion -- 
#BSUB -N 
### -- Specify the output and error file. %J is the job-id -- 
#BSUB -o Output_DS4_2p_4activity_indi.out 

# Change to activity directory
cd ../data/DS4/DS4_2p/DS4_2p_4activity_indi

# Clean up previous runs
rm -f configuration_file_emcee_run_DS4_2p_4activity_indi.log Output_DS4_2p_4activity_indi.out

# Activate PyORBIT environment
source /work2/lbuc/iara/anaconda3/etc/profile.d/conda.sh
conda activate pyorbit

# Run PyORBIT analysis
pyorbit_run emcee DS4_2p_4activity_indi.yaml > configuration_file_emcee_run_DS4_2p_4activity_indi.log
pyorbit_results emcee DS4_2p_4activity_indi.yaml -all >> configuration_file_emcee_run_DS4_2p_4activity_indi.log

# Create results directory and copy files
mkdir -p ./DS4_2p_4activity_indi
cp DS4_2p_4activity_indi.yaml ./DS4_2p_4activity_indi/
cp configuration_file_emcee_run_DS4_2p_4activity_indi.log ./DS4_2p_4activity_indi/

# Deactivate environment
conda deactivate

echo "Job DS4_2p_4activity_indi completed at: $(date)"
