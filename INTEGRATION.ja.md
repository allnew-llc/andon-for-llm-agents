[English](./INTEGRATION.md)

# 導入ガイド

## 概要

このガイドでは、ANDON for LLM Agents を Claude Code プロジェクトに完全に導入する方法を説明します。

## アーキテクチャ

```
┌────────────────────────────────────────────────────────────┐
│                    Claude Code Session                       │
│                                                              │
│  ┌──────────┐   PreToolUse    ┌───────────────────────┐    │
│  │  Agent    │ ──────────────→ │ tps-andon-pretool     │    │
│  │  (Bash)   │                 │ - quote validation     │    │
│  │           │                 │ - ANDON block check    │    │
│  │           │   PostToolUse   │                        │    │
│  │           │ ──────────────→ │ tps-andon-posttool    │    │
│  │           │                 │ → tps-kaizen-runtime   │    │
│  │           │                 │   - failure classify   │    │
│  │           │                 │   - incident create    │    │
│  │           │                 │   - auto-standardize   │    │
│  │           │                 │                        │    │
│  │           │   PostToolUse   │ kaizen-learning-capture│    │
│  │           │ ──────────────→ │ - fix commit detection │    │
│  └──────────┘                 └───────────────────────┘    │
│                                         │                    │
│                                         ▼                    │
│                            ┌─────────────────────┐          │
│                            │  ~/.claude/state/    │          │
│                            │  ├── andon-open.json │          │
│                            │  └── kaizen/         │          │
│                            │      ├── incidents/  │          │
│                            │      ├── registry    │          │
│                            │      └── history/    │          │
│                            └─────────────────────┘          │
└────────────────────────────────────────────────────────────┘
```

## ステップバイステップ セットアップ

### 1. ファイルのコピー

```bash
# プロジェクトルートから
mkdir -p .claude/hooks .claude/rules .claude/commands

# コアフック（必須）
cp hooks/tps-kaizen-runtime.py .claude/hooks/
cp hooks/tps-andon-posttool-guard.sh .claude/hooks/
cp hooks/tps-andon-pretool-guard.sh .claude/hooks/
cp hooks/tps-andon-control.sh .claude/hooks/
chmod +x .claude/hooks/*.sh

# 学習キャプチャフック（推奨）
cp hooks/kaizen-learning-capture.sh .claude/hooks/
chmod +x .claude/hooks/kaizen-learning-capture.sh

# Meta-ANDON ガード（パイプラインプロジェクトに推奨）
cp hooks/meta_andon_guard.py .claude/hooks/

# ルール（CLAUDE.md または .claude/rules/ に追加）
cp rules/70-kaizen-learning.md .claude/rules/
cp rules/45-quality-driven-execution.md .claude/rules/

# スキル（オプションだが推奨）
mkdir -p .claude/commands
cp skills/tps-kaizen/tps-kaizen.md .claude/commands/
# スキル本体とリファレンスを docs ディレクトリにコピー
cp -r skills/tps-kaizen docs/skills/tps-kaizen
```

### 2. フックの登録

`.claude/settings.json` に追加：

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [".claude/hooks/tps-andon-pretool-guard.sh"]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          ".claude/hooks/tps-andon-posttool-guard.sh",
          ".claude/hooks/kaizen-learning-capture.sh"
        ]
      }
    ]
  }
}
```

### 3. CLAUDE.md にルールを追加

方法 A：ルールファイルを参照

```markdown
# CLAUDE.md

## Rules
- `.claude/rules/70-kaizen-learning.md` — ANDON + Kaizen 学習キャプチャ
- `.claude/rules/45-quality-driven-execution.md` — 品質駆動実行
```

方法 B：インライン（ルールファイルを使用しない場合）

`rules/70-kaizen-learning.md` の内容を `CLAUDE.md` に直接コピーしてください。

### 4. インストールの確認

```bash
# フックが実行可能か確認
ls -la .claude/hooks/

# ランタイムのテスト
python3 .claude/hooks/tps-kaizen-runtime.py status
# 出力: "ANDON: CLEAR"

