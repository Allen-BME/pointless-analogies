# Git Workflow

This document provides the Git workflow we will use for the Pointless Analogies Project.

## Initial Setup

Before setting up, it is vitally important to know that Git does not store versions of files - **it stores individual changes made to files in the repository.** Different versions of files are then constructed from the history of changes.

### Set up Git and the GitHub CLI

You can download Git using whatever package manager you prefer, and the steps for downloading the GitHub CLI can be found [here](https://cli.github.com/manual/).

### (Optional) Set up the ssh-agent

Although not necessary, setting up the ssh-agent will allow you to only type in the passphrase for your SSH key once per terminal session, which can be very convenient for performing lots of remote actions. Instructions can be found [here](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent?platform=linux). Once set up you will need to manually re-activate the ssh-agent every terminal session, which can be done with `eval $(ssh-agent)` followed by `ssh-add`.

### Fork the repository

`gh fork Allen-BME/pointless-analogies`

This creates a new repository called *pointless-analogies* under your GitHub account which derives from the main repository. **You will also be given an option to create a local clone of your forked repo, which you should do.** You can do this afterwards if you so choose. In your local directory is a copy of everything in your forked repo on GitHub at the time, which should be the same as what is in the main repo at the time. There is also a hidden directory within *pointless-analogies* which contains all the information needed by Git for versioning, branching, connection with the remote repository, and anything else Git needs.

## Editing

You can directly edit the files in your *pointless-analogies* directory using whatever code editor you choose. As far as code editing is concerned, this is just a normal directory. However, there are some specific ways we will be editing our files to make sure we don't overwrite each other's code.

### Pull any changes

`git pull`
This updates your local repository with all the changes made to the remote repository. Secretly it is a combination of `git fetch`, which grabs changes made to the remote repository, and `git merge`, which merges these changes with your local repository. **This should be run every time you do something with the main branch**, whether creating a branch or merging it.

### Create a branch

`git branch <BRANCH NAME>`
This creates a new branch of development from the branch you are currently on. Any changes made on this branch are completely independent of any other branch, which makes it ideal to develop and test new features without breaking the main branch's functionality at any point. The branch name can be anything, but it's best to make it descriptive to the feature you're trying to add. **All code should be written in a branch dedicated to the feature you're adding. Code should never be written in the main branch.**

### Go to a branch

`git checkout <BRANCH NAME>`
This changes the branch you are currently working on to the target branch, which updates all the files in your directory with changes from that branch. You haven't changed your directory, Git has just edited all the files in it to match the files in your new working branch.

**Shortcut:** `git checkout -b <BRANCH NAME>`
This both creates a new branch and changes your target branch to that new branch.

### Stage your changes

`git add <FILE NAME>`
This "stages" any changes to files you add, which essentially tells Git "these are the files I've finished changing and am ready to commit". You can add any number of files you want, either by separate `git add` commands or one after the other in the same command, and can even add all the files in your directory with the `--all` or `-A` flags. However, **adding a file does not update your branch** - it just tells Git that you will use this file to change the branch later. Also, files are added as is, meaning that if you modify any added files before committing, the additional modifications you made will **not** be committed.

### Commit your changes

`git commit -m "<COMMIT MESSAGE>"`
This command takes every change you've added with `git add` and actually modifies the current branch with them. This command can technically be run as just `git commit`, but a message should **always** be included with the `-m` flag. **The commit message should give a high level overview of what you changed, and should probably be fairly short.** It's a good idea to commit your changes whenever you get something working, even if you didn't complete the full feature, since Git won't let you check out to another branch if you have any changes that haven't been committed, added or not.

**Shortcut:** `git commit -a -m "<COMMIT MESSAGE>"`
This adds all the files in your directory and commits them at the same time.

### Merge your branch

`git merge <BRANCH NAME>`
This attempts to combine your current branch and the branch you specify into a new commit on your current branch. There are two types of merges:

1. **Fast-Forward Merge:** Any two branches will always share some common ancestor. If your branch hasn't changed since that common ancestor, then it's very easy to combine the two; Only one branch has any changes! Your branch just becomes the branch you were merging with - same data and everything. If you imagine the most recent commit on your branch as a pointer to a node in a tree, your branch just now points to the same node as the branch you were merging with. **Fast-Forward Merges cannot have merge conflicts.**

2. **Merge Commit:** If both branches have been changed since their most recent common ancestor, then Git creates a new commit on your branch with the changes from the most recent commits of both branches. Git does its best to combine the changes smoothly, but sometimes it runs into a **merge conflict** (more details below).

### Rebase your branch

`git rebase <BRANCH NAME>`
This is an alternative way to combine changes from two branches. Instead of combining the two most recent commits from both branches, `git rebase` finds the most recent common ancestor of the two branches (called the **base**) and creates a list of every change to each branch since then. It then tries to apply each change to the base **in the order in which they were made.** Merge conflicts can still occur for conflicting individual changes, but it's much clearer which change was made when and which order to resolve the change in. The end result of this command is that your branch's commit history is erased and **your branch's base is now the most recent commit of the branch you were rebasing with**, which makes it ripe for the other branch to perform a fast-forward merge with your branch. This is fantastic for adding the changes from the main branch to a feature branch, but because it erases commit history **`git rebase` should never be used when on the main branch**, since someone may have created a branch from one of the main branch's now deleted commits.

## Pushing to the Remote Repository

There are two conditions which should **always** be met before pushing to the remote repository:

1. **Your main branch is up-to-date with any changes to the remote repo.** That means if anyone has pushed anything to the repo after you began development, you've already pulled those changes, rebased your feature branch with them, and merged your main branch with your feature branch.
2. **Your code has been fully tested.** The idea is that the main branch on the remote repo should always work perfectly, and only when you've made sure your code also works perfectly should you push it to the main branch. You don't have to develop all on your own, though. If you need to push your unfinished branch because you need help, you can run `git push --set-upstream origin <BRANCH NAME>` from within your feature branch to push just that branch to the remote repo. After that, `git push` and `git pull` will push and pull changes to and from your remote feature branch when run within that branch, just like they do within the main branch.

Once both conditions have been met, you can run `git push` from your main branch to push your changes to the remote repository.

## Merge Conflicts

Occasionally you may encounter merge conflicts, either when using `git merge` or `git rebase`. The best way to resolve these conflicts from the teamwork side of things is to try and keep as much code as possible and talk to your team when you're unsure what to do. From the technical side of things, however, resolving merge conflicts is not as hard as it may seem.

When Git detects a merge conflict, it pauses the merging process and adds some text to the places in the file with conflicts. You can manually resolve these conflicts by removing this text, editing the file to combine the code however you want, running `git add` on the previously conflicted files, and running `git merge --continue` or `git rebase --continue`, depending on which command you were originally running. However, there are also many tools to help you resolve these conflicts, some of which may be baked into your code editor. VS Code, for example, has a great merge editor that makes this process much easier (tutorial [here](https://www.youtube.com/watch?v=HosPml1qkrg))

## Simplified Workflow

Suppose you want to add a feature to the code. This is the process you would follow:

`git pull`
`git checkout -b <BRANCH NAME>`
*Edit the code, run tests, etc.*
`git commit -a -m "<COMMIT MESSAGE>"`
`git fetch origin main:main` *shortcut to update main branch with remote changes*
`git rebase main`
*Run automated tests.*
`git checkout main`
`git pull`
*In the unlikely case that any changes were made to the remote repository since you started rebasing (which you find out through* `git pull`*), return to rebasing.*
`git merge <BRANCH NAME>`
`git push`

## Fork and commit guide
I personally found the steps on this repo helpful.
https://github.com/firstcontributions/first-contributions
