#!/bin/bash

echo "Submitting all PyORBIT jobs..."
echo "================================"

job_count=0
submitted_jobs=()

for script in run_*.sh; do
    if [ -f "$script" ]; then
        echo "Submitting: $script"
        job_id=$(bsub < "$script" | grep -oE '[0-9]+')
        if [ $? -eq 0 ]; then
            submitted_jobs+=("$job_id")
            ((job_count++))
            echo "   Job ID: $job_id"
        else
            echo "   Failed to submit: $script"
        fi
        sleep 1  # Small delay between submissions
    fi
done

echo ""
echo "Summary: $job_count jobs submitted"
echo "Job IDs: ${submitted_jobs[*]}"
echo ""
echo "Monitor with: ./monitor_jobs.sh"
