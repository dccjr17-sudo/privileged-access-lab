# Personal exercise evidence

- `01-policy.png`: User ran `show_policy.py` and confirmed PA100 targets APP-SERVER-01, allows Jamie (E101), requires Riley (E901), limits duration to 30 minutes, forbids self approval, and specifies rotation after use. This displays configuration; it does not demonstrate approval, session, or rotation enforcement.
- `02-request-pending.png`: User created PAM-21aeee4c3ff4 for Jamie (E101), PA100 on APP-SERVER-01, for 30 minutes of approved patch maintenance. Status PENDING; access not granted; assigned approver Riley (E901).
- `03-self-approval-blocked.png`: User attempted to approve the request as Jamie (E101). Review rejected because self approval is not allowed. The saved request remained PENDING with access_granted false.
- `04-approved-repeat-blocked.png`: Riley (E901) approved the request. Access remained ungranted pending session start. User repeated approval and received "Only pending requests can be reviewed"; the original approval was retained.
- `05-session-started.png`: Jamie started SES-72f3e7895cfb on APP-SERVER-01. The local session became ACTIVE for 30 minutes, expiring at 2026-10-10T00:15:13.035066+00:00. No real connection was made.
- `06-allowed-activity.png`: Jamie submitted check_patch_status for APP-SERVER-01 during the active session. The action was ALLOWED (simulated) and recorded in the request's local activity history. No command ran or server changed.
- `07-disallowed-action.png`: Jamie submitted the fictional delete_logs action. The maintenance policy rejected it and recorded a DENIED activity entry. Nothing was deleted.
- `08-wrong-target.png`: Jamie attempted check_patch_status against DB-SERVER-01. The session rejected the target mismatch and recorded the denied attempt.
- `09-session-closed.png`: Jamie closed SES-72f3e7895cfb after the maintenance exercise. Status CLOSED, access_granted false, and fictional session credential metadata changed from version 1 to 2. Closure and rotation were saved in the same request record; no real password changed.
- `10-closed-session-blocked.png`: Jamie attempted check_patch_status after closure. The action was rejected because an active session is required; the denied attempt was added to local activity history.
- `11-duration-limit.png`: Jamie requested 60 minutes against a 30-minute maximum. The request was rejected before persistence. The requests folder still contained only the original closed request.
- `12-one-minute-request.png`: Jamie created PAM-abe841bb5545 for one minute on APP-SERVER-01 to exercise expiration. Status PENDING, access not granted, assigned approver E901.
- `13-one-minute-approved.png`: Riley (E901) approved PAM-abe841bb5545 for the expiration exercise. Status APPROVED; access remained ungranted pending session start.
- `14-one-minute-session.png`: Jamie started SES-c7afa9c683c1 using PAM-abe841bb5545. The local authorization became ACTIVE with expiration at 2026-10-09T23:57:18.163370+00:00, one minute after start. No real connection was made.
- `15-one-minute-allowed-before-expiry.png`: Jamie's patch check ran at 23:56:52.900185 UTC, before the 23:57:18.163370 UTC expiration, and was correctly allowed. This is evidence of activity within the window, not of expiration rejection.
- `16-expired-session-blocked.png`: Jamie repeated check_patch_status after the expiration deadline. The session rejected the action as expired and saved a DENIED audit entry. Expiration is checked on activity attempts; this lab has no background cleanup service.
- `17-expiration-session-closed.png`: Jamie closed SES-c7afa9c683c1 after the expiration test. Status CLOSED, access_granted false, fictional session credential version changed from 1 to 2. Both personally exercised requests are now closed.
