#!/bin/sh 
### General options 
### -- specify queue -- 
#BSUB -q hpc
### -- set the job Name -- 
#BSUB -J DS6_3p_CCFs
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
# #BSUB -u 
### -- send notification at start -- 
# #BSUB -B 
### -- send notification at completion -- 
# #BSUB -N 
### -- Specify the output and error file. %J is the job-id -- 
#BSUB -o Output_DS6_3p_CCFs.out 

# Change to activity directory
cd ../data/DS6/DS6_3p/DS6_3p_CCFs

# Clean up previous runs
rm -f configuration_file_emcee_run_DS6_3p_CCFs.log Output_DS6_3p_CCFs.out

# Activate PyORBIT environment
source /work2/lbuc/iara/anaconda3/etc/profile.d/conda.sh
conda activate pyorbit

# Run PyORBIT analysis
pyorbit_run emcee DS6_3p_CCFs.yaml > configuration_file_emcee_run_DS6_3p_CCFs.log
pyorbit_results emcee DS6_3p_CCFs.yaml -all >> configuration_file_emcee_run_DS6_3p_CCFs.log

# Create results directory and copy files
mkdir -p ./DS6_3p_CCFs
cp DS6_3p_CCFs.yaml ./DS6_3p_CCFs/
cp configuration_file_emcee_run_DS6_3p_CCFs.log ./DS6_3p_CCFs/

# Deactivate environment
conda deactivate

echo "Job DS6_3p_CCFs completed at: $(date)"
