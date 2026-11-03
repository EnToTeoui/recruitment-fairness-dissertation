# Publish the prepared repository

Recommended name: `recruitment-fairness-dissertation`. The repository should contain `README.md`, `data/`, `runners/` and the other folders at its root, not just the ZIP archive.

## GitHub Desktop on Windows

1. Extract the ZIP into a permanent folder and keep the full `recruitment-fairness-dissertation` folder structure, including `.github` and `.gitignore`.
2. Install GitHub Desktop and sign in to your GitHub account.
3. Choose **File > Add local repository** and select the extracted project folder. If Desktop says it is not a Git repository, choose the offered option to create a repository there. Check the final local path carefully: it must be the folder containing the prepared README, not a new empty nested folder. The name should be `recruitment-fairness-dissertation`.
4. Review the files in Changes. Do not include `generated/`, `.venv/`, credentials or new raw-response directories; the supplied `.gitignore` excludes these. Keep all archived `data/` CSVs.
5. Commit with a summary such as `Add dissertation replication materials`.
6. Select **Publish repository**. Clear **Keep this code private** if you want everyone to access it, then publish under your own account.
7. Open the published page and confirm the README, dataset folders and workflow appear. Copy that repository URL for the dissertation appendix.

The full counterfactual pool exceeds the browser's individual-file upload limit, so use GitHub Desktop or Git rather than dragging all files into the website. Do not upload only the ZIP: the scripts and instructions should be directly browsable.

## Git command line alternative

After extracting, run these commands from the project root. Configure your own Git author identity if Git requests it; do not use an invented identity.

```powershell
git init -b main
git add .
git commit -m "Add dissertation replication materials"
```

Create an empty GitHub repository named `recruitment-fairness-dissertation` under your account. Do not initialise another README or licence on GitHub because those are already in this folder. Copy the actual HTTPS URL from GitHub and use it in place of `YOUR_REPOSITORY_URL`:

```powershell
git remote add origin YOUR_REPOSITORY_URL
git push -u origin main
```

References: [GitHub new repository guide](https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-new-repository), [GitHub Desktop local repository guide](https://docs.github.com/en/desktop/adding-and-cloning-repositories/adding-a-repository-from-your-local-computer-to-github-desktop).