# 制御スクリプトのテスト
.claude/hooks/tps-andon-control.sh status
# 出力: "ANDON: CLEAR"
```

---

## 設定

### 環境変数

| 変数 | デフォルト | 説明 |
|------|----------|------|
| `ANDON_WORKSPACE` | （自動検出） | ワークスペースルートパスの上書き |
| `ANDON_STATE_DIR` | `<workspace>/.claude/state` | 状態ディレクトリの上書き |
| `ANDON_CONFIDENCE_AUTO` | `0.70` | 自動標準化の閾値 |
| `ANDON_CONFIDENCE_MANUAL` | `0.70` | この閾値未満はクローズ時に手動承認が必要 |
| `META_ANDON_FAILURE_THRESHOLD` | `3` | Meta-ANDON を発動する連続失敗回数 |

### 失敗パターンのカスタマイズ

`tps-kaizen-runtime.py` の `CLASSIFICATION_RULES` を編集：

```python
CLASSIFICATION_RULES = [
    # (cause_id, label, confidence, regex_pattern)
    ("my_custom_error", "My custom error", 0.90, r"my specific pattern"),
    # ... 既存ルールを維持 ...
]
```

### 前進系ブロックのカスタマイズ

`tps-andon-pretool-guard.sh` の `block_patterns` を編集してブロックコマンドを追加/削除：

```python
block_patterns = [
    r"\bgit\s+push\b",
    r"\bmy-deploy-command\b",  # 独自のコマンドを追加
    # ...
]
```

---

## 使い方

### 通常フロー（自動）

1. Claude Code でコーディング中
2. Bash コマンドが失敗（非ゼロ終了）
3. ANDON が自動的にオープン — インシデントレポートが表示される
4. 前進系コマンドがブロックされる
5. 問題を修正
6. 根本原因に対して Five Whys を実行
7. ANDON をクローズ：`.claude/hooks/tps-andon-control.sh close "root cause: X; prevention: Y"`

### 手動 ANDON

フックが検知しない問題に対して、ANDON を手動でオープンすることもできます：

```
/tps-kaizen andon "deployment failed silently with exit 0"
```

### ステータス確認

```bash
.claude/hooks/tps-andon-control.sh status
```

### 自動標準化のロールバック

自動生成された標準化ルールが間違っている場合：

```bash
.claude/hooks/tps-andon-control.sh rollback INC-20260305-abc123
# または最新をロールバック：
.claude/hooks/tps-andon-control.sh rollback latest
```

---

## スキル セットアップ（オプション）

`/tps-kaizen` スキルは構造化されたコマンドを提供します。セットアップ方法：

1. `skills/tps-kaizen/tps-kaizen.md` を `.claude/commands/tps-kaizen.md` にコピー
2. スキル内のファイルパスを docs ディレクトリを指すように更新
3. リファレンスファイルを `docs/skills/tps-kaizen/references/` にコピー

Claude Code で使用：
```
/tps-kaizen andon "tests are failing after dependency update"
/tps-kaizen five-whys "build fails on CI but passes locally"
/tps-kaizen kaizen "test coverage improvement"
/tps-kaizen audit
/tps-kaizen capture
```

---

## 既存パイプラインとの統合

### CI/CD 統合

Meta-ANDON ガードは CI の実行追跡と統合できます：

```python
from hooks.meta_andon_guard import evaluate_meta_andon

result = evaluate_meta_andon(
    artifacts_dir=Path("docs/pipeline"),
    consecutive_failures=3,
    failure_run_ids=["run-001", "run-002", "run-003"],
)

if result["blocked"]:
    print("Meta-ANDON: Blocked! Create required analysis artifacts first.")
    print(f"Missing: {result['missing_artifacts']}")
```

### カスタム状態ディレクトリ

プロジェクトが異なる状態ディレクトリを使用する場合：

```bash
export ANDON_STATE_DIR="/path/to/my/state"
```

---

## トラブルシューティング

### ANDON がクローズできない

**成果物の不足**：必要なファイルがすべて存在するか確認：
```bash
ls ~/.claude/state/kaizen/incidents/INC-*/
# evidence.json, analysis.json, actions.json, report.md が必要
```

**低信頼度**：根本原因の信頼度が 0.70 未満の場合、クローズ理由に `manual-approved:` を含めてください：
```bash
.claude/hooks/tps-andon-control.sh close "manual-approved: verified root cause was X"
```

### フックが動作しない

1. `.claude/settings.json` にフック設定があるか確認
2. フックファイルが実行可能か確認：`chmod +x .claude/hooks/*.sh`
3. Python 3 が利用可能か確認：`python3 --version`

### 状態ディレクトリの問題

ランタイムは状態ディレクトリを自動作成します。パーミッションエラーが出る場合：
```bash
mkdir -p ~/.claude/state/kaizen
```
