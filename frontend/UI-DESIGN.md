# NetDocAi frontend UI direction

## Design references

- Figma dashboard and foundations: https://www.figma.com/design/fAPqBtXJV6S1WHSJ9GxNsA
- Canva visual direction guide: https://canva.link/opvrfc5avvksirg

## Product experience principles

1. **Evidence before claims.** A finding should show the observed evidence before suggesting impact or remediation.
2. **Explain the next step.** Where data is available, show why the finding matters, a safe recommended action, and how to verify the change.
3. **Separate configuration analysis from live state.** Never imply that a configuration-only analysis is active monitoring or proves reachability.
4. **Severity is meaningful.** Use red, amber, and blue sparingly to distinguish priority; do not turn every panel into an alert.
5. **Preserve the existing workflow.** Keep authentication, upload/paste, analysis, saved reports, syslog reports, and export behavior intact while improving presentation.
6. **Progressively disclose detail.** Summary first; interfaces, VLANs, routing, security, evidence, and verification remain available without overwhelming the report.
7. **Graceful data compatibility.** Optional finding fields must not break older saved reports. Missing evidence or remediation should be omitted, not invented.

## Visual foundations

- Canvas: #070B12
- Surface: #0D131D
- Raised surface: #131D2B
- Primary text: #E8EEF8
- Muted text: #8B98AC
- Primary accent: #4B82F6
- Secondary accent: #3DD4E3
- Critical: restrained red
- High: restrained orange
- Medium: restrained amber
- Low/informational: blue or neutral slate
- Typography: Inter when available, with a system sans-serif fallback
- Layout: clear hierarchy, consistent spacing, 1px low-contrast borders, rounded but restrained surfaces

## Accessibility and interaction

- All interactive controls must have keyboard-visible focus.
- Maintain readable contrast for body text and status labels.
- Respect prefers-reduced-motion.
- Do not use color alone to communicate severity; include a text label.
- Keep long device names, evidence lines, and filenames wrapping or horizontally scrollable rather than clipping.
- On small screens, allow metric cards and report tabs to wrap or scroll without hiding content.

## Current frontend work

- Global type rendering, focus states, text selection, and reduced-motion defaults were improved in src/index.css.
- Finding cards use a stronger evidence-first hierarchy and optionally display impact, remediation steps, verification steps, confidence, rule ID, and references. Older finding shapes remain supported.
- Report summary metrics use consistent cards and clearer labels for configuration and syslog reports.
- The Figma dashboard uses illustrative sample values to communicate layout only; it is not live data and should not be presented as actual product metrics.
