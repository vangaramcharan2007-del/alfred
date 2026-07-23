# Jarvis X: Final Architecture

## The "One Alfred" Principle
Jarvis X centralizes task orchestration under a single agent: **Alfred**. 
Alfred acts as the ultimate router, breaking down user intents and delegating them to specialized subagents.

## Core Flow
1. **User Input:** Voice, Text, or UI.
2. **Alfred Orchestrator:** Classifies intent using the `IntentClassifier`.
3. **Mission Engine:** Tracks long-running goals and state.
4. **Model Router (`OmniRoute`):** Routes context to the optimal LLM (local or cloud).
5. **Skill Loader & Tool Registry:** Dynamically loads capabilities.
6. **Execution:** Actions are performed in safe sandboxes.
7. **Memory:** Results are persisted to Vault and Operational DB.

## Subsystems
- **Hermes Event Bus:** High-speed pub/sub system connecting agents.
- **ShadowBroker:** Manages external API connections.
- **OmniRoute:** Central LLM gateway with fallback logic.
