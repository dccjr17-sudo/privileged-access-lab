# Privileged Access Management Lab

Guided, AI-assisted local simulation of CyberArk-style PAM concepts for fictional Northstar Labs. This is not a CyberArk product implementation. No real passwords, production systems, or privileged accounts are used.

## Status

Core guided exercises completed with 17 personal evidence screenshots. Both exercised sessions are CLOSED with access_granted false. All 10 automated tests passed. The portfolio package includes source, policies, tests, documentation, and evidence; publication is pending.

## Run and review

See [reproduction instructions](docs/reproduce.md), [personal results](docs/lab-results.md), and [evidence index](evidence/README.md).

Run `python -m unittest discover -s tests -v` for deterministic checks without modifying personal exercise state. Python 3.10 or newer is required; no additional packages are needed.

## Scenario

Jamie, an IT analyst, needs temporary administrative access to a fictional server to install an approved patch. Riley approves the request. Access is limited to the target and approved time window. The simulation records session activity, expires access, and models credential rotation after use.

## Guided phases

1. Inventory privileged accounts and targets.
2. Model a vault and access policies using fictional credential references.
3. Request access with a reason, target, and duration; require independent approval.
4. Issue temporary authorization and enforce expiry.
5. Record simulated session commands and block actions outside the approved scope.
6. Record fictional session credential metadata changing from version 1 to 2 at closure. Block further activity on the closed session.
7. Validate denied requests, expiry, revocation, and audit records; publish source, checks, and evidence.

## Boundaries

The inventory contains fictional credential references, not a secure secret store. Closure records a per-session fictional credential version change; there is no account-wide vault rotation or credential-version authentication. Session activity is locally simulated, not an SSH/RDP recording. Temporary authorization represents approved access; it does not modify operating-system privileges. Expiry is enforced on activity attempts, with manual closure for final cleanup and rotation metadata. There is no background expiry service. Local records and reviewer IDs are editable lab inputs, not authenticated or tamper-proof controls. Run commands sequentially; concurrent updates are not supported. Actual CyberArk access would require a separately verified environment.
