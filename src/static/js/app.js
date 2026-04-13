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

function applyTheme(theme) {
  document.documentElement.setAttribute("data-theme", theme);
  const toggle = document.getElementById("themeToggle");
  if (toggle) {
    toggle.textContent = theme === "dark" ? "ライトモード" : "ダークモード";
  }
}

function initTheme() {
  const saved = localStorage.getItem("emm_theme");
  const theme = saved === "dark" ? "dark" : "light";
  applyTheme(theme);

  const toggle = document.getElementById("themeToggle");
  if (!toggle) {
    return;
  }
  toggle.addEventListener("click", () => {
    const current = document.documentElement.getAttribute("data-theme");
    const next = current === "dark" ? "light" : "dark";
    localStorage.setItem("emm_theme", next);
    applyTheme(next);
  });
}

function bindSliderDisplay() {
  document.querySelectorAll("input[type='range']").forEach((slider) => {
    const key = slider.dataset.key;
    const valueNode = document.getElementById(`${key}_v`);
    const update = () => {
      valueNode.textContent = Number(slider.value).toFixed(2);
      const min = Number(slider.min);
      const max = Number(slider.max);
      const val = Number(slider.value);
      const percent = ((val - min) / (max - min)) * 100;
      slider.style.setProperty("--fill-percent", `${percent}%`);
    };
    slider.addEventListener("input", update);
    update();
  });
}

async function submitForm() {
  sessionStorage.setItem("emm_generate_mode", "generate");
  sessionStorage.setItem("emm_generate_payload", JSON.stringify(getPayload()));
  window.location.href = "/loading";
}

function startLoadingTest() {
  sessionStorage.setItem("emm_generate_mode", "test");
  sessionStorage.setItem("emm_generate_payload", JSON.stringify(getPayload()));
  window.location.href = "/loading";
}

async function testInput() {
  const testButton = document.getElementById("testButton");
  testButton.disabled = true;
  setResult("入力値をバックエンドへ送信して確認中...");

  try {
    const res = await fetch("/test-input", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(getPayload()),
    });
    const data = await res.json();
    setResult(`接続テスト結果\n${JSON.stringify(data, null, 2)}`);
  } catch (error) {
    setResult(`通信エラー\n${error}`);
  } finally {
    testButton.disabled = false;
  }
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
      } else {
        appendLog("生成成功");
        appendLog(`GLB: ${data.glb_path}`);
        appendLog(`BLEND: ${data.blend_path}`);
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
  const testButton = document.getElementById("testButton");
  const loadingTestButton = document.getElementById("loadingTestButton");
  if (!runButton || !testButton || !loadingTestButton) {
    return;
  }
  runButton.addEventListener("click", submitForm);
  testButton.addEventListener("click", testInput);
  loadingTestButton.addEventListener("click", startLoadingTest);
  bindSliderDisplay();
}

function initLoadingPage() {
  const backButton = document.getElementById("backButton");
  if (!backButton) {
    return;
  }
  const video = document.getElementById("loadingVideo");
  appendLog("loading ページ初期化");
  if (video) {
    appendLog(`canPlayType(video/webm)=${video.canPlayType("video/webm")}`);
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

initTheme();
initIndexPage();
initLoadingPage();
