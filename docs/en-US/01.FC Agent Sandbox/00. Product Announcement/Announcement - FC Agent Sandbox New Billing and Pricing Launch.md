# Announcement: Launch of New Billing Model for FC Agent Sandbox
Thank you for your continued support of FC Agent Sandbox. To provide a runtime environment that better aligns with the needs of Agent development in the AI era, Function Compute (FC) will gradually roll out a new billing model across different regions starting from July 31, 2026, at 00:00 (UTC+8). 

By establishing a scenario-based computing power matrix and significantly lowering our pricing, we are committed to delivering highly competitive, industry-leading cost-performance advantages. This update will empower your AI business to achieve lean cost control and drive efficiency.


## I. Key Changes
[New Pricing for FC Agent Sandbox](../03.Pricing/02.Pay-as-you-go.md)

### 1. Three Scenario-Based Computing Specs: Match on Demand, Pay with Precision
To meet the diverse demands of different business scenarios, such as "compute-intensive" or "latency-sensitive" workloads, FC Agent Sandbox introduces three major editions—Eco, Std, and Pro. With differentiated computing power pricing, we enable true "on-demand matching and precise payment."

| Edition | Typical Scenarios | Computing Features | 	Hibernation Capabilities | 
| --- | --- | --- | --- | 
| Eco(Economy) | Ideal for AI startups, personal debugging, and Tool Use validation. | Ultra-low barrier: Allows occasional performance fluctuations; the top choice for cost-efficiency. | No Hibernation | 
| Std(Standard·Recommended) | Ideal for enterprise Copilots, code execution, and offline sampling. | General & Balanced: Relatively stable performance with low-latency response; enterprise-grade production-ready. |Hibernation |
| Pro(Professional·Recommended) | Ideal for high-concurrency consumer-facing Agents, complex computation, and large-scale online RL simulation. | Elastic & High-Throughput: Supports millions of concurrent requests with ultra-low latency; perfectly powers code execution and distributed high-throughput RL sampling. | Deep & Shallow Hibernation | 

*Note: For detailed feature matrix differences among the editions, please refer to the upcoming official documentation, which will be released alongside the launch of the new FC Agent Sandbox billing model.*

### 2. Simplified Billing &  Massive Cost Savings 
FC Agent Sandbox has transitioned to an intuitive pay-as-you-go model based on the formula: **[Unit Price of Computing Resource × Computing Run Duration]**, making your bills clear and easy to understand. Concurrently, we have slashed unit prices to pass on cost savings directly to you—significantly reducing your scale-up operational costs and ensuring that AI innovation is no longer constrained by budget.


## II. Applicability & Transition Notice
*   **Applicable To**: The revised pricing structure is exclusively valid for FC Agent Sandbox clients utilizing the **E2B SDK** integration.
*   **Migration Path**: Customers currently on "Sandbox Functions" or "AgentRun Sandbox" who wish to benefit from the new pricing are required to transition to the **E2B SDK** interface.
*   **Active Account Upgrade**: Existing E2B SDK instances will be **automatically transitioned to the Pro tier** upon the effective date of the new pricing, enabling immediate access to "Shallow Hibernation" capabilities. For configuration adjustments to Eco or Std tiers, please contact us via DingTalk Group (**179855020297**).
