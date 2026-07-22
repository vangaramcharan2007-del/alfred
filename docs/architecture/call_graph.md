# Jarvis X Call Graph & Layer Diagram

## Dependency Graph
```mermaid
graph TD
    User([User Request]) --> Alfred[Alfred Orchestrator]
    Alfred --> MissionEngine[Mission Engine]
    Alfred --> MemorySystem[Memory System]
    MissionEngine --> PlanningEngine[Planning Engine]
    MissionEngine --> CapabilityIntelligence[Capability Intelligence Layer]
    CapabilityIntelligence --> Matcher[Capability Matcher]
    CapabilityIntelligence --> Ranker[Skill Ranker]
    Matcher --> WorkflowHistory[(Workflow DB)]
    Ranker --> ExecutionCost[(Cost & Permissions)]
    CapabilityIntelligence --> SkillExecutor[Skill Executor]
    SkillExecutor --> BaseSkill[Base Skill Interfaces]
    BaseSkill --> ToolRegistry[Tool Registry]
    ToolRegistry --> PermissionManager[Permission Manager]
    PermissionManager --> Execution[Execution Layer]
    BaseSkill --> LLMRouter[OmniRouterClient]
    LLMRouter --> OmniRoute[OmniRoute Gateway]
    OmniRoute --> Provider[Models]
```

## Layer Diagram
```mermaid
flowchart TD
    subgraph L1 [Top Level]
        U[User Interface / APIs / Dashboard]
    end
    
    subgraph L2 [Orchestration Layer]
        A[Alfred]
        ME[Mission Engine]
    end
    
    subgraph L3 [Intelligence Layer]
        CI[Capability Intelligence]
        LLM[OmniRoute]
        MEM[Memory System]
    end
    
    subgraph L4 [Execution Layer]
        S[Skills]
        T[Tool Registry]
        P[Permission Manager]
    end
    
    L1 --> L2
    L2 --> L3
    L3 --> L4
```

## Execution Flow (One Alfred Rule)
1. **User** invokes an intent via Dashboard, CLI, or API.
2. **Alfred** intercepts the intent and categorizes it.
3. If it requires work, Alfred delegates to the **Mission Engine**.
4. The **Mission Engine** determines steps and invokes the **Capability Intelligence Layer**.
5. The **Matcher & Ranker** locate the best **Skill** for the step.
6. The **Skill** attempts execution.
7. If the Skill requires tools (OS, Sandbox, Browser), it requests them from the **Tool Registry**.
8. The **Tool Registry** enforces security boundaries via the **Permission Manager**.
9. The **Execution** finally occurs.
