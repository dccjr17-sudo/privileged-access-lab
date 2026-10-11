# Reproduce the exercise

Requires Python 3.10 or newer; standard library only. Open a terminal in the repository folder. On Windows, replace `python` with the full path to your Python executable if needed.

```powershell
python -m unittest discover -s tests -v
python show_policy.py
python request_access.py --account PA100 --requester E101 --target APP-SERVER-01 --minutes 30 --purpose "approved patch maintenance"
```

Copy the generated request ID and replace `PAM-REQUEST-ID` below:

```powershell
python review_access.py --request PAM-REQUEST-ID --reviewer E101 --decision approve --reason "Test self approval"
python review_access.py --request PAM-REQUEST-ID --reviewer E901 --decision approve --reason "Approved maintenance"
python start_session.py --request PAM-REQUEST-ID --requester E101 --target APP-SERVER-01
python session_action.py --request PAM-REQUEST-ID --requester E101 --target APP-SERVER-01 --action check_patch_status
python session_action.py --request PAM-REQUEST-ID --requester E101 --target APP-SERVER-01 --action delete_logs
python session_action.py --request PAM-REQUEST-ID --requester E101 --target DB-SERVER-01 --action check_patch_status
python close_session.py --request PAM-REQUEST-ID --requester E101 --reason "Maintenance complete"
python session_action.py --request PAM-REQUEST-ID --requester E101 --target APP-SERVER-01 --action check_patch_status
```

Expected: self approval rejected; Riley approval accepted without granting access; session start accepted; patch check allowed; disallowed action and wrong target rejected; closure removes access and records fictional rotation; post-closure action rejected. Rejected controls exit with a nonzero status intentionally.

For duration validation, repeat request creation with `--minutes 60`: rejected before saving. For expiration, create a new request with `--minutes 1`, approve and start it, then wait until its displayed UTC deadline has passed before attempting check_patch_status. Expect an expiration rejection. Close that session afterward for cleanup. No system clock manipulation is needed.

Requests are saved in `runtime/requests/`, which is excluded from the portfolio package and Git. Commands must run sequentially. No external service, credentials, network connection, or CyberArk subscription is required.

## Onboarding

The published inventory includes personally onboarded PA103. Use a new ID, PA104, to reproduce onboarding without removing that evidence entry:

```powershell
python onboard_account.py --account PA104 --name lab-server-admin-03 --target APP-SERVER-03 --type LocalAdministrator --owner E901 --safe SAFE-WINDOWS-LAB
```

Repeat the same command: expect duplicate rejection. Request PA104 through request_access.py: expect rejection because onboarding does not create an access policy. The command changes the local inventory CSV; review the change before committing it.

## Emergency workflow

```powershell
python emergency_access.py request --requester E101 --account PA100 --target APP-SERVER-01 --minutes 5 --incident INC-1001 --reason "Service outage; Riley unavailable"
```

Replace BG-REQUEST-ID below with the generated ID:

```powershell
python emergency_access.py review --request BG-REQUEST-ID --reviewer E101 --decision approve --reason "Test self approval"
python emergency_access.py review --request BG-REQUEST-ID --reviewer E999 --decision approve --reason "Incident verified"
python emergency_session.py start --request BG-REQUEST-ID --actor E101 --target APP-SERVER-01
python emergency_session.py action --request BG-REQUEST-ID --actor E101 --target APP-SERVER-01 --action restart_service
python emergency_session.py action --request BG-REQUEST-ID --actor E101 --target APP-SERVER-01 --action delete_logs
python emergency_session.py close --request BG-REQUEST-ID --actor E101 --reason "Recovery exercise complete"
python emergency_session.py followup --request BG-REQUEST-ID --actor E999 --reason "Reviewed recovery action, denied unrelated action, closure and fictional rotation"
```

Expected: self approval rejected; E999 approval accepted; five-minute session active with post-use review pending; restart allowed; delete_logs rejected; closure removes access and records fictional rotation while review remains pending; independent follow-up completes the review. Perform activity checks before the five-minute deadline; expired activity is rejected. Emergency records are separate under runtime/emergency/ and excluded from publication. All actions are simulated.
