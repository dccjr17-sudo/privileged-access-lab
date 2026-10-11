# Demonstrated results

The learner personally ran the guided commands and provided 28 screenshots. Codex assisted with implementation, documentation, and automated verification. This project demonstrates PAM concepts through a local Python simulation, not CyberArk product administration.

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
| Safe design | Windows, database, and service account placement and responsibilities documented |
| Onboarding | PA103 added to SAFE-WINDOWS-LAB; duplicate rejected; access without a policy rejected |
| Emergency approval | Incident INC-1001 linked to separate request; self approval rejected; E999 approval accepted |
| Emergency activity | Fictional restart allowed; unrelated delete_logs action denied |
| Emergency cleanup | Session closed; access removed; fictional rotation recorded |
| Post-use review | E999 completed required review after closure |

Evidence index: [screenshots and descriptions](../evidence/README.md). Reproduction steps: [guide](reproduce.md).

The rotation model records metadata; it does not test a real password, invalidate a token, rotate a shared account secret, or integrate with a vault. Expiry is checked on attempted activity, not by a background service. Local files are editable, identities are supplied as command inputs, and audit history is not tamper-proof. These boundaries are part of the project scope.
