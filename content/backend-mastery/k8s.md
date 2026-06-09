---
module: 44
name: Kubernetes Architecture
---
- l1 | Control Plane — API server, etcd, scheduler, controller manager | m44-l1-control-plane
- l2 | Worker Nodes — kubelet, kube-proxy, CRI, node lifecycle | m44-l2-worker-nodes
- l3 | The API & Resource Model — controllers, reconciliation, watches | m44-l3-api-model
- l4 | kubectl Mastery — jsonpath, explain, dry-run, port-forward | m44-l4-kubectl

---
module: 45
name: Workloads
---
- l1 | Pods Deep Dive — lifecycle, init containers, sidecars, probes | m45-l1-pods
- l2 | Deployments — rolling updates, maxSurge, rollback, pause | m45-l2-deployments
- l3 | StatefulSets — stable identity, PVC templates, ordered scaling | m45-l3-statefulsets
- l4 | DaemonSets, Jobs & CronJobs — node workloads, batch, TTL | m45-l4-daemonsets-jobs
- l5 | Resource Management — requests/limits, QoS, LimitRange, ResourceQuota | m45-l5-resources

---
module: 46
name: Kubernetes Networking
---
- l1 | Networking Model & CNI — Calico, Flannel, Cilium compared | m46-l1-model
- l2 | Services — ClusterIP, NodePort, LoadBalancer, endpoint slices | m46-l2-services
- l3 | Ingress & Gateway API — controllers, TLS, path/host routing | m46-l3-ingress
- l4 | Network Policies — ingress/egress, default-deny, namespace isolation | m46-l4-network-policies

---
module: 47
name: Configuration & Storage
---
- l1 | ConfigMaps & Secrets — env vs file mount, encryption at rest | m47-l1-configmaps-secrets
- l2 | Persistent Volumes — PV, PVC, StorageClass, dynamic provisioning | m47-l2-persistent-volumes
- l3 | Helm — charts, values, templating, hooks, OCI registries | m47-l3-helm
- l4 | Kustomize — bases, overlays, patches — when to use over Helm | m47-l4-kustomize

---
module: 48
name: Kubernetes Security
---
- l1 | RBAC — roles, bindings, service accounts, least privilege | m48-l1-rbac
- l2 | Pod Security — SecurityContext, PodSecurity admission | m48-l2-pod-security
- l3 | Secrets Management — Sealed Secrets, External Secrets, Vault | m48-l3-secrets-mgmt

---
module: 49
name: Observability & Autoscaling
---
- l1 | Logging in Kubernetes — Fluentd/Fluent Bit, sidecar pattern | m49-l1-logging
- l2 | Metrics — metrics-server, Prometheus Operator, ServiceMonitor | m49-l2-metrics
- l3 | HPA, VPA & KEDA — custom metrics, event-driven autoscaling | m49-l3-hpa-vpa
- l4 | Cluster Autoscaler & Karpenter — node provisioning, spot, scale-to-zero | m49-l4-cluster-autoscaler

---
module: 50
name: Advanced Kubernetes
---
- l1 | Custom Resources & Operators — CRDs, controller pattern, kubebuilder | m50-l1-operators
- l2 | Service Mesh — Istio/Linkerd, mTLS, traffic management | m50-l2-service-mesh
- l3 | GitOps — ArgoCD, Flux, app-of-apps, multi-cluster | m50-l3-gitops
- l4 | K8s Internals — admission webhooks, API aggregation, informers | m50-l4-internals
