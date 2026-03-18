[English](./README.md)

# ANDON for LLM Agents

[![CI](https://github.com/allnew-llc/andon-for-llm-agents/actions/workflows/test.yml/badge.svg)](https://github.com/allnew-llc/andon-for-llm-agents/actions/workflows/test.yml)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)

**リーン生産方式（TPS）の原則を LLM 支援コーディングに適用。**

不良を後工程に流さない。すべての失敗から学ぶ。改善を体系的に標準化する。

---

## 課題

LLM コーディングエージェントには、時間を浪費し品質を低下させる構造的弱点があります：

1. **盲目的リトライループ** — コマンドが失敗すると、同じことを繰り返すか、場当たり的に変更する
2. **モグラ叩きデバッグ** — 1つのエラーを直すと別のエラーが出る、の繰り返し
3. **揮発する学び** — デバッグセッションの知見が会話の終了とともに消える
4. **サイレントな仕様逸脱** — エージェントが要件を暗黙に緩和してテストを通す
5. **Gate ゲーミング** — 品質の高い成果物を作る代わりに、チェック通過だけを最適化する

これらは特定の LLM のバグではなく、目標最適化システムの**構造的性質**です。

## 解決策：LLM エージェントのための TPS

リーン生産方式は、同様の問題を 2 本の柱で解決します：

### 柱 1：Jidoka（自働化）— 異常時停止

不良を検知したら、**ラインを即座に停止する**。不良を次工程に流さない。

```
検知 → 停止 → 修正 → 調査 → 再発防止 → 標準更新
```

LLM コーディングへの適用：
| TPS の概念 | ソフトウェアでの実践 |
|------------|-------------------|
| 異常検知 | 非ゼロ終了コード、テスト失敗、ビルドエラー |
| ライン停止（ANDON） | 前進系コマンド（push、deploy、publish）をブロック |
| 修正 | revert または最小限のパッチで正常状態を復元 |
| 調査 | 実際のコード/ログに基づく Five Whys 根本原因分析 |
| Poka-yoke | コンパイル時チェック、テスト、pre-commit フックの追加 |

### 柱 2：Kaizen（改善）— 学びを標準化する

すべての失敗は学びの機会。知見を捕捉し、適切な場所にルーティングし、標準を更新して同じ問題を二度と起こさない。

```
学びの捕捉 → 標準へルーティング → 更新 → 検証
```

防止レベル（常に L1〜L2 を目指す）：
| レベル | 種類 | 信頼性 | 例 |
|--------|------|--------|----|
| L1 | Poka-yoke（不可能にする） | 最高 | コンパイルエラー、型制約 |
| L2 | 自動検出 | 高 | テスト、CI チェック、リンタールール |
| L3 | 標準化 | 中 | ドキュメント、チェックリスト |
| L4 | 警告 | 低 | コメント、リマインダー |

---

## ANDON の位置づけ

ANDON はコーディングエージェントの代替ではなく、その周囲を包む**安全と学習のレイヤー**です。

主要 AI 企業はコーディングエージェントの安全メカニズムを導入しています：サンドボックス隔離（OpenAI Codex）、フックシステム（Anthropic Claude Code）、計画批評（Google Jules）、セキュリティスキャン（GitHub Copilot）、反復上限（Amazon Q）。これらはエージェントを**より賢く**するか、環境を**より安全に**する方向のアプローチです。

ANDON は異なるギャップに対応します：**失敗から学び、再発を防止する**仕組みです。

| 課題 | 対応する既存手法 | ANDON の役割 |
|------|----------------|-------------|
| コード生成品質 | Codex（RL 学習）、Jules（Planning Critic） | 補完 — 対象外 |
| コードセキュリティスキャン | Copilot（CodeQL）、Claude Code Security | 補完 — 対象外 |
| サンドボックス隔離 | Codex（コンテナ）、GitHub Actions | 補完 — 対象外 |
| 失敗 → ライン停止 → 根本原因分析 | **ANDON** | 中核的な対象領域 |
| 反復失敗パターン検知 | **ANDON（Meta-ANDON）** | 中核的な対象領域 |
| 失敗 → 標準化された再発防止 | **ANDON（Kaizen）** | 中核的な対象領域 |
| 専門業務の出力安全ガード | **ANDON（Pack 0）** | コーディングエージェント向けの中核的な対象領域 |
| 仕様逸脱の防止 | **ANDON** | 中核的な対象領域 |
| ドメイン固有の失敗分類 | **ANDON（Knowledge Packs）** | 拡張可能なプラグインシステム |

ANDON はフックやコールバックをサポートする任意の LLM コーディングエージェント — Claude Code、Codex、AutoGPT/LangChain 等のカスタム実装、独自 CLI エージェント — と連携できます。

学術研究もこのニーズを裏付けています：UC Berkeley の MAST 分類体系（2025）は、マルチエージェント LLM システムの**失敗率が 41〜86.7%** に達し、失敗の 79% がオーケストレーション起因であることを明らかにしました。ANDON の構造的アプローチ — 検知・停止・分析・標準化 — は、個々のエージェントの性能最適化ではなく、こうしたシステミックな失敗に直接対処します。

---

## 同梱内容

```
andon-for-llm-agents/
├── README.md                          # English README
├── README.ja.md                       # このファイル（日本語版）
├── LICENSE                            # Apache-2.0
├── NOTICE                             # 著作権・特許通知
├── CONTRIBUTING.md                    # コントリビューションガイド & CLA
├── CONTRIBUTING-PACKS.md              # Knowledge Pack 仕様
├── CODE_OF_CONDUCT.md                 # Contributor Covenant
├── SECURITY.md                        # 脆弱性報告ポリシー
├── INTEGRATION.md                     # 完全な導入ガイド
├── pyproject.toml                     # PEP 621 プロジェクトメタデータ
├── .github/                           # CI & コミュニティテンプレート
│   └── workflows/test.yml            # GitHub Actions CI
├── rules/                             # CLAUDE.md / AGENTS.md ルールモジュール
│   ├── 70-kaizen-learning.md          # コア ANDON + Kaizen ルール
│   └── 45-quality-driven-execution.md # Gate ゲーミング防止
├── hooks/                             # Claude Code フックスクリプト
│   ├── tps-kaizen-runtime.py          # ANDON ランタイムエンジン（インシデント管理）
│   ├── tps-andon-control.sh           # ユーザー向け ANDON 制御 CLI
│   ├── tps-andon-pretool-guard.sh     # PreToolUse: ANDON オープン時に前進系をブロック
│   ├── tps-andon-posttool-guard.sh    # PostToolUse: 失敗の自動検知
│   ├── kaizen-learning-capture.sh     # PostToolUse: 修正コミット時に知見キャプチャを促進
│   ├── meta_andon_guard.py            # Meta-ANDON: 反復失敗パターンの検知
│   ├── output_safety_guard.py         # Pack 0: 出力安全ガードエンジン
│   ├── domain_classifier.py           # ドメイン分類 + スキルルーティング
│   ├── pack_loader.py                 # Knowledge Pack ローダー + バリデーター
│   ├── andon_cli.py                   # Pack 管理 CLI
│   └── safety_patterns/               # Pack 0 ガードパターン定義
│       ├── upl.yaml                   #   非弁行為
│       └── unqualified.yaml           #   無資格専門業務
├── packs/                             # Knowledge Packs
│   ├── andon-pack-japan-legal/        # 日本法の法令検索・e-Gov API 連携
│   ├── andon-pack-ios-development/    # iOS アプリ開発 & App Store
│   ├── andon-pack-gdpr/              # EU GDPR コンプライアンス
│   ├── andon-pack-financial/         # 金融サービス（PCI-DSS, AML/KYC）
│   └── andon-pack-hipaa/             # HIPAA ヘルスケアコンプライアンス
├── skills/                            # スキル定義（スラッシュコマンド）
│   └── tps-kaizen/
│       ├── tps-kaizen.md              # メインスキルエントリーポイント
│       ├── SKILL.md                   # スキル詳細ドキュメント
│       └── references/
├── tests/                             # テストスイート
│   └── test_output_safety_guard.py    # Pack 0 + 分類器 + ローダーのテスト
└── examples/                          # 導入例
    ├── demo-run.py                    # インタラクティブデモ（すぐ試せます！）
    ├── locales/                       # i18n ロケールファイル
    │   ├── en.json                    #   英語（デフォルト）
    │   └── ja.json                    #   日本語
    ├── sample-pack/                   # サンプル Knowledge Pack（Web API セキュリティ）
    ├── claude-code-settings.json      # フック登録例
    └── minimal-setup.md               # 3ファイルでクイックスタート
```

---

## Pack 0：出力安全ガード

コアランタイムに同梱。キーワードベースのヒューリスティックフィルターで、LLM コーディングエージェントの出力に専門業務領域（法務・医療・金融等）に関連するパターンが含まれる場合に免責事項を挿入します。これは簡易的な安全網であり、検出や抑止を保証するものではありません。

| # | カテゴリ | レベル | アクション |
|---|---------|--------|-----------|
| 1 | 非弁行為 | GUARD | 免責事項 + 弁護士への照会 |
| 2 | 無資格専門業務 | GUARD | 免責事項 + 専門家への照会 |

**ガードレベル**：GUARD は元の出力を保持しつつ免責事項を挿入します。WARN は注意書きを追加します。フレームワークは Knowledge Pack 用に BLOCK（出力全体の置換）もサポートしています。

コンテンツモデレーション（暴力、自傷、差別等）は意図的にスコープ外です — 基盤 LLM 自身の安全層がそれらのカテゴリを処理します。Pack 0 は、LLM コーディングエージェントがドキュメントやコメント内に法務・財務・建築等の専門的アドバイスを生成する可能性に特化しています。

---

## Knowledge Packs

ドメイン固有の失敗検知、分類、スキル推奨で ANDON を拡張します。Pack は `knowledge-pack.yaml` マニフェストで定義される自己完結型プラグインです。

### 利用可能な Pack

| Pack | ドメイン | 規制対象 | スキル数 | ステータス |
|------|---------|---------|---------|-----------|
| `andon-pack-japan-legal` | 日本法（e-Gov API） | はい | 6 | Stable |
| `andon-pack-ios-development` | iOS / App Store | いいえ | 5 | Stable |
| `andon-pack-gdpr` | EU GDPR | はい | 8 | Alpha |
| `andon-pack-financial` | 金融サービス（PCI-DSS, AML/KYC） | はい | 6 | Alpha |
| `andon-pack-hipaa` | HIPAA ヘルスケア | はい | 7 | Alpha |
| `sample-web-api-security` | API セキュリティ（サンプル） | いいえ | 3 | Example |

### Pack CLI

```bash
# インストール済み Pack の一覧
andon pack list

# Pack の検証
andon pack validate packs/andon-pack-japan-legal

# Pack の詳細表示
andon pack info andon-pack-japan-legal

# Pack のインストール
andon pack install ./my-custom-pack
```

### 独自 Pack の作成

完全な仕様は [CONTRIBUTING-PACKS.md](./CONTRIBUTING-PACKS.md) を参照してください。

```bash
# サンプルからスタート
cp -r examples/sample-pack my-pack
# knowledge-pack.yaml を編集し、skills/ にスキルを追加
andon pack validate ./my-pack
```

### 規制ドメインの強制

士業（法律、医療、金融）をカバーする Pack は、Pack 0 を依存関係として宣言する必要があります。Pack ローダーは、この依存関係なしに規制ドメインをカバーする Pack の読み込みを**拒否**します — 出力安全ガードなしにドメイン専門知識がデプロイされることを防ぎます。

> **注意**: Knowledge Packs は法的対応や法令遵守、規制適合を保証するものではありません。ヒューリスティックな失敗検知とスキル参照のみを提供します。法的判断は弁護士等の法律専門家にご相談ください。

### デモを試す

```bash
python3 examples/demo-run.py
```

5 つのインタラクティブシナリオを実行します：ANDON インシデント検知、Pack 0 安全ガード、出力変換、Knowledge Pack スキル推奨、Meta-ANDON パターン検知。

---

## クイックスタート（3 ファイル、5 分）

失敗時の ANDON ライン停止を実現する最小構成：

### インストール

```bash
pip install andon-for-llm-agents
```

ソースからインストールする場合：

```bash
git clone https://github.com/allnew-llc/andon-for-llm-agents.git
cd andon-for-llm-agents
pip install .
```

### 1. フックをコピー

```bash
# プロジェクトルートから
mkdir -p .claude/hooks
cp hooks/tps-kaizen-runtime.py .claude/hooks/
cp hooks/tps-andon-posttool-guard.sh .claude/hooks/
cp hooks/tps-andon-pretool-guard.sh .claude/hooks/
cp hooks/tps-andon-control.sh .claude/hooks/
chmod +x .claude/hooks/*.sh
```

### 2. Claude Code の設定にフックを登録

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
        "hooks": [".claude/hooks/tps-andon-posttool-guard.sh"]
      }
    ]
  }
}
```

### 3. CLAUDE.md にルールを追加

`rules/70-kaizen-learning.md` の内容をプロジェクトの `CLAUDE.md` または `.claude/rules/` ディレクトリに追記してください。

**以上です。** Bash コマンドが失敗すると：
- ANDON がインシデント追跡とともに自動的にオープン
- 前進系コマンド（git push、deploy）がブロック
- 根本原因分析の成果物が自動生成
- 根本原因を修正した後に ANDON をクローズ

---

## フルセットアップ

[INTEGRATION.md](./INTEGRATION.md) を参照：
- Kaizen 学習キャプチャフックの追加
- 反復失敗検知のための Meta-ANDON の追加
- `/tps-kaizen` スキルコマンドのセットアップ
- 品質駆動実行ルールの追加
- 失敗分類とドメインマッピングのカスタマイズ

---

## 主要コンセプト

### ANDON（ライン停止）

Bash コマンドが非ゼロコードで終了した場合：

1. **PostToolUse フック**が失敗を検知
2. **ランタイム**が失敗を分類（7 カテゴリ、信頼度スコア付き）
3. 証跡、分析、防止策を含む**インシデント**を作成
4. **ANDON 状態**を「open」に設定
5. **PreToolUse フック**が前進系コマンドをブロック：
   - `git push`、`git merge`、`git rebase`
   - `vercel deploy`、`firebase deploy`、`npm publish`
   - `xcodebuild archive`
6. **ANDON 中に許可**：診断コマンド、修正、`kaizen:` コミット

根本原因分析後に **ANDON をクローズ**：
```bash
.claude/hooks/tps-andon-control.sh close "root cause: missing dep; fix: added to requirements"
```

### Meta-ANDON（パターン検知）

エージェントがモグラ叩きループに嵌っていることを検知：

**トリガー：**
- 3 回以上の連続 full-run 失敗（異なるフェーズでも発動）
- 1 セッション内で異なるフェーズで 2 回以上 ANDON オープン *（計画中）*
- 修正 → 実行 → 別の失敗 → 修正 → 実行 → 別の失敗、2 サイクル *（計画中）*

**対応：**
0. **プランモード** — 即座に `EnterPlanMode` に移行（読み取り専用の探索、実装禁止）
1. **パターン Five Whys** — 「なぜ毎回違うポイントで失敗するのか？」
2. **机上通し検証** — 実行前に残り全フェーズを机上でレビュー
3. **一括修正計画** — プランを記述し、`ExitPlanMode` でユーザー承認を取得
4. **実装** — プラン承認後にのみ、発見した問題をまとめて修正

### 人間トライアル制限

ユーザーの操作を伴う操作（ログイン、手入力、再認証）に対する**連続最大 2 回の試行**：
- 2 回失敗後：ライン停止
- 再開条件：根本原因仮説、検証、新しいアプローチ

### 仕様境界ガード

エージェントがテストを通すために要件を暗黙に緩和することを防止：
- 明示的なユーザー承認なしに要件の意味を変更不可
- 「提案が先、実装は承認後」— 仕様変更をバグ修正として実装しない
- 違反時は即座に停止・ロールバック

### 品質駆動実行（Gate ゲーミング防止）

LLM は見える目標関数を最適化する。Gate 条件が見える状態では、Gate を通す最小出力を生成する。

**解決策：目的起点の実行**

```
思考順序：
1. このフェーズの目的は何か？
2. どんな品質の成果物を作るか？
3. 成果物を網羅的に作成
4. 品質を自己評価
5. Gate に提出（Gate 条件を事前に見ずに）

