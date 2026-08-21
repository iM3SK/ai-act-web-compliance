# Mandatory Legal Preflight

This is a fail-closed gate. Run it before every use of the skill that could
produce a legal conclusion, compliance recommendation, label choice,
generation workflow, or implementation.

## Live checks

1. Record the current date, time zone, target jurisdiction, and publication
   territory.
2. Open EUR-Lex and identify the newest consolidation of Regulation (EU)
   2024/1689. Check Article 3(60), Article 50, Articles 74 to 85, Article 99,
   Article 111, and Article 113 as relevant. Open every amending act listed by
   the consolidation.
3. Open the Commission's final Article 50 Guidelines page and download or open
   the current final Guidelines. Do not use the consultation draft.
4. Open the Commission Article 50 FAQ, Code of Practice page, current Code, and
   EU icons page. Record their visible update dates and whether the Code has
   been assessed as adequate.
5. For every named Member State, check its official legislation register,
   government or ministry material, designated-authority material, penalty
   procedure, and any national rules relevant to the use case. If a process is
   ended, withdrawn, merged, or says that another process supersedes it, open
   the named successor and record both process identifiers, statuses, and
   dates. Never treat the ended file as the current process.
6. Check any sector-specific primary law triggered by the content. Typical
   examples are consumer protection, political advertising, privacy,
   accessibility, copyright, media, health, or child-safety rules.

Use the canonical links and priority order in
[official sources](official-sources.md). Search may discover a source, but the
opened primary document is the evidence.

## Change test

Compare the live observations with the dated baseline in
[official sources](official-sources.md). A difference in any of these fields is
material until reviewed:

- consolidation date, CELEX identifier, or listed amending act;
- text or application date of the relevant AI Act provisions;
- publication/update date or status of final Guidelines, FAQ, or Code;
- icon archive link, licence, semantic variants, or placement rules;
- Member State implementing-law process identifier, successor chain, stage, or
  designated authority;
- applicable harmonised standard or official technical guidance.

When a difference is found, re-read the affected provisions and update the
analysis for the current run. Do not silently keep the baseline conclusion.
If the workspace copy is being maintained and the user has authorised writes,
update the baseline and assets in a separate, reviewable change.

## Preflight record

Include this compact record in the working evidence and reproduce the complete
record at the end of every legal or compliance answer. A prose summary does not
replace it. Do not omit a required field; record an explicit unavailable result
when the source could not be meaningfully inspected. Parse the final fenced
block as YAML before returning and reject malformed or duplicate fields.

```yaml
checked_at: YYYY-MM-DDTHH:MM:SS+TZ
jurisdiction: EU/EEA and named Member State
ai_act_consolidation: CELEX identifier and consolidation date
official_guidance: title, status, and update date
code_and_icons: title, status, and update date
national_sources: exact authority and legislation-register sources, dates, and results
changes_since_baseline: none observed | concise list
unavailable_sources: none | concise list
```

Do not write `unavailable_sources: none` unless every relevant national source
above was queried through an official authority page, document, register, or
search and its relevant result could be meaningfully inspected. An HTTP success
status, file existence, unrelated document, general web search, another
source's summary, or silence in one register does not prove the status of the
others. List an unparseable or relevance-unverified result as unavailable and
apply the failure behavior below.

## Failure behavior

If an official source is unavailable, contradictory, or not yet published,
map the gap to the conclusions it could change. For every affected conclusion:

- do not issue a definitive `required`, `not required`, `compliant`, or
  `non-compliant` conclusion;
- state the exact missing or conflicting evidence;
- provide only an inventory of facts that remain stable and a checklist for
  the next live check;
- escalate a disputed or high-impact interpretation to qualified counsel or
  the competent authority.

Do not let an unresolved national authority, penalty procedure, or sector rule
silently weaken the gap, but do not use it to block an independently supported
EU Article 50 classification that it cannot change. Scope the supported result
to EU law and explicitly withhold the unresolved national or sectoral result.
