# Workflow: Deploy Project

**Description:** Commits and pushes all current changes to the remote Git repository. It will guide you through configuration if needed.

---

### Steps

1.  **Check Git User Config:**
    - Run `git config user.name` and `git config user.email`.
    - If either is empty, inform the user and ask for the values. Then run the `git config --global` commands to set them.

2.  **Check Git Remote:**
    - Run `git remote -v`.
    - If no 'origin' remote exists, inform the user that the repository needs to be initialized and linked to a remote (e.g., on GitHub). Stop the workflow and provide guidance.

3.  **Stage and Commit:**
    - Stage all changes by running: `git add .`
    - Ask the user for a commit message.
    - Commit the changes using the provided message: `git commit -m "..."`

4.  **Push to Remote:**
    - Push the changes to the `main` branch: `git push origin main`
    - Confirm the push was successful. If it fails due to authentication, guide the user on setting up an SSH key or a Personal Access Token.
