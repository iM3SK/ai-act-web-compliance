# Web Implementation Guide

Use these patterns only after the live legal preflight and content
classification. They demonstrate accessible disclosure mechanics; they do not
decide whether Article 50 applies.

## Reusable assets

- `assets/web/ai-disclosure.css` contains a small component style.
- `assets/web/examples.html` demonstrates image, video, audio, text, and
  chatbot placements using the bundled SVG icons.
- `assets/eu-icons/svg/` is preferred for web delivery; PNG variants support
  systems that cannot render SVG.

Copy only the required assets into the owning website project. Keep the
original source and licence record with the implementation.

## Implementation contract

1. Put the disclosure in the server-rendered or initial accessible DOM when it
   is needed at first exposure. Do not depend on a delayed third-party script.
2. Pair the icon with visible text. Use an empty image `alt` when the adjacent
   text already conveys the same meaning.
3. Use an `<aside>`, `<p>`, `<figcaption>`, or other native semantic element
   appropriate to the content. Do not add an ARIA role that duplicates native
   semantics.
4. Position an image/video badge in the same containing block as the media.
   Reserve enough space and z-index so cookie banners, player controls, and
   other overlays do not cover it.
   Put custom playback or fullscreen controls in a dedicated non-overlapping
   toolbar or reserved layout row. Never absolutely position a custom control
   over the native media control strip. When fullscreen must include a sibling
   disclosure, fullscreen the labelled wrapper and keep its custom toolbar
   outside the native control surface.
5. **CODE implementation:** For audio-only deepfakes, edit the audio master to
   include the audible disclaimer at the beginning. The visible HTML label is
   an additional cue, not a substitute.
6. Do not present an EU AI-content icon as the prescribed Article 50(1) chatbot
   notice. A clear text notice can satisfy the interaction disclosure; assess
   its design separately from Article 50(4) content labelling.
7. When a CMS creates downloads, thumbnails, social cards, or transcoded video,
   propagate the disclosure to those outputs and verify the final URLs.
8. Keep second-layer details optional and supplemental. The first layer must
   already disclose artificial generation or manipulation.

## Target-site verification

Verify the integrated component, not only the bundled example:

- narrow and wide viewports;
- light, dark, and actual media backgrounds;
- keyboard access and visible focus for any details control;
- screen-reader announcement without duplicated or missing wording;
- video controls, captions, fullscreen, picture-in-picture, and overlays;
- autoplay and interruption behavior for audio/video;
- production CDN/CMS output, download, and reshare paths;
- console and network errors.

If any required route or assistive-technology check cannot be run, record it as
a coverage gap rather than claiming complete accessibility.
