#!/bin/bash
#
# git-inital-commit.sh
#
# Push initial commit of a new Git repo to my Gitoris server
#

if [ -n "$1" ]; then
    REPO="$1"
    shift
else
    echo "Usage: $0 <REPO-NAME>"
    exit 1
fi

if [ -n "$1" ]; then
    BRANCH="$1"
else
    BRANCH="master"
fi

SERVER="git.chrisarndt.de"

git remote add origin $SERVER:$REPO.git
git push -u origin $BRANCH
