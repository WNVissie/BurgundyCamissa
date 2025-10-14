# Instructions.md

This file contains all the commands and actions you use regularly for the project. Add new commands and notes as needed.

## Backend (Flask)
```
python shift-roster-backend\src\main.py
```

## Frontend (React/Vite)
```
cd shift-roster-frontend
npm
```

## Git Commands
```
git add .
git commit -m "<your message>"
git push
git branch
git checkout <branchname>
git pull
```

## Other Useful Actions
- Update database schema
- Run seed scripts
- Check logs
- Merge branches

---
Add more instructions below as you discover new actions!

Git commits:

Your process is correct! Here’s a clear summary:

Edit a file:

It appears in Changes (unstaged).
Stage (+) a file:

It moves to Staged Changes.
If you edit the file again, you must stage it again to update the staged version.
Commit:
git ommit -m xx " (-m is for message)

Only the files in Staged Changes are saved in the commit.
Unstaged changes remain local and are not committed.
Push:

After you commit, use push (git push) to upload your commits to the remote repository (GitHub).
Push only sends committed changes to GitHub.
You should push after every commit (or after a batch of commits) to keep GitHub up to date.
Summary:

Push after you commit to sync your local commits with GitHub.
Unstaged changes are always local until you stage, commit, and push.

see which branch you are in:
git branch

q for quit

to check state of version history:  git log --all

to view previous versions:  git checkout # copy the # of the commit from git 

to restore
