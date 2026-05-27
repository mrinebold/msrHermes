# Environment Report

Generated: 2026-05-27 12:15:24 CDT

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
- Did not install Tailscale; it remains missing.
- Did not enable SSH Remote Login; `com.openssh.sshd` reports `state = not running`.
- Did not configure Google OAuth.
- Did not pull models. DevMonster is the intended worker direction for the next planning pass.
- Did not install Home Assistant.
- Did not expose public ports.
- Did not edit shell profiles. Google Cloud SDK reported optional PATH/completion profile instructions, but they were not applied.

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
WARNING: proceeding, even though we could not update PATH: Operation not permitted (os error 1)
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
Tailscale not found

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
/dev/disk2s1s1   228Gi    12Gi    62Gi    16%    459k  648M    0%   /

exit_status=0
```

### memory

```text
      Memory: 16 GB
Mach Virtual Memory Statistics: (page size of 16384 bytes)
Pages free:                                    84206.
Pages active:                                 268777.
Pages inactive:                               224798.
Pages speculative:                             44271.
Pages throttled:                                   0.
Pages wired down:                             122251.
Pages purgeable:                                2647.
"Translation faults":                      146636112.
Pages copy-on-write:                         9486040.
Pages zero filled:                          63571968.
Pages reactivated:                           4473066.
Pages purged:                                 485266.
File-backed pages:                            246618.
Anonymous pages:                              291228.
Pages stored in compressor:                   618368.
Pages occupied by compressor:                 269541.
Decompressions:                              2387499.
Compressions:                                3536649.
Pageins:                                     7005561.
Pageouts:                                      63645.
Swapins:                                           0.
Swapouts:                                          0.

exit_status=0
```

### Ollama status

```text
Warning: could not connect to a running Ollama instance
Warning: client version is 0.24.0
Error: Head "http://127.0.0.1:11434/": dial tcp 127.0.0.1:11434: connect: operation not permitted

exit_status=0
```

### Google Cloud CLI status

```text
WARNING: Could not setup log file in /Users/michaelrinebold/.config/gcloud/logs, (PermissionError: [Errno 1] Operation not permitted: '/Users/michaelrinebold/.config/gcloud/logs/2026.05.27/12.15.27.554237.log'.
The configuration directory may not be writable. To learn more, see https://cloud.google.com/sdk/docs/configurations#creating_a_configuration
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
drwxr-x---+ 52 michaelrinebold  staff  1664 May 27 12:13 ..
drwxr-xr-x   9 michaelrinebold  staff   288 May 27 12:08 helio-command-center

exit_status=0
```
