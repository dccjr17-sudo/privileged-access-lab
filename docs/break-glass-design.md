# Emergency access exercise

This fictional workflow addresses an outage in which the normal account owner Riley (E901) is unavailable. It uses a separately designated emergency approver, not an unrestricted bypass of approval.

| Rule | Exercise design |
| --- | --- |
| Requester | Jamie / E101 |
| Emergency approver | Jordan / E999, fictional incident commander |
| Account and target | PA100 on APP-SERVER-01 only |
| Incident | Required incident reference and nonempty outage reason |
| Maximum duration | 5 minutes |
| Allowed activity | check_service_status, restart_service; fictional actions only |
| Independence | Requester cannot approve own emergency request |
| Closure | Remove simulated access and record fictional credential rotation |
| Follow-up | Jordan records a required post-use review; closure alone does not complete the review |

Emergency requests will be stored separately from normal requests. An incident reference is a lab input, not an integration with an incident-management platform or proof of a real outage. The workflow will not overwrite an ordinary request's decision or grant PA103 access. Activities and decisions remain editable local records; no real privileged access is issued.

The local workflow is implemented and personally exercised, including independent approval, allowed recovery activity, denial of an unrelated action, closure, fictional rotation metadata, and completed post-use review. Evidence screenshots 21 through 28 document these results. This design does not implement an offline recovery account, physical sealed credentials, or an authenticated CyberArk emergency workflow. Expiry is checked on activity attempts; closure and post-use review are explicit steps.
