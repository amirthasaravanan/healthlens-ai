/**
 * 🩺 DISEASE RISK PREDICTOR LOGIC
 * Collects data from the form, sends it to the Flask backend,
 * and redirects the user to the results page.
 */
async function predictDisease() {
    // 1. Gather input values from the form in predict.html
    const data = {
        age: document.querySelector('[name="age"]').value,
        bp: document.querySelector('[name="bp"]').value,
        sugar: document.querySelector('[name="sugar"]').value,
        bmi: document.querySelector('[name="bmi"]').value,
        smoking: document.querySelector('[name="smoking"]').value,
        activity: document.querySelector('[name="activity"]').value
    };

    // 2. Validate that all fields are filled
    if (!data.age || !data.bp || !data.sugar || !data.bmi || !data.smoking || !data.activity) {
        alert("Please fill in all health metrics before analyzing.");
        return;
    }

    // 3. Send data to the Flask route /predict-disease
    try {
        const res = await fetch('/predict-disease', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        if (!res.ok) throw new Error("Server error");

        const results = await res.json();

        // 4. Save results to localStorage so they can be accessed on results.html
        localStorage.setItem('healthResults', JSON.stringify(results));

        // 5. Redirect the user to the new results page
        window.location.href = "/results";

    } catch (error) {
        console.error("Prediction Error:", error);
        alert("Something went wrong with the analysis. Please try again.");
    }
}

/**
 * 📄 MEDICAL REPORT SIMPLIFIER LOGIC
 * Handles the text area and file upload for medical reports.
 */
async function simplify() {
    const reportText = document.getElementById("report").value;
    const fileInput = document.getElementById("file-upload"); // Matches the new ID in simplify.html
    const btn = document.querySelector(".analyze-btn");
    
    // 1. Validation: Check if we have either text OR a file
    const hasFile = fileInput && fileInput.files.length > 0;
    
    if (!reportText && !hasFile) { 
        alert("Please paste text or upload a PDF first."); 
        return; 
    }

    // 2. UI Feedback
    btn.innerText = "Analyzing Report... Please wait";
    btn.disabled = true;

    // 3. Prepare Data
    const formData = new FormData();
    
    if (hasFile) {
        // If there's a file, we send the file object
        formData.append("file", fileInput.files[0]);
    } else {
        // Otherwise, we send the pasted text
        formData.append("text", reportText);
    }

    try {
        // 4. Send to Flask
        const res = await fetch('/simplify-report', {
            method: 'POST',
            body: formData // Fetch handles the Content-Type automatically for FormData
        });
        
        if (!res.ok) throw new Error("Server had an issue processing the report.");
        
        const result = await res.json();
        
        // 5. Save and Redirect
        console.log("AI Response Received:", result);
        localStorage.setItem('simplifiedReport', JSON.stringify(result));
        
        window.location.href = "/simplified-report"; 

    } catch (error) {
        console.error("Error:", error);
        btn.innerText = "Simplify the Report";
        btn.disabled = false;
        alert("Something went wrong. Make sure you are using a valid PDF.");
    }
}