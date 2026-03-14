import os
import subprocess

# --- パス設定 ---
SRC_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SRC_DIR)

# 1. Blenderアプリのパス (環境に合わせて変更してください)
BLENDER_APP_PATH = "/Applications/Blender 3.app/Contents/MacOS/Blender"

# 2. テストで読み込むGLBファイルのパス
# ※ ここは実際に存在するGLBファイルの名前に書き換えてください！
GLB_FILE_PATH = os.path.join(PROJECT_ROOT, "exported_models", "monster_J5_C4_A2_S2_Fe1.glb")

# 出力ファイルと一時スクリプトのパス
OUTPUT_BLEND_PATH = os.path.join(PROJECT_ROOT, "import_test_result.blend")
TEMP_SCRIPT_PATH = os.path.join(SRC_DIR, "temp_importer.py")

def main():
    if not os.path.exists(GLB_FILE_PATH):
        print(f"❌ エラー: GLBファイルが見つかりません。\nパスを確認してください: {GLB_FILE_PATH}")
        return

    # ==========================================
    # 1. Blender内部で動かすスクリプトを動的に作成
    # ==========================================
    blender_code = f"""
import bpy
import addon_utils

print("\\n--- インポートテスト開始 ---")

# アドオンを強制的に有効化
addon_utils.enable("io_scene_gltf2")

# 初期にあるキューブなどのオブジェクトを全て削除してまっさらにする
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# GLBのインポート
glb_path = r"{GLB_FILE_PATH}"
try:
    bpy.ops.import_scene.gltf(filepath=glb_path)
    print("✅ GLBインポート成功！")
except Exception as e:
    print(f"❌ インポート失敗: {{e}}")

# 名前をつけて保存
bpy.ops.wm.save_as_mainfile(filepath=r"{OUTPUT_BLEND_PATH}")
print("--- インポートテスト終了 ---\\n")
"""
    # スクリプトをファイルとして書き出す
    with open(TEMP_SCRIPT_PATH, "w", encoding="utf-8") as f:
        f.write(blender_code.strip())

    # ==========================================
    # 2. バックグラウンドでインポート処理を実行
    # ==========================================
    print("🔄 バックグラウンドでBlender処理を実行中...")
    import_cmd = [
        BLENDER_APP_PATH,
        "--background",
        "--factory-startup",
        "--python", TEMP_SCRIPT_PATH
    ]
    
    try:
        subprocess.run(import_cmd, check=True)
        print(f"✨ 処理完了！保存先: {OUTPUT_BLEND_PATH}")
    except subprocess.CalledProcessError as e:
        print(f"❌ コマンド実行エラー: {e}")
        return

    # ==========================================
    # 3. 処理結果のBlenderファイルをUI付きで開く
    # ==========================================
    print("🖥️ 結果をBlenderで開きます...")
    open_cmd = [
        BLENDER_APP_PATH,
        OUTPUT_BLEND_PATH
    ]
    subprocess.run(open_cmd)

if __name__ == "__main__":
    main()
