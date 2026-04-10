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

function applyTheme(theme) {
  document.documentElement.setAttribute("data-theme", theme);
  const toggle = document.getElementById("themeToggle");
  toggle.textContent = theme === "dark" ? "ライトモード" : "ダークモード";
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
  const raw = sessionStorage.getItem("emm_generate_payload");
  if (!raw) {
    setResult("入力値が見つかりません。入力画面に戻って再実行してください。");
    return;
  }

  let payload;
  try {
    payload = JSON.parse(raw);
  } catch (error) {
    setResult(`入力値の読み込みに失敗しました\n${error}`);
    return;
  }

  try {
    const res = await fetch("/generate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await res.json();
    if (data.success) {
      setResult(`生成成功\nGLB: ${data.glb_path}\nBLEND: ${data.blend_path}`);
    } else {
      setResult(`生成失敗\n${data.error || "不明なエラー"}`);
    }
  } catch (error) {
    setResult(`通信エラー\n${error}`);
  } finally {
    sessionStorage.removeItem("emm_generate_payload");
  }
}

function initIndexPage() {
  const runButton = document.getElementById("runButton");
  const testButton = document.getElementById("testButton");
  if (!runButton || !testButton) {
    return;
  }
  runButton.addEventListener("click", submitForm);
  testButton.addEventListener("click", testInput);
  bindSliderDisplay();
}

function initLoadingPage() {
  const backButton = document.getElementById("backButton");
  if (!backButton) {
    return;
  }
  backButton.addEventListener("click", () => {
    window.location.href = "/";
  });
  runGenerateFromSession();
}

initTheme();
initIndexPage();
initLoadingPage();
