# Architecture

```mermaid
flowchart TD
 A[Reference image] --> B[InsightFace CPU]
 B --> C[SerpApi Google Lens]
 C --> D[Public candidate images]
 D --> E[Independent face matching]
 E --> F[Canonical evidence SHA-256]
 F --> G[Polygon Amoy registry]
 G --> H[Read-only verification]
```

The search client is isolated from face analysis, downloading is bounded and failure-tolerant, and the blockchain layer receives only a 32-byte fingerprint. A missing credential, inaccessible image, absent face, malformed API response, failed transaction, or mismatched verification prevents a false success.
