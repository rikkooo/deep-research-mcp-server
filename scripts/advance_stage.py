import re
import sys
import subprocess
from pathlib import Path
from datetime import datetime, timezone

from config import STAGES

# Define constants for filenames
PROJECT_REQUIREMENTS_FILENAME = "PROJECT_REQUIREMENTS.md"
PROJECT_APPROVAL_FILENAME = "PROJECT_APPROVAL.md"

class WorkflowState:
    """Manages reading and writing the state to the master workflow file."""

    def __init__(self, master_path):
        self.path = master_path
        self.lines = self.path.read_text().splitlines()
        self.data = {}
        self._parse()

    def _parse(self):
        """Parses key-value pairs from the file."""
        for line in self.lines:
            if ":" in line:
                key, value_part = line.split(":", 1)
                # Strip the comment from the value before storing it
                value = value_part.split("#", 1)[0].strip()
                self.data[key.strip()] = value

    def get(self, key, default=None):
        """Gets a value from the parsed state."""
        return self.data.get(key, default)

    def set(self, key, value):
        """Sets a value in the state. This updates the raw lines."""
        self.data[key] = str(value)
        for i, line in enumerate(self.lines):
            if line.strip().startswith(key + ":"):
                comment = ""
                if "#" in line:
                    comment = " #" + line.split("#", 1)[1].strip()
                self.lines[i] = f"{key}: {value}{comment}"
                break

    def update_checklist(self, existing_stage, next_stage):
        """Updates the StageStatus checklist based on the new stage."""
        in_checklist_section = False
        for i, line in enumerate(self.lines):
            if line.strip().startswith("StageStatus (checklist):"):
                in_checklist_section = True
                continue
            if in_checklist_section and line.strip().startswith("- ["):
                match = re.match(r"^(\s*-\s*\[)(.)(\]\s*)(.*?)(\s*)$", line)
                if not match:
                    continue
                stage_name = match.group(4).strip()
                if stage_name == next_stage:
                    self.lines[i] = f"{match.group(1)}x{match.group(3)}{stage_name}{match.group(5)}"

    def save(self):
        """Saves the updated lines back to the file."""
        self.path.write_text("\n".join(self.lines) + "\n")


class WorkflowManager:
    """Orchestrates the workflow advancement process."""

    def __init__(self, master_file, next_stage):
        self.state = WorkflowState(Path(master_file))
        self.existing_stage = self.state.get("CurrentStage")
        self.next_stage = next_stage
        self.project_root = self.state.path.parent.parent

    def _run_command(self, command):
        """Helper to run a shell command and print its output."""
        print(f"Running command: '{' '.join(command)}' in {self.project_root}")
        result = subprocess.run(command, cwd=self.project_root, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        if result.returncode != 0:
            print(f"Error: Command '{' '.join(command)}' failed with exit code {result.returncode}", file=sys.stderr)
        return result.returncode == 0

    def _get_requirement_title(self, req_id):
        """Finds the title for a given requirement ID in the requirements file."""
        req_path = Path(self.state.path.parent, PROJECT_REQUIREMENTS_FILENAME)
        if not req_path.exists():
            return None
        lines = req_path.read_text().splitlines()
        pattern = re.compile(r"-\s*\[.\]\s*\*\*ID\s+" + re.escape(req_id) + r"\*\*\s*–\s*_(.*?)_")
        for line in lines:
            match = pattern.search(line)
            if match:
                return match.group(1).strip()
        return None

    def _handle_git_operations(self):
        """Manages Git repository initialization, commit, and push."""
        git_dir = self.project_root / ".git"
        is_git_repo = git_dir.is_dir()
        repo_url = "https://github.com/rikkooo/deep-research-mcp-server.git"

        if not is_git_repo:
            print("[GIT] This is not a Git repository. Initializing...")
            if not self._run_command(["git", "init"]): return

        # Ensure branch is 'main' to match GitHub's default
        print("[GIT] Ensuring local branch is 'main'...")
        if not self._run_command(["git", "branch", "-M", "main"]): return

        # Ensure remote is configured correctly
        remotes_result = subprocess.run(["git", "remote", "-v"], cwd=self.project_root, capture_output=True, text=True)
        if "origin" not in remotes_result.stdout:
            print(f"[GIT] Adding remote 'origin' with URL: {repo_url}")
            if not self._run_command(["git", "remote", "add", "origin", repo_url]): return
        elif repo_url not in remotes_result.stdout:
            print(f"[GIT] Remote 'origin' has incorrect URL. Updating it...")
            if not self._run_command(["git", "remote", "set-url", "origin", repo_url]): return
        
        # Add a .gitignore and remove vendor directories if needed.
        # This is a one-time operation that creates a cleanup commit.
        gitignore_path = self.project_root / ".gitignore"
        if not gitignore_path.exists():
            print("[GIT] Creating .gitignore and cleaning vendor directories from index...")
            gitignore_content = (
                "# Python\n"
                "venv/\n"
                "__pycache__/\n"
                "*.pyc\n\n"
                "# Node\n"
                "node_modules/\n"
                "npm-debug.log\n"
                "package-lock.json\n"
            )
            gitignore_path.write_text(gitignore_content)
            self._run_command(["git", "add", ".gitignore"])
            self._run_command(["git", "rm", "-r", "--cached", "node_modules", "--ignore-unmatch"])
            self._run_command(["git", "rm", "-r", "--cached", "venv", "--ignore-unmatch"])
            # Check if there's anything to commit for the cleanup
            status_result = subprocess.run(["git", "status", "--porcelain"], cwd=self.project_root, capture_output=True, text=True)
            if status_result.stdout:
                self._run_command(["git", "commit", "-m", "chore: Add .gitignore and remove vendor dirs"])

        print("[GIT] Committing changes for completed requirement...")
        req_id = self.state.get("RequirementPointer")
        req_title = self._get_requirement_title(req_id)
        if not req_title:
            req_title = f"Completed work for requirement {req_id}"

        commit_message = f"feat(req-{req_id}): {req_title}"
        
        if not self._run_command(["git", "add", "."]): return

        status_result = subprocess.run(["git", "status", "--porcelain"], cwd=self.project_root, capture_output=True, text=True)
        if not status_result.stdout:
            print("[GIT] No new application changes to commit.")
            print("[GIT] Attempting to push existing commits...")
            if not self._run_command(["git", "push", "origin", "main"]):
                 print("[GIT] Push failed.", file=sys.stderr)
            return

        if not self._run_command(["git", "commit", "-m", commit_message]): return

        print("[GIT] Pushing changes to remote repository...")
        if not self._run_command(["git", "push", "-u", "origin", "main"]):
            print("[GIT] Push failed.", file=sys.stderr)

    def _log_approval(self):
        """Logs the approval of a requirement in the approval file."""
        req_id = self.state.get("RequirementPointer")
        approval_path = Path(self.state.path.parent, PROJECT_APPROVAL_FILENAME)
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S %Z")
        log_entry = f"- [x] **Req ID {req_id}** – Approved by Validator at {timestamp}\n"
        with approval_path.open("a") as f:
            f.write(log_entry)
        print(f"Logged approval for Req ID {req_id} in {PROJECT_APPROVAL_FILENAME}")

    def _complete_requirement_cycle(self):
        """Handles logic for completing a full cycle for one requirement."""
        if self.existing_stage == "Deployer" and self.next_stage == "Engineer":
            current_req_id = int(self.state.get("RequirementPointer", 1))
            self._check_off_requirement(str(current_req_id))
            next_req_id = current_req_id + 1
            self.state.set("RequirementPointer", next_req_id)
            print(f"Incremented RequirementPointer to: {next_req_id}")

    def _check_off_requirement(self, req_id):
        """Checks off a completed requirement in the requirements file."""
        req_path = Path(self.state.path.parent, PROJECT_REQUIREMENTS_FILENAME)
        if not req_path.exists():
            print(f"Error: {PROJECT_REQUIREMENTS_FILENAME} not found.", file=sys.stderr)
            return
        lines = req_path.read_text().splitlines()
        pattern = re.compile(r"^(\s*-\s*\[\s\]\s*(?:\*\*ID\s+|ID\s+))(" + re.escape(req_id) + r")((?:\s*\*\*|\s+).*)$")
        updated = False
        for i, line in enumerate(lines):
            match = pattern.match(line)
            if match:
                lines[i] = f"{match.group(1).replace('[ ]', '[x]')}{match.group(2)}{match.group(3)}"
                updated = True
                break
        if updated:
            req_path.write_text("\n".join(lines) + "\n")
            print(f"Updated checkbox for Req ID {req_id} in {PROJECT_REQUIREMENTS_FILENAME}")
        else:
            print(f"Warning: Could not find unchecked requirement for ID {req_id}", file=sys.stderr)

    def advance(self):
        """Executes the full workflow advancement logic."""
        if self.existing_stage == "Validator" and self.next_stage == "Deployer":
            self._handle_git_operations()
            self._log_approval()
        self._complete_requirement_cycle()
        self.state.set("CurrentStage", self.next_stage)
        self.state.update_checklist(self.existing_stage, self.next_stage)
        self.state.save()
        print(f"Advanced workflow. Current stage is now: {self.next_stage}")

def main():
    """Main function to run the script from the command line."""
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <path_to_master_file> <next_stage>", file=sys.stderr)
        sys.exit(1)
    master_file = sys.argv[1]
    next_stage = sys.argv[2]
    if next_stage not in STAGES:
        print(f"Error: '{next_stage}' is not a valid stage. Must be one of {STAGES}", file=sys.stderr)
        sys.exit(1)
    manager = WorkflowManager(master_file, next_stage)
    manager.advance()

if __name__ == "__main__":
    main()
