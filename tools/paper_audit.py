#!/usr/bin/env python3
"""Recompute every quantitative claim in the process paper from the record.

The paper's first method rule is 'artifacts over process': claims are
verified against the artifact, not against assertions about it. This script
is that rule applied to the paper itself. It reads data/critique_corpus.json
(the verbatim afternoon utterance record) and the git log, and prints the
numbers the paper quotes. If the paper and this output disagree, the paper
is wrong.

    python3 tools/paper_audit.py
"""
import json, os, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
LOOP_START, LOOP_END = "83dc417", "f77ef68"   # first and last repair commits
REVIEW_COMMIT = "4a96210"                      # interleaved review-response commit


def git(*args):
    return subprocess.run(["git", "-C", REPO] + list(args),
                          capture_output=True, text=True).stdout


def main():
    corpus = json.load(open(os.path.join(REPO, "data", "critique_corpus.json")))
    allutt = corpus["utterances"]
    utt = [u for u in allutt if not u.get("window")]          # day 1, afternoon loop
    day2 = [u for u in allutt if u.get("window") == "submission"]
    crit = [u for u in utt if u["category"] in
            ("defect", "escalation", "verification", "redirection")]
    excluded = [u for u in utt if u not in crit]

    print("== utterances (critique channel, afternoon loop) ==")
    print("critique utterances:", len(crit))
    print("words:", sum(len(u["text"].split()) for u in crit))
    by = {}
    for u in crit:
        by.setdefault(u["category"], []).append(u["id"])
    for k in ("defect", "escalation", "verification", "redirection"):
        print(f"  {k}: {len(by.get(k, []))}  (ids {by.get(k, [])})")
    print("multi-label (secondary) flags:",
          sum(1 for u in crit if u.get("secondary")))
    print("excluded from critique counts:",
          [(u["id"], u["category"]) for u in excluded])
    print("screenshot messages in window:", len(corpus["screenshot_messages"]))

    print("\n== commits (afternoon loop) ==")
    log = git("log", "--reverse", "--format=%h %ad %s",
              "--date=format:%H:%M", f"{LOOP_START}~1..{LOOP_END}")
    lines = log.strip().splitlines()
    repair = [l for l in lines if not l.startswith(REVIEW_COMMIT)]
    print(f"repair commits: {len(repair)} "
          f"(+1 interleaved review commit {REVIEW_COMMIT})")
    for l in lines:
        print("  " + l)

    print("\n== inserted lines (repair commits, excluding the review commit) ==")
    def shortstat(rng, *paths):
        out = git("diff", "--shortstat", *rng, "--", *paths) if paths else \
              git("diff", "--shortstat", *rng)
        return out.strip()
    # the review commit's insertions (generated audit appendix) are excluded
    first = shortstat((f"{LOOP_START}~1", LOOP_START))
    rest = shortstat((REVIEW_COMMIT, LOOP_END))
    rest_tools = shortstat((REVIEW_COMMIT, LOOP_END), "tools/")
    first_tools = shortstat((f"{LOOP_START}~1", LOOP_START), "tools/")
    print("first repair commit:", first)
    print("  of which tools/:", first_tools)
    print("remaining repair span:", rest)
    print("  of which tools/:", rest_tools)

    print("\n== per-episode commit check ==")
    for u in crit:
        if u.get("commit"):
            subj = git("log", "-1", "--format=%s", u["commit"]).strip()
            print(f"  utterance {u['id']:>2} -> {u['commit']} {subj[:60]}")

    if day2:
        d2crit = [u for u in day2 if u["category"] in
                  ("defect", "escalation", "verification", "redirection")]
        print("\n== utterances (second window: submission prep, 11--14 July) ==")
        print("critique utterances:", len(d2crit))
        print("words:", sum(len(u["text"].split()) for u in d2crit))
        by2 = {}
        for u in d2crit:
            by2.setdefault(u["category"], []).append(u["id"])
        for k in ("defect", "escalation", "verification", "redirection"):
            if by2.get(k): print(f"  {k}: {len(by2[k])}  (ids {by2[k]})")
        print("excluded:", [(u["id"], u["category"]) for u in day2 if u not in d2crit])
        print("answering commits (submission window):")
        log2 = git("log", "--reverse", "--format=%h %ad %s",
                   "--date=format:%H:%M", "d43519f~1..babbbbf")
        for l in log2.strip().splitlines():
            print("  " + l)


def emit_appendix():
    """Write paper/critique_appendix.tex from the corpus — the same
    no-drift pattern as the orthography paper's audit appendix."""
    corpus = json.load(open(os.path.join(REPO, "data", "critique_corpus.json")))
    esc = lambda t: (t.replace("&", "\\&").replace("%", "\\%").replace("#", "\\#")
                      .replace("_", "\\_"))
    def rowset(us):
        rows = []
        for u in us:
            cat = u["category"] + ("*" if u.get("secondary") else "")
            commit = u.get("commit") or "—"
            rows.append(f"{u['id']} & {esc(u['text'])} & {cat} & \\texttt{{{commit}}} \\\\")
        return "\n".join(rows)
    day1 = [u for u in corpus["utterances"] if not u.get("window")]
    day2 = [u for u in corpus["utterances"] if u.get("window") == "submission"]
    body = rowset(day1)
    if day2:
        body += ("\n\\midrule\n\\multicolumn{4}{@{}l}{\\emph{Second window: the submission day (11 July); "
                 "timestamps approximated by the answering commit.}} \\\\\n\\midrule\n" + rowset(day2))
    tex = ("% GENERATED by tools/paper_audit.py --emit-appendix — edit the corpus, not this file\n"
           "\\begin{longtable}{@{}p{0.04\\linewidth}p{0.66\\linewidth}p{0.13\\linewidth}p{0.09\\linewidth}@{}}\n"
           "\\toprule\n"
           "\\# & Utterance (verbatim; typos preserved) & Category & Commit \\\\\n"
           "\\midrule\n\\endhead\n" + body + "\n\\bottomrule\n\\end{longtable}\n")
    out = os.path.join(REPO, "paper", "critique_appendix.tex")
    open(out, "w").write(tex)
    print("wrote", out, f"({len(corpus['utterances'])} rows)")


if __name__ == "__main__":
    import sys
    if "--emit-appendix" in sys.argv:
        emit_appendix()
    else:
        main()
