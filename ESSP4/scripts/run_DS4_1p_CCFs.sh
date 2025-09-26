#!/bin/sh 
### General options 
### -- specify queue -- 
#BSUB -q hpc
### -- set the job Name -- 
#BSUB -J DS4_1p_CCFs
### -- ask for number of cores (default: 1) -- 
#BSUB -n 1
### -- specify that the cores must be on the same host -- 
#BSUB -R "span[hosts=1]"
### -- specify that we need 3GB of memory per core/slot -- 
#BSUB -R "rusage[mem=3GB]"
### -- specify that we want the job to get killed if it exceeds 4GB per core/slot -- 
#BSUB -M 4GB
### -- set walltime limit: hh:mm -- 
#BSUB -W 8:00
### -- set the email address -- 
#BSUB -u icogo@dtu.dk
### -- send notification at start -- 
#BSUB -B 
### -- send notification at completion -- 
#BSUB -N 
### -- Specify the output and error file. %J is the job-id -- 
#BSUB -o ./out/Output_DS4_1p_CCFs.out 

# Change to activity directory
cd ../data/DS4/DS4_1p/DS4_1p_CCFs

# Clean up previous runs
rm -f configuration_file_emcee_run_DS4_1p_CCFs.log Output_DS4_1p_CCFs.out

# Activate PyORBIT environment
source /work2/lbuc/iara/anaconda3/etc/profile.d/conda.sh
conda activate pyorbit

# Run PyORBIT analysis
pyorbit_run emcee DS4_1p_CCFs.yaml > configuration_file_emcee_run_DS4_1p_CCFs.log
pyorbit_results emcee DS4_1p_CCFs.yaml -all >> configuration_file_emcee_run_DS4_1p_CCFs.log

# Create results directory and copy files
mkdir -p ./DS4_1p_CCFs
cp DS4_1p_CCFs.yaml ./DS4_1p_CCFs/
cp configuration_file_emcee_run_DS4_1p_CCFs.log ./DS4_1p_CCFs/

# Deactivate environment
conda deactivate

echo "Job DS4_1p_CCFs completed at: $(date)"
