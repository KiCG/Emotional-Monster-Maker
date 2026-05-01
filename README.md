# Emotional Monster Maker

**Emotional Monster Maker** は、ユーザーが入力した「感情パラメータ」に基づいて、AIがオリジナルの3Dモンスターを自動生成し、さらにそのモデルを自動で3DプリントするPythonツールです。

「喜び」「穏やかさ」「怒り」「悲しみ」「恐怖」の5つの感情数値を入力すると、Google Gemini がその感情を視覚的な特徴（形状、色、テクスチャ）に変換し、Tripo AI がそれを3Dモデル（.glb）として具現化します。その後、Blenderによる自動リサイズと動画レンダリング、PrusaSlicerによるスライスを経て、OctoPrint経由で接続された3Dプリンターへ直接印刷ジョブを送信します。

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Gemini API](https://img.shields.io/badge/AI-Google%20Gemini-orange.svg)
![Tripo API](https://img.shields.io/badge/AI-Tripo3D-purple.svg)
![Blender](https://img.shields.io/badge/3D-Blender-blue.svg)
![OctoPrint](https://img.shields.io/badge/Print-OctoPrint-green.svg)

## 🚀 機能

- **感情パラメータ入力**: 5つの感情（Joy, Calm, Anger, Sadness, Fear）を1〜5のスケールでWeb UI（iPadやスマホ等）から直感的に指定可能。
- **動的プロンプト生成**: Google Gemini 2.5 Flash を使用し、感情の組み合わせから最適な3D生成用プロンプトを作成。
- **Text-to-3D 生成**: Tripo API を使用し、プロンプトから高速に3Dモデルを生成。
- **Blender自動処理**: 生成されたモデルをBlenderのテンプレートに読み込み、自動でリサイズ＆アニメーション動画（WebM形式）をレンダリング。
- **自動3Dプリント**: PrusaSlicer（またはCreality Print）をバックグラウンドで呼び出しG-Codeを生成。その後、OctoPrintへAPI経由で送信し、接続された3Dプリンタで印刷を自動開始。

## 📦 必要要件

### ソフトウェア・API
- Python 3.8 以上
- Google Cloud (Gemini) API Key
- Tripo AI API Key
- Blender 4.0 以上
- PrusaSlicer (または Creality Print)
- OctoPrint サーバー

### ハードウェア
- OctoPrintと接続された3Dプリンター

## 🛠 インストールとセットアップ

### 1. リポジトリのクローン
```bash
git clone https://github.com/KiCG/Emotional-Monster-Maker
cd Emotional-Monster-Maker
```

### 2. ライブラリのインストール
```bash
pip install -r requirements.txt
```

### 3. OctoPrintのインストール（まだ環境がない場合）
ローカルPC経由で3Dプリンタを制御するため、OctoPrintをインストールします（仮想環境での構築を推奨します）。
```bash
cd ~
python3 -m venv OctoPrint
source OctoPrint/bin/activate
pip install pip --upgrade
pip install octoprint
```

### 4. 設定ファイルの準備
リポジトリに含まれる `config_example.py` をコピーして `config.py` を作成し、ご自身の各種APIキーやURLを設定してください。
```bash
cp config_example.py config.py
```
```python
# config.py
GEMINI_API_KEY = "ここにGeminiのAPIキー"
TRIPO_API_KEY = "ここにTripoのAPIキー"
OCTOPRINT_URL = "http://localhost:5001" # OctoPrintのURL
OCTOPRINT_API_KEY = "ここにOctoPrintのAPIキー"
```

## 🎮 使い方

### 0. 事前準備 (OctoPrintの起動とスリープ対策)

1. **OctoPrintサーバーの起動**
ターミナルから以下のコマンドを実行して、OctoPrintサーバーを立ち上げます。
```bash
/Users/<username>/OctoPrint/bin/octoprint serve --port 5001
```
*(※環境に合わせてOctoPrintの実行パスは変更してください)*

2. **PCのスリープ無効化（重要）**
3Dプリント中にPC（MacBook等）がスリープ状態になると、プリンターへの通信が途絶え、印刷が途中で停止してしまいます。印刷中は必ずPCがスリープしないように設定してください。
> **💡 TIP (MacBookユーザー向け)**: 
> 画面を閉じてもスリープを防止してくれる無料アプリ **[Amphetamine](https://apps.apple.com/jp/app/amphetamine/id937984704?mt=12)** の利用を強く推奨します。


### Web UI経由で実行する（推奨）
MacBook側でWebサーバーを起動し、iPadやスマートフォンのブラウザからアクセスして操作できます。

1. **MacBookでサーバー起動**
```bash
python src/web_app.py
```
2. **ブラウザからアクセス**
MacBookとiPadを同じWi-Fiに接続し、iPadのSafari等で `http://<MacBookのIPアドレス>:8000` にアクセスします。（例: `http://192.168.1.15:8000`）
3. **生成と印刷**
スライダーで感情値を設定して「生成を開始」を押すと、3Dモデルの生成、動画のレンダリング、そして3Dプリンターへの出力が全自動で行われます。

### CLIで直接実行する
ターミナルから直接プログラムを実行することも可能です。
```bash
python src/main.py
```

## 📂 フォルダ構成
```text
Emotional-Monster-Maker/
├── exported_models/       # 生成された3Dモデル(.glb, .stl)、G-Code、処理済み.blendの保存先
├── src/                   # ソースコード
│   ├── __init__.py         
│   ├── blender_process.py # Blender内部でのワークフロー制御と動画レンダリング
│   ├── blender_resize.py  # 頂点データを直接操作するリサイズ処理
│   ├── execute.py         # Blenderのバックグラウンド起動を管理
│   ├── main.py            # AIパイプラインのメイン処理
│   ├── print_manager.py   # スライサー呼び出しとOctoPrint送信処理
│   ├── prompt.py          # Gemini用のプロンプト定義
│   ├── web_app.py         # WebUI（Flask）用アプリケーション
│   ├── static/            # WebUI用静的ファイル (CSS, JS, 動画素材)
│   └── templates/         # WebUI用HTMLテンプレート
├── config.py              # 設定ファイル (環境構築時に作成・Git対象外)
├── Emotional-Monster-Maker_template.blend # ベースとなるBlenderテンプレートファイル
├── requirements.txt       # 必要なライブラリ一覧
└── README.md              # 本ドキュメント
```
