function getPayload() {
  return {
    joy: parseFloat(document.getElementById("joy").value),
    calm: parseFloat(document.getElementById("calm").value),
    anger: parseFloat(document.getElementById("anger").value),
    sadness: parseFloat(document.getElementById("sadness").value),
    fear: parseFloat(document.getElementById("fear").value),
  };
}

function setResult(text) {
  const result = document.getElementById("result");
  if (result) {
    result.textContent = text;
  }
}

function appendLog(message) {
  const result = document.getElementById("result");
  if (!result) return;
  const now = new Date().toLocaleTimeString();
  const prefix = result.textContent && !result.textContent.endsWith("\n") ? "\n" : "";
  result.textContent += `${prefix}[${now}] ${message}`;
}

async function submitForm() {
  sessionStorage.setItem("emm_generate_mode", "generate");
  sessionStorage.setItem("emm_generate_payload", JSON.stringify(getPayload()));
  window.location.href = "/loading";
}

async function runGenerateFromSession() {
  appendLog("runGenerateFromSession 開始");
  const raw = sessionStorage.getItem("emm_generate_payload");
  const mode = sessionStorage.getItem("emm_generate_mode") || "generate";
  if (!raw) {
    setResult("入力値が見つかりません。入力画面に戻って再実行してください。");
    appendLog("payload が sessionStorage に存在しません");
    return;
  }

  let payload;
  try {
    payload = JSON.parse(raw);
  } catch (error) {
    setResult(`入力値の読み込みに失敗しました\n${error}`);
    appendLog(`JSON.parse 失敗: ${error}`);
    return;
  }

  const loadingTitle = document.getElementById("loadingTitle");
  const loadingNote = document.getElementById("loadingNote");
  if (mode === "test") {
    if (loadingTitle) {
      loadingTitle.textContent = "モンスター孵化準備テスト中・・・";
    }
    if (loadingNote) {
      loadingNote.textContent = "3Dモデル生成は行わず、入力受信のみテストします。";
    }
  }

  const endpoint = mode === "test" ? "/test-input" : "/generate";
  try {
    appendLog(`エンドポイント ${endpoint} へリクエスト送信`);
    const res = await fetch(endpoint, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    appendLog(`レスポンス受信 status=${res.status}`);
    const data = await res.json();
    if (data.success) {
      if (mode === "test") {
        appendLog("接続テスト成功");
        appendLog(JSON.stringify(data, null, 2));
        appendLog("10秒後に結果画面へ遷移します（テスト用）...");
        setTimeout(() => {
          window.location.href = "/result";
        }, 10000);
      } else {
        appendLog("生成成功");
        appendLog(`GLB: ${data.glb_path}`);
        appendLog(`BLEND: ${data.blend_path}`);
        if (data.print_time) {
          sessionStorage.setItem("emm_print_time", data.print_time);
        }
        window.location.href = "/result";
      }
    } else {
      appendLog(`生成失敗: ${data.error || "不明なエラー"}`);
    }
  } catch (error) {
    appendLog(`通信エラー: ${error}`);
  } finally {
    sessionStorage.removeItem("emm_generate_payload");
    sessionStorage.removeItem("emm_generate_mode");
    appendLog("runGenerateFromSession 終了");
  }
}

function initIndexPage() {
  const runButton = document.getElementById("runButton");
  const loadingTestButton = document.getElementById("loadingTestButton");
  const emotionForm = document.getElementById("emotionForm");

  if (runButton) {
    runButton.addEventListener("click", () => submitForm());
  }

  if (loadingTestButton) {
    loadingTestButton.addEventListener("click", () => {
      sessionStorage.setItem("emm_generate_mode", "test");
      sessionStorage.setItem("emm_generate_payload", JSON.stringify(getPayload()));
      window.location.href = "/loading";
    });
  }

  if (emotionForm) {
    // スライダーの値表示の更新
    const sliders = emotionForm.querySelectorAll('input[type="range"]');
    sliders.forEach((slider) => {
      const updateValue = () => {
        const valSpan = document.getElementById(`${slider.id}_v`);
        if (valSpan) valSpan.textContent = parseFloat(slider.value).toFixed(2);
        
        // プログレスバー風の色付け
        const percent = ((slider.value - slider.min) / (slider.max - slider.min)) * 100;
        slider.style.setProperty("--fill-percent", `${percent}%`);
      };
      slider.addEventListener("input", updateValue);
      updateValue(); // 初期表示
    });
  }
}

function initLoadingPage() {
  const backButton = document.getElementById("backButton");
  if (!backButton) {
    return;
  }
  const video = document.getElementById("loadingVideo");
  appendLog("loading ページ初期化");
  if (video) {
    appendLog(`canPlayType(video/mp4)=${video.canPlayType("video/mp4")}`);
    appendLog(`video source=${video.currentSrc || video.getAttribute("src") || "not selected yet"}`);
    video.addEventListener("loadedmetadata", () => {
      appendLog(`video loadedmetadata ${video.videoWidth}x${video.videoHeight}`);
    });
    video.addEventListener("loadstart", () => {
      appendLog("video loadstart");
    });
    video.addEventListener("loadeddata", () => {
      appendLog("video loadeddata");
    });
    video.addEventListener("canplay", () => {
      appendLog("video canplay");
    });
    video.addEventListener("playing", () => {
      appendLog("video playing");
    });
    video.addEventListener("error", () => {
      const code = video.error ? video.error.code : "unknown";
      appendLog(`video error code=${code}`);
    });
    video.load();
    const playPromise = video.play();
    if (playPromise && typeof playPromise.then === "function") {
      playPromise
        .then(() => appendLog("video.play() resolved"))
        .catch((error) => appendLog(`video.play() rejected: ${error}`));
    }
    setTimeout(() => {
      appendLog(`video readyState=${video.readyState} networkState=${video.networkState}`);
    }, 1000);
  } else {
    appendLog("video 要素が見つかりません");
  }
  backButton.addEventListener("click", () => {
    window.location.href = "/";
  });
  runGenerateFromSession();
}

initIndexPage();
initLoadingPage();
