import bpy
import addon_utils

print("\n--- インポートテスト開始 ---")

# アドオンを強制的に有効化
addon_utils.enable("io_scene_gltf2")

# 初期にあるキューブなどのオブジェクトを全て削除してまっさらにする
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# GLBのインポート
glb_path = r"/Users/kishiryusei/Emotional-Monster-Maker/exported_models/monster_J5_C4_A2_S2_Fe1.glb"
try:
    bpy.ops.import_scene.gltf(filepath=glb_path)
    print("✅ GLBインポート成功！")
except Exception as e:
    print(f"❌ インポート失敗: {e}")

# 名前をつけて保存
bpy.ops.wm.save_as_mainfile(filepath=r"/Users/kishiryusei/Emotional-Monster-Maker/import_test_result.blend")
print("--- インポートテスト終了 ---\n")