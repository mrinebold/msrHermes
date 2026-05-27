# Home Assistant Plan

## Objective

Connect to Home Assistant without exposing services publicly and require approval before taking actions that affect the physical environment.

## Phases

1. Confirm Home Assistant URL and access path.
2. Prefer LAN or Tailscale-only access.
3. Create a long-lived access token only after approval.
4. Start with read-only telemetry.
5. Add action allowlists for approved domains and entities.
6. Log every service call and automation trigger.

## Guardrails

- No public ingress.
- No unaudited automations.
- No write actions without explicit policy.
- Treat locks, alarms, garage doors, HVAC, and power controls as high-risk actions.
