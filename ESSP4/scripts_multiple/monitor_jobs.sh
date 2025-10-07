#!/bin/bash

echo "PyORBIT Job Monitor (Multi-Instrument)"
echo "======================================="

echo "All your jobs:"
bjobs

echo ""
echo "PyORBIT jobs (multi-instrument, 4 activity indicators):"
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
echo "Jobs by dataset:"
for ds in DS1 DS2 DS3 DS4 DS5 DS6 DS7 DS8 DS9; do
    ds_count=$(bjobs | grep -c -E "(${ds}_[1-3]p_4activity_indi)")
    if [ $ds_count -gt 0 ]; then
        echo "  $ds: $ds_count jobs"
    fi
done

echo ""
echo "Jobs by planet configuration:"
for planet in 1p 2p 3p; do
    planet_count=$(bjobs | grep -c -E "(DS[1-9]_${planet}_4activity_indi)")
    if [ $planet_count -gt 0 ]; then
        echo "  $planet: $planet_count jobs"
    fi
done

echo ""
echo "Refresh with: ./monitor_jobs.sh"
echo "Detailed job info: bjobs -l JOB_ID"
