# Generation and Publication Workflow

Use this workflow whenever content may be generated, edited, or published with
AI. It joins the provider-side technical layer with the deployer-side human
disclosure layer without treating one as a substitute for the other.

Normative labels used below:

- **LAW:** requirement stated in the current AI Act;
- **CODE:** commitment for a signatory relying on the current voluntary Code;
- **RECOMMENDED:** implementation control that must not be presented as a legal
  requirement without a current primary source.

## Before generation

1. Run the mandatory legal preflight.
2. Record the intended territory, channel, audience, media type, and whether
   the output will be public, downloadable, shareable, live, or clipped.
3. Classify the organisation as provider, deployer, or both.
4. Pre-classify the intended output:
   - direct AI interaction;
   - possible deepfake;
   - public-interest text;
   - artistic, creative, satirical, fictional, or analogous work;
   - ordinary content outside Article 50 but subject to another law.
5. Decide whether the result will be fully AI-generated, partially AI-modified,
   or use the basic icon with a precise text/interactive explanation.
6. Choose a generation service that documents its machine-readable marking
   and detection capability. Record limitations and do not assume a provider
   name proves Article 50(2) compliance.
7. Define human review, editorial responsibility, label text, accessible
   alternative, and placement before producing the asset.

## During generation

- Keep the first exported original and its native provenance metadata.
- Do not ask a tool or pipeline to remove a watermark, signature, Content
  Credential, or other AI-transparency mark.
- Record the system/tool, relevant version if available, generation date,
  output identifier, source assets, and the type of AI operation.
- Store prompts only when needed for a stated purpose. Minimise personal,
  confidential, and credential-like data and apply an appropriate retention
  rule.
- For modified content, keep the human-made input and record what region,
  object, voice, scene, or passage AI changed.
- Do not manufacture C2PA assertions, timestamps, signatures, or review
  evidence. Provenance must be emitted and cryptographically bound by a
  capable trusted workflow.

## After generation

1. Verify the actual output, not the provider's marketing page:
   - inspect embedded metadata or Content Credentials;
   - use the provider's official detection mechanism where available;
   - record the result, method, timestamp, and limitations;
   - treat a detector score as evidence with uncertainty, not proof by itself.
2. Re-run the deepfake and public-interest-text classification against the
   finished asset and its intended context.
3. Select the icon and wording using
   [icons and labels](icons-and-labels.md).
4. Apply the human-facing label at or before first exposure. For deepfakes and
   in-scope public-interest text, do not rely solely on machine marking.
5. Apply substantive human review and named editorial responsibility when the
   workflow intends to use the public-interest-text exception. Correctness,
   source quality, misleading implications, and material omissions must be in
   scope; grammar-only review is insufficient.

## Publication

- **LAW, all modalities:** provide applicable information clearly and
  distinguishably, in an accessible manner, no later than first interaction or
  exposure.
- **CODE, image:** place the label on or immediately adjacent to the asset with
  no intervening overlay. Embed it in the distributed file or use an equivalent
  persistent UI overlay; aim to preserve it in downloads and reshares.
- **CODE, video:** show it at the beginning and, where possible, at regular
  intervals and after interruptions. For live or clip-prone video, persistent
  or repeated placement is the safer implementation.
- **CODE, audio-only:** put a short plain-language audible disclaimer at the
  beginning. For long-form or live audio, add appropriate reminders and at
  least repeat after interruptions. Add a visual disclosure whenever a screen
  is available.
- **CODE, text:** place the disclosure above or at the top, near the headline,
  or in a beginning colophon. A contextual first-exposure notice may be used
  for very short text where an inline label would harm usability.
- **LAW, chatbot/agent:** display the required AI-interaction notice from the
  start of the first interaction, unless the restrictive `obvious interaction`
  exception applies and is documented.

Use the reusable patterns in `assets/web/` and verify them in the target site's
real component and supported viewports.

## Delivery and post-publication verification

1. Check the served production asset after CDN, CMS, image optimisation,
   transcoding, and social preview generation. These stages can alter files or
   strip metadata.
2. Test wide and narrow viewports, keyboard access where interactive, screen
   reader naming, contrast, overlays, autoplay, and limited-duration notices.
3. Download and reshare through the supported path; verify that the visible
   disclosure and available provenance survive as intended.
4. Retain a proportionate evidence record: classification, tool/provider,
   source asset, markings found, chosen disclosure, review/editorial owner,
   publication URL/date, verification result, and correction history.
5. Provide a reporting route for missing or incorrect labels and correct a
   substantiated error without undue delay.

## Technical provenance

Content Credentials/C2PA can carry signed provenance and AI-related source
information, but it is not automatically an Article 50 safe harbour. When the
current C2PA specification is used, follow its current `c2pa.actions`,
`digitalSourceType`, ingredient, and AI-disclosure rules and validate the
manifest. Do not hard-code an older specification without the live preflight.
