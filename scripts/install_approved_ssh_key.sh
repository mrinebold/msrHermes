#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  scripts/install_approved_ssh_key.sh --name <machine-name> --pubkey-file <path-to-public-key>

Installs one approved public key into ~/.ssh/authorized_keys.
Does not print key contents, install private keys, use sudo, or store keys in the repo.

Approved import locations:
  /tmp
  /private/tmp
  $HOME/Downloads
  sandbox/ssh_import
USAGE
}

machine_name=""
pubkey_file=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --name)
      machine_name="${2:-}"
      shift 2
      ;;
    --pubkey-file)
      pubkey_file="${2:-}"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      printf 'error=unknown_argument\n' >&2
      usage >&2
      exit 1
      ;;
  esac
done

if [[ -z "$machine_name" || -z "$pubkey_file" ]]; then
  printf 'error=missing_required_argument\n' >&2
  usage >&2
  exit 1
fi

if [[ "$machine_name" =~ [^A-Za-z0-9._-] ]]; then
  printf 'error=invalid_machine_name\n' >&2
  exit 1
fi

if [[ ! -f "$pubkey_file" ]]; then
  printf 'error=pubkey_file_missing\n' >&2
  exit 1
fi

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
pubkey_abs="$(cd "$(dirname "$pubkey_file")" && pwd)/$(basename "$pubkey_file")"
downloads_dir="$HOME/Downloads"

case "$pubkey_abs" in
  /tmp/*|/private/tmp/*|"$downloads_dir"/*|"$repo_root"/sandbox/ssh_import/*)
    ;;
  *)
    printf 'error=unapproved_import_location\n' >&2
    exit 1
    ;;
esac

if grep -Eq 'BEGIN .*PRIVATE KEY|OPENSSH PRIVATE KEY' "$pubkey_abs"; then
  printf 'error=refusing_private_key_file\n' >&2
  exit 1
fi

first_line="$(awk 'NF {print; exit}' "$pubkey_abs")"
if [[ ! "$first_line" =~ ^(ssh-ed25519|ssh-rsa)[[:space:]][A-Za-z0-9+/=]+([[:space:]].*)?$ ]]; then
  printf 'error=invalid_public_key_format\n' >&2
  exit 1
fi

SSH_DIR="${HERMES_SSH_HOME:-$HOME/.ssh}"
AUTHORIZED_KEYS="$SSH_DIR/authorized_keys"
mkdir -p "$SSH_DIR"
chmod 700 "$SSH_DIR"
touch "$AUTHORIZED_KEYS"
chmod 600 "$AUTHORIZED_KEYS"

timestamp="$(date -u '+%Y%m%dT%H%M%SZ')"
backup_path="$AUTHORIZED_KEYS.phase7g-$timestamp.bak"
cp "$AUTHORIZED_KEYS" "$backup_path"
chmod 600 "$backup_path"

key_material="$(printf '%s\n' "$first_line" | awk '{print $1" "$2}')"
if awk '{print $1" "$2}' "$AUTHORIZED_KEYS" | grep -Fxq "$key_material"; then
  print_status="already_present"
else
  {
    printf '# hermes-access %s %s\n' "$machine_name" "$timestamp"
    printf '%s\n' "$first_line"
  } >> "$AUTHORIZED_KEYS"
  print_status="installed"
fi

chmod 700 "$SSH_DIR"
chmod 600 "$AUTHORIZED_KEYS"

printf 'status=%s\n' "$print_status"
printf 'machine=%s\n' "$machine_name"
printf 'authorized_keys=%s\n' "$AUTHORIZED_KEYS"
printf 'backup=%s\n' "$backup_path"
