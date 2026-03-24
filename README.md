<p align="center">
  <img src="assets/AEGIS_logo_aegis-sdk.svg" width="80" alt="AEGIS™ SDK">
</p>

<p align="center">
  <strong>aegis-sdk</strong><br>
  Client SDK and integration libraries for the AEGIS™ governance platform
</p>

<p align="center">
  <a href="https://github.com/aegis-initiative"><img src="https://img.shields.io/badge/org-aegis--initiative-0084e7?style=flat-square&logo=github" alt="Org"></a>
  <a href="https://aegis-platform.net"><img src="https://img.shields.io/badge/domain-aegis--platform.net-48BB78?style=flat-square" alt="Domain"></a>
  <img src="https://img.shields.io/badge/npm-%40aegis--initiative%2Fsdk-48BB78?style=flat-square&logo=npm" alt="npm">
  <img src="https://img.shields.io/badge/pypi-aegis--sdk-48BB78?style=flat-square&logo=pypi" alt="PyPI">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-BSL--1.1-blue?style=flat-square" alt="License"></a>
  <img src="https://img.shields.io/badge/ip--owner-Finnoybu%20IP%20LLC-blueviolet?style=flat-square" alt="IP Owner">
</p>

---

## Overview

`aegis-sdk` is the primary integration surface for developers building on top of AEGIS™. It provides TypeScript/JavaScript and Python client libraries that wrap the AEGIS™ platform API, making it straightforward to integrate governance enforcement into any AI system.

> **Capability without constraint is not intelligence™**

---

## Packages

| Package | Language | Registry | Install |
|---|---|---|---|
| `@aegis-initiative/sdk` | TypeScript / JavaScript | npm | `npm install @aegis-initiative/sdk` |
| `aegis-sdk` | Python | PyPI | `pip install aegis-sdk` |

---

## Quick Start

### TypeScript

```typescript
import { AegisClient } from '@aegis-initiative/sdk';

const aegis = new AegisClient({ baseUrl: 'https://demo.aegis-platform.net' });

const decision = await aegis.propose({
  actor: { id: 'agent-001', type: 'ai-agent' },
  action: { capability: 'database.query', parameters: { query: '...' } }
});

if (decision.outcome === 'ALLOW') {
  // execute
}
```

### Python

```python
from aegis_sdk import AegisClient

aegis = AegisClient(base_url="https://demo.aegis-platform.net")

decision = aegis.propose(
    actor={"id": "agent-001", "type": "ai-agent"},
    action={"capability": "database.query", "parameters": {"query": "..."}}
)

if decision.outcome == "ALLOW":
    # execute
```

---

## Governance Outcomes

Both SDKs return one of four governance outcomes:

| Outcome | Meaning |
|---|---|
| `ALLOW` | Action approved — proceed with execution |
| `DENY` | Action rejected — do not execute |
| `ESCALATE` | Requires elevated review before proceeding |
| `REQUIRE_CONFIRMATION` | Requires explicit human approval |

---

## Repository Structure

```
aegis-sdk/
├── packages/
│   ├── sdk-ts/        # TypeScript/JavaScript SDK
│   └── sdk-py/        # Python SDK
└── docs/              # SDK reference documentation
```

---

## Documentation

Full SDK reference: [aegis-docs.com/sdk](https://aegis-docs.com/sdk)

---

## Related Repositories

| Repo | Relationship |
|---|---|
| [aegis-platform](https://github.com/aegis-initiative/aegis-platform) | Platform API this SDK wraps |
| [aegis-docs](https://github.com/aegis-initiative/aegis-docs) | SDK reference docs published here |
| [aegis-ops](https://github.com/aegis-initiative/aegis-ops) | npm and PyPI publish pipeline |
| [aegis-core](https://github.com/aegis-initiative/aegis-core) | Enforcement engine underlying the platform |

---

## License & Trademark

Licensed under the [Apache License 2.0](LICENSE).

AEGIS™ and **"Capability without constraint is not intelligence™"** are trademarks of **Finnoybu IP LLC**.  
Use of AEGIS™ marks in derivative works must not imply endorsement without explicit written permission.