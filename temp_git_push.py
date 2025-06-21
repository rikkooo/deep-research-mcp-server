import sys
from pathlib import Path

# Add the 'scripts' directory to the Python path to import WorkflowManager
sys.path.append('scripts')

from advance_stage import WorkflowManager

def main():
    """
    Manually triggers the git operations to push the repository state.
    """
    print("--- Running one-time Git push script ---")
    # Initialize WorkflowManager. The arguments are placeholders since we are only calling _handle_git_operations.
    master_file = "docs/WORKFLOW_MASTER.md"
    manager = WorkflowManager(master_file, "Deployer")
    manager._handle_git_operations()
    print("--- Git push script finished ---")

if __name__ == "__main__":
    main()
