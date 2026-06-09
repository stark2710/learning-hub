---
module: 40
name: Docker Internals
---
- l1 | How Docker Works — namespaces, cgroups, overlayfs, runc, containerd | m40-l1-how-docker-works
- l2 | Images & Layers — Dockerfile, layer caching, content addressing | m40-l2-images-layers
- l3 | Containers — lifecycle, networking modes, volumes vs bind mounts | m40-l3-containers
- l4 | Docker CLI Mastery — build, run, exec, inspect, stats internals | m40-l4-cli-mastery

---
module: 41
name: Production Dockerfiles
---
- l1 | Dockerfile Best Practices — minimal images, non-root, .dockerignore | m41-l1-best-practices
- l2 | Multi-stage Builds — build vs runtime stages, Go/Java/Python examples | m41-l2-multi-stage
- l3 | Image Security — Trivy/Grype, distroless, cosign, SBOM | m41-l3-image-security

---
module: 42
name: Docker Networking & Storage
---
- l1 | Docker Networking — bridge internals, custom networks, DNS, port mapping | m42-l1-networking
- l2 | Docker Volumes — named volumes, bind mounts, tmpfs, volume drivers | m42-l2-volumes
- l3 | Docker Compose — services, health checks, profiles, secrets | m42-l3-compose

---
module: 43
name: Docker in Production
---
- l1 | Container Registries — ECR, Harbor, tagging strategies | m43-l1-registries
- l2 | Resource Constraints — CPU shares, memory limits, OOM killer | m43-l2-resources
- l3 | Docker Security Hardening — rootless, seccomp, AppArmor | m43-l3-hardening
