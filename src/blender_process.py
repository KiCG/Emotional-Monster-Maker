import bpy
import sys
import os
import addon_utils

print("\n--- 🟢 Blender内部プロセス開始 ---")

# 引数からglbパスを取得
argv = sys.argv
if "--" in argv:
    argv = argv[argv.index("--") + 1:]
    glb_path = argv[0]
else:
    glb_path = "default.glb"

# =========================================================
# 【重要】オフになっている「GLBインポーター」だけを有効化する
# =========================================================
addon_utils.enable("io_scene_gltf2")

# 既存のオブジェクトを選択解除
for o in bpy.context.scene.objects:
    o.select_set(False)

print(f"📦 GLBインポート開始: {glb_path}")
try:
    bpy.ops.import_scene.gltf(filepath=glb_path)
    print("✅ GLBインポート完了")
except Exception as e:
    print(f"❌ インポート処理でエラーが発生しました: {e}")

imported_objects = bpy.context.selected_objects

# resize.pyの絶対パスを取得
script_dir = os.path.dirname(os.path.abspath(__file__))
resize_script_path = os.path.join(script_dir, "blender_resize.py")

for obj in imported_objects:
    # メッシュ以外（ライトやカメラ等）は無視する
    if obj.type != 'MESH':
        continue
        
    bpy.context.view_layer.objects.active = obj
    
    print(f"📐 リサイズ処理実行: {obj.name}")
    if os.path.exists(resize_script_path):
        with open(resize_script_path, "r", encoding="utf-8") as f:
            exec(f.read())
    else:
        print(f"❌ エラー: {resize_script_path} が見つかりません。")

print("💾 変更を上書き保存中...")
bpy.ops.wm.save_mainfile()
print("--- 🔴 Blender内部プロセス完了 ---\n")
