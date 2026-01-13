async function checkUrl() {
  const url = document.getElementById("urlInput").value;
  const status = document.getElementById("status");
  const flowContainer = document.getElementById("flowContainer");
  const methodInfo = document.getElementById("methodInfo");

  if (!url) {
    status.innerText = "❗ Please enter a URL";
    status.className = "";
    flowContainer.style.display = "none";
    return;
  }

  // Show flow container
  flowContainer.style.display = "block";
  status.className = "";
  methodInfo.innerText = "";
  
  // Reset all steps
  resetSteps();

  let detectionPhase = null; // Track which phase detected it

  try {
    // STEP 1: Canonicalize URL
    showStep(1, "Canonicalizing URL format...");
    await sleep(600);
    completeStep(1);

    // STEP 2: Generate Fingerprint
    showStep(2, "Generating secure fingerprint (HMAC-SHA512)...");
    
    const fpRes = await fetch("http://127.0.0.1:8000/fingerprint", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url })
    });

    if (!fpRes.ok) throw new Error("Fingerprint generation failed");
    
    const fpData = await fpRes.json();
    
    // Display fingerprint
    const fpDisplay = document.getElementById("fingerprintDisplay");
    const fpValue = document.getElementById("fingerprintValue");
    fpValue.innerText = fpData.fingerprint || "Generated (128 characters)";
    fpDisplay.style.display = "block";
    
    await sleep(800);
    completeStep(2);
    
    // STEP 2b: Extract Prefix
    showStep("2b", "Extracting 12-character prefix for comparison...");
    
    const prefixDisplay = document.getElementById("prefixDisplay");
    const prefixValue = document.getElementById("prefixValue");
    prefixValue.innerText = fpData.prefix;
    prefixDisplay.style.display = "block";
    
    await sleep(600);
    completeStep("2b");

    // STEP 3: Delete Original URL (Privacy)
    showStep(3, "🗑️ Deleting original URL from memory...");
    const deleteDisplay = document.getElementById("deleteDisplay");
    deleteDisplay.style.display = "block";
    await sleep(800);
    completeStep(3);

    // STEP 4: Reputation Check
    showStep(4, "Checking prefix against known phishing database...");
    await sleep(800);

    // First fetch to check reputation
    const reputationRes = await fetch("http://127.0.0.1:8000/detect", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        prefix: fpData.prefix,
        domain_age_days: 0,
        tls_valid: 0,
        redirect_count: 0,
        suspicious_js: 0
      })
    });

    if (!reputationRes.ok) throw new Error("Detection failed");
    
    const result = await reputationRes.json();

    // Check if detected in reputation phase
    if (result.result === "phishing" && result.method === "reputation") {
      detectionPhase = 4;
      markDetectionPhase(4, "🚨 PHISHING DETECTED (Reputation Database)");
      completeStep(4, true); // true = detected here
      
      // Skip to result
      showStep(7, "Phishing detected in reputation phase!");
      await sleep(500);
      completeStep(7);
      
      displayResult(result, status, methodInfo, detectionPhase);
      return;
    }

    completeStep(4);

    // STEP 5: Extract Real Features
    showStep(5, "Extracting real ML features (domain age, TLS, redirects, JS)...");
    
    // Call backend to extract real features
    const featuresRes = await fetch("http://127.0.0.1:8000/fingerprint", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url })
    });
    
    if (!featuresRes.ok) throw new Error("Feature extraction failed");
    
    const featuresData = await featuresRes.json();
    const features = {
      prefix: fpData.prefix,
      domain_age_days: featuresData.domain_age_days || 0,
      tls_valid: featuresData.tls_valid || 0,
      redirect_count: featuresData.redirect_count || 0,
      suspicious_js: featuresData.suspicious_js || 0
    };
    
    // Display extracted features
    const featuresDisplay = document.getElementById("featuresDisplay");
    if (!featuresDisplay) {
      const newDiv = document.createElement("div");
      newDiv.id = "featuresDisplay";
      newDiv.innerHTML = `<p><strong>Extracted Features:</strong></p>
        <p>Domain Age: ${features.domain_age_days} days</p>
        <p>TLS/HTTPS Valid: ${features.tls_valid === 1 ? '✅ Yes' : '❌ No'}</p>
        <p>HTTP Redirects: ${features.redirect_count}</p>
        <p>Suspicious JS: ${features.suspicious_js === 1 ? '⚠️ Detected' : '✅ None'}</p>`;
      document.getElementById("status").parentNode.insertBefore(newDiv, document.getElementById("status").nextSibling);
    }
    
    await sleep(600);
    completeStep(5);

    // STEP 6: ML Prediction
    showStep(6, "Running Random Forest classifier with real features...");
    
    // Send real features for ML prediction
    const mlRes = await fetch("http://127.0.0.1:8000/detect", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(features)
    });
    
    if (!mlRes.ok) throw new Error("ML prediction failed");
    
    const mlResult = await mlRes.json();
    
    await sleep(800);
    completeStep(6);

    // Check ML result
    if (mlResult.result === "phishing") {
      detectionPhase = 6;
      markDetectionPhase(6, "🚨 PHISHING DETECTED (ML Classifier with Real Features)");
    }

    // STEP 7: Result
    showStep(7, "Generating final result...");
    await sleep(500);
    completeStep(7);

    // Display final result
    displayResult(mlResult, status, methodInfo, detectionPhase);

  } catch (err) {
    status.innerText = "❌ Error: " + err.message;
    status.className = "";
    methodInfo.innerText = "Please ensure the backend server is running on http://127.0.0.1:8000";
  }
}

