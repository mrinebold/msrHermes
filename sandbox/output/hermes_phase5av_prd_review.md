what is ready
- Hermes CLI installed locally in isolated HERMES_HOME profiles.
- Managed adapter runner configured for foreground usage.
- Manual adapter service procedure via scripts/adapter_service_start.sh.
- Task inbox usage.
- Adapter binding restricted to 127.0.0.1.
- Local-only hardening of tests, docs, and config examples.

what is not ready
- Sensitive prompts or shell/file-edit authority expansion.
- Hermes autonomous resident mode or resident operation without explicit approval.
- Agent Bus reads/writes.
- Real credentials or credentialed integrations.
- Desktop launch.
- Automatic RunAtLoad or KeepAlive.
- Cloud-provider integrations.
- Broad filesystem or privacy permission grants.

top 5 risks
1. Unauthorized authority expansion (shell/file-edit).
2. Security compromise via the introduction of real credentials.
3. Uncontrolled background execution via unauthorized resident mode or RunAtLoad.
4. Privilege escalation through sudo usage or ~/.hermes modification.
5. Data leakage or integrity loss via Agent Bus activity.

next safest phase
Phase 5AV

exact non-goals
Sensitive prompts, shell/file-edit authority expansion, Hermes autonomous resident mode, resident operation without explicit approval, Agent Bus reads/writes, real credentials, Desktop launch, ~/.hermes modification, sudo, cloud-provider integrations, automatic RunAtLoad, and KeepAlive.

whether human approval is required
Yes, human approval is required for any transition to new phases or the activation of features involving resident mode, Agent Bus activity, or credentialed integrations.
