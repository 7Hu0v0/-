---
name: create-ex
description: Create and maintain a Codex-compatible ex persona skill from user-provided relationship descriptions, chat exports, iMessage/SMS files, photo metadata, or social media exports. Use when the user asks to create, distill, update, correct, list, rollback, or delete an "前任 skill", "ex skill", or "前任 claw".
---

# Create Ex Skill

Use this skill to help the user build a local AI persona from materials they provide. It is adapted for Codex first, while keeping the prompt and parser layout compatible with Claude Code and OpenClaw style skill folders.

Always match the user's language. For Chinese requests, respond in Chinese.

## Privacy And Boundaries

- Treat all relationship data as sensitive. Ask the user to provide only material they are comfortable processing in the current AI session.
- Prefer small representative excerpts over full private archives when possible.
- Do not help deceive, harass, impersonate the real person in real-world communications, or claim the generated persona is the actual person.
- Frame the output as a local reflective/roleplay skill built from user-provided memories.

## Triggers

Start creation when the user says things like:

- `帮我创建一个前任 skill`
- `我想做一个前任 claw`
- `我想蒸馏一个前任`
- `新建前任`
- `create an ex skill`

Enter update mode when the user says:

- `我有新聊天记录`
- `追加`
- `这不对`
- `她不会这样`
- `她应该是...`
- `update this ex skill`

List or manage existing skills when the user says:

- `/list-exes`
- `/ex-rollback {slug} {version}`
- `/delete-ex {slug}`

## Paths

The skill directory is the folder containing this `SKILL.md`.

Common install locations:

- Codex global: `~/.codex/skills/create-ex`
- Codex project-local: `.codex/skills/create-ex`
- Claude Code global: `~/.claude/skills/create-ex`
- Claude Code project-local: `.claude/skills/create-ex`
- OpenClaw: `~/.openclaw/workspace/skills/create-ex`

Default generated persona directory:

- In a project: `./exes/{slug}/`
- Global Codex install target, when the user wants Codex to discover generated personas directly: `~/.codex/skills/ex-{slug}/`

When running scripts, use absolute paths when possible:

```bash
python3 /path/to/create-ex/tools/wechat_parser.py --help
```

If a Claude environment variable exists, `${CLAUDE_SKILL_DIR}` may still be used. In Codex, resolve the directory explicitly instead.

## Bundled Resources

- `prompts/intake.md`: optional intake question reference
- `prompts/memories_analyzer.md`: shared memory extraction dimensions
- `prompts/persona_analyzer.md`: persona extraction and tag translation
- `prompts/memories_builder.md`: `memories.md` generation template
- `prompts/persona_builder.md`: `persona.md` generation template
- `prompts/merger.md`: incremental update guidance
- `prompts/correction_handler.md`: correction handling guidance
- `tools/wechat_parser.py`: WeChat export parser
- `tools/imessage_parser.py`: iMessage parser
- `tools/sms_parser.py`: SMS parser
- `tools/photo_analyzer.py`: EXIF timeline extractor
- `tools/social_media_parser.py`: social export parser
- `tools/skill_writer.py`: writes generated skill files
- `tools/version_manager.py`: lists and rolls back versions

Load prompt files only when needed for the current step.

## Creation Flow

### 1. Intake

Ask only these three questions first:

1. 昵称/代号是什么？这是必填项。
2. 基本信息一句话：在一起多久、怎么认识、分手多久、她做什么，想到什么写什么。
3. 性格画像一句话：MBTI、星座、依恋类型、恋爱标签、你对她的印象。

Summarize the answers and continue unless the user corrects them.

### 2. Source Material

Ask how the user wants to provide source material:

```text
原材料怎么提供？

[A] 微信聊天记录：导出的 txt/html 文件
[B] iMessage / 短信：chat.db 或导出文件
[C] 照片：指定文件夹，只提取 EXIF 时间线
[D] 社交媒体：微博/豆瓣/小红书/Instagram 导出
[E] 其他文件：PDF / 图片截图 / 任意文本
[F] 直接粘贴：复制内容到对话里
[G] 跳过：只用手动描述生成
```

