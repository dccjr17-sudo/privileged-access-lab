# Safe and vault design

This is a design for the fictional Northstar Labs simulation. A safe is a logical collection of privileged account metadata with defined responsibilities. No encrypted vault or CyberArk safe is created.

## Account placement

| Safe | Accounts | Purpose | Account owner |
| --- | --- | --- | --- |
| SAFE-WINDOWS-LAB | PA100 / lab-server-admin / APP-SERVER-01 | Approved server maintenance | Riley / E901 |
| SAFE-DATABASE-LAB | PA101 / lab-database-admin / DB-SERVER-01 | Database administration | Riley / E901 |
| SAFE-SERVICE-LAB | PA102 / lab-backup-service / BACKUP-SERVER-01 | Noninteractive backup service | Riley / E901 |

Each account belongs to one safe. Sharing an owner does not give a requester access to every safe. Only PA100 currently has an executable access policy. PA101 and PA102 remain inventory entries; access requests for them fail closed.

## Responsibilities

| Identity or role | Responsibilities | Access boundary |
| --- | --- | --- |
| Jamie / E101 | Request and use approved PA100 maintenance sessions | Cannot approve own requests or administer safes |
| Riley / E901 | Own accounts and review ordinary access requests | Ownership does not automatically start a session |
| Vault administrator role | Maintain safe membership and onboard account metadata | Separate design role; not implemented as an authenticated identity |
| Emergency reviewer role | Review emergency use and follow-up evidence | To be assigned before implementing break-glass |

## Onboarding requirements

Before adding an account, validate a unique account ID, unique account name and target pair, supported account type, an existing safe, and an assigned owner. Store only a fictional credential reference. An inventory entry alone must not grant access. A separate approved policy is required before interactive use. Service accounts must not inherit the interactive PA100 policy.

## Normal access

Jamie requests PA100 for approved patch maintenance on APP-SERVER-01, for at most 30 minutes. Riley approves independently. Session start validates the request and policy again. Activity checks enforce target, requester, allowed action, and expiration. Closure removes local authorization and records fictional session credential rotation metadata.

## Emergency access design

Break-glass will be a separate workflow with an incident reference, a specific account and target, a short time limit, and explicit emergency authorization rules. It must record emergency use, deny unrelated actions, and require a follow-up review. It must not silently turn an ordinary denied request into an approved session. The next implementation step will define the emergency identities and approval model before accepting emergency requests.

## Implementation status

Safe placement is recorded in the CSV inventory. Onboarding validates account ID uniqueness, account name/target uniqueness, safe existence, allowed type, and owner. PA103 onboarding, duplicate rejection, and access denial without a policy were personally exercised. The emergency workflow also checks PA100's safe assignment. General authenticated safe membership enforcement is not implemented. The simulation uses editable local files and command-input identities. It does not provide encryption, real authentication, secret retrieval, account-wide password rotation, or tamper-proof audit storage.
