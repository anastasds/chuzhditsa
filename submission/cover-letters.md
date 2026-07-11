# Draft cover letters

Drafts for the recommended first-choice venues. Placeholders in `[brackets]`
are **[you]** to fill (arXiv IDs once assigned, DOI once minted, contact
details). The builder finalizes wording once the venue and any format limits
are confirmed. All three disclose the AI-authorship arrangement up front,
because at these venues the disclosure is a point in the work's favor, not a
liability to bury.

---

## Typeface paper → *TUGboat*

Dear Editors,

I am submitting *The letter as a program: constructing the Chuzhditsa typeface*
for consideration in *TUGboat*. It is a case study in parametric typeface
construction that takes up Knuth's thesis directly: a four-style Cyrillic
family generated with no drawn master at any point, from centerline primitives
expanded by a roughly seven-hundred-line engine in which terminals, joins,
optical corrections, fitting, and OpenType behavior are all code. The paper's
core is not that a font can be generated but the concrete taxonomy of how
naive centerline expansion fails typographically -- folding concave joins,
clogging arcs, unadapted fitting -- and how each failure was diagnosed and
repaired, with the engine's OpenType layer functioning as a machine-testable
reference implementation of the writing system it serves.

The conceptual claim is scoped to what the artifact supports: parametric type
fails as a theory of all letterforms and succeeds as a theory of one design
language at a time -- Hofstadter's half of the 1982 debate for the quantifier
"all," Knuth's for "one at a time." The complete source, fonts, and shaping-
test harness are public at https://github.com/anastasds/chuzhditsa (Zenodo DOI to be minted); a preprint is at
arXiv:[id]. The work was constructed and drafted by a language model under my
direction and criticism; that process is itself documented in a companion
paper, and I take full authorial responsibility for the submission.

I am glad to supply the binaries and build toolchain to reviewers, and I note
that expert Cyrillic type review would strengthen the paper -- a review I would
welcome the journal arranging.

Sincerely,
Anastas Stoyanovsky
Unaffiliated · anastas@stoyanovs.ky

---

## Orthography paper → *Written Language & Literacy*

Dear Editors,

I am submitting *Chuzhditsa: a phonological citation register for Cyrillic* for
consideration. The paper identifies a
functional layer that most orthographies lack -- phonological citation, between
loanword adaptation and technical transcription -- and works out one concrete,
implementable occupant of it for Slavic Cyrillic: a compositional grammar of
diacritic operations assembled from attested Cyrillic material, a prosodic
stratum, and a register-marking typeface whose Glagolitic-derived forms carry
the "foreignness" signal that Japanese distributes over katakana.

I want to be exact about the paper's claims, because the scoping is deliberate.
It demonstrates a coherent, technically implementable candidate, evaluated
against the phonologies of twenty languages by an internally scored coverage
audit; it does *not* claim communicative success. Whether readers recover
pronunciations, whether transcribers converge, and whether the typeface reads
as "citation" rather than "archaic" are empirical questions I identify as the
next study rather than answer here. The full mapping, the machine-readable
audit dataset, and the fonts are public at https://github.com/anastasds/chuzhditsa (Zenodo DOI to be minted); a
preprint is at arXiv:[id]. A companion paper documents the typeface's
construction, and the system was constructed and drafted by a language model
under my direction, for which I take full authorial responsibility.

I would welcome review by a phonologist of the target inventories and by a
specialist in Cyrillic orthographic adaptation, and would value the editors'
help in arranging it.

Sincerely,
Anastas Stoyanovsky
Unaffiliated · anastas@stoyanovs.ky

---

## Process paper → *Digital Creativity*

Dear Editors,

I am submitting *The critic and the builder: how the Chuzhditsa papers were
written* as a research-through-design case study. It documents an unusual
configuration in human-AI creative production: over one day, a language model
built a designed writing system, a parametric typeface, and their academic
papers, while I -- neither linguist nor type designer -- contributed no code
and almost no prose, only criticism: twenty-five artifact-level verdicts
totalling 401 words, withholding directions toward solutions by design. The
paper's finding is that this criticism changed the builder's operative method,
not merely its outputs, and it is unusually auditable for an n=1 account: the
complete utterance corpus, the commit history, and an audit script that
recomputes every count (and that caught the paper's own earlier miscount) ship
with it.

I present it strictly as a documented case worth instrumenting, not as a
demonstration of a superior workflow, and the limitations section is candid
about n=1, retrospective intent, and a favorable task. The paper was itself
drafted by the participating model under my direction, which the manuscript
discloses and analyzes as part of its subject; I take full authorial
responsibility. The companion papers it studies are public at
https://github.com/anastasds/chuzhditsa and at arXiv:[id typeface], arXiv:[id orthography], so the
artifacts it describes are independently inspectable.

Sincerely,
Anastas Stoyanovsky
Unaffiliated · anastas@stoyanovs.ky
