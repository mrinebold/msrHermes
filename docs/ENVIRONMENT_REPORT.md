# Environment Report

Generated: 2026-05-27 12:26:04 CDT

Mode: read-only inspection. No installs, sudo, shell profile edits, deletions, or public service exposure.

## Phase 1 Summary

Generated after approved Phase 1 foundation work on 2026-05-27.

- Initialized this folder as a local Git repository.
- Added remote `origin` as `https://github.com/mrinebold/HelioCommandCenter.git`.
- Created initial commit `059a225` with message `Initial Helio Command Center scaffold`.
- Added `.gitignore` for macOS, Python, Node, logs, secrets, and local env files.
- Installed OrbStack via Homebrew cask.
- Installed Ollama app via Homebrew cask.
- Installed Google Cloud SDK via Homebrew cask.
- Did not enable SSH Remote Login; `com.openssh.sshd` reports `state = not running`.
- Did not configure Google OAuth.
- Did not pull models. DevMonster is the intended worker direction for the next planning pass.
- Did not install Home Assistant.
- Did not expose public ports.
- Did not edit shell profiles. Google Cloud SDK reported optional PATH/completion profile instructions, but they were not applied.

## Phase 2A Tailscale Summary

Generated after approved Phase 2A Tailscale check-in work on 2026-05-27.

- Tailscale was already installed as the Homebrew cask `tailscale-app`; no Tailscale install was required.
- Opened the Tailscale app for user login/check-in.
- Tailscale is running and checked into the `mrinebold.github` tailnet.
- Tailscale version: `1.98.2`.
- Hostname: `michaels-mac-mini`.
- MagicDNS name: `michaels-mac-mini.taila2da57.ts.net`.
- Tailscale IPv4: `100.80.79.75`.
- Tailscale IPv6: `fd7a:115c:a1e0::d837:4f4b`.
- MagicDNS is enabled tailnet-wide with suffix `taila2da57.ts.net`.
- This Mac does not appear to be advertising itself as an exit node: status reports `ExitNode` as `false` and `ExitNodeOption` as `false`.
- This Mac is not using an exit node: `ExitNodeID` and `ExitNodeIP` are empty.
- This Mac is not advertising subnet routes: `AdvertiseRoutes` is `null`.
- This Mac is not advertising services: `AdvertiseServices` is `null`.
- Tailscale SSH is not enabled locally: `RunSSH` is `false`.
- Security concern: Tailscale DNS is enabled, so name resolution now includes tailnet DNS behavior.
- Security concern: Tailscale file-sharing capability appears available in the tailnet capability map, but no file sharing state was changed during Phase 2A.
- Unknown: public sharing controls and ACL posture were not audited from the Tailscale admin console.
- No SSH Remote Login change was made.
- No DevMonster connection was attempted.
- No Google authentication was performed.
- No models were pulled.
- No Home Assistant install was performed.
- No autonomous services were started.

## Phase 2C DevMonster Endpoint Discovery

Generated after approved Phase 2C inference endpoint discovery on 2026-05-27.

- Target host: `devmonster-4`.
- Target MagicDNS: `devmonster-4.taila2da57.ts.net`.
- Target Tailscale IPv4: `100.93.120.124`.
- Preferred MagicDNS target did not resolve for `/usr/bin/curl` during this retry, so checks fell back to `100.93.120.124`.
- Checked common AI/API ports: `11434`, `8000`, `8080`, and `3000`.
- Used only non-invasive `curl` checks: `HEAD /`, `GET /`, `GET /v1/models`, and `GET /api/tags`.
- Port `11434` refused connections for all checked paths; no Ollama-compatible endpoint was detected.
- Port `8000` refused connections for all checked paths; no OpenAI-compatible endpoint was detected.
- Port `8080` refused connections for all checked paths; no OpenAI-compatible endpoint was detected.
- Port `3000` refused connections for all checked paths; no OpenAI-compatible endpoint was detected.
- No server type or response headers could be identified because all checked ports refused connections.
- No prompts were sent.
- No completions were generated.
- No authentication was attempted.
- No ports were exposed publicly.
- DevMonster was not modified.
- No installs, SSH enablement, Home Assistant install, or autonomous services were started.

