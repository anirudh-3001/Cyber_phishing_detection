async function checkUrl() {
  const url = document.getElementById("urlInput").value;
  const status = document.getElementById("status");
  const flowContainer = document.getElementById("flowContainer");
  const methodInfo = document.getElementById("methodInfo");

  if (!url) {
    status.innerText = "❗ Please enter a URL";
    flowContainer.style.display = "none";
    return;
  }

  flowContainer.style.display = "block";
  status.innerText = "";
  methodInfo.innerText = "";
  resetSteps();

  try {
    /* ---------------- STEP 1 ---------------- */
    showStep(1, "Canonicalizing URL...");
    await sleep(400);
    completeStep(1);

    /* ---------------- STEP 2 ---------------- */
    showStep(2, "Generating fingerprint (HMAC-SHA512)...");
    const fpRes = await fetch("http://127.0.0.1:8000/fingerprint", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url })
    });

    if (!fpRes.ok) throw new Error("Fingerprint API failed");
    const fpData = await fpRes.json();

    document.getElementById("fingerprintValue").innerText = fpData.fingerprint;
    document.getElementById("fingerprintDisplay").style.display = "block";
    await sleep(500);
    completeStep(2);

    /* ---------------- STEP 2b ---------------- */
    showStep("2b", "Extracting prefix...");
    document.getElementById("prefixValue").innerText = fpData.prefix;
    document.getElementById("prefixDisplay").style.display = "block";
    await sleep(400);
    completeStep("2b");

    /* ---------------- STEP 3 ---------------- */
    showStep(3, "Deleting original URL (privacy)...");
    document.getElementById("deleteDisplay").style.display = "block";
    await sleep(400);
    completeStep(3);

    /* ---------------- STEP 4 ---------------- */
    showStep(4, "Reputation + ML + Hybrid analysis...");
    await sleep(300);

    /* ---------------- STEP 5 + 6 (ONE CALL ONLY) ---------------- */
    const detectRes = await fetch("http://127.0.0.1:8000/detect", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        prefix: fpData.prefix,

        domain_age_days: fpData.domain_age_days,
        tls_valid: fpData.tls_valid,
        redirect_count: fpData.redirect_count,
        suspicious_js: fpData.suspicious_js,

        url_length: fpData.url_length,
        dot_count: fpData.dot_count,
        hyphen_count: fpData.hyphen_count,
        digit_ratio: fpData.digit_ratio,
        has_at: fpData.has_at,
        entropy: fpData.entropy
      })
    });

    if (!detectRes.ok) throw new Error("Detection failed");
    const result = await detectRes.json();

    completeStep(4);
    showStep(7, "Final decision generated");
    await sleep(300);
    completeStep(7);

    displayResult(result, status, methodInfo);

  } catch (err) {
    status.innerText = "❌ Error: " + err.message;
    methodInfo.innerText = "Ensure backend is running at http://127.0.0.1:8000";
  }
}

/* ---------------- UI HELPERS ---------------- */

function showStep(stepNum, text) {
  const step = document.getElementById("step" + stepNum);
  if (!step) return;
  step.classList.add("active");
  step.querySelector(".step-description").innerText = text;
}

function completeStep(stepNum) {
  const step = document.getElementById("step" + stepNum);
  if (!step) return;
  step.classList.remove("active");
  step.classList.add("completed");
  step.querySelector(".step-number").innerText = "✓";
}

function resetSteps() {
  [1, 2, "2b", 3, 4, 5, 6, 7].forEach(id => {
    const step = document.getElementById("step" + id);
    if (step) {
      step.className = "flow-step";
      step.querySelector(".step-number").innerText = id;
    }
  });

  ["fingerprintDisplay", "prefixDisplay", "deleteDisplay"].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.style.display = "none";
  });
}

function displayResult(result, statusElement, methodElement) {
  let text = "";

  if (result.result === "phishing") {
    statusElement.innerText = "🚨 PHISHING DETECTED";
    statusElement.className = "phishing";
  } else {
    statusElement.innerText = "✅ WEBSITE IS LEGITIMATE";
    statusElement.className = "legitimate";
  }

  text += `Detection Method: ${result.method.toUpperCase()}\n\n`;

  if (result.reasons && result.reasons.length > 0) {
    text += "Reasons:\n";
    result.reasons.forEach(r => {
      text += `• ${r}\n`;
    });
  }

  if (result.feature_contributions) {
    text += "\nTop contributing features:\n";

    Object.entries(result.feature_contributions)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 5)
      .forEach(([feature, score]) => {
        text += `• ${feature} – ${(score * 100).toFixed(1)}%\n`;
      });
  }

  text += `\nConfidence: ${(result.confidence * 100).toFixed(1)}%`;

  methodElement.innerText = text;
}


function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}
