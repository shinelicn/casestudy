#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

PAGES_URL="${PAGES_URL:-https://shinelicn.github.io/casestudy/}"
DEFAULT_MESSAGE="Publish site $(date '+%Y-%m-%d %H:%M:%S')"
COMMIT_MESSAGE="${1:-$DEFAULT_MESSAGE}"

require_cmd() {
  if ! command -v "$1" >/dev/null 2>&1; then
    printf 'Missing required command: %s\n' "$1" >&2
    exit 1
  fi
}

require_cmd git
require_cmd python3

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  printf 'Run this script inside the repository.\n' >&2
  exit 1
fi

if command -v gh >/dev/null 2>&1; then
  if ! gh auth status --hostname github.com >/dev/null 2>&1; then
    printf 'GitHub CLI is installed but not authenticated.\n' >&2
    exit 1
  fi
fi

CURRENT_BRANCH="$(git symbolic-ref --quiet --short HEAD || true)"
if [ -z "$CURRENT_BRANCH" ]; then
  printf 'Detached HEAD is not supported. Checkout a branch first.\n' >&2
  exit 1
fi

printf 'Exporting static site...\n'
python3 -m py_compile app.py modules/fus_demo.py scripts/export_static_site.py
python3 scripts/export_static_site.py

printf 'Staging changes...\n'
git add -A

if ! git diff --cached --quiet; then
  printf 'Creating commit: %s\n' "$COMMIT_MESSAGE"
  git commit -m "$COMMIT_MESSAGE"
else
  printf 'No file changes to commit.\n'
fi

printf 'Syncing with origin/main...\n'
git fetch origin main

if ! git merge-base --is-ancestor origin/main HEAD; then
  printf 'Rebasing %s onto origin/main...\n' "$CURRENT_BRANCH"
  git rebase origin/main
fi

if [ "${PUBLISH_SKIP_PUSH:-0}" = "1" ]; then
  printf 'Skipping push because PUBLISH_SKIP_PUSH=1.\n'
  exit 0
fi

printf 'Pushing %s to origin/main...\n' "$CURRENT_BRANCH"
git push origin HEAD:main

printf 'Publish complete.\n%s\n' "$PAGES_URL"
