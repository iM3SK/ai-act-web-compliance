# Enforcement, Detection, and Evidence

Use the current consolidated AI Act and national implementing law for the
specific case. This reference explains the evidence paths; it does not predict
which authority will open a case or what penalty it will impose.

## Who enforces

The Commission's current Article 50 FAQ states that national competent market
surveillance authorities mainly enforce Article 50. The AI Office has the
limited/exclusive competences defined by the current AI Act for specified AI
systems, and the European Data Protection Supervisor covers EU institutions.
Confirm the relevant Member State designation and procedure during every
preflight because national implementing frameworks can change.

## How a case can start and be checked

Authorities do not need a universal `AI detector`. Depending on their current
legal powers and the facts, evidence can include:

- complaints, whistleblower reports, trusted flagger or platform reports, and
  publicly visible website/content inspection;
- provider machine-readable marks, signed metadata, Content Credentials,
  watermark detectors, and digitally signed detection results;
- generation/export records, source and edited files, model or system
  documentation, terms, acceptable-use policies, review records, publication
  history, and label implementation evidence;
- reasoned information requests, access to documentation or detection tools,
  remote checks, product/content sampling, inspections, and corrective-action
  follow-up within the powers granted by the AI Act, Regulation (EU) 2019/1020,
  and national procedure;
- inconsistencies between a public label, embedded provenance, the provider's
  detection result, the production pipeline, and the organisation's account.

Forensic classifiers can support an inquiry, but the Commission's technical
studies and Code recognise limitations. Metadata can be stripped, watermarks
can be damaged, and forensic detection can produce uncertain results. Absence
of a detected mark is not proof that content is human-made; a detector score is
not proof on its own that content is AI-made.

## Evidence strength

| Evidence                                            | What it can support                                      | Important limit                                                                     |
| --------------------------------------------------- | -------------------------------------------------------- | ----------------------------------------------------------------------------------- |
| Valid signed provenance plus verified asset hash    | Origin and recorded processing assertions for that asset | Proves the signed assertions, not truth of every semantic claim or legal compliance |
| Provider watermark plus official detector           | Link to a provider's marking technique                   | Reliability and robustness vary by media and transformations                        |
| Native source/export and audit trail                | Reconstructs creation and publication workflow           | Integrity, access, and completeness must be assessed                                |
| Visible label captured at first exposure            | Human-facing disclosure implementation                   | Does not prove provider-side machine marking or correct classification              |
| Human/editorial review policy and responsible owner | Supports use of the public-interest-text exception       | Must reflect substantive real practice, not grammar-only or paper compliance        |
| Standalone forensic AI score                        | Investigative lead                                       | Probabilistic and vulnerable to false positives/negatives and model drift           |
| Style, fluency, or visual impression                | Reason to ask questions                                  | Not reliable proof of AI origin                                                     |

## Penalties

Under the current consolidated Article 99, failure to comply with Article 50
can be subject to administrative fines up to EUR 15 million or, for an
undertaking, up to 3% of total worldwide annual turnover for the preceding
financial year, whichever is higher. For SMEs, including startups, the cap is
the lower of the percentage or fixed amount. For small mid-cap companies
(SMCs), current Article 99(6a) applies the same lower-cap rule to the fines in
Article 99(4) and (5).
Incorrect, incomplete, or misleading information supplied in reply to a
competent request has a separate current ceiling of EUR 7.5 million or, for an
undertaking, 1% of total worldwide annual turnover for the preceding financial
year, whichever is higher. The current lower-cap rules for SMEs and SMCs apply;
verify the live consolidated text during preflight.

The maximum is not an automatic fine. The current Article 99 factors include
nature, gravity, duration, consequences, affected persons, earlier fines,
organisation size and turnover, financial benefit, cooperation, responsibility
and controls, how the infringement became known, intent/negligence, and harm
mitigation. Member-State law determines national penalty and procedural
details within the AI Act framework.

## Practical defence file

Maintain proportionate, truthful evidence that can be reproduced:

- dated classification and legal preflight;
- provider/deployer role and system documentation;
- source asset, generation/edit record, and provenance validation;
- selected icon, wording, placement, accessibility, and production screenshots;
- download/reshare and metadata-preservation checks;
- substantive review/editorial-responsibility record where relied on;
- correction reports and remediation history.

Do not retain full prompts, personal data, or confidential content merely
because evidence may be useful. Define purpose, access, minimisation, and
retention under applicable privacy and security rules.
