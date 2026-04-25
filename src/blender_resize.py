import bpy

# 目標サイズ (メートル単位: 0.05 = 50mm)
TARGET_SIZE = 0.025
obj = bpy.context.active_object

# 対象がメッシュ（ポリゴン）データの場合のみ処理する
if obj and obj.type == 'MESH':
    # 現在の寸法を取得
    dims = obj.dimensions
    max_dim = max(dims.x, dims.y, dims.z)
    
    if max_dim > 0:
        # スケール倍率を計算 (目標 / 現在の最大長)
        scale_factor = TARGET_SIZE / max_dim
        
        # =========================================================
        # 【重要】裏起動でクラッシュする bpy.ops.object.transform_apply の代わりに、
        # メッシュの頂点座標(ジオメトリ)を直接縮小して適用状態にします。
        # =========================================================
        mesh = obj.data
        for vert in mesh.vertices:
            vert.co *= scale_factor
            
        # 変更をBlender内部に更新
        mesh.update()
        
        print(f"✅ {obj.name} を最大寸法 {TARGET_SIZE}m にリサイズしました (Headless Safe)")
