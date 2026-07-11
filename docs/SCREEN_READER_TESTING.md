# Screen-Reader Testing

`--screen-reader --screen-reader-engine chromium --announce-transcript` uses Chromium accessibility-tree evidence from the browser run to build an ordered announcement transcript.

It can detect empty computed names, repeated confusing announcements, and focus landing in hidden accessibility-tree content. Native NVDA, JAWS, VoiceOver, and TalkBack adapters are scaffolded and capability-reported, but A11yway does not claim they ran unless the adapter actually runs.

Chromium tree evidence is deterministic browser evidence, not full screen-reader certification.
