# システムアーキテクチャ: Emotional Monster Maker

## 概要

Emotional Monster Maker は、ユーザーが入力した5つの感情パラメータを基に、AIが3Dモデルを生成し、Blenderで加工後、自動で3Dプリントするエンドツーエンドのパイプラインシステム。

---

## ディレクトリ構成

```
Emotional-Monster-Maker/
├── src/
│   ├── main.py                  # AIパイプライン中核処理
│   ├── web_app.py               # Flask Webサーバー (メインエントリポイント)
│   ├── execute.py               # Blenderサブプロセス管理
│   ├── blender_process.py       # Blender内で実行されるPythonスクリプト
│   ├── blender_resize.py        # メッシュ頂点スケーリング (ヘッドレス対応)
│   ├── print_manager.py         # スライサー & OctoPrint 連携
│   ├── prompt.py                # Gemini向けプロンプトテンプレート
│   ├── static/
│   │   ├── css/app.css          # スタイルシート (ダークテーマ、レスポンシブ)
│   │   ├── js/app.js            # フロントエンドロジック
│   │   └── media/              # 画像・動画アセット
│   └── templates/
│       ├── index.html           # 感情入力画面
│       ├── loading.html         # 生成中画面
│       └── result.html          # 印刷時間表示画面
├── Emotional-Monster-Maker_template.blend  # HologramShader入りBlenderテンプレート
├── config_example.py            # 設定テンプレート (config.py にコピーして使用)
├── requirements.txt             # Python依存パッケージ
├── exported_models/             # 出力ファイル置き場 (GLB, STL, G-code, Blend)
└── README.md
```

---

## 技術スタック

| レイヤー | 技術 | 用途 |
|---------|------|------|
| フロントエンド | HTML5 / CSS3 / Vanilla JS | 感情スライダー、ナビゲーション、動画表示 |
| Webフレームワーク | Flask | HTTPサーバー、テンプレート、JSON API |
| AI (テキスト生成) | Google Gemini 2.5 Flash | 感情 → 3Dプロンプト生成 |
| AI (3Dモデル生成) | Tripo AI v2 API | テキスト → 3Dモデル (GLB) |
| 3D編集 | Blender 4.0+ (Python API) | GLBインポート、マテリアル適用、STL書き出し、アニメーションレンダリング |
| スライシング | PrusaSlicer / Creality Print | STL → G-code変換 |
| プリンター制御 | OctoPrint HTTP API | 3Dプリンターへのジョブ送信・管理 |
| バックエンド | Python 3.8+ | 全体オーケストレーション、API呼び出し |
| データフォーマット | GLB / STL / G-code | 3Dモデル交換・印刷データ |

---

## パイプラインフロー

```
ユーザー入力 (感情5パラメータ: joy / calm / anger / sadness / fear)
        │
        ▼
バリデーション & 正規化 (main.py)
  └─ 1〜5の範囲チェック、小数点2桁に丸め
        │
        ▼
プロンプト生成 (main.py + prompt.py)
  └─ Gemini API → 感情値から英語の3D説明文を生成
  └─ リトライ: 指数バックオフ (2s → 4s → 8s)
        │
        ▼
3Dモデル生成 (main.py → Tripo AI API)
  └─ POST /v2/openapi/task (text_to_model)
  └─ 5秒ごとにポーリング (最大3分)
  └─ 成功時: GLBファイルをダウンロード
  └─ タイムアウト時: キャッシュ済みモデルにフォールバック
        │
        ▼
Blender処理 (execute.py → blender_process.py)
  ├─ template.blend を感情値ごとの .blend にコピー
  ├─ Blenderをヘッドレスモードで起動 (--background)
  ├─ GLBをインポート
  ├─ メッシュスケーリング (blender_resize.py)
  ├─ HologramShaderマテリアルを適用
  ├─ STLに書き出し
  └─ アニメーションをWebMでレンダリング → static/media/ に保存
        │
        ▼
3Dプリント (print_manager.py)
  ├─ PrusaSlicer で STL → G-code (スケール1000x, サポート付き)
  ├─ G-codeヘッダから印刷予測時間を解析
  ├─ OctoPrint API に G-code をアップロード
  └─ auto_print=True の場合、即時印刷を開始
        │
        ▼
結果表示
  └─ レンダリング動画をループ再生
  └─ ハッチング完了予定時刻を表示 (印刷時間 + 5分バッファ)
```

---

## 主要モジュール

