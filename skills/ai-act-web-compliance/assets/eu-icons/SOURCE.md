# Official EU AI Content Icons

These 24 assets are byte-identical extracted files from the European
Commission archives downloaded on 20 August 2026. Only the filenames were
normalised.

## Source and licence

- Source page: [EU Icons for labelling AI-generated content](https://digital-strategy.ec.europa.eu/en/policies/eu-icons-labelling-ai-generated-content)
- Official SVG archive: [document 129546](https://ec.europa.eu/newsroom/dae/redirection/document/129546)
- Official PNG archive: [document 129547](https://ec.europa.eu/newsroom/dae/redirection/document/129547)
- SVG archive SHA-256:
  `F76707B69B546677B173975C018528E5E549E12AFB05550F32C2F46500FFBEFD`
- PNG archive SHA-256:
  `AEDC51656497A2E8F3E42798E5749A929952F5B262BAD368EE3057F58C0F52C7`

The Commission source page states that the icons are available for everyone
to use freely without attribution to the Commission or AI Office. Use by a
non-signatory must not be presented as adherence to the Code of Practice.
Recheck the live page before each compliance use.

## Filename mapping

| Normalised prefix | Original semantic label |
| ----------------- | ----------------------- |
| `ai-generated-`   | `LABEL_AI GENERATED`    |
| `ai-modified-`    | `LABEL_AI MODIFIED`     |
| `ai-basic-`       | `LABEL_AI`              |

| Normalised suffix | Original visual variant |
| ----------------- | ----------------------- |
| `black`           | `black`                 |
| `black-50`        | `black transparent`     |
| `white`           | `white`                 |
| `white-50`        | `white transparent`     |

The files in `SHA256SUMS.txt` allow byte-integrity verification after the
rename. Run `scripts/verify-pack.ps1` from the skill root.
