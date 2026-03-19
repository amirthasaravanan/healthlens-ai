
async function predictDisease() {
    
    const data = {
        age: document.querySelector('[name="age"]').value,
        bp: document.querySelector('[name="bp"]').value,
        sugar: document.querySelector('[name="sugar"]').value,
        bmi: document.querySelector('[name="bmi"]').value,
        smoking: document.querySelector('[name="smoking"]').value,
        activity: document.querySelector('[name="activity"]').value
    };

   
    if (!data.age || !data.bp || !data.sugar || !data.bmi || !data.smoking || !data.activity) {
        alert("Please fill in all health metrics before analyzing.");
        return;
    }

   
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


async function simplify() {
    const reportText = document.getElementById("report").value;
    const fileInput = document.getElementById("file-upload"); 
    const btn = document.querySelector(".analyze-btn");
    
    const hasFile = fileInput && fileInput.files.length > 0;
    
    if (!reportText && !hasFile) { 
        alert("Please paste text or upload a PDF first."); 
        return; 
    }

    
    btn.innerText = "Analyzing Report... Please wait";
    btn.disabled = true;

    
    const formData = new FormData();
    
    if (hasFile) {
       
        formData.append("file", fileInput.files[0]);
    } else {
        
        formData.append("text", reportText);
    }

    try {
       
        const res = await fetch('/simplify-report', {
            method: 'POST',
            body: formData 
        });
        
        if (!res.ok) throw new Error("Server had an issue processing the report.");
        
        const result = await res.json();
        
        
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
