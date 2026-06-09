---
module: 33
name: AWS Foundations
---
- l1 | Global Infrastructure — Regions, AZs, ARNs, Shared Responsibility | m33-l1-infrastructure
- l2 | IAM Deep Dive — Roles, Policies, Assume-Role, SCPs | m33-l2-iam
- l3 | VPC — Subnets, Route Tables, SG vs NACLs, VPC Peering | m33-l3-vpc
- l4 | EC2 — Instance Types, AMIs, EBS, Placement Groups | m33-l4-ec2

---
module: 34
name: Compute & Containers
---
- l1 | ECS & Fargate — Task Definitions, Services, Task Roles | m34-l1-ecs
- l2 | EKS — Managed Node Groups, VPC CNI, IRSA | m34-l2-eks
- l3 | Lambda — Execution Model, Cold Starts, Layers, Destinations | m34-l3-lambda
- l4 | Auto Scaling — ASG, Lifecycle Hooks, Scaling Policies | m34-l4-autoscaling

---
module: 35
name: Storage & Databases
---
- l1 | S3 Deep Dive — Storage Classes, Lifecycle, Presigned URLs | m35-l1-s3
- l2 | RDS & Aurora — Multi-AZ, Read Replicas, RDS Proxy | m35-l2-rds-aurora
- l3 | DynamoDB — Partition Key Design, GSI, DAX, Single-Table | m35-l3-dynamodb
- l4 | ElastiCache — Redis Cluster Mode, Eviction, Backup | m35-l4-elasticache

---
module: 36
name: Networking & CDN
---
- l1 | Load Balancers — ALB vs NLB, Listener Rules, WAF Integration | m36-l1-load-balancers
- l2 | CloudFront — Distributions, Behaviors, Lambda@Edge, OAC | m36-l2-cloudfront
- l3 | Route 53 — Routing Policies, Health Checks, Private Zones | m36-l3-route53

---
module: 37
name: Messaging & Event-Driven
---
- l1 | SQS — Standard vs FIFO, Visibility Timeout, DLQ | m37-l1-sqs
- l2 | SNS & EventBridge — Fan-out, Filtering, Event Buses | m37-l2-sns-eventbridge
- l3 | Kinesis — Streams vs Firehose, Shards, Enhanced Fan-out | m37-l3-kinesis
- l4 | Step Functions — State Machines, Error Handling, SDK Integrations | m37-l4-step-functions

---
module: 38
name: Observability & IaC
---
- l1 | CloudWatch — Metrics, Logs, Alarms, Logs Insights | m38-l1-cloudwatch
- l2 | X-Ray & CloudTrail — Distributed Tracing, Audit Logging | m38-l2-xray-cloudtrail
- l3 | IaC — CDK vs CloudFormation vs Terraform on AWS | m38-l3-iac

---
module: 39
name: Security & Cost
---
- l1 | AWS Security — KMS, Secrets Manager, WAF, GuardDuty, Shield | m39-l1-security
- l2 | Cost Optimization & Well-Architected Framework | m39-l2-cost
