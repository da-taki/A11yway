# Media Testing

`--media` inspects HTML audio/video/image animation evidence.

Checks include autoplay, controls, muted state, loop, caption tracks, caption language, transcript links, decorative background video review, and animated GIF review.

For local media files (`.mp3`, `.mp4`, `.webm`, and similar), A11yway uses optional media metadata tooling when available. If mutagen or an external media inspector is missing, it reports the local-media metadata module as unavailable instead of guessing.

Muted decorative background video is not automatically treated as a caption failure. A11yway does not infer missing audio description from the presence of video alone.
