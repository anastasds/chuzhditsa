# Chuzhditsa iOS keyboard

A custom iOS keyboard for the chuzhditsa extended-Cyrillic system: a Bulgarian
phonetic base layout where every extension letter lives on a long-press of its
featural base key (у → ў ӱ ӯ, с → ҫ, т → т̢ тʰ тӀ …), keycaps rendered in the
Chuzhditsa typeface, and a symbols page carrying the tone/length/aspiration
marks. No network access, no Full Access request — pure input.

## Layout logic

The long-press map *is* the featural grammar: each extension letter hides
behind the base letter it is derived from, so knowing the system means knowing
the keyboard. Combining marks (◌̄ ◌́ ◌̀ ◌̌ ◌̨ ◌̢) and the modifier letters
(ʰ ʱ Ӏ) sit on the 123 page and compose with whatever was just typed.

## Building (requires a Mac with Xcode 15+)

```sh
brew install xcodegen
cd ios
cp ../fonts/Chuzhditsa-Regular.otf Keyboard/     # keycap font, bundled as a resource
xcodegen generate
open Chuzhditsa.xcodeproj
```

In Xcode: select your development team on **both** targets (Signing &
Capabilities), then run the `ChuzhditsaApp` scheme on a device. Enable the
keyboard under Settings → General → Keyboard → Keyboards → Add New Keyboard →
Чуждица.

After `xcodegen generate`, add `Chuzhditsa-Regular.otf` to the
ChuzhditsaKeyboard target's resources if it isn't picked up automatically
(drag it into the Keyboard group with "ChuzhditsaKeyboard" membership checked).

## Publishing to the App Store

1. **Apple Developer Program** membership ($99/year) on your Apple ID.
2. In Xcode: Product → Archive with a Distribution certificate; upload via the
   Organizer to App Store Connect.
3. In App Store Connect: create the app (bundle id `com.anastasds.chuzhditsa`),
   fill the listing — screenshots of the keyboard in use, the hero image from
   `docs/hero.png` adapts well — and submit for review.
4. Review notes worth writing in advance: the keyboard requests **no Full
   Access** (App Review guideline 4.4 compliance), functions fully offline,
   and the container app contains setup instructions (also 4.4). Mention that
   the unusual characters are standard Unicode Cyrillic extensions.
5. Expect one review cycle of questions about the purpose of a specialty
   keyboard; linking the whitepaper in the review notes helps.

## Files

| File | Purpose |
|---|---|
| `project.yml` | XcodeGen project definition (app + keyboard extension) |
| `App/ChuzhditsaApp.swift` | Container app: setup instructions (bilingual) |
| `Keyboard/KeyboardViewController.swift` | The keyboard: keys, shift, long-press popups, font registration |
| `Keyboard/Layout.swift` | Layout data: rows + featural long-press alternates |
