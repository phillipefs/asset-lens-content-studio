# Asset Lens Content Studio

## Purpose

This repository creates publishable Asset Lens social content. Every production
request must end with a rendered PNG and a validated caption, not only an idea,
prompt, or draft.

## Sources of Truth

1. `.agents/skills/asset-lens-post-studio/SKILL.md` is the canonical workflow.
2. Its `references/approved_examples/` directory is the visual authority.
3. `references/brand/logo_official.png` and `brand_guide.md` own identity.
4. `references/product-brief.md` and `feature-catalog.md` own product claims.
5. `references/compliance.md` owns editorial guardrails.

The Claude entry under `.claude/skills/` is only a discovery adapter. Never put
scripts, assets, or independent rules there. Edit the canonical skill only.

## Required Workflow

1. Read the canonical skill and the relevant product/compliance references.
2. Review every approved example before choosing a composition.
3. Use a real product screenshot whenever the subject has a matching screen.
4. Create a new `instagram/YYYY-MM-DD-slug/` directory; never overwrite an
   unrelated post.
5. Create `render.json` and `copy.md`.
6. Render with the canonical `scripts/run.py`.
7. Run `scripts/verify_output.py` on PNG, copy, and config.
8. Open every final PNG and review framing, readability, brand, and clipping.
9. Iterate at most three times, then report any remaining limitation honestly.

## Product and Compliance Invariants

- Brand name: exactly `Asset Lens`, never `Asset Lens Data`.
- Position the product as an informational quantitative panel.
- Never promise returns or present a classification as an instruction.
- Never use buy/sell calls, price targets, urgency, or personalized advice.
- Never invent metrics that look like real product data.
- Mark hypothetical numbers as illustrative.
- Date mutable claims and snapshots; reconfirm them before reuse.
- Never hardcode an expected asset total as a permanent product fact.
- Keep the exact disclaimer in art and copy:
  `Conteúdo informacional. Não é recomendação de investimento.`

## Inputs and Outputs

- Store source screenshots under `inputs/screenshots/` with an adjacent metadata
  file recording origin and date.
- `copy.md` and `render.json` are versionable source artifacts.
- `post.png`, `slide-*.png`, and render HTML are generated locally and ignored by
  Git, but they must exist and pass verification before delivery.
- Preserve real screenshots: crop only for framing; do not recreate or alter
  their data.

## Validation

From the project root:

```powershell
python scripts/validate_studio.py
python scripts/smoke_test.py
```

For one publication:

```powershell
python .agents/skills/asset-lens-post-studio/scripts/run.py --config instagram/<post>/render.json
python .agents/skills/asset-lens-post-studio/scripts/verify_output.py instagram/<post>/post.png instagram/<post>/copy.md instagram/<post>/render.json
```

## Repository Safety

- Do not initialize Git, commit, push, publish, or create a remote unless the
  user explicitly asks.
- Do not add secrets, private user data, credentials, or unpublished financial
  records.
- Keep changes inside this repository unless the user explicitly expands scope.
- Do not remove or rewrite approved examples without explicit approval.