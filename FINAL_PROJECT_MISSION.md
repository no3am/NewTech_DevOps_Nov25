# Final Project Mission: Production-Grade Multi-Cluster Observability on AWS EKS

**Audience:** Senior DevOps Students  
**Format:** Markdown brief — what to build, not how. No code snippets in this document.

---

## Mission Statement

As your CTO, I am assigning you the design, implementation, and documentation of a **production-grade, multi-cluster observability solution** on AWS EKS. You will use **Terraform** for infrastructure and the **LGTM stack** (Loki, Grafana, Tempo, Mimir) as the observability backbone. This is not a lab exercise—treat it as a real deployment that would run in a scaling startup environment. Your architecture decisions, security posture, and operational runbooks will be evaluated accordingly.

---

## 1. The Infrastructure (IaC)

- **Terraform** must be the single source of truth for all AWS and EKS provisioning. No manual cluster creation.
- Provision **two separate EKS clusters** in AWS:
  - **Cluster A (Workload):** Hosts the **Google Online Boutique** microservices demo. This cluster represents your application fleet; it must be deployable, reachable, and instrumented.
  - **Cluster B (Observability HQ):** Hosts the **centralized LGTM stack** (Loki, Grafana, Tempo, Mimir). This cluster is the single pane of glass for metrics, logs, and traces.
- Document your Terraform module layout (e.g., separate modules for VPC, EKS, add-ons). State management and remote backends are your responsibility—choose and justify your approach.
- You must determine where to host **Docker images** (e.g., AWS ECR) and **Helm charts** (e.g., ECR for OCI, or another registry). Do not assume these are provided.

---

## 2. The Data Pipeline

- **Metrics, logs, and traces** from Cluster A must be **securely shipped** to Cluster B. No data must reside only on Cluster A for long-term observability.
- You are required to **choose and implement a networking strategy** for cross-cluster communication. Options include (but are not limited to):
  - **Public endpoints** with strict security groups and encryption in transit.
  - **VPC Peering** between the two clusters’ VPCs.
  - **AWS PrivateLink** for private, scalable exposure of Observability HQ services.
- Justify your choice in the README: trade-offs (cost, complexity, security, operational burden) must be clearly explained. The pipeline must be production-appropriate (auth, TLS, least-privilege access).

---

## 3. The “Cloud Native” Storage

- **No long-term reliance on local or node-attached disks** for observability data. All durable storage for the LGTM stack must be **AWS S3** (or S3-compatible) for:
  - **Mimir** (metrics)
  - **Loki** (logs)
  - **Tempo** (traces)
- Implement **IRSA (IAM Roles for Service Accounts)** so that Loki, Grafana, Tempo, and Mimir components can **securely access S3** without long-lived access keys. Document which service accounts and IAM roles map to which components.
- Bucket naming, lifecycle policies, and encryption (SSE-S3 or SSE-KMS) are your design decisions—document them.

---

## 4. CI/CD & GitOps

- The **final submission** must be a **GitHub repository** (or, if your cohort uses it, GitLab—adjust accordingly).
- Include a **working CI/CD pipeline** (e.g., GitHub Actions or GitLab CI) that:
  - **Lints** and **plans** Terraform (and optionally applies in a controlled way).
  - **Deploys or prepares** Helm chart releases for the LGTM stack and/or the Boutique app (strategy is up to you: apply in CI vs. GitOps sync).
- The pipeline must be reproducible: another engineer should be able to re-run it from the repo. Secrets (e.g., AWS credentials, Grafana admin password) must be handled via the platform’s secret store, not committed.

---

## 5. The “Day 2” Challenge (Bonus / Advanced)

- **Upgrades:** Describe the **strategy for upgrading EKS versions** with **zero downtime** for the observability data. Consider control plane upgrades, node group rollouts, and how you would avoid gaps in metrics/logs/traces during the cutover.
- **Scaling:** **Implement or describe** how to use **Horizontal Pod Autoscaler (HPA)** for the **Mimir Ingesters** based on **custom metrics** (e.g., from Prometheus/Mimir). The goal is to show that the observability stack itself can scale with load.

---

## 6. Deliverables

Your repository must include:

| Deliverable | Description |
|-------------|-------------|
| **README.md** | Professional overview with a **clear architecture diagram** (e.g., draw.io, Mermaid, or similar) showing both clusters, data flow, and storage. |
| **Terraform** | All `.tf` files (and any `.tfvars` or backend config) needed to reproduce the two EKS clusters and supporting AWS resources. |
| **Helm** | All `values.yaml` (or equivalent) files used to deploy the LGTM stack and the Google Online Boutique on their respective clusters. |
| **Proof of Life** | A **“Proof of Life”** section in the README: a **screenshot of a Grafana dashboard in Cluster B** showing **traces** and **metrics** originating from **Cluster A** (e.g., Boutique services). This is the non-negotiable evidence that the pipeline works end-to-end. |

---

## 7. Tone & Expectations

- **Professional and real-world:** Assume this will be reviewed by a staff engineer or CTO. Naming, documentation, and security choices matter.
- **Demanding:** We expect justified design decisions, not “it worked on my machine.” Think production: backups, encryption, least privilege, and upgrade paths.
- **Ownership:** You must figure out where to host **Docker images** (e.g., ECR) and **Helm charts** (e.g., ECR OCI or another registry). Document your choices in the README.

---

*Good luck. Build something you’d be proud to run in production.*

— **CTO**
