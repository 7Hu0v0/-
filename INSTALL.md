# 安装说明

## Codex

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

安装后，在 Codex 里说：

```text
使用 create-ex 帮我做一个前任 skill
```

## Claude Code

```bash
mkdir -p ~/.claude/skills
git clone https://github.com/7Hu0v0/- ~/.claude/skills/create-ex
```

然后说：

```text
/create-ex
```

## OpenClaw

```bash
git clone https://github.com/7Hu0v0/- ~/.openclaw/workspace/skills/create-ex
```

重启 session 后说：

```text
帮我创建一个前任 skill
```

## 依赖

基础功能只需要 Python 3.9+。

推荐安装：

```bash
pip3 install -r requirements.txt
```

可选：

```bash
pip3 install Pillow
```

## 快速验证

```bash
cd ~/.codex/skills/create-ex
python3 tools/wechat_parser.py --help
python3 tools/imessage_parser.py --help
python3 tools/photo_analyzer.py --help
python3 tools/skill_writer.py --action list --base-dir ./exes
```

## 数据准备

- 微信：推荐用 WechatExporter 导出 txt/html。
- iMessage：可使用导出文件；直接读取 `chat.db` 需要 macOS Full Disk Access 权限。
- 照片：放到同一文件夹，工具只提取 EXIF 时间线。
- 社交媒体：使用平台提供的数据导出或自己整理成 JSON/TXT。
- 没有文件也可以：只用你的描述生成一个初版，再后续修正。
