# Mobile Testing

`--mobile --device android-small --orientation portrait --orientation landscape` runs Playwright device emulation.

Checks include viewport overflow, small touch targets, orientation metadata, hover-dependent hooks, and mobile-layout observations. Device profiles include `android-small`, `android-large`, `iphone-small`, `iphone-large`, and `tablet`.

Playwright emulation is useful evidence, but it is not equivalent to real TalkBack or mobile VoiceOver testing.
