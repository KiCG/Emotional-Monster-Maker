# Emotional Monster Maker

**Emotional Monster Maker** は、ユーザーが入力した「感情パラメータ」に基づいて、AIがオリジナルの3Dモンスターを自動生成するPythonツールです。

「喜び」「穏やかさ」「怒り」「悲しみ」「恐怖」の5つの感情数値を入力すると、Google Gemini がその感情を視覚的な特徴（形状、色、テクスチャ）に変換し、Tripo AI がそれを3Dモデル（.glb）として具現化します。

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Gemini API](https://img.shields.io/badge/AI-Google%20Gemini-orange.svg)
![Tripo API](https://img.shields.io/badge/AI-Tripo3D-purple.svg)

## 🚀 機能

- **感情パラメータ入力**: 5つの感情（Joy, Calm, Anger, Sadness, Fear）を1〜5のスケールで指定可能。
- **動的プロンプト生成**: Google Gemini 2.5 Flash を使用し、感情の組み合わせから最適な3D生成用プロンプトを作成。
- **Text-to-3D 生成**: Tripo API を使用し、プロンプトから高速に3Dモデルを生成。
- **自動ダウンロード**: 生成されたモデル（.glb形式）を自動でローカルフォルダに保存。
- **自動リサイズ**:　glbファイルをテンプレートblenderファイルでインポートし、特定の大きさにリサイズ。

## 📦 必要要件

- Python 3.8 以上
- Google Cloud (Gemini) API Key
- Tripo AI API Key
- Blender 4.0 以上

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

### 3. APIキーの設定
```python
# config.py
GEMINI_API_KEY = "ここにGeminiのAPIキー"
TRIPO_API_KEY = "ここにTripoのAPIキー"
```

### 使い方
以下のコマンドでプログラムが実行します
```bash
python src/main.py
```

### iPadからパラメータ入力する（Web UI）
MacBook側でWebサーバーを起動し、iPadのブラウザからアクセスできます。

1. MacBookでサーバー起動
```bash
python src/web_app.py
```
2. MacBookとiPadを同じWi-Fiに接続
3. iPadのSafariで `http://<MacBookのIPアドレス>:8000` にアクセス
4. スライダーで感情値を設定して「生成を開始」を押す

> 例: `http://192.168.1.15:8000`

### フォルダ構成
```text
Emotional-Monster-Maker/
├── exported_models/       # 生成されたモデルと、処理済み.blendの保存先
├── src/                   # ソースコード
│   ├── __init__.py         
│   ├── blender_process.py # Blender内部でのワークフロー制御
│   ├── blender_resize.py  # 頂点データを直接操作するリサイズ処理（※名前を統一）
│   ├── execute.py         # Blenderのバックグラウンド起動を管理
│   ├── main.py            # ユーザー入力を受け取るメイン実行ファイル
│   └── prompt.py          # Gemini用のプロンプト定義
├── config.py              # 設定ファイル (Git対象外)
├── Emotional-Monster-Maker_template.blend # 処理のベースとなるテンプレートファイル
├── requirements.txt       # 必要なライブラリ一覧
└── README.md              # 説明書
```
