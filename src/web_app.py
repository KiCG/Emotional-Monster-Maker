from flask import Flask, jsonify, render_template, request

try:
    from main import generate_monster, validate_emotion_values
except ModuleNotFoundError:
    from src.main import generate_monster, validate_emotion_values

app = Flask(__name__)

@app.get("/")
def index():
    return render_template("index.html")


@app.get("/loading")
def loading():
    return render_template("loading.html")


@app.post("/generate")
def generate():
    payload = request.get_json(silent=True) or {}
    result = generate_monster(
        payload.get("joy", 1),
        payload.get("calm", 1),
        payload.get("anger", 1),
        payload.get("sadness", 1),
        payload.get("fear", 1),
    )
    status = 200 if result.get("success") else 400
    return jsonify(result), status


@app.post("/test-input")
def test_input():
    payload = request.get_json(silent=True) or {}
    ok, normalized, error = validate_emotion_values(
        payload.get("joy"),
        payload.get("calm"),
        payload.get("anger"),
        payload.get("sadness"),
        payload.get("fear"),
    )
    response = {
        "success": ok,
        "received": payload,
        "normalized": normalized if ok else None,
        "message": "iPadからの入力を受信しました。" if ok else error,
    }
    return jsonify(response), 200 if ok else 400


if __name__ == "__main__":
    # iPadなど別端末からアクセスできるよう 0.0.0.0 で待ち受け
    app.run(host="0.0.0.0", port=8000)