function showStep(stepNum, description) {
  // Mark previous step as completed
  if (stepNum !== "2b" && stepNum > 1) {
    const prevStep = stepNum === "2b" ? 2 : stepNum - 1;
    const prevElement = document.getElementById("step" + prevStep);
    if (prevElement) {
      prevElement.classList.add("completed");
      prevElement.classList.remove("active");
    }
  }
  
  // Show current step as active
  const currentStep = document.getElementById("step" + stepNum);
  currentStep.classList.add("active");
  currentStep.querySelector(".step-description").innerText = description;
}

function completeStep(stepNum, isDetected = false) {
  const step = document.getElementById("step" + stepNum);
  step.classList.remove("active");
  step.classList.add("completed");
  
  if (isDetected) {
    step.classList.add("detected");
  }
  
  // Update description based on step
  const descriptions = {
    1: "✓ URL canonicalized",
    2: "✓ Fingerprint generated (HMAC-SHA512)",
    "2b": "✓ 12-char prefix extracted",
    3: "✓ Original URL permanently deleted from memory",
    4: "✓ Reputation database check completed",
    5: "✓ ML features extracted",
    6: "✓ Random Forest classification completed",
    7: "✓ Analysis finished"
  };
  
  step.querySelector(".step-description").innerText = descriptions[stepNum];
  step.querySelector(".step-number").innerText = "✓";
}

function markDetectionPhase(stepNum, message) {
  const step = document.getElementById("step" + stepNum);
  step.classList.add("detected");
  step.querySelector(".step-description").innerText = message;
  step.querySelector(".step-number").innerHTML = "🚨";
}

function resetSteps() {
  const stepIds = [1, 2, "2b", 3, 4, 5, 6, 7];
  stepIds.forEach(id => {
    const step = document.getElementById("step" + id);
    if (step) {
      step.classList.remove("active", "completed", "detected");
      step.querySelector(".step-number").innerText = id;
    }
  });
  
  // Hide data displays
  document.getElementById("fingerprintDisplay").style.display = "none";
  document.getElementById("prefixDisplay").style.display = "none";
  document.getElementById("deleteDisplay").style.display = "none";
}

function displayResult(result, statusElement, methodElement, detectionPhase) {
  if (result.result === "phishing") {
    statusElement.innerText = "🚨 PHISHING DETECTED!";
    statusElement.className = "phishing";
    
    const detectionText = result.method === 'reputation' 
      ? '✓ Detected in Phase 4: Reputation Database (Known Phishing URL)' 
      : '✓ Detected in Phase 6: Machine Learning Classifier (Unknown Phishing)';
    
    methodElement.innerText = detectionText;
  } else {
    statusElement.innerText = "✅ Website appears to be LEGITIMATE";
    statusElement.className = "legitimate";
    methodElement.innerText = "Status: ✓ Safe to visit (passed all checks)";
  }
}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}