| モジュール | 責務 |
|-----------|------|
| `main.py` | パイプライン全体のオーケストレーション。感情バリデーション、Gemini/Tripo API呼び出し、ポーリング、ファイル管理 |
| `web_app.py` | Flaskアプリ。ルート定義 (`/`, `/loading`, `/result`, `/generate`, `/test-input`) とJSON APIエンドポイント |
| `execute.py` | Blenderテンプレートのコピーと `subprocess.run()` でのヘッドレスBlender起動 |
| `blender_process.py` | Blender内部で実行。GLBインポート、マテリアル置換、STL書き出し、アニメーションレンダリング |
| `blender_resize.py` | 頂点座標を直接操作してメッシュをスケーリング (ヘッドレスモードでの `transform_apply()` クラッシュを回避) |
| `print_manager.py` | PrusaSlicer CLIの呼び出しとOctoPrint HTTP APIクライアント |
| `prompt.py` | 感情パラメータを埋め込むGemini向けプロンプトテンプレート |
| `app.js` | スライダー操作、フォーム送信、sessionStorageによる状態管理、ページ遷移 |

---

## 設定ファイル (config.py)

`config_example.py` をコピーして `config.py` を作成し、各値を設定する。

```python
GEMINI_API_KEY      # Google AI Studio APIキー
TRIPO_API_KEY       # Tripo AI APIキー (tr_*** 形式)
OCTOPRINT_URL       # OctoPrintサーバーのURL (例: http://localhost:5001)
OCTOPRINT_API_KEY   # OctoPrint認証トークン
BLENDER_CLI         # Blender実行ファイルのパス
PRUSA_SLICER_CLI    # PrusaSlicer実行ファイルのパス
CREALITY_PRINT_CLI  # Creality Print (代替スライサー)
```

---

## ファイル命名規則

感情値から一意のファイル名を生成する。小数点は `p` に置換。

```
monster_J{joy}_C{calm}_A{anger}_S{sadness}_Fe{fear}
例: monster_J3p50_C2p00_A4p10_S1p00_Fe5p00
```

各感情ごとに `exported_models/{filename_base}/` ディレクトリを作成し、以下を格納:

| ファイル | 内容 |
|---------|------|
| `{name}.glb` | Tripo AIが生成した3Dモデル |
| `{name}.stl` | Blenderが出力した印刷用メッシュ |
| `{name}.gcode` | スライサーが生成したプリンターコマンド |
| `{name}.blend` | 処理済みBlenderシーン |
| `result-loop.webm` | レンダリングしたアニメーション動画 |

---

## 外部API連携

### Google Gemini API
- モデル: `gemini-2.5-flash`
- 入力: 感情値を埋め込んだプロンプト
- 出力: 英語の3D形状説明文
- エラー処理: 指数バックオフで最大3回リトライ

### Tripo AI API
- ベースURL: `https://api.tripo3d.ai/v2/openapi`
- 認証: `Authorization: Bearer {TRIPO_API_KEY}`
- タスク作成: `POST /task` (`text_to_model` タイプ)
- 状態確認: `GET /task/{task_id}` (5秒ごと、最大3分)
- 完了時: GLBダウンロードURLを取得

### OctoPrint API
- 認証: `X-Api-Key` ヘッダー
- ファイルアップロード: `POST /api/files/local` (multipart)
- 自動印刷: フォームデータに `print=true` を付与

---

## エントリポイント

| 方法 | コマンド | 用途 |
|------|---------|------|
| Web UI | `python src/web_app.py` | ブラウザ / iPad / スマートフォンから操作 (ポート 8000) |
| CLI | `python src/main.py` | ローカルテスト・自動化スクリプト |
| Python import | `from src.main import generate_monster` | 外部スクリプトからのプログラム的呼び出し |

---

## 設計上の重要な判断

1. **頂点直接操作**: ヘッドレスBlenderでは `transform_apply()` がクラッシュするため、頂点座標 (`vert.co`) を直接スケーリング
2. **マテリアルテンプレート化**: HologramShaderを `.blend` テンプレートに事前定義し、生成モデルに適用
3. **フォールバック機構**: Tripoがタイムアウトした場合、キャッシュ済みモデルでパイプラインを継続
4. **sessionStorage**: ページ遷移間の感情状態管理をバックエンドセッションなしで実現
5. **絶対パス管理**: `SRC_DIR` / `PROJECT_ROOT` をスクリプト位置から算出し、OSを問わずポータブルに動作
6. **サブプロセス分離**: BlenderはPythonとは別プロセスで起動。引数はCLI経由で受け渡し
