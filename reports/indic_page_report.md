# A11yway Accessibility Report

## Summary

- Source: examples/sample_indic_page.html
- Source type: file
- Issues found: 4
- Agents used: Keyboard-only student
- Checks run: html_form_labels, interactive_names, image_alt_text, heading_structure, page_metadata, media_accessibility, indic_language_checks

### Counts By Severity

- high: 3
- medium: 1

### Counts By Issue Type

- missing_lang_indic: 2
- lang_mismatch: 1
- mixed_script_element: 1

## Issues Found

### 1. Indic-script text lacks a matching lang attribute

- Issue type: missing_lang_indic
- Rule: Indic-script text lacks a matching lang attribute
- Category: Language
- Severity: high
- Why it matters: Text-to-speech picks a voice from the declared language, so Devanagari, Gurmukhi, Tamil, or other Indic-script text under a missing or non-matching lang is read as garbled English.
- Suggested fix: Add a lang attribute matching the text's language (for example lang="pa" for Gurmukhi) on the element or a fitting ancestor.
- Manual review: Confirm the actual language: several languages share a script (Hindi and Marathi both use Devanagari), so the right lang value needs a human decision.
- Static check limitation: Script detection uses Unicode ranges and is a heuristic. Transliterated text (Hindi written in Latin letters) cannot be detected at all.

Evidence:

- tag: p
- line: 18
- reason: Devanagari text inherits lang="en", which does not match the script, so text-to-speech reads it with the wrong voice.

```html
छात्रवृत्ति के लिए आवेदन की अंतिम तिथि 15 अगस्त है।
```

### 2. Indic-script text lacks a matching lang attribute

- Issue type: missing_lang_indic
- Rule: Indic-script text lacks a matching lang attribute
- Category: Language
- Severity: high
- Why it matters: Text-to-speech picks a voice from the declared language, so Devanagari, Gurmukhi, Tamil, or other Indic-script text under a missing or non-matching lang is read as garbled English.
- Suggested fix: Add a lang attribute matching the text's language (for example lang="pa" for Gurmukhi) on the element or a fitting ancestor.
- Manual review: Confirm the actual language: several languages share a script (Hindi and Marathi both use Devanagari), so the right lang value needs a human decision.
- Static check limitation: Script detection uses Unicode ranges and is a heuristic. Transliterated text (Hindi written in Latin letters) cannot be detected at all.

Evidence:

- tag: p
- line: 21
- reason: Gurmukhi text inherits lang="en", which does not match the script, so text-to-speech reads it with the wrong voice.

```html
ਵਜ਼ੀਫ਼ੇ ਲਈ ਅਰਜ਼ੀ ਦੀ ਆਖਰੀ ਮਿਤੀ 15 ਅਗਸਤ ਹੈ।
```

### 3. Declared lang contradicts the text's script

- Issue type: lang_mismatch
- Rule: Declared lang contradicts the text's script
- Category: Language
- Severity: high
- Why it matters: A lang attribute promising one language over text written in a different script makes screen readers pick the wrong voice, which is worse than no declaration at all.
- Suggested fix: Correct the lang attribute to match the language actually written in the element.
- Manual review: Languages sharing a script cannot be told apart here; the check only fires when the script itself contradicts the declaration.
- Static check limitation: Script detection uses Unicode ranges and cannot judge transliterated or romanized text.

Evidence:

- tag: p
- line: 24
- reason: The element declares lang="ta" but its text is dominantly Devanagari script, so a screen reader picks the wrong voice.

```html
आवेदन पत्र स्कूल कार्यालय से प्राप्त करें।
```

### 4. Latin and Indic scripts mix without a lang boundary

- Issue type: mixed_script_element
- Rule: Latin and Indic scripts mix without a lang boundary
- Category: Language
- Severity: medium
- Why it matters: When one text run mixes scripts without lang-tagged boundaries, speech engines cannot switch voices and commonly garble one of the languages.
- Suggested fix: Wrap each language's text in an element with the matching lang attribute so speech engines can switch voices.
- Manual review: Short mixes are often fine; the check already ignores numbers, short acronyms, and single loanwords, but listen with a real screen reader to confirm impact.
- Static check limitation: A conservative heuristic: it requires several Latin words next to Indic text in one text node and may miss subtler mixes or flag intentional bilingual lines.

Evidence:

- tag: p
- line: 27
- reason: One text node mixes Devanagari text with 5 Latin words and no lang-tagged boundary, which commonly garbles text-to-speech.

```html
Please bring your income certificate क्योंकि यह आवेदन के लिए आवश्यक है।
```

## Limitations

- This prototype only runs static HTML checks.
- It does not replace a full human accessibility audit.
- It does not yet perform browser-based interaction testing.
