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

### Update your forked repository

`gh repo sync <YOUR FORKED REPO NAME>`

This updates the main branch in your forked repository on GitHub with any changes made to the main branch in the source repository. You can optionally add the `-b <BRANCH NAME>` flag to specify a specific branch in your fork and the source to sync. This command does **not** update your local repository, only the one on GitHub.

### Fetch any changes

`git fetch origin`

Git stores the addresses of all remote repositories associated with your local repository. `origin` is the name of the repo the local repository was cloned from, and is the default for most remote operations. This command retrieves all the changes made to the main branch at the origin and puts them in the local branch `origin/main`.

### Merge the remote changes

`git merge origin/main`

This attempts to combine your current branch and the `origin/main` branch into a new commit on your current branch. There are two types of merges:

1. **Fast-Forward Merge:** Any two branches will always share some common ancestor. If your branch hasn't changed since that common ancestor, then it's very easy to combine the two; Only one branch has any changes! Your branch just becomes the branch you were merging with - same data and everything. If you imagine the most recent commit on your branch as a pointer to a node in a tree, your branch just now points to the same node as the branch you were merging with. **Fast-Forward Merges cannot have merge conflicts.**
2. **Merge Commit:** If both branches have been changed since their most recent common ancestor, then Git creates a new commit on your branch with the changes from the most recent commits of both branches. Git does its best to combine the changes smoothly, but sometimes it runs into a **merge conflict** (more details below).

**Shortcut:** `git pull origin`

This runs both `git fetch origin` and `git merge origin/main`.

### Rebase your branch

`git rebase <BRANCH NAME>`

This is an alternative way to combine changes from two branches. Instead of combining the two most recent commits from both branches, `git rebase` finds the most recent common ancestor of the two branches (called the **base**) and creates a list of every change to each branch since then. It then tries to apply each change to the base **in the order in which they were made.** Merge conflicts can still occur for conflicting individual changes, but it's much clearer which change was made when and which order to resolve the change in. The end result of this command is that your branch's commit history is erased and **your branch's base is now the most recent commit of the branch you were rebasing with**, which makes it ripe for the other branch to perform a fast-forward merge with your branch. This is fantastic for adding the changes from the main branch to a feature branch, but because it erases commit history, **`git rebase` should never be used when on a branch that any other branches have been made from**.

**Shortcut:** `git pull origin` can still be used for `git rebase` if the default behavior is set to rebase, which can be done with `git config pull.rebase true`.

### Stage your changes

`git add <FILE NAME>`

This "stages" any changes to files you add, which essentially tells Git "these are the files I've finished changing and am ready to commit". You can add any number of files you want, either by separate `git add` commands or one after the other in the same command, and can even add all the files in your directory with the `--all` or `-A` flags. However, **adding a file does not update your branch** - it just tells Git that you will use this file to change the branch later. Also, files are added as is, meaning that if you modify any added files before committing, the additional modifications you made will **not** be committed.

### Commit your changes

`git commit -m "<COMMIT MESSAGE>"`
This command takes every change you've added with `git add` and actually modifies the current branch with them. This command can technically be run as just `git commit`, but a message should **always** be included with the `-m` flag. **The commit message should give a high level overview of what you changed, and should probably be fairly short.** It's a good idea to commit your changes whenever you get something working, even if you didn't complete the full feature, since Git won't let you check out to another branch if you have any changes that haven't been committed, added or not.

**Shortcut:** `git commit -a -m "<COMMIT MESSAGE>"`
This adds all the files in your directory and commits them at the same time.

### Keep your branch up to date

Using the same sync, fetch, and merge/rebase commands as before, you should update your local main branch with any changes from the source repo **before every push operation**. A good practice is to also update your local main branch after every commit, although this is not required.

## Making a pull request

There are two conditions which should **always** be met before making a pull request:

1. **Your forked repo's main branch is up-to-date with your changes and any changes to the source repo.** That means if anyone has pushed anything to the repo after you began development, you've already synced those changes to your forked repo, fetched those changes to your local repo, and rebased your main branch with them. You've also run `git push` from within your main branch to push your changes to your forked repo.
2. **Your code has been fully tested.** The idea is that the main branch on the source repo should always work perfectly, and only when you've made sure your code also works perfectly should you make a pull request. You don't have to develop all on your own, though. If you need to push your unfinished code because you need help, you can create a new branch with `git checkout -b <BRANCH NAME>` and push that branch to your forked repo with `git push --set-upstream origin <BRANCH NAME>` from within your new branch. After that, `git push` and `git pull` will push and pull changes to and from your new remote branch when run within that branch, just like they do within the main branch.

Once both conditions have been met, you can run `gh pr create --title "<TITLE OF PULL REQUEST>" --body "<DETAILS OF PULL REQUEST>"` from your main branch to create a pull request from the source repo. The `--title` and `--body` flags can be left out and the GitHub CLI will interactively ask for this information. Alternatively, you can use the flag `--fill` to automatically generate the title and body from your commits.

To merge the pull request, go to the source repo (`Allen-BME/pointless-analogies`) in a web browser, go to pull requests, and merge your pull request. There shouldn't be any merge conflicts if you followed all the previous steps.

## Merge Conflicts

Occasionally you may encounter merge conflicts, either when using `git merge` or `git rebase`. The best way to resolve these conflicts from the teamwork side of things is to try and keep as much code as possible and talk to your team when you're unsure what to do. From the technical side of things, however, resolving merge conflicts is not as hard as it may seem.

When Git detects a merge conflict, it pauses the merging process and adds some text to the places in the file with conflicts. You can manually resolve these conflicts by removing this text, editing the file to combine the code however you want, running `git add` on the previously conflicted files, and running `git merge --continue` or `git rebase --continue`, depending on which command you were originally running. However, there are also many tools to help you resolve these conflicts, some of which may be baked into your code editor. VS Code, for example, has a great merge editor that makes this process much easier (tutorial [here](https://www.youtube.com/watch?v=HosPml1qkrg))

## Simplified Workflow

Suppose you want to add a feature to the code. This is the process you would follow, assuming you've already set up your fork and local repository:

`gh repo sync <YOUR FORKED REPO NAME>`

`git pull origin`

*Edit the code, run tests, etc.*

`git commit -a -m "<COMMIT MESSAGE>"`

`git pull origin`

*Run tests.*

`git push origin`

`gh pr create`

## Fork and commit guide

There are also some helpful steps for the Git workflow [here](https://github.com/firstcontributions/first-contributions).
