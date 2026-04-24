import os
import subprocess
import sys

# 既存のGLBファイルを使ってパイプライン後半（Blender処理〜OctoPrint）をテストするスクリプト

SRC_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SRC_DIR)
sys.path.append(PROJECT_ROOT)

EXECUTE_PY_PATH = os.path.join(SRC_DIR, "execute.py")
BLENDER_SCRIPT_PATH = os.path.join(SRC_DIR, "blender_process.py")
BASE_BLEND_PATH = os.path.join(PROJECT_ROOT, "Emotional-Monster-Maker_template.blend")

# 過去に生成成功したGLBファイルのパスを指定（必要に応じて書き換えてください）
TEST_GLB_PATH = os.path.join(PROJECT_ROOT, "exported_models", "monster_J1p30_C4p81_A1p01_S1p22_Fe1p00.glb")
TEST_BLEND_PATH = os.path.join(PROJECT_ROOT, "exported_models", "test_monster.blend")

def run_test():
    if not os.path.exists(TEST_GLB_PATH):
        print(f"❌ エラー: テスト用のGLBファイルが見つかりません: {TEST_GLB_PATH}")
        return

    print("=========================================================")
    print("🚀 テスト開始: STL書き出し 〜 スライス 〜 3Dプリント")
    print("=========================================================")
    print("\n1️⃣ Blenderでの自動処理（インポート＆リサイズ＆STL出力）を開始します...")
    
    cmd = [
        "python", EXECUTE_PY_PATH,
        BASE_BLEND_PATH,
        TEST_BLEND_PATH,
        TEST_GLB_PATH,
        BLENDER_SCRIPT_PATH
    ]
    
    try:
        subprocess.run(cmd, check=True)
        print("✅ Blenderの処理が完了しました。")
        
        print("\n2️⃣ 3Dプリントの自動処理（スライス & OctoPrint送信）を開始します...")
        from src.print_manager import slice_stl, upload_to_octoprint
        
        stl_path = os.path.splitext(TEST_GLB_PATH)[0] + ".stl"
        gcode_path = slice_stl(stl_path)
        
        if gcode_path:
            # OctoPrintが稼働していればここで印刷が開始されます
            upload_to_octoprint(gcode_path, auto_print=True)
        else:
            print("⚠️ スライスに失敗したため、印刷はスキップされました。")
            
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Blender処理中にエラーが発生しました: {e}")
    except Exception as e:
        print(f"\n❌ エラーが発生しました: {e}")

if __name__ == "__main__":
    run_test()
