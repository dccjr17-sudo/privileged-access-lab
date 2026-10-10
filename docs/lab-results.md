# Demonstrated results

The learner personally ran the guided commands and provided 17 screenshots. Codex assisted with implementation, documentation, and automated verification. This project demonstrates PAM concepts through a local Python simulation, not CyberArk product administration.

| Control | Personal result |
| --- | --- |
| Inventory and policy | PA100 local administrator; APP-SERVER-01; requester E101; approver E901; maximum 30 minutes |
| Request | Pending request granted no access |
| Independent approval | E101 self approval rejected; E901 approval accepted |
| Repeated approval | Already approved request could not be reviewed again |
| Temporary authorization | Session started with explicit expiration timestamp |
| Activity scope | Patch-status check allowed; delete_logs action rejected |
| Target scope | DB-SERVER-01 rejected for APP-SERVER-01 session |
| Duration | 60-minute request rejected before saving |
| Expiration | One-minute session allowed activity before deadline and rejected activity after deadline |
| Closure | Both sessions CLOSED, access_granted false |
| Rotation model | Each closure recorded per-session fictional credential version 1 to 2 |
| Audit | Allowed and denied activity recorded locally |

Evidence index: [screenshots and descriptions](../evidence/README.md). Reproduction steps: [guide](reproduce.md).

The rotation model records metadata; it does not test a real password, invalidate a token, rotate a shared account secret, or integrate with a vault. Expiry is checked on attempted activity, not by a background service. Local files are editable, identities are supplied as command inputs, and audit history is not tamper-proof. These boundaries are part of the project scope.
