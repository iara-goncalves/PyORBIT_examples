#!/bin/sh 
### General options 
### -- specify queue -- 
#BSUB -q hpc
### -- set the job Name -- 
#BSUB -J HD102365_submission3p
### -- ask for number of cores (default: 1) -- 
#BSUB -n 48
### -- specify that the cores must be on the same host -- 
#BSUB -R "span[hosts=1]"
### -- specify that we need 1GB of memory per core/slot -- 
#BSUB -R "rusage[mem=8GB]"
### -- specify that we want the job to get killed if it exceeds 2GB per core/slot -- 
#BSUB -M 8GB
### -- set walltime limit: hh:mm -- 
#BSUB -W 72:00
### -- set the email address -- 
#BSUB -u jzhao@space.dtu.dk
### -- send notification at start -- 
#BSUB -B 
### -- send notification at completion -- 
#BSUB -N 
### -- Specify the output and error file. %J is the job-id -- 
#BSUB -o /work2/lbuc/iara/GitHub/PyORBIT_examples/HD102365/Output_submission3.out

# Change to configuration directory
cd /work2/lbuc/iara/GitHub/PyORBIT_examples/HD102365

# Clean up previous runs
rm -f configuration_file_dynesty_run_submission3.log

# Activate PyORBIT environment
source /work2/lbuc/iara/anaconda3/etc/profile.d/conda.sh
conda activate pyorbit

# Run PyORBIT analysis
pyorbit_run dynesty submission3.yaml > configuration_file_dynesty_run_submission3.log
pyorbit_results dynesty submission3.yaml -all >> configuration_file_dynesty_run_submission3.log

# Deactivate environment
conda deactivate

echo "Job submission3 HD102365 completed at: $(date)"
