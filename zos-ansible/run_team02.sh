#!/usr/bin/env bash

set -Eeuo pipefail

INVENTORY="${INVENTORY:-inventory}"
HOST_LIMIT="${HOST_LIMIT:-zoslab}"
SCP_ARGS="${SCP_ARGS:--O}"
REMOTE="${REMOTE:-origin}"
BRANCH="${BRANCH:-main}"

echo "================================================"
echo " TEAM02 repository automation runner"
echo "================================================"

REPO_ROOT="$(git rev-parse --show-toplevel)"
cd "$REPO_ROOT"

echo
echo "================================================"
echo " Phase 1: Check required commands"
echo "================================================"

required_commands=(
  git
  ansible-playbook
  yamllint
  ansible-lint
)

for command_name in "${required_commands[@]}"; do
  if ! command -v "$command_name" >/dev/null 2>&1; then
    echo "ERROR: Required command is not installed: $command_name"
    exit 1
  fi

  echo "Found: $command_name"
done

echo
echo "================================================"
echo " Phase 2: Update repository"
echo "================================================"

# Ignore this runner itself when determining whether local work exists,
# because the script may be edited locally before it is committed.
if [[ -n "$(git status --porcelain --untracked-files=all)" ]]; then
  echo "WARNING: Local changes are present:"
  git status --short
  echo
  echo "Skipping git pull to avoid overwriting local work."
else
  echo "Pulling latest changes from $REMOTE/$BRANCH..."

  git pull \
    --ff-only \
    "$REMOTE" \
    "$BRANCH"
fi

echo
echo "================================================"
echo " Phase 3: Discover repository YAML files"
echo "================================================"

mapfile -t YAML_FILES < <(
  git ls-files '*.yml' '*.yaml' |
    sort
)

if [[ ${#YAML_FILES[@]} -eq 0 ]]; then
  echo "ERROR: No committed YAML files were found."
  exit 1
fi

echo "Committed YAML files:"
printf '  - %s\n' "${YAML_FILES[@]}"

echo
echo "================================================"
echo " Phase 4: Discover Ansible playbooks"
echo "================================================"

mapfile -t PLAYBOOKS < <(
  printf '%s\n' "${YAML_FILES[@]}" |
    while read -r file; do
      # A playbook normally has a top-level list item and a hosts declaration.
      # This prevents GitHub Actions workflows, inventories, and variable files
      # from being passed to ansible-playbook.
      if grep -Eq '^[[:space:]]*-[[:space:]]+(name:|hosts:)' "$file" &&
         grep -Eq '^[[:space:]]+hosts:' "$file"; then
        echo "$file"
      fi
    done |
    sort
)

if [[ ${#PLAYBOOKS[@]} -eq 0 ]]; then
  echo "ERROR: No committed Ansible playbooks were found."
  exit 1
fi

echo "Committed Ansible playbooks:"
printf '  - %s\n' "${PLAYBOOKS[@]}"

echo
echo "================================================"
echo " Phase 5: Run yamllint"
echo "================================================"

yamllint "${YAML_FILES[@]}"

echo
echo "All committed YAML files passed yamllint."

echo
echo "================================================"
echo " Phase 6: Run Ansible syntax checks"
echo "================================================"

for playbook in "${PLAYBOOKS[@]}"; do
  echo
  echo "Syntax-checking: $playbook"

  ansible-playbook \
    -i "$INVENTORY" \
    "$playbook" \
    --syntax-check \
    --scp-extra-args="$SCP_ARGS"
done

echo
echo "All committed playbooks passed syntax validation."

echo
echo "================================================"
echo " Phase 7: Run ansible-lint"
echo "================================================"

ansible-lint "${PLAYBOOKS[@]}"

echo
echo "All committed playbooks passed ansible-lint."

echo
echo "================================================"
echo " Phase 8: Execute committed playbooks"
echo "================================================"

for playbook in "${PLAYBOOKS[@]}"; do
  echo
  echo "Running: $playbook"

  ansible-playbook \
    -i "$INVENTORY" \
    "$playbook" \
    --limit "$HOST_LIMIT" \
    --scp-extra-args="$SCP_ARGS"

  echo "Completed: $playbook"
done

echo
echo "================================================"
echo " All repository quality checks and playbooks passed"
echo "================================================"