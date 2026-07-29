# AI-assisted auditing (AGENT_GUIDE)

The audit splits into two stages with very different reliability
requirements, and the design keeps them strictly separate:

1. **Extraction** — transcribing printed values from a PDF into the
   audit-record JSON. This is tedious and error-prone for humans and is
   where an AI assistant (Claude, GPT, etc.) genuinely helps.
2. **Judgment** — deciding whether the numerical chain reproduces. This is
   pure deterministic arithmetic and is done ONLY by the engine
   (`libs-audit`), never by the language model.

This separation matters. A language model can misread a table; the engine
cannot mis-divide. So the model proposes a record, a **human verifies every
number against the PDF**, and only then is the verified record fed to the
engine. The finding that gets reported is the engine's output, which anyone
can rerun.

## Workflow

```
PDF ──(LLM extraction prompt below)──> draft record.json
      ──(human checks every value against the PDF; fills 'source' notes)──>
      verified record.json ──(libs-audit record.json -o report.md)──>
      deterministic PASS/FAIL report
```

## Automated extraction command

```bash
export ANTHROPIC_API_KEY=sk-ant-...     # read from env, never stored
pdftotext paper.pdf paper.txt
libs-audit-extract paper.txt -o draft_record.json
```

The draft is stamped `"verification": "DRAFT — UNVERIFIED"`; `libs-audit`
prints a prominent warning for such records until a human replaces the stamp
with `verified by <name>, <date>` after completing the checklist below.

## Extraction prompt (manual alternative — copy-paste, attach the PDF and template.json)

> You are assisting with a reproducibility audit of a CF-LIBS/LIPS
> publication. Fill the attached `template.json` using ONLY values printed
> in the attached paper (tables, equations, figure axis labels,
> accompanying text). Rules:
> 1. Never estimate, interpolate, round differently, or fill gaps from
>    background knowledge. If a value is not printed, omit the field and
>    list it under a top-level `"missing"` array instead.
> 2. For every block, fill the `"source"` field with the exact table,
>    equation or section where the value appears.
> 3. Transcribe coefficients at full printed precision, including
>    zero slopes (write 0.0, do not "fix" them).
> 4. If the paper states the same quantity with different exponents or
>    units in different places, record each variant in a top-level
>    `"conflicts"` array with locations; do not resolve the conflict.
> 5. For the `"qualitative"` block, set a flag true only if the diagnostic
>    is explicitly reported with numerical inputs, not merely mentioned.
> 6. Output only the completed JSON.

## Human verification checklist (do not skip)

- [ ] Every `method_value` / `reference_value` matches the printed table.
- [ ] Every equation coefficient matches at full printed precision,
      including signs and zero slopes.
- [ ] Exponents/normalizations (10^16 vs 10^17) match each stated location;
      conflicts are recorded, not resolved.
- [ ] Units in the record match the paper's units.
- [ ] Each `source` note is specific enough for a stranger to find the value.
- [ ] The `qualitative` flags reflect the printed record, not charitable
      inference.

## Interpreting the report

The engine's statuses are defined in `engine.py`. Two cautions:

- **FAIL means "not reproducible from the printed record"**, nothing more.
  Typographical errors, rounding, unreported full-precision coefficients or
  an undocumented calculation pathway can all produce a FAIL and can all be
  resolved by author clarification. Reports generated with this tool should
  say so, as the framework paper does.
- **NOT_REPORTED flags missing minimum-reporting items** (Table 3 of the
  framework paper); absence of a diagnostic is a completeness finding, not
  evidence the underlying physics is wrong.

## Extending the engine

`engine.py` checks linear empirical relations, the Eq.-(2)-style Stark
normalization, tolerance-based validation and qualitative flags. Papers
using full CF closure (Boltzmann plots, Saha–Boltzmann, self-absorption
corrections) need additional check functions; add one function per
deterministic step, return `CheckResult` objects, and register the function
in `run_audit`. Keep the rule: the model may draft inputs, only code judges.
