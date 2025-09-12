#!/bin/bash

echo "Canceling all PyORBIT jobs..."
echo "============================="

job_ids=$(bjobs | grep -E "(DS[1-9]_[1-3]p_[24]activity)" | awk '{print $1}')

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