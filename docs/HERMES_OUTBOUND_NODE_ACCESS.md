# Hermes Outbound Node Access

Status: Phase 7G outbound private-access model

## DevMonster

Known approved private endpoint:

```sh
curl http://100.93.120.124:11434/api/version
```

Known identity:

- Tailscale hostname: `devmonster-4.taila2da57.ts.net`
- Tailscale IPv4: `100.93.120.124`
- Ollama endpoint: `http://100.93.120.124:11434`

This endpoint is used by the local model adapter as an inference worker. DevMonster does not receive operational authority over the Mac mini.

## civic-main

Previously known LAN IP:

```text
192.168.68.100
```

Preferred future access:

- Tailscale hostname/IP once confirmed.
- SSH key dedicated to Mac mini outbound access.

## civic-dev

Previously known LAN IP:

```text
192.168.68.101
```

Warning:

- Phase 7G discovery also found `192.168.68.101` on the Mac mini, so this LAN mapping is stale or conflicting.
- Do not rely on the civic-dev LAN IP until the network map is manually verified.

Preferred future access:

- Tailscale hostname/IP once confirmed.
- SSH key dedicated to Mac mini outbound access.

## Suggested SSH Config Pattern

Generate examples with:

```sh
python3 scripts/generate_macmini_outbound_ssh_config.py
```

Rules:

- do not store private keys in repo
- do not enable broad trust
- use one key per remote machine
- prefer Tailscale names/IPs over LAN IPs
- use LAN fallback only after manual verification

## Non-Goals

Outbound SSH planning does not approve:

- external integrations
- Agent Bus writes
- GitHub token use
- Home Assistant control
- broad filesystem access
- Hermes command execution
- persistent tunnels
