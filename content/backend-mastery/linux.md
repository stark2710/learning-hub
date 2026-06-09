---
module: 28
name: Linux Fundamentals
---
- l1 | Filesystem Hierarchy — inodes, hard vs soft links, /proc & /sys | m28-l1-filesystem
- l2 | Permissions & Users — chmod, ACLs, setuid, PAM | m28-l2-permissions
- l3 | Processes & Signals — fork/exec, kill, zombie processes | m28-l3-processes
- l4 | Package Management — apt, dnf, shared libraries | m28-l4-packages

---
module: 29
name: Shell Scripting & CLI Mastery
---
- l1 | Bash Fundamentals — variables, loops, functions, quoting | m29-l1-bash
- l2 | Text Processing — grep, sed, awk, xargs pipelines | m29-l2-text-processing
- l3 | Shell Scripting Patterns — set -euo pipefail, traps, getopts | m29-l3-scripting-patterns
- l4 | Terminal Productivity — tmux, vim survival, dotfiles | m29-l4-productivity

---
module: 30
name: Linux Networking
---
- l1 | Network Stack — TCP/IP on Linux, ip/ss, socket buffers | m30-l1-network-stack
- l2 | Firewalls — iptables, nftables, conntrack, NAT | m30-l2-firewalls
- l3 | DNS & HTTP Tools — dig, curl, netcat, tcpdump | m30-l3-dns-http
- l4 | SSH Deep Dive — tunnels, ProxyJump, hardening | m30-l4-ssh

---
module: 31
name: Linux Performance & Observability
---
- l1 | CPU & Memory — top, vmstat, /proc/meminfo, OOM killer | m31-l1-cpu-memory
- l2 | Disk & I/O — iostat, iotop, lsof, strace | m31-l2-disk-io
- l3 | Performance Analysis — perf, USE method, flame graphs | m31-l3-perf-analysis
- l4 | Systemd & Services — unit files, journald, cgroups v2 | m31-l4-systemd

---
module: 32
name: Linux Internals & Containers
---
- l1 | Kernel Architecture — syscalls, /proc & /sys deep dive | m32-l1-kernel
- l2 | Containers Under the Hood — namespaces, cgroups, overlayfs | m32-l2-containers
- l3 | Linux Security — capabilities, seccomp, SELinux/AppArmor | m32-l3-security