Recommended next step before integration:

- Confirm on DevMonster which process should expose Gemma4, which bind address it uses, and which private Tailscale port/path should be used before Helio attempts metadata or inference requests.

### macOS version

```text
ProductName:		macOS
ProductVersion:		26.5
BuildVersion:		25F71

exit_status=0
```

### chip architecture

```text
Darwin mac-mini.local 25.5.0 Darwin Kernel Version 25.5.0: Mon Apr 27 20:41:26 PDT 2026; root:xnu-12377.121.6~2/RELEASE_ARM64_T8132 arm64

exit_status=0
```

### Homebrew status

```text
Homebrew 5.1.14

exit_status=0
```

### Git status

```text
git version 2.50.1 (Apple Git-155)
## main
 M docs/ENVIRONMENT_REPORT.md
 M scripts/check_environment.sh

exit_status=0
```

### Python version

```text
Python 3.9.6

exit_status=0
```

### Node version

```text
v25.6.1

exit_status=0
```

### Codex CLI status

```text
codex-cli 0.133.0

exit_status=0
```

### Docker or OrbStack status

```text
Docker CLI not found
Version: 2.1.3 (2010300)
Commit: 7a3258b7336a8a47b75771e87ef7b74ba4bba8eb (v2.1.3)

exit_status=0
```

### Tailscale status

```text
1.98.2
  tailscale commit: aaf7caef13becf6989e9e81f66412f3edc564c38
  long version: 1.98.2-taaf7caef1-gc4a37aed9
  other commit: c4a37aed97b8b6dcc3fb32d87281c069fd2359d7
  go version: go1.26.3 (tailscale/go e877d97384)

Status:
100.80.79.75   michaels-mac-mini    mrinebold@  macOS    -                           
100.92.126.17  civic-main           mrinebold@  linux    -                           
100.96.95.115  ipad-pro-12-9-gen-5  mrinebold@  iOS      offline, last seen 60d ago  
100.92.128.26  iphone-15-pro-max    mrinebold@  iOS      -                           
100.77.8.69    rinebolddomain       mrinebold@  windows  -                           

IPs:
100.80.79.75
fd7a:115c:a1e0::d837:4f4b

DNS:

=== 'Use Tailscale DNS' status ===

Tailscale DNS: enabled.

Tailscale is configured to handle DNS queries on this device.
Run 'tailscale set --accept-dns=false' to revert to your system default DNS resolver.

=== MagicDNS configuration ===

This is the DNS configuration provided by the coordination server to this device.

MagicDNS: enabled tailnet-wide (suffix = taila2da57.ts.net)

Other devices in your tailnet can reach this device at michaels-mac-mini.taila2da57.ts.net.

Resolvers (in preference order):
  (no resolvers configured, system default will be used: see 'System DNS configuration' below)

Split DNS Routes:
  - ts.net.                        -> 199.247.155.53
  - ts.net.                        -> 2620:111:8007::53

Search Domains:
  - taila2da57.ts.net

=== System DNS configuration ===

This is the DNS configuration that Tailscale believes your operating system is using.
Tailscale may use this configuration if 'Override Local DNS' is disabled in the admin console,
or if no resolvers are provided by the coordination server.

Nameservers:
  - 192.168.68.1
  - 8.8.8.8

Search domains:
  (no search domains found)

[this is a preliminary version of this command; the output format may change in the future]

Prefs:
	"RouteAll": true,
	"ExitNodeID": "",
	"ExitNodeIP": "",
	"ExitNodeAllowLANAccess": false,
	"RunSSH": false,
	"WantRunning": true,
	"LoggedOut": false,
	"AdvertiseRoutes": null,
	"AdvertiseServices": null,

exit_status=0
```

