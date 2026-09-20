# Announcement: Launch of New Billing Model for FC Agent Sandbox
Thank you for your continued support of FC Agent Sandbox. To provide a runtime environment that better aligns with the needs of Agent development in the AI era, Function Compute (FC) will gradually roll out a new billing model across different regions starting from July 31, 2026, at 00:00 (UTC+8). 

By establishing a scenario-based computing power matrix and significantly lowering our pricing, we are committed to delivering highly competitive, industry-leading cost-performance advantages. This update will empower your AI business to achieve lean cost control and drive efficiency.


## I. Key Changes
[New Pricing for FC Agent Sandbox](../03.Pricing/02.Pay-as-you-go.md)

### 1. Three Scenario-Based Computing Specs: Match on Demand, Pay with Precision
To meet the differentiated needs of diverse business scenarios — such as "compute-intensive" and "latency-sensitive" workloads — Cloud Sandbox introduces three major tiers: **Eco**, **Std**, and **Pro**. Each tier offers differentiated compute QoS pricing, truly enabling "match-on-demand, pay-per-use" precision billing.

| Tier | Computing Features | Typical Scenarios  | Hibernation Capabilities |
| :--- | :--- | :--- | :--- |
| **Eco (Economy)** | **Ultra-low barrier:** Allows compute fluctuation; best value for cost-sensitive tasks. | AI prototyping, personal debugging, Tool Use validation. | No Hibernation |
| **Std (Standard)** | **Balanced performance:** Relatively stable, low-latency response; suitable for enterprise production. | High-concurrency C-end Agents, complex computation, large-scale sampling and RL simulation. | Hibernation |
| **Pro (Professional)** | **Rigid resource delivery:** Dedicated resource pool ensures zero compute fluctuation; supports 1ms ultra-fast wake-up from shallow sleep. | Dedicated resources with zero jitter; production-grade RL training, financial quant trading, multi-agent long-chain orchestration. | Deep & Shallow Hibernation |

> *Note: Detailed functional differences across tiers will be documented in upcoming official releases, aligned with the launch of this new pricing model.*


### 2. Simplified Billing &  Massive Cost Savings 
FC Agent Sandbox has transitioned to an intuitive pay-as-you-go model based on the formula: **[Unit Price of Computing Resource × Computing Run Duration]**, making your bills clear and easy to understand. Concurrently, we have slashed unit prices to pass on cost savings directly to you—significantly reducing your scale-up operational costs and ensuring that AI innovation is no longer constrained by budget.


## II. Applicability & Transition Notice
*   **Applicable To**: The revised pricing structure is exclusively valid for FC Agent Sandbox clients utilizing the **E2B SDK** integration.
*   **Migration Path**: Customers currently on "Sandbox Functions" or "AgentRun Sandbox" who wish to benefit from the new pricing are required to transition to the **E2B SDK** interface.
*   **Active Account Upgrade**: Existing E2B SDK instances will be **automatically transitioned to the Pro tier** upon the effective date of the new pricing, enabling immediate access to "Shallow Hibernation" capabilities. For configuration adjustments to Eco or Std tiers, please contact us via DingTalk Group (**179855020297**).
