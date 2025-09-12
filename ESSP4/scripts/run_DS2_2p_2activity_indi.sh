#!/bin/sh 
### General options 
### -- specify queue -- 
#BSUB -q hpc
### -- set the job Name -- 
#BSUB -J DS2_2p_2activity_indi
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
#BSUB -o Output_DS2_2p_2activity_indi.out 

# Change to activity directory
cd ../data/DS2/DS2_2p/DS2_2p_2activity_indi

# Clean up previous runs
rm -f configuration_file_emcee_run_DS2_2p_2activity_indi.log Output_DS2_2p_2activity_indi.out

# Activate PyORBIT environment
source /work2/lbuc/iara/anaconda3/etc/profile.d/conda.sh
conda activate pyorbit

# Run PyORBIT analysis
pyorbit_run emcee DS2_2p_2activity_indi.yaml > configuration_file_emcee_run_DS2_2p_2activity_indi.log
pyorbit_results emcee DS2_2p_2activity_indi.yaml -all >> configuration_file_emcee_run_DS2_2p_2activity_indi.log

# Create results directory and copy files
mkdir -p ./DS2_2p_2activity_indi
cp DS2_2p_2activity_indi.yaml ./DS2_2p_2activity_indi/
cp configuration_file_emcee_run_DS2_2p_2activity_indi.log ./DS2_2p_2activity_indi/

# Deactivate environment
conda deactivate

echo "Job DS2_2p_2activity_indi completed at: $(date)"
