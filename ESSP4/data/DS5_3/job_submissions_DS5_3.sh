#!/bin/sh 
### General options 
### -- specify queue -- 
#BSUB -q hpc
### -- set the job Name -- 
#BSUB -J DS5_iara
### -- ask for number of cores (default: 1) -- 
#BSUB -n 16
### -- specify that the cores must be on the same host -- 
#BSUB -R "span[hosts=1]"
### -- specify that we need 4GB of memory per core/slot -- 
#BSUB -R "rusage[mem=4GB]"
### -- specify that we want the job to get killed if it exceeds 5 GB per core/slot -- 
#BSUB -M 5GB
### -- set walltime limit: hh:mm -- 
#BSUB -W 24:00 
### -- set the email address -- 
# please uncomment the following line and put in your e-mail address,
# if you want to receive e-mail notifications on a non-default address
#BSUB -u icogo@dtu.dk
### -- send notification at start -- 
#BSUB -B 
### -- send notification at completion -- 
#BSUB -N 
### -- Specify the output and error file. %J is the job-id -- 
### -- -o and -e mean append, -oo and -eo mean overwrite -- 
#BSUB -o Output_DS5_3.out 

cd /work2/lbuc/iara/GitHub/PyORBIT_examples/ESSP4/data/DS5_3

rm -f configuration_file_emcee_run_DS5_3.log Output_DS5_3.out

source /work2/lbuc/iara/anaconda3/etc/profile.d/conda.sh
conda activate pyorbit

pyorbit_run emcee DS5_3.yaml  >  configuration_file_emcee_run_DS5_3.log
pyorbit_results emcee DS5_3.yaml -all >> configuration_file_emcee_run_DS5_3.log

cp DS5_3.yaml ./DS5_3
cp configuration_file_emcee_run_DS5_3.log ./DS5_3

conda deactivate