# Secure AI Architecture Review Checklist

## Identity and Access

- [ ] User identity is authenticated
- [ ] Role-based access is defined
- [ ] Administrative access is limited
- [ ] Service accounts are documented
- [ ] Access revocation process exists

## Data and Context

- [ ] Data sources are inventoried
- [ ] Sensitive data is classified
- [ ] Retrieval scope is controlled
- [ ] Context is minimized
- [ ] Source attribution is available

## Model Layer

- [ ] Model selection criteria are documented
- [ ] Deployment location is understood
- [ ] Model limitations are documented
- [ ] Evaluation process exists
- [ ] Output validation is defined

## Tool and API Layer

- [ ] Tool inventory exists
- [ ] Read-only and write-capable tools are separated
- [ ] High-risk actions require approval
- [ ] API calls are logged
- [ ] Tool permissions are reviewed periodically

## Memory

- [ ] Memory use is justified
- [ ] Memory categories are defined
- [ ] Sensitive memory restrictions exist
- [ ] Memory review process exists
- [ ] Deletion process exists

## Logging and Governance

- [ ] Prompt and response metadata is logged appropriately
- [ ] Tool invocation logs are retained
- [ ] Policy decisions are recorded
- [ ] SIEM export is considered
- [ ] Incident review process exists

## Operational Readiness

- [ ] Monitoring is defined
- [ ] Ownership is assigned
- [ ] Change control applies
- [ ] Risk exceptions are documented
- [ ] Review cadence is established
