import sys
import os
import subprocess
import requests
import time
from typing import Dict, Tuple

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
try:
    import prompt
except ModuleNotFoundError:
    from src import prompt

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

def validate_emotion_values(joy, calm, anger, sadness, fear) -> Tuple[bool, Dict[str, float], str]:
    values = {
        "joy": joy,
        "calm": calm,
        "anger": anger,
        "sadness": sadness,
        "fear": fear,
    }
    normalized = {}
    for key, value in values.items():
        try:
            number = round(float(value), 2)
        except (TypeError, ValueError):
            return False, {}, f"{key} は 1〜5 の数値で指定してください。"
        if number < 1 or number > 5:
            return False, {}, f"{key} は 1〜5 の範囲で指定してください。"
        normalized[key] = number
    return True, normalized, ""


def emotion_to_filename_part(value: float) -> str:
    return f"{value:.2f}".replace(".", "p")


def generate_monster(joy, calm, anger, sadness, fear):
    ok, normalized, error = validate_emotion_values(joy, calm, anger, sadness, fear)
    if not ok:
        return {"success": False, "error": error}

    joy = normalized["joy"]
    calm = normalized["calm"]
    anger = normalized["anger"]
    sadness = normalized["sadness"]
    fear = normalized["fear"]

    # 1. Geminiでプロンプトを生成
    formatted_prompt = prompt.base_prompt.format(
        joy=joy, calm=calm, anger=anger, sadness=sadness, fear=fear
    )
    
    print(f"--- Geminiに感情パラメータを送信中... ---")
    
    max_retries = 3
    retry_delay = 2  # 初回リトライ時の待機秒数
    tripo_prompt = None

    for attempt in range(max_retries + 1):
        try:
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=formatted_prompt
            )
            tripo_prompt = response.text.strip()
            print(f"📝 生成されたプロンプト:\n>> {tripo_prompt}\n")
            break  # 成功したらループを抜ける
        except Exception as e:
            if attempt < max_retries:
                print(f"⚠️ Geminiエラーが発生しました（{e}）。{retry_delay}秒後にリトライします... ({attempt + 1}/{max_retries})")
                time.sleep(retry_delay)
                retry_delay *= 2  # 次回リトライ時は待機時間を2倍にする（指数的バックオフ）
            else:
                print(f"❌ Geminiエラー: {e}")
                return {"success": False, "error": f"Geminiエラー: {e}"}

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
        req = requests.post(tripo_url, headers=headers, json=payload, timeout=30)
        
        if req.status_code != 200:
            print(f"\n❌ Tripoからのエラー返答 ({req.status_code}):")
            print(req.text)
            return {"success": False, "error": f"Tripoエラー ({req.status_code})"}
            
        req.raise_for_status() 
        task_id = req.json().get("data", {}).get("task_id")
        
    except Exception as e:
        print(f"❌ 通信エラー: {e}")
        return {"success": False, "error": f"通信エラー: {e}"}

    if not task_id:
        print("Tripoタスクの作成に失敗しました。")
        return {"success": False, "error": "Tripoタスクの作成に失敗しました。"}

    # 3. 生成完了のポーリング
    print(f"Tripoで3D生成中... (Task ID: {task_id})")
    
    max_poll_attempts = 60 # 5秒 × 60回 = 最大5分
    poll_count = 0
    
    while poll_count < max_poll_attempts:
        poll_count += 1
        try:
            status_res = requests.get(f"{tripo_url}/{task_id}", headers=headers, timeout=30).json()
            status = status_res.get("data", {}).get("status")
            
            if status == "success":
                output = status_res["data"]["output"]
                result_url = output.get("model") or output.get("pbr_model")
                
                # パスとファイル名の生成
                filename_base = (
                    f"monster_J{emotion_to_filename_part(joy)}"
                    f"_C{emotion_to_filename_part(calm)}"
                    f"_A{emotion_to_filename_part(anger)}"
                    f"_S{emotion_to_filename_part(sadness)}"
                    f"_Fe{emotion_to_filename_part(fear)}"
                )
                target_dir = os.path.join(EXPORT_DIR, filename_base)
                glb_filename = f"{filename_base}.glb"
                blend_filename = f"{filename_base}.blend"
                
                print("生成成功！ファイルをダウンロードします...")
                # GLBファイルの保存
                saved_filepath = os.path.join(target_dir, glb_filename)
                download_and_save(result_url, saved_filepath)
                
                # 複製後のBlenderファイルの保存先を決定 (絶対パス)
                new_blend_path = os.path.join(target_dir, blend_filename)
                
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
                    # ==========================================
                    # 3Dプリントの自動実行 (スライス & OctoPrint送信)
                    # ==========================================
                    print("\n🖨️ 3Dプリントの自動処理を開始します...")
                    try:
                        from src.print_manager import slice_stl, upload_to_octoprint
                        stl_path = os.path.splitext(saved_filepath)[0] + ".stl"
                        gcode_path, print_time = slice_stl(stl_path)
                        if gcode_path:
                            # 実際にOctoPrintが稼働していればここで印刷が開始されます
                            upload_to_octoprint(gcode_path, auto_print=True)
                        else:
                            print("⚠️ スライスに失敗したため、印刷はスキップされました。")
                    except Exception as e:
                        print(f"❌ 3Dプリント処理中にエラーが発生しました: {e}")

                    print(f"\n✨ すべてのパイプライン処理が完了しました！")
                    print(f"📂 出力されたBlenderファイル: {new_blend_path}")
                    return {
                        "success": True,
                        "glb_path": saved_filepath,
                        "blend_path": new_blend_path,
                        "print_time": print_time,
                        "task_id": task_id,
                    }
                except subprocess.CalledProcessError as e:
                    print(f"\n❌ Blender処理中にエラーが発生しました: {e}")
                    return {"success": False, "error": f"Blender処理エラー: {e}"}
                except FileNotFoundError:
                    print(f"\n❌ 実行ファイルが見つかりません。パスを確認してください: {EXECUTE_PY_PATH}")
                    return {"success": False, "error": f"実行ファイルが見つかりません: {EXECUTE_PY_PATH}"}
            
            elif status == "failed":
                print("生成に失敗しました。")
                return {"success": False, "error": "Tripoでのモデル生成に失敗しました。"}
            
            elif status in ["running", "queued"]:
                print(".", end="", flush=True)
                time.sleep(5)
            else:
                print(f"Status: {status}")
                time.sleep(5)
                
        except Exception as e:
            print(f"ポーリングエラー: {e}")
            return {"success": False, "error": f"ポーリングエラー: {e}"}

    # 最大回数に達してループを抜けた場合はタイムアウトとする
    print("❌ Tripoの生成がタイムアウトしました。")
    return {"success": False, "error": "Tripoでのモデル生成がタイムアウト（5分超過）しました。"}

def download_and_save(url, filepath):
    # 保存先ディレクトリが存在しない場合は作成
    target_dir = os.path.dirname(filepath)
    if not os.path.exists(target_dir):
        os.makedirs(target_dir, exist_ok=True)
    
    response = requests.get(url)
    with open(filepath, "wb") as f:
        f.write(response.content)
    print(f"保存完了: {filepath}")
    
    return filepath

def run_cli():
    print("=== Emotional Monster Maker Generator ===")
    print("各感情を 1〜5 の数値で入力してください")
    
    try:
        j = input("Joy (喜び): ").strip() or "1"
        c = input("Calm (穏やか): ").strip() or "1"
        a = input("Anger (怒り): ").strip() or "1"
        s = input("Sadness (悲しみ): ").strip() or "1"
        fe = input("Fear (恐怖): ").strip() or "1"
        
        result = generate_monster(j, c, a, s, fe)
        if not result.get("success"):
            print(f"❌ エラー: {result.get('error', '不明なエラー')}")
        
    except KeyboardInterrupt:
        print("\n中止しました。")


# --- 実行 ---
if __name__ == "__main__":
    run_cli()