NG パターン：
❌ Gate 条件を読む → 通過する最小限を作る → 次フェーズ
```

---

## 内部の仕組み

### 失敗分類

ランタイムは失敗を 7 カテゴリに信頼度スコア付きで分類：

| カテゴリ | 信頼度 | パターン |
|---------|--------|---------|
| `command_not_found` | 0.94 | `command not found` |
| `python_module_missing` | 0.88 | `ModuleNotFoundError` |
| `node_module_missing` | 0.84 | `Cannot find module` |
| `permission_denied` | 0.82 | `Permission denied` |
| `path_missing` | 0.79 | `No such file or directory` |
| `timeout` | 0.68 | `timed out` |
| `assertion_failure` | 0.62 | `AssertionError`, `failed` |
| `unknown_failure` | 0.35 | （フォールバック） |

### 自動標準化

信頼度 >= 0.70 の場合、防止ルールが標準化レジストリに自動追加：

```json
{
  "type": "required_command",
  "value": "uv",
  "source_incident": "INC-20260305-abc123",
  "active": true
}
```

ロールバックはいつでも可能：
```bash
.claude/hooks/tps-andon-control.sh rollback INC-20260305-abc123
```

### インシデント成果物

各インシデントで生成されるもの：
```
~/.claude/state/kaizen/incidents/INC-YYYYMMDD-HHMMSS-hash/
├── evidence.json      # 失敗コマンド、終了コード、出力、git コンテキスト
├── analysis.json      # 分類、信頼度、防止策
├── actions.json       # 自動生成された防止策 + 標準化
├── report.md          # 人間可読なインシデントレポート
├── events.json        # 全失敗イベント（ANDON が複数の失敗をまたぐ場合）
├── payload-latest.json # 生のフックペイロード
└── rollback/
    └── standardization-registry.before.json  # 標準化前の状態
