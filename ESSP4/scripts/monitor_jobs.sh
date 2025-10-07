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
