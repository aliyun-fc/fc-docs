# Announcement: Launch of the New Billing Model for FC Agent Sandbox

Thank you for using FC Agent Sandbox. To better support AI agent development, Function Compute will gradually roll out a new billing model across regions starting at 00:00 on July 31, 2026 (UTC+8). The new model provides compute editions for different workloads and lowers resource prices to help control operating costs.

## I. Key Changes

For details, see [Pay-as-you-go](../03.Pricing/02.Pay-as-you-go.md).

### 1. Three Compute Editions

FC Agent Sandbox introduces Eco, Std, and Pro editions for workloads with different compute and latency requirements.

| Edition | Typical Scenarios | Compute Characteristics | Hibernation Capabilities |
| --- | --- | --- | --- |
| Eco (Economy) | AI startups, personal debugging, and tool-use validation | Allows occasional compute fluctuations and suits cost-sensitive workloads | None |
| Std (Standard) | Enterprise copilots, code execution, and offline sampling | Balanced compute with relatively stable performance and low-latency responses | Deep hibernation |
| Pro (Professional) | High-concurrency consumer agents, complex computation, and large-scale online RL simulation | High-throughput compute for large-scale concurrency, code execution, and distributed RL sampling | Deep and light hibernation |

The detailed feature matrix will be published with the new billing model.

### 2. Simplified Billing and Lower Prices

FC Agent Sandbox uses a pay-as-you-go formula of compute resource unit price × compute runtime. Resource prices are also reduced to lower the cost of running workloads at scale.

## II. Applicability and Transition

- Applicability: The new pricing applies only to users who access FC Agent Sandbox through the E2B SDK.
- Migration: Existing Sandbox Function and AgentRun Sandbox users must switch to E2B SDK access to use the new pricing.
- Automatic upgrade: Existing FC Agent Sandbox users who access the service through the E2B SDK will be moved to the Pro edition when the new pricing takes effect because their current service includes light hibernation. To switch to another edition, contact the DingTalk group 179855020297.