### SSH Remote Login status

```text
You need administrator access to run this tool... exiting!
system/com.openssh.sshd = {
	active count = 0
	path = /System/Library/LaunchDaemons/ssh.plist
	type = LaunchDaemon
	state = not running

	program = /usr/libexec/sshd-keygen-wrapper
	arguments = {
		sshd-keygen-wrapper
	}

	stderr path = /dev/null
	default environment = {
		PATH => /usr/bin:/bin:/usr/sbin:/sbin
	}

	environment = {
		OSLogRateLimit => 64
		MallocSpaceEfficient => 0
		XPC_SERVICE_NAME => com.openssh.sshd
	}

	domain = system
	minimum runtime = 10
	exit timeout = 5
	runs = 0
	last exit code = (never exited)

	event triggers = {
		Listeners => {
			keepalive = 0
			service = com.openssh.sshd
			stream = com.apple.bonjour.registration
			monitor = com.apple.UserEventAgent-System
			descriptor = {
				"Bonjour" => [
					0 = "ssh"
					1 = "sftp-ssh"
				]
				"SockServiceName" => "ssh"
			}
		}
	}

	event channels = {
		"com.apple.bonjour.registration" = {
			port = 0x0
			active = 0
			managed = 1
			reset = 0
			hide = 0
			watching = 1
		}
	}

	sockets = {
		"Listeners" = {
			type = stream
			service name = ssh

			sockets = {
				7 (no bytes to read)
				8 (no bytes to read)
			}

			active = 0
			passive = 1
			bonjour = 1
			ipv4v6 = 0
			receive_packet_info = 0
		}
	}

	spawn type = interactive (4)
	jetsam priority = 180
	jetsam memory limit (active, soft) = 30 MB
	jetsam memory limit (inactive, soft) = 30 MB
	jetsamproperties category = daemon
	jetsam thread limit = 32
	cpumon = default

exit_status=0
```

### disk space

```text
Filesystem        Size    Used   Avail Capacity iused ifree %iused  Mounted on
/dev/disk2s1s1   228Gi    12Gi    62Gi    16%    459k  646M    0%   /

exit_status=0
```

### memory

```text
17179869184
Mach Virtual Memory Statistics: (page size of 16384 bytes)
Pages free:                                   129780.
Pages active:                                 281638.
Pages inactive:                               273368.
Pages speculative:                              7622.
Pages throttled:                                   0.
Pages wired down:                             136267.
Pages purgeable:                               21173.
"Translation faults":                      148621725.
Pages copy-on-write:                         9619662.
Pages zero filled:                          64923319.
Pages reactivated:                           4493009.
Pages purged:                                 491495.
File-backed pages:                            218388.
Anonymous pages:                              344240.
Pages stored in compressor:                   451881.
Pages occupied by compressor:                 184956.
Decompressions:                              2469747.
Compressions:                                3566239.
Pageins:                                     7075335.
Pageouts:                                      64195.
Swapins:                                           0.
Swapouts:                                          0.

exit_status=0
```

### Ollama status

```text
Warning: could not connect to a running Ollama instance
Warning: client version is 0.24.0
Error: timed out waiting for server to start

exit_status=0
```

### Google Cloud CLI status

```text
Google Cloud SDK 570.0.0
bq 2.1.32
core 2026.05.22
gcloud-crc32c 1.0.0
gsutil 5.37

exit_status=0
```

### existing ~/Projects contents

```text
total 0
drwxr-xr-x   3 michaelrinebold  staff    96 May 26 10:56 .
drwxr-x---+ 53 michaelrinebold  staff  1696 May 27 12:26 ..
drwxr-xr-x   9 michaelrinebold  staff   288 May 27 12:08 helio-command-center

exit_status=0
```
