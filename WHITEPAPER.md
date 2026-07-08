# Chuzhditsa: what it is, in plain language

*A whitepaper for readers who don't do linguistics for a living.*

## The problem

Say you speak Bulgarian, or Serbian, or Ukrainian, and you want to write the word
*weekend*. Your alphabet has no letter for the English *w*, so you write у or в and hope.
Your neighbor picks the other one. A newspaper picks a third spelling, a subtitler a
fourth. The word *Thatcher* loses its *th*; *Washington* has circulated in two competing
spellings for a century (Вашингтон / Уошингтън). Every Cyrillic-writing language handles
foreign words this way: improvised, inconsistent, and lossy.

Japanese solved this problem centuries ago, and solved it twice over. Foreign words are
written in **katakana** — a separate set of characters that (1) follows fixed rules, so any
foreign word has exactly one spelling, and (2) *looks* different, so a reader instantly
knows the word is a guest. Nothing like this exists for Cyrillic.

Chuzhditsa (Bulgarian *чуждица*, "foreignism") is that missing thing: a designed extension
of Cyrillic that writes foreign words the way they actually sound, plus a typeface that
makes them visually recognizable — katakana's whole job, done for the Cyrillic world.

## How it works: three layers

**Layer 1 — your alphabet, untouched.** Bulgarian text stays Bulgarian; Serbian stays
Serbian. Chuzhditsa never changes how you write your own language.

**Layer 2 — new letters for missing sounds.** English *th*, the German *ü*, Arabic's deep
*h*, the *ng* of *ring*, French nasal vowels — sounds Cyrillic normally mangles each get a
letter. Here is the trick that keeps this from being an alphabet soup: almost nothing was
invented. The letters come from three honest sources:

- **Revivals.** Old Bulgarian had letters for nasal vowels — the yuses ѫ and ѧ — used in
  spelling until 1945. French *bonjour* finally gives them a job again: бѫжур.
- **Imports.** Some fifty languages write in Cyrillic, and they already built most of what's
  needed: Kazakh has қ and ң, Bashkir has ҙ for the *th* in *this*, Belarusian has ў for *w*,
  Serbian has џ for *j* in *jazz*. Chuzhditsa borrows them with the decades of real-world use
  they carry.
- **One rule, applied everywhere.** Where a letter still had to be derived, a small grammar
  of marks does it — each mark means exactly one thing. A hook below means "pronounced
  further back or off the native grid" (Bulgarian already does this: щ is just ш with a
  hook). Two dots mean "same vowel, said at the front of the mouth." A tiny raised һ means
  "with a puff of air" — which is how Hindi's four kinds of *t* all fit without a single new
  letter: т, тʰ, т̢, т̢ʰ.

**Layer 3 — optional music.** Stress marks, tone marks (for Mandarin or Vietnamese), and a
length mark. These live in dictionaries and textbooks, not in everyday text — exactly as
katakana ignores Japanese pitch accent and no one minds.

The result was tested against the twenty most-spoken languages in the world, from English
and Arabic to Hindi and Korean. English *thanks* comes out ҫӓңкс — three sounds Bulgarian
couldn't write, each now unambiguous. And the system is deterministic: two people
transcribing the same word arrive at the same spelling, which is the entire point.

## The typeface is half the idea

Rules alone don't give you katakana's second superpower — recognizing a foreign word at a
glance. That job belongs to the **Chuzhditsa typeface**: four styles (regular, bold, italic,
bold italic), built entirely by code, in which foreign words are meant to be set. Its look
is borrowed from **Glagolitic**, the ornate, loopy first Slavic alphabet of 863 AD, which
Cyrillic later displaced. There's a deliberate poetry in that: the oldest Slavic letterforms
now mark the newest words.

The font is also where the spelling rules become physical. When you type нь, the font fuses
it into one letter-shape (the same fusion Vuk Karadžić performed for Serbian in 1818). When
you type the soft sign plus an old nasal, out comes the medieval ligature ѩ. The rules of
the writing system are literally executable code inside the font files.

Everything uses real Unicode characters — no private hacks — so chuzhditsa text can be
typed, copied, searched, and indexed like any other text.

## One system, many languages

Chuzhditsa was piloted on Bulgarian but works for the whole Slavic family. The font covers
every Slavic Cyrillic alphabet (Russian, Ukrainian, Belarusian, Serbian, Macedonian,
Bulgarian), and Latin-written Slavic languages map in cleanly — Polish *ą* turns out to be
the direct descendant of the very yus the system revives. Some languages profit even for
their *own* sounds: Slovak *ä* and Slovenian's unwritten schwa both finally get letters. As
an outside test, Albanian — not Slavic at all — fit without a single new rule.

A few honest limits, stated rather than hidden: all the world's r-sounds collapse into р;
six-tone languages get squeezed into four marks; click consonants are future work. And one
firm boundary: chuzhditsa marks *words*, never *speakers*. Writing someone's accented
speech in the foreign register — the ugly trick sometimes played with katakana — is the one
use the design explicitly rejects.

## About the name

In prescriptive Bulgarian, a *чуждица* is a foreign word the language would supposedly be
better off without — the purist's sneer. The name is chosen against that usage. Where
purism hands the foreign word an expulsion order, this system hands it a well-made costume
and a seat at the table.

## What exists today

- **8 font files** (4 styles × TTF/OTF), free under the SIL Open Font License
- **The specification** in English, Bulgarian, and Ukrainian, with ~125 worked examples
  across 20 languages, plus short guides in Slovak, Serbian, Croatian, Slovenian, Bosnian,
  Macedonian, and Albanian
- **A type specimen** (`specimen.html`) you can open in any browser
- **A machine-readable sound-to-letter table** (`data/chuzhditsa.json`) for building tools
- **An academic manuscript** (`paper/chuzhditsa.pdf`), typeset in the typeface it describes

Where could it realistically live? History gives clear instructions. Esperanto was easy to
learn and went nowhere: adopting it meant joining a new identity instead of exercising an
old one. Utah's Deseret alphabet had a church behind it and died anyway. The two winners
took the opposite path: Hangul, designed in the 1440s, survived four and a half *centuries*
in humble places — women's letters, popular fiction — before Korean nationalism raised it
to official status; and katakana never asked anyone to change anything at all, growing from
monks' margin notes into a standard over a thousand years. The lesson: change nothing that
exists, attach to an identity people already have, and live in a small niche until the
practice is real. So: dictionary pronunciation fields, where the IPA scares general
readers; language classrooms, as a Cyrillic-native bridge into English or Arabic or
Mandarin sounds; subtitles, museums, and newsrooms, for names standard transcription
mangles. It is not a petition to reform anyone's orthography — it's an extra register,
sitting beside your alphabet, for the words that arrive from abroad.

Думи от чужбина, писани на чуждица — *words from abroad, written in chuzhditsa.*
