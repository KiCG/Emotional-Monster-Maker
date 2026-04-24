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

    # =========================================================
    # シェーダー（マテリアル）の差し替え処理
    # =========================================================
    # ここにあらかじめ用意したマテリアル名を指定してください
    TARGET_MATERIAL_NAME = "HologramShader" 
    
    if TARGET_MATERIAL_NAME in bpy.data.materials:
        new_mat = bpy.data.materials[TARGET_MATERIAL_NAME]
        print(f"🎨 マテリアルを '{TARGET_MATERIAL_NAME}' に差し替えます: {obj.name}")
        
        # もしマテリアルスロットが空なら追加する
        if len(obj.material_slots) == 0:
            bpy.ops.object.material_slot_add()
            
        # 全てのマテリアルスロットを差し替え
        for slot in obj.material_slots:
            slot.material = new_mat
    else:
        print(f"⚠️ マテリアル '{TARGET_MATERIAL_NAME}' がBlendファイル内に見つかりません。GLBのデフォルトを使用します。")

# =========================================================
# STLファイルへの書き出し
# =========================================================
bpy.ops.object.select_all(action='DESELECT')
for obj in imported_objects:
    if obj.type == 'MESH':
        obj.select_set(True)

if glb_path != "default.glb":
    stl_path = os.path.splitext(glb_path)[0] + ".stl"
    print(f"📦 STLエクスポートを開始します: {stl_path}")
    
    # STLアドオンを明示的に有効化
    try:
        addon_utils.enable("io_mesh_stl")
    except Exception as e:
        print(f"⚠️ STLアドオンの有効化に失敗しました（無視して続行します）: {e}")
        
    try:
        # 選択されたメッシュのみをSTLとして書き出し
        if not bpy.context.selected_objects:
            print("⚠️ 警告: エクスポート対象のオブジェクトが選択されていません。")
        else:
            print(f"ℹ️ {len(bpy.context.selected_objects)}個のオブジェクトをSTLとして書き出します。")
            
        # Blender 4.2+ では wm.stl_export を使用し、それ以前では export_mesh.stl を使用する
        if hasattr(bpy.ops.wm, "stl_export"):
            bpy.ops.wm.stl_export(filepath=stl_path, export_selected_objects=True)
        else:
            bpy.ops.export_mesh.stl(filepath=stl_path, use_selection=True)
            
        print(f"✅ STLエクスポート完了")
    except Exception as e:
        print(f"❌ STLエクスポートエラー: {e}")

print("💾 変更を上書き保存中...")
bpy.ops.wm.save_mainfile()

# =========================================================
# アニメーションのレンダリング処理
# =========================================================
print("🎬 アニメーションのレンダリングを開始します...")
# Webアプリのソースとして使われる固定パスに上書き出力するよう設定
script_dir = os.path.dirname(os.path.abspath(__file__))
output_video_path = os.path.join(script_dir, "static", "media", "result-loop.webm")
bpy.context.scene.render.filepath = output_video_path

# レンダリングを実行（Blenderファイルで設定したフォーマット、カメラ設定などが引き継がれます）
try:
    bpy.ops.render.render(animation=True)
    
    # Blenderはアニメーション出力時に「0001-0100」のようなフレーム範囲をファイル名に自動付与するため、リネームする
    import glob
    base_dir = os.path.dirname(output_video_path)
    base_name, ext = os.path.splitext(os.path.basename(output_video_path))
    search_pattern = os.path.join(base_dir, f"{base_name}*{ext}")
    generated_files = glob.glob(search_pattern)
    
    for f in generated_files:
        if f != output_video_path and (f.endswith(f"{ext}")):
            # すでに同名のファイルが存在する場合は削除
            if os.path.exists(output_video_path):
                os.remove(output_video_path)
            os.rename(f, output_video_path)
            break
            
    print(f"✅ レンダリング完了: {output_video_path}")
except Exception as e:
    print(f"❌ レンダリング中にエラーが発生しました: {e}")

print("--- 🔴 Blender内部プロセス完了 ---\n")
