#!/bin/bash

echo "PyORBIT Job Monitor"
echo "==================="

echo "All your jobs:"
bjobs

echo ""
echo "PyORBIT jobs:"
bjobs | grep -E "(DS[1-9]_[1-3]p_(2activity|4activity|5activity|CCFs|white_noise))"

echo ""
echo "Job summary:"
total_jobs=$(bjobs | grep -c -E "(DS[1-9]_[1-3]p_(2activity|4activity|5activity|CCFs|white_noise))")
running_jobs=$(bjobs | grep RUN | grep -c -E "(DS[1-9]_[1-3]p_(2activity|4activity|5activity|CCFs|white_noise))")
pending_jobs=$(bjobs | grep PEND | grep -c -E "(DS[1-9]_[1-3]p_(2activity|4activity|5activity|CCFs|white_noise))")

echo "Total PyORBIT jobs: $total_jobs"
echo "Running: $running_jobs"
echo "Pending: $pending_jobs"

echo ""
echo "White noise jobs:"
bjobs | grep -E "(DS[1-9]_[1-3]p_white_noise)"

echo ""
echo "Activity indicator jobs:"
bjobs | grep -E "(DS[1-9]_[1-3]p_(2activity|4activity|5activity|CCFs))"

echo ""
echo "Refresh with: ./monitor_jobs.sh"
echo "Detailed job info: bjobs -l JOB_ID"
