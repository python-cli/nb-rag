#!/usr/bin/env bash

# Add the new subcommand name with `_subcommands add <name>`.
_subcommands add "rag"

# Define help and usage text with `_subcommands describe <subcommand> <usage>`.
_subcommands describe "rag" <<HEREDOC
Usage:
  nb rag

Description:
  Print "Hello, World!"
HEREDOC

# Define the subcommand as a function, named with a leading underscore.

_rag() {
    cd ~/gitRepo/nb-rag
    # Activate the pipenv shell and execute nb-rag with all arguments
    pipenv run nb-rag "$@"
}
