# ROOK SLM™ Reference Architecture

## Architecture View

ROOK SLM™ is organized around a layered control model for governed AI behavior.

```text
User / Interface Layer
        ↓
Intent & Persona Layer
        ↓
Policy & Boundary Layer
        ↓
Context / Retrieval Layer
        ↓
Model Inference Layer
        ↓
Tool / API Orchestration Layer
        ↓
Logging, Audit, and Governance Layer
```

## Layer Descriptions

### User / Interface Layer

The point where users interact with the system. This may include a chat interface, internal portal, command workflow, or embedded assistant.

Design concerns:

- User identity
- Role context
- Session boundaries
- Input validation
- User experience

### Intent & Persona Layer

Determines what the user is trying to accomplish and which approved AI persona, workflow, or task mode should handle the request.

Example conceptual personas:

- Cybersecurity Strategist
- AI Systems Architect
- Creative Songwriting Collaborator

Design concerns:

- Persona separation
- Scope control
- Task classification
- Misrouting prevention
- Purpose alignment

### Policy & Boundary Layer

Acts as the control plane for what the system may access, retrieve, remember, or invoke.

Design concerns:

- Role-based access
- Policy gates
- Sensitive data handling
- Approval workflows
- Safe failure behavior

### Context / Retrieval Layer

Provides relevant information to the model while enforcing source, scope, and sensitivity limits.

Design concerns:

- Retrieval scope
- Trusted sources
- Claim-to-source metadata
- Chunking strategy
- Data classification
- Context minimization

### Model Inference Layer

Runs the selected model or models. In ROOK SLM™, this may be local-first, edge-capable, or otherwise tightly scoped to the use case.

Design concerns:

- Model selection
- Local versus hosted inference
- Performance constraints
- Data exposure
- Output quality validation
- Citation and accuracy validation

### Tool / API Orchestration Layer

Controls access to external functions, APIs, automations, or enterprise systems.

Design concerns:

- Tool allowlists
- Read/write separation
- Human-in-the-loop approval
- Rate limits
- Output validation
- Transaction logging

### Logging, Audit, and Governance Layer

Maintains visibility into system behavior and supports compliance, security monitoring, and lifecycle improvement.

Design concerns:

- Prompt and response metadata
- Tool invocation logs
- Policy decision records
- SIEM export
- Data classification events
- Compliance reporting

## Architectural Principle

No layer should implicitly trust another layer. Each boundary should have a defined purpose, control, and evidence trail.
<p align="center">
  <img src="../assets/LOGO.png" width="200">
</p>

<p align="center">
  <sub>ROOK SLM™ — Boundary-First Intelligence</sub>
</p>
