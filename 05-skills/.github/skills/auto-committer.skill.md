---
name: auto-committer
description: Analyzes staged changes, generates a conventional commit message, and commits the code.
auto-trigger: When the user says "commit this", "write a commit message", or asks to commit changes.
---

# Auto-Committer Skill

When triggered, you must execute this exact workflow:
1. Run git status to verify there are staged changes. If nothing is staged, politely tell the user to stage their files first and STOP.
2. Run git diff --staged to analyze the exact code changes.
3. Generate a strict Conventional Commit message (e.g., eat: added book validation, ix: patched save bug). 
4. Present the proposed commit message to the user and ask for confirmation.
5. If the user approves, run git commit -m "<MESSAGE>" to commit the code.