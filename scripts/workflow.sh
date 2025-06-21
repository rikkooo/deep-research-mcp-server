#!/bin/bash

# This script automates advancing the workflow to the next stage.
# It should be run from the root of the project directory.

# --- Configuration ---
MASTER_FILE="docs/WORKFLOW_MASTER.md"
ADVANCE_SCRIPT_PATH="scripts/advance_stage.py" # Path relative to project root
# Load stages dynamically from the python config file
STAGES=($(python3 -c "import sys; sys.path.append('scripts'); from config import STAGES; print(' '.join(STAGES))"))

# --- Validation ---
if [ ! -f "$MASTER_FILE" ]; then
    echo "Error: Master workflow file not found at '$MASTER_FILE'."
    echo "Please run this script from the root of your project directory."
    exit 1
fi

if [ ! -f "$ADVANCE_SCRIPT_PATH" ]; then
    echo "Error: The core script 'advance_stage.py' was not found at '$ADVANCE_SCRIPT_PATH'."
    exit 1
fi

# --- Logic ---
# Get the current stage from the master file
current_stage=$(grep "CurrentStage:" "$MASTER_FILE" | awk '{print $2}')

if [ -z "$current_stage" ]; then
    echo "Error: Could not determine CurrentStage from '$MASTER_FILE'."
    exit 1
fi

# Find the next stage in the sequence
next_stage=""
for i in "${!STAGES[@]}"; do
    if [[ "${STAGES[$i]}" == "$current_stage" ]]; then
        # If it's the last stage, loop back to the first
        if (( i == ${#STAGES[@]} - 1 )); then
            next_stage=${STAGES[0]}
        else
            next_stage=${STAGES[i+1]}
        fi
        break
    fi
done

if [ -z "$next_stage" ]; then
    echo "Error: Current stage '$current_stage' is not a valid stage. Check STAGES in this script and $MASTER_FILE."
    exit 1
fi

echo "Current stage is: $current_stage"
echo "Advancing to next stage: $next_stage"

# Call the python script with the correct arguments
python3 "$ADVANCE_SCRIPT_PATH" "$MASTER_FILE" "$next_stage"
