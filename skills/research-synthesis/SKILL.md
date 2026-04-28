---
name: research-synthesis
description: Synthesize multi-source research into structured answers or research reports with explicit source hierarchy, evidence tables, and conflict handling. Use when Codex needs to combine task context, local documents, database results, web research, and model background knowledge for research briefs, market scans, comparisons, diligence notes, policy or strategy summaries, or any answer where traceability and synthesis matter more than raw drafting.
---

# Research Synthesis

Build evidence-backed research outputs from mixed sources. Prefer synthesis over filler, show what the evidence supports, and make conflicts and gaps explicit instead of smoothing them away.

## Default Mode

- Default to Chinese output unless the user explicitly asks for another language.
- Treat `structured answer` and `research report` as the two primary deliverables.
- For large or open-ended tasks, stop after the research framework and wait for confirmation before drafting the full report.
- For smaller tasks, still build the framework internally first, then proceed directly to the final answer.

## Workflow

1. Define the research target.
- Identify the decision, question, or comparison the user actually cares about.
- Infer the likely audience and output form if the user does not specify them.
- Rewrite the task into one core question and a small set of sub-questions.

2. Inventory sources.
- Check task-local context first.
- Read user-provided files, local documents, tables, or database results before reaching for the web.
- Use model knowledge for orientation, terminology, and search direction, not as the sole basis for important factual claims.

3. Fill gaps before writing.
- Try to resolve obvious missing pieces by reading more local material, querying available data, or browsing primary sources.
- Do not stop at the first plausible answer when higher-priority evidence is still accessible.
- After filling what you can, list the remaining gaps plainly.

If the user provides no task-local materials, switch to `external research mode`.
- Define the scope before broad searching.
- Prefer official primary sources first, then high-quality secondary sources.
- Treat model knowledge only as orientation, not as decisive evidence.
- Be explicit about coverage limits, source freshness, and unresolved gaps.
- Do not present a fully confident synthesis when the evidence base is still thin.

4. Build the framework first.
- Produce a framework that is as close to MECE as the topic allows.
- Do not force artificial symmetry if the domain is inherently overlapping.
- Separate: confirmed findings, open questions, assumptions, and unresolved conflicts.
- For large tasks, present the framework and wait for confirmation.

5. Synthesize only after the framework is stable.
- Convert the framework into a structured answer or research report.
- Prefer grouping by decision-relevant dimensions, not by source chronology.
- Keep strong claims tied to evidence and scope conditions.

6. Attach evidence.
- Include an evidence table for meaningful research outputs.
- Mark source type, confidence, and conflict status for each key conclusion.

7. Do a final anti-slop pass.
- Remove filler, generic transitions, and repeated summary lines.
- Compress bullet lists that exist only for formatting rather than meaning.
- Keep the writing dense, specific, and decision-useful.

## Source Discipline

Follow the source rules in [references/source-priority.md](references/source-priority.md).

Use this priority order by default:

1. Task-provided data, local documents, and database results.
2. Official primary sources.
3. High-quality secondary sources.
4. Model background knowledge for context only.

When task-provided material conflicts with outside information, say so explicitly. Do not silently blend them into a single narrative.

When higher-priority sources conflict with each other, surface the disagreement, explain what differs, and avoid false reconciliation.

## Output Standards

Use the templates in [references/output-templates.md](references/output-templates.md).

Minimum output requirements:

1. State the question or scope.
2. Present the core synthesis, not a document dump.
3. Distinguish facts, interpretation, and uncertainty.
4. Note material conflicts, caveats, and missing data.
5. Include an evidence table for non-trivial research outputs.

Only include a `Methods and Sources` section in the full `research report` format, not in the default structured answer.

## Evidence Table

Use the schema and confidence rubric in [references/evidence-table.md](references/evidence-table.md).

At minimum, each evidence row should capture:

- conclusion
- main supporting source
- source type
- confidence
- conflict or caveat
- notes on scope or staleness

## Writing Rules

Use [references/anti-slop-writing.md](references/anti-slop-writing.md) for the final writing pass.

Default writing stance:

- Prefer synthesis over exhaustive transcription.
- Prefer concrete claims over abstract framing.
- Prefer short sections with real informational gain over polished but empty prose.
- Avoid template-heavy bullet spam unless the material is naturally list-shaped.

## Failure Modes To Avoid

- Writing a polished answer before checking the best available sources.
- Treating model memory as evidence when primary or task-local data exists.
- Hiding source conflicts to keep the narrative smooth.
- Producing a fake-MECE outline that duplicates ideas across sections.
- Returning generic consultant prose instead of research conclusions.

## Reference Files

- [references/source-priority.md](references/source-priority.md): Source hierarchy, conflict rules, and confidence discipline.
- [references/output-templates.md](references/output-templates.md): Framework, structured answer, and research report templates.
- [references/evidence-table.md](references/evidence-table.md): Evidence table columns and confidence rubric.
- [references/anti-slop-writing.md](references/anti-slop-writing.md): Final pass rules to reduce generic AI-sounding prose.
