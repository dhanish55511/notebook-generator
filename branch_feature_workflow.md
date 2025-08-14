## dhanish_github_personal – Git Feature Branch Workflow

1. Navigate into your repo and check status

  cd notebook-generator
  git branch          # lists local branches
  git status          # shows any uncommitted changes
  
  * cd notebook-generator moves into your cloned repo.
  * git branch shows your current local branches.
  * git status tells you which files are modified or staged.

2️. Start from main

  git checkout main
  git pull origin main
  
  * Always update main before starting new work.
  * Ensures your feature branch starts from the latest code.

3️. Create a new feature branch

  git checkout -b feature/refine-url-interpreter-handling
  git branch
  
  * git checkout -b <branch> creates a new branch and switches to it.
  * git branch now shows your new branch with * indicating the active branch.
  * Name branches by purpose: feature/, bugfix/, hotfix/, etc.

  **Use Conventional Commits**

    <type>(optional-scope): <short summary>
    
    Types:
    
    * feat → New feature
    * fix → Bug fix
    * docs → Documentation only changes
    * style → Code style (formatting, missing semicolons, etc.)
    * refactor → Code change that neither fixes a bug nor adds a feature
    * perf → Performance improvement
    * test → Adding/updating tests
    * chore → Maintenance tasks, build scripts, dependencies


4️. Inspect branches

  git branch -r       # lists remote branches
  git branch -a       # lists all branches (local + remote)
  
  * Helps verify branch setup and see if the remote has any branches to sync with.


5️. Make changes
  
  * Edit or replace files inside the repo only.
  * Never replace the .git folder, as it stores your repository’s history.

6️. Stage and commit changes

  git add .
  git commit -m "feat: update output generation and dynamic interpreter selection" \
             -m "- Dynamically scrapes interpreter from the URL passed to the notebook
  - Converts scraped data into a compatible .dsnb notebook format
  - Improves the output file generation logic for consistency"
  
  * git add . stages all changes.
  * git commit -m ... -m ... commits with a title and detailed description.
  * Using feat: clarifies that this is a new feature.

7️. Push feature branch to remote

  git push -u origin feature/refine-url-interpreter-handling
  
  * -u sets upstream, so future git push/git pull commands default to this branch.
  * Branch now exists on GitHub and can be used to create a PR.

8️. Open a Pull Request (PR)

  * Base branch: main
  * Compare branch: your feature branch
  * Include: what changed, why, and testing instructions

9️. Merge PR

  * Review → merge → optionally squash commits
  * main now contains your changes

10. Verify commit history

  git log

  * Shows the commit history for your current branch.
  * Confirms your feature commit is recorded.

11. Delete the feature branch locally

  git branch -D feature/refine-url-interpreter-handling
  git branch
  
  * Deletes the branch locally.
  * git branch confirms it’s gone.

12. Delete the feature branch on remote

  git checkout main   # or master if that’s the default branch
  git branch -D feature/refine-url-interpreter-handling  # in case not deleted locally
  git push origin --delete feature/refine-url-interpreter-handling
  git status
  
  * Switch to main/master before deleting locally.
  * git push origin --delete removes the branch from GitHub.
  * git status ensures your working directory is clean.

**Key Points**

* Always branch from main to avoid conflicts.
* Use descriptive commit messages and Conventional Commit types.
* Keep feature branches focused on one task.
* Delete branches after merging to maintain a clean repo.

