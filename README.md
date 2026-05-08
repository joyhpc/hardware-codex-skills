# hardware-codex-skills

Codex skills for hardware engineering workflows.

This repository stores reusable, method-level skills. It should not store project facts, supplier-specific claims, real part-number decisions, credentials, or customer data.

## Skills

- `critical-component-selection`: freeze-grade hardware component selection workflow for schematic, BOM, pin assignment, layout, lifecycle, vendor-evidence, and engineering-verification decisions.

## Install Locally

Expose a skill to Codex by symlinking it into the runtime skills directory:

```bash
ln -s /home/ubuntu/hardware-projects/hardware-codex-skills/critical-component-selection \
  /home/ubuntu/.codex/skills/critical-component-selection
```

## Repository Boundaries

- Put reusable skill workflows here.
- Put project decisions and evidence in project repositories.
- Put component knowledge, design guides, and domain checklists in the hardware knowledge base.
- Put executable project-management tooling in project-tracker.
