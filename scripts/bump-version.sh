#!/usr/bin/env bash
# Bump versions for a version group declared in .version-bump.json.
# Usage: scripts/bump-version.sh [--group <name>] [new-semver]
#   default group: marketplace (tracks VERSION for every generated runtime manifest and OpenCode npm package).
#   scripts/bump-version.sh 0.2.3
set -euo pipefail

command -v jq >/dev/null 2>&1 || {
	echo "bump-version: jq is required" >&2
	exit 1
}

GROUP="marketplace"
NEW=""
while [ $# -gt 0 ]; do
	case "$1" in
	--group)
		GROUP="${2:?--group needs a name}"
		shift 2
		;;
	--group=*)
		GROUP="${1#*=}"
		shift
		;;
	-h | --help)
		sed -n '2,9p' "$0" | sed 's/^# \{0,1\}//'
		exit 0
		;;
	-*)
		echo "bump-version: unknown flag '$1'" >&2
		exit 2
		;;
	*)
		NEW="$1"
		shift
		;;
	esac
done

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CONFIG="$REPO_ROOT/.version-bump.json"
[ -f "$CONFIG" ] || {
	echo "bump-version: $CONFIG not found" >&2
	exit 1
}

version_file="$(jq -r --arg g "$GROUP" '.groups[] | select(.name == $g) | .version_file' "$CONFIG")"
if [ -z "$version_file" ] || [ "$version_file" = "null" ]; then
	echo "bump-version: unknown group '$GROUP' (known: $(jq -r '.groups[].name' "$CONFIG" | paste -sd, -))" >&2
	exit 2
fi

if [ -z "$NEW" ]; then
	[ -f "$REPO_ROOT/$version_file" ] || {
		echo "bump-version: $version_file not found for group '$GROUP'" >&2
		exit 1
	}
	NEW="$(tr -d '[:space:]' <"$REPO_ROOT/$version_file")"
fi

if ! [[ "$NEW" =~ ^[0-9]+\.[0-9]+\.[0-9]+([-+][0-9A-Za-z.-]+)?$ ]]; then
	echo "bump-version: '$NEW' is not a valid semver" >&2
	exit 2
fi

dotted_to_jq_path() { echo ".$1" | sed -E 's/\.([0-9]+)/[\1]/g'; }

written=0
missing=0
while IFS=$'\t' read -r relpath field; do
	abs="$REPO_ROOT/$relpath"
	if [ ! -f "$abs" ]; then
		echo "bump-version: skipping missing $relpath" >&2
		missing=$((missing + 1))
		continue
	fi
	if [ "$field" = "__raw__" ]; then
		printf '%s\n' "$NEW" >"$abs"
	elif [[ "$relpath" == *.toml ]]; then
		VERSION="$NEW" perl -0pi -e 's/(\[plugin\][^\[]*?\nversion\s*=\s*")[^"]+(" )/$1$ENV{VERSION}$2/s; s/(\[plugin\][^\[]*?\nversion\s*=\s*")[^"]+("\n)/$1$ENV{VERSION}$2/s' "$abs"
	else
		tmp="$(mktemp)"
		jq --arg v "$NEW" "$(dotted_to_jq_path "$field") = \$v" "$abs" >"$tmp"
		mv "$tmp" "$abs"
	fi
	written=$((written + 1))
done < <(jq -r --arg g "$GROUP" '.groups[] | select(.name == $g) | .files[] | [.path, .field] | @tsv' "$CONFIG")

if [ "$GROUP" = "marketplace" ] && [ -f "$REPO_ROOT/README.md" ]; then
	VERSION="$NEW" perl -0pi -e 's/Version: [0-9]+\.[0-9]+\.[0-9]+/Version: $ENV{VERSION}/g; s/version-[0-9]+\.[0-9]+\.[0-9]+-blue/version-$ENV{VERSION}-blue/g; s/Stable — v[0-9]+\.[0-9]+\.[0-9]+/Stable — v$ENV{VERSION}/g' "$REPO_ROOT/README.md"
fi

echo "bump-version: group '$GROUP' -> $NEW (wrote $written files, $missing skipped)"
