import os
import subprocess
import requests

CREALITY_PRINT_CLI = "/Applications/Creality Print.app/Contents/MacOS/CrealityPrint"
OCTOPRINT_URL = "http://localhost:5001" # 環境に合わせて変更してください
OCTOPRINT_API_KEY = "w_31UZFV3L1TUveWo3CrLQM167laqdB4hCh4Yt8Uyfg" # 実際のAPIキーに変更してください

PRUSA_SLICER_CLI = "/Applications/Original Prusa Drivers/PrusaSlicer.app/Contents/MacOS/PrusaSlicer"

def slice_stl(stl_path: str) -> str:
    """
    STLファイルをPrusaSlicerでスライスし、生成されたG-Codeファイルのパスを返す。
    """
    if not os.path.exists(stl_path):
        print(f"❌ エラー: STLファイルが見つかりません: {stl_path}")
        return None

    gcode_dir = os.path.dirname(stl_path)
    gcode_filename = os.path.basename(stl_path).replace('.stl', '.gcode')
    gcode_path = os.path.join(gcode_dir, gcode_filename)
    
    print(f"🔪 PrusaSlicerによるスライスを開始します: {stl_path}")
    
    # 実行コマンドの構築
    # --scale 1000: Blenderの1単位(m)をスライサーの1単位(mm)に変換し、さらに5cmに合わせるため1000倍
    cmd = [
        PRUSA_SLICER_CLI,
        "--export-gcode",
        "--output", gcode_path,
        "--scale", "1000",
        "--support-material", # サポート材を有効化
        stl_path
    ]
    
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"✅ スライス完了！出力先: {gcode_path}")
        return gcode_path
        
    except subprocess.CalledProcessError as e:
        print(f"❌ スライス処理エラー: {e.stderr}")
        return None


def upload_to_octoprint(gcode_path: str, auto_print: bool = True):
    """
    OctoPrintへG-codeをアップロードし、自動で印刷を開始する。
    """
    if not gcode_path or not os.path.exists(gcode_path):
        print("❌ アップロードするG-codeが見つかりません。")
        return

    print(f"🌐 OctoPrintへアップロード中: {gcode_path}")
    
    url = f"{OCTOPRINT_URL}/api/files/local"
    headers = {"X-Api-Key": OCTOPRINT_API_KEY}
    
    with open(gcode_path, 'rb') as f:
        files = {'file': (os.path.basename(gcode_path), f)}
        data = {}
        if auto_print:
            data['print'] = 'true'
            
        try:
            response = requests.post(url, headers=headers, files=files, data=data)
            
            if response.status_code == 201:
                print("✅ アップロード（と印刷指示）が成功しました！")
            else:
                print(f"❌ OctoPrintエラー: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"❌ 通信エラー: {e}")

if __name__ == "__main__":
    # ターミナルから直接テストするための処理
    import sys
    if len(sys.argv) > 1:
        test_stl = sys.argv[1]
        print(f"🔧 テスト実行: {test_stl}")
        gcode = slice_stl(test_stl)
        if gcode:
            # スライス成功時に自動でOctoPrintへ送信（テスト時は安全のため自動プリントをオフにすることも可能ですが、今回はそのままオンにします）
            upload_to_octoprint(gcode, auto_print=True)
    else:
        print("使用法: python src/print_manager.py <stlファイルのパス>")
