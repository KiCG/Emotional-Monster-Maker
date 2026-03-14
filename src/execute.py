import sys
import shutil
import subprocess

# 引数が正しく渡されているかチェック (スクリプト名 + 4つの引数 = 合計5つ)
if len(sys.argv) < 5:
    print("エラー: 必要な引数が不足しています。")
    print("使い方: python execute.py <base_blend> <new_blend> <glb_target> <blender_script>")
    sys.exit(1)

# main.py から渡された引数を変数に格納
base_blend_path = sys.argv[1]
new_blend_path = sys.argv[2]
glb_target_path = sys.argv[3]
blender_script_path = sys.argv[4]

# 1. 特定のBlenderファイルを複製
try:
    shutil.copy(base_blend_path, new_blend_path)
    print(f"Blenderファイル {new_blend_path} を作成しました。")
except FileNotFoundError:
    print(f"エラー: 元となるファイル '{base_blend_path}' が見つかりません。")
    sys.exit(1)


# 2. 複製したファイルを開き、Blender内スクリプトを実行
cmd = [
    "/Applications/Blender 3.app/Contents/MacOS/Blender",
    "--factory-startup",  # 1. まずまっさらな初期状態にする
    "--background",       # 2. 画面なしモードにする
    new_blend_path,       # 3. その上で、対象のBlenderファイルを開く（重要！）
    "--python", blender_script_path, # 4. スクリプトを実行
    "--", glb_target_path
]

print("Blender内部処理を実行中...")
subprocess.run(cmd)
print("Blender内部処理が完了しました。")
