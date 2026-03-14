import sys
import os
import subprocess
import requests
import time

# ---------------------------------------------------------
# パスの自動計算と設定
# ---------------------------------------------------------
# main.pyが存在するディレクトリ (srcフォルダ) の絶対パスを取得
SRC_DIR = os.path.dirname(os.path.abspath(__file__))

# その1つ上の階層 (Emotional-Monster-Maker フォルダ) の絶対パスを取得
PROJECT_ROOT = os.path.dirname(SRC_DIR)

# プロジェクトルートにパスを通す (config.py などがルートにある場合への備え)
sys.path.append(PROJECT_ROOT)

from google import genai
import config 
import prompt

# --- API設定 ---
GEMINI_API_KEY = config.GEMINI_API_KEY
TRIPO_API_KEY = config.TRIPO_API_KEY

# --- ファイルパスの定義 (すべて絶対パス) ---
# 実行するPythonスクリプト群 (srcフォルダ内)
EXECUTE_PY_PATH = os.path.join(SRC_DIR, "execute.py")
BLENDER_SCRIPT_PATH = os.path.join(SRC_DIR, "blender_process.py")

# データファイル群 (プロジェクトルート直下)
BASE_BLEND_PATH = os.path.join(PROJECT_ROOT, "Emotional-Monster-Maker_template.blend")
EXPORT_DIR = os.path.join(PROJECT_ROOT, "exported_models")

# APIのセットアップ
client = genai.Client(api_key=GEMINI_API_KEY)

def generate_monster(joy, calm, anger, sadness, fear):
    # 1. Geminiでプロンプトを生成
    formatted_prompt = prompt.base_prompt.format(
        joy=joy, calm=calm, anger=anger, sadness=sadness, fear=fear
    )
    
    print(f"--- Geminiに感情パラメータを送信中... ---")
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=formatted_prompt
        )
        tripo_prompt = response.text.strip()
        print(f"📝 生成されたプロンプト:\n>> {tripo_prompt}\n")
    except Exception as e:
        print(f"❌ Geminiエラー: {e}")
        return

    # 2. Tripo APIへタスク送信
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {TRIPO_API_KEY}", 
        "api-key": f"{TRIPO_API_KEY}"
    }
    payload = {
        "type": "text_to_model",
        "prompt": tripo_prompt,
        "model_version": "v2.0-20240919"
    }
    
    tripo_url = "https://api.tripo3d.ai/v2/openapi/task"
    
    try:
        req = requests.post(tripo_url, headers=headers, json=payload)
        
        if req.status_code != 200:
            print(f"\n❌ Tripoからのエラー返答 ({req.status_code}):")
            print(req.text)
            return
            
        req.raise_for_status() 
        task_id = req.json().get("data", {}).get("task_id")
        
    except Exception as e:
        print(f"❌ 通信エラー: {e}")
        return

    if not task_id:
        print("Tripoタスクの作成に失敗しました。")
        return

    # 3. 生成完了のポーリング
    print(f"Tripoで3D生成中... (Task ID: {task_id})")
    
    while True:
        try:
            status_res = requests.get(f"{tripo_url}/{task_id}", headers=headers).json()
            status = status_res.get("data", {}).get("status")
            
            if status == "success":
                output = status_res["data"]["output"]
                result_url = output.get("model") or output.get("pbr_model")
                
                # パスとファイル名の生成
                filename_base = f"monster_J{joy}_C{calm}_A{anger}_S{sadness}_Fe{fear}"
                glb_filename = f"{filename_base}.glb"
                blend_filename = f"{filename_base}.blend"
                
                print("生成成功！ファイルをダウンロードします...")
                # GLBファイルの保存 (絶対パスが返ってくる)
                saved_filepath = download_and_save(result_url, glb_filename)
                
                # 複製後のBlenderファイルの保存先を決定 (絶対パス)
                new_blend_path = os.path.join(EXPORT_DIR, blend_filename)
                
                # ==========================================
                # execute.py の呼び出し
                # ==========================================
                print("\nBlenderでの自動処理（インポート＆リサイズ）を開始します...")
                try:
                    cmd = [
                        "python", EXECUTE_PY_PATH,
                        BASE_BLEND_PATH,      # 絶対パス
                        new_blend_path,       # 絶対パス
                        saved_filepath,       # 絶対パス
                        BLENDER_SCRIPT_PATH   # 絶対パス
                    ]
                    subprocess.run(cmd, check=True)
                    print(f"\n✨ すべてのパイプライン処理が完了しました！")
                    print(f"📂 出力されたBlenderファイル: {new_blend_path}")
                except subprocess.CalledProcessError as e:
                    print(f"\n❌ Blender処理中にエラーが発生しました: {e}")
                except FileNotFoundError:
                    print(f"\n❌ 実行ファイルが見つかりません。パスを確認してください: {EXECUTE_PY_PATH}")
                
                break
            
            elif status == "failed":
                print("生成に失敗しました。")
                break
            
            elif status in ["running", "queued"]:
                print(".", end="", flush=True)
                time.sleep(5)
            else:
                print(f"Status: {status}")
                time.sleep(5)
                
        except Exception as e:
            print(f"ポーリングエラー: {e}")
            break

def download_and_save(url, filename):
    # 保存先ディレクトリが存在しない場合は作成
    if not os.path.exists(EXPORT_DIR):
        os.makedirs(EXPORT_DIR)
    
    filepath = os.path.join(EXPORT_DIR, filename)
    response = requests.get(url)
    with open(filepath, "wb") as f:
        f.write(response.content)
    print(f"保存完了: {filepath}")
    
    return filepath

# --- 実行 ---
if __name__ == "__main__":
    print("=== Emotional Monster Maker Generator ===")
    print("各感情を 1〜5 の数値で入力してください")
    
    try:
        j = input("Joy (喜び): ") or "1"
        c = input("Calm (穏やか): ") or "1"
        a = input("Anger (怒り): ") or "1"
        s = input("Sadness (悲しみ): ") or "1"
        fe = input("Fear (恐怖): ") or "1"
        
        generate_monster(j, c, a, s, fe)
        
    except KeyboardInterrupt:
        print("\n中止しました。")
