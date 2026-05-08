# Persona Routing Concept

## Overview

Persona routing is the process of directing a user request to the appropriate task mode, advisory lens, or specialized AI behavior profile.

In ROOK SLM™, personas are not merely writing styles. They represent scoped operating modes with defined purpose, boundaries, and governance expectations.

## Example Conceptual Personas

### Cybersecurity Strategist

Focus:

- Threat modeling
- Security architecture review
- Risk framing
- Executive security communication

Boundary considerations:

- Avoid exposing exploit-enabling detail unnecessarily
- Prioritize defensive context
- Support policy and governance alignment

### AI Systems Architect

Focus:

- AI architecture design
- Context management
- Model deployment planning
- Controlled orchestration

Boundary considerations:

- Limit implementation detail in public-facing contexts
- Emphasize secure design patterns
- Validate data and tool boundaries

### Creative Songwriting Collaborator

Focus:

- Lyric development
- Song structure
- Creative ideation
- Revision support

Boundary considerations:

- Separate creative memory from technical or business memory
- Avoid mixing personal creative drafts with enterprise context
- Respect authorship and licensing considerations

## Persona Governance

Persona routing should answer:

- What is this persona allowed to do?
- What data can it access?
- What tools can it invoke?
- What memory can it use?
- What outputs require review?

## Failure Modes

Common persona-routing risks include:

- User intent misclassification
- Cross-contamination between personas
- Overbroad memory access
- Inconsistent tone or domain assumptions
- Tool access beyond persona scope

## Design Principle

A persona should have a defined job, a defined boundary, and a defined evidence trail.
