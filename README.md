# 前任 Claw / Create Ex Skill

把聊天记录、照片时间线、社交媒体导出和你的主观描述，整理成一个本地 AI persona skill。这个版本基于 [perkfly/ex-skill](https://github.com/perkfly/ex-skill) 做 Codex 适配，同时保留 Claude Code 和 OpenClaw 的安装思路。

它适合做：

- Codex skill：`~/.codex/skills/create-ex`
- Claude Code skill：`~/.claude/skills/create-ex`
- OpenClaw skill：`~/.openclaw/workspace/skills/create-ex`

> 这不是为了冒充真实的人。请把它当作基于记忆材料的本地反思、角色练习或写作 persona。

## 支持的数据来源

| 来源 | 支持内容 |
| --- | --- |
| 微信聊天记录 | WechatExporter 等工具导出的 txt/html/csv |
| iMessage | macOS `chat.db` 或导出文件 |
| 短信 | XML/CSV/TXT |
| 照片 | EXIF 日期、地点等元数据时间线 |
| 社交媒体 | 微博、豆瓣、小红书、Instagram 导出 |
| 其他文件 | PDF、截图、Markdown、TXT |
| 手动描述 | 只靠昵称、关系信息、性格标签也能生成 |

## 安装

### Codex

全局安装：

```bash
mkdir -p ~/.codex/skills
git clone https://github.com/7Hu0v0/- ~/.codex/skills/create-ex
```

项目内安装：

```bash
mkdir -p .codex/skills
git clone https://github.com/7Hu0v0/- .codex/skills/create-ex
```

### Claude Code

```bash
mkdir -p ~/.claude/skills
git clone https://github.com/7Hu0v0/- ~/.claude/skills/create-ex
```

### OpenClaw

```bash
git clone https://github.com/7Hu0v0/- ~/.openclaw/workspace/skills/create-ex
```

### 可选依赖

```bash
pip3 install -r requirements.txt
```

`pypinyin` 用于把中文昵称转成 slug。照片扩展格式可按需安装 `Pillow`。

## 使用

在 Codex 里说：

```text
使用 create-ex 帮我做一个前任 skill
```

或：

```text
我想做一个前任 claw
```

然后按提示提供：

1. 昵称/代号
2. 关系基本信息
3. 性格画像
4. 可选原材料：聊天记录、照片文件夹、社交媒体导出、截图、PDF 或直接粘贴文本

默认会生成到当前项目的 `exes/{slug}/`。如果你希望 Codex 直接识别生成的人格 skill，可以让 Codex 写入 `~/.codex/skills/ex-{slug}/`。

## 从 iOS 微信备份导出单聊

仓库提供 `tools/ios_chat_exporter.py`，用于从 Finder/iTunes 未加密备份中提取出的新版微信 `message_N.sqlite` 合并单聊。每个联系人会话表名按微信内部 `user_id` 的 MD5 计算。

```bash
python3 tools/ios_chat_exporter.py \
  --source /path/to/message_2.sqlite wxid_example old_account \
  --source /path/to/message_3.sqlite wxid_example2 new_account \
  --output-dir /private/output \
  --basename merged_chat
```

输出：

```text
merged_chat.jsonl
merged_chat.txt
```

完整聊天记录包含高度敏感信息，不应提交到 GitHub。可用 `tools/chat_style_analyzer.py` 在本地生成风格证据摘要：

```bash
python3 tools/chat_style_analyzer.py merged_chat.jsonl --output style_evidence.md
```

## 项目结构

```text
.
├── SKILL.md
├── agents/openai.yaml
├── prompts/
├── tools/
├── requirements.txt
├── INSTALL.md
└── LICENSE
```

## 隐私提醒

- 聊天记录和亲密关系描述非常敏感，建议先脱敏。
- 优先提供有代表性的小样本，不要默认上传完整历史。
- 生成内容只代表模型根据材料做出的推断，不等于真实人物本人。

## 来源

本项目基于 MIT 许可的 [perkfly/ex-skill](https://github.com/perkfly/ex-skill) 改造。
