# Create Ex Skill

Create a local AI persona skill from relationship descriptions, selected chat exports, photo metadata, social media exports, screenshots, PDFs, or pasted text.

This repository is adapted from [perkfly/ex-skill](https://github.com/perkfly/ex-skill) for Codex, while keeping the folder layout usable in Claude Code and OpenClaw.

## Install

Codex global install:

```bash
mkdir -p ~/.codex/skills
git clone https://github.com/7Hu0v0/- ~/.codex/skills/create-ex
```

Codex project-local install:

```bash
mkdir -p .codex/skills
git clone https://github.com/7Hu0v0/- .codex/skills/create-ex
```

Claude Code:

```bash
mkdir -p ~/.claude/skills
git clone https://github.com/7Hu0v0/- ~/.claude/skills/create-ex
```

OpenClaw:

```bash
git clone https://github.com/7Hu0v0/- ~/.openclaw/workspace/skills/create-ex
```

Optional dependencies:

```bash
pip3 install -r requirements.txt
```

## Usage

In Codex, say:

```text
Use create-ex to help me create an ex persona skill.
```

The skill will ask for:

1. A nickname or codename
2. A one-line relationship summary
3. A one-line personality impression
4. Optional source material

Generated personas are written to `exes/{slug}/` by default. If you want Codex to discover the generated persona directly, ask it to write the generated skill to `~/.codex/skills/ex-{slug}/`.

## Privacy

Relationship data is sensitive. Prefer representative excerpts, remove private identifiers where possible, and do not use the generated persona to impersonate or deceive the real person.
