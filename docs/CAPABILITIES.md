# A11yway Capabilities

Run:

```bash
python -m a11yway.main --capabilities
```

Capability states are `available_verified`, `available_untested`, `unavailable`, or `unsupported_on_current_platform`.

The command reports Playwright, Chromium/Firefox/WebKit launch status, Windows support, NVDA/JAWS/VoiceOver/TalkBack adapter status, ADB devices, PDF and Office parsing libraries, FFmpeg, and optional Python libraries. Missing optional tools disable only the related adapter; core static checks continue.