```

---

## カスタマイズ

### カスタム失敗パターンの追加

`tps-kaizen-runtime.py` の `rules` リストを編集：

```python
rules = [
    # (cause_id, label, confidence, regex_pattern)
    ("my_custom_error", "Custom error description", 0.90, r"my specific pattern"),
    # ... 既存ルール ...
]
```

### ドメイン固有のスキル推奨の追加

`tps-kaizen-runtime.py` の `DOMAIN_SKILL_MAP` と `DOMAIN_KEYWORDS` が失敗コンテキストを推奨スキルにマッピングします。プロジェクトのスキルセットに合わせてカスタマイズしてください。

### 信頼度閾値の調整

```python
CONFIDENCE_AUTOMATION_THRESHOLD = 0.70    # 標準化の自動適用
CONFIDENCE_MANUAL_REVIEW_THRESHOLD = 0.70  # クローズ時に手動承認を要求
```

---

## 哲学

> 「品質は工程で作り込むものであり、検査で後付けするものではない。」— W. Edwards Deming

> 「標準は上から押し付けるものではなく、現場の作業者自身が設定すべきものだ。」— 大野耐一

> 「標準なきところに改善なし。」— 大野耐一

このフレームワークは 3 つの信念を体現しています：

1. **検知だけでは不良は止まらない。** 検知 → 即座の例外 → ライン停止が必要。誰も読まない違反ログは劇場である。

2. **LLM は指示されなければ自省しない。** 目の前の問題を解く能力は高いが、自らの行動パターンを俯瞰して見ることはしない。ルールで明示的に停止と分析を強制する必要がある。

3. **すべての失敗は贈り物** — ただし、学びを捕捉し、適切な標準にルーティングし、再発防止を検証した場合に限る。

---

## 背景

このフレームワークは [AllNew LLC](https://www.allnew.work) が Claude Code と Codex を使った iOS アプリ開発のために開発しました。LLM エージェントが以下のような実際のインシデントから生まれました：

- テストゼロでアプリを出荷
- 1 回の実行で 14 個中 14 個のパイプラインセーフガードをバイパス
- Gate を通すために要件の意味を暗黙に変更
- ユーザー認証を伴う 5 回以上のリトライループにはまる

各インシデントは Five Whys で分析され、防止策がこのフレームワークに体系化されました。

---

## コントリビューション

コントリビューション歓迎！関心のある分野：

- **追加の失敗分類パターン**（他の言語/フレームワーク向け）
- **IDE 統合**（Claude Code 以外 — Cursor、Windsurf 等）
- **翻訳**（現在は英語 + 日本語）
- **ケーススタディ**（ANDON/Kaizen を LLM コーディングワークフローに適用した事例）

---

## 謝辞

このプロジェクトは**トヨタ生産方式（TPS）**および**リーン生産方式**の伝統に着想を得ています。ANDON、Kaizen、Jidoka、Poka-yoke の概念は、トヨタ自動車株式会社において、エンジニア、管理者、そして生産現場の作業者が数十年にわたる共同の努力の中で築き上げてきたものです。

*品質は工程で作り込むものであり、検査で後付けするものではない*という洞察は、世界中の製造業を変革し、その起源をはるかに超えた分野に影響を与え続けています。

これらのアイデアを LLM 支援ソフトウェア開発に適用することは、その深遠な知識体系へのささやかな敬意の表明です。このフレームワークにもし優れた点があるとすれば、それはこの伝統に帰するものであり、至らぬ点があるとすれば、それは私たちの力不足によるものです。

TPS の遺産に貢献されたすべての方々 — その創始者、洗練させた実践者、そして日々これらの原則を体現している現場の作業者の皆様 — に、心からの尊敬と感謝を捧げます。

---

## ライセンス

Apache License 2.0。[LICENSE](./LICENSE) を参照してください。

特許通知：本ソフトウェアに実装されている特定の方法は、AllNew LLC が出願中の特許の対象です（特願2026-035626, 特願2026-035627, 特願2026-035831, 特願2026-035832, 特願2026-035943）。特許が付与された場合、Apache 2.0 第 3 条により、ユーザーには永続的かつロイヤリティフリーの特許ライセンスが供与されます。詳細は [NOTICE](./NOTICE) を参照してください。

商標通知：ANDON、Kaizen、Jidoka、Poka-yoke、TPS はリーン生産方式に由来する用語です。Claude は Anthropic, PBC の製品です。Cursor、Windsurf、Codex はそれぞれの所有者の製品です。本プロジェクトは上記いずれの企業とも提携・推奨関係にありません。