The user may mix sources.

### 3. Parse Source Material

Use these commands with the actual skill directory path:

```bash
python3 {skill_dir}/tools/wechat_parser.py --file {path} --target "{name}" --output /tmp/wechat_out.txt
python3 {skill_dir}/tools/imessage_parser.py --file {path} --target "{phone_or_name}" --output /tmp/imessage_out.txt
python3 {skill_dir}/tools/imessage_parser.py --direct --target "{phone_or_name}" --output /tmp/imessage_out.txt
python3 {skill_dir}/tools/sms_parser.py --file {path} --target "{phone_or_name}" --output /tmp/sms_out.txt
python3 {skill_dir}/tools/photo_analyzer.py --dir {photo_directory} --output /tmp/photo_timeline.txt
python3 {skill_dir}/tools/social_media_parser.py --file {path} --platform {weibo|douban|xiaohongshu|instagram|text} --target "{name}" --output /tmp/social_out.txt
```

Read the generated `/tmp/*_out.txt` files before analysis.

For PDFs, screenshots, and pasted text, read or inspect them directly with the available Codex tools.

### 4. Analyze

Use the relevant prompt references:

- Memories: relationship timeline, shared routines, preferences, conflict patterns, emotional dynamics.
- Persona: speech style, emotional logic, attachment style, conflict behavior, boundaries, correction rules.

Avoid inventing precise facts not supported by the user's description or source material. Mark uncertain inferences as inferred.

### 5. Preview

Show a short preview before writing:

```text
共同记忆摘要：
- 在一起：...
- 重要时刻：...
- 日常仪式：...
- 她的偏好：...

Persona 摘要：
- 核心性格：...
- 表达风格：...
- 吵架模式：...
- 关系里的触发点：...
```

Ask for confirmation only when the next step writes files or when the user gave ambiguous identity/source choices.

### 6. Write Files

Create this structure:

```text
exes/{slug}/
├── SKILL.md
├── memories.md
├── persona.md
├── meta.json
├── versions/
└── knowledge/
    ├── chats/
    ├── photos/
    └── social/
```

For Codex-global persona installation, write the same generated skill into:

```text
~/.codex/skills/ex-{slug}/
```

Use `tools/skill_writer.py` when content files are ready:

```bash
python3 {skill_dir}/tools/skill_writer.py --action create --slug {slug} --meta /tmp/ex_meta.json --memories /tmp/memories.md --persona /tmp/persona.md --base-dir ./exes
```

If writing directly into Codex global skills:

```bash
python3 {skill_dir}/tools/skill_writer.py --action create --slug ex-{slug} --meta /tmp/ex_meta.json --memories /tmp/memories.md --persona /tmp/persona.md --base-dir ~/.codex/skills
```

## Update Flow

When appending new source material:

1. Parse/read the new material.
2. Read existing `memories.md`, `persona.md`, and `meta.json`.
3. Use `prompts/merger.md`.
4. Back up the current version.
5. Append only incremental changes.
6. Regenerate `SKILL.md`.
7. Update `meta.json`.

When the user corrects the persona:

1. Use `prompts/correction_handler.md`.
2. Decide whether the correction belongs to memories, persona, or both.
3. Add a dated correction record.
4. Regenerate `SKILL.md`.

## Management Commands

List generated personas:

```bash
python3 {skill_dir}/tools/skill_writer.py --action list --base-dir ./exes
```

List versions:

```bash
python3 {skill_dir}/tools/version_manager.py --action list --slug {slug} --base-dir ./exes
```

Rollback:

```bash
python3 {skill_dir}/tools/version_manager.py --action rollback --slug {slug} --version {version} --base-dir ./exes
```

Delete only after the user clearly confirms:

```bash
rm -rf ./exes/{slug}
```
