# Environment Report

Generated: 2026-05-26 11:09:14 CDT

Mode: read-only inspection. No installs, sudo, shell profile edits, deletions, or public service exposure.

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
fatal: not a git repository (or any of the parent directories): .git

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
OrbStack CLI not found

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
/dev/disk2s1s1   228Gi    12Gi    69Gi    15%    459k  727M    0%   /

exit_status=0
```

### memory

```text
      Memory: 16 GB
Mach Virtual Memory Statistics: (page size of 16384 bytes)
Pages free:                                     4264.
Pages active:                                 362969.
Pages inactive:                               359379.
Pages speculative:                              3477.
Pages throttled:                                   0.
Pages wired down:                             123478.
Pages purgeable:                               14226.
"Translation faults":                       18519673.
Pages copy-on-write:                          752378.
Pages zero filled:                           8253654.
Pages reactivated:                           1737513.
Pages purged:                                 142231.
File-backed pages:                            262958.
Anonymous pages:                              462867.
Pages stored in compressor:                   403679.
Pages occupied by compressor:                 160282.
Decompressions:                               925037.
Compressions:                                1628073.
Pageins:                                     1687853.
Pageouts:                                      16872.
Swapins:                                           0.
Swapouts:                                          0.

exit_status=0
```

### Ollama status

```text
Ollama not found

exit_status=0
```

### Google Cloud CLI status

```text
Google Cloud CLI not found

exit_status=0
```

### existing ~/Projects contents

```text
total 0
drwxr-xr-x   3 michaelrinebold  staff    96 May 26 10:56 .
drwxr-x---+ 51 michaelrinebold  staff  1632 May 26 11:01 ..
drwxr-xr-x   7 michaelrinebold  staff   224 May 26 11:08 helio-command-center

exit_status=0
```

