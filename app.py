from google import genai
from flask import Flask, request, jsonify, render_template
import json
import pypdf

app = Flask(__name__)

client = genai.Client(api_key="myapikey") 


safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
]





@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict')
def predict_page():
    return render_template('predict.html')

@app.route('/results')
def results_page():
    return render_template('results.html')

@app.route('/simplify')
def simplify_page():
    return render_template('simplify.html')

def calculate_percentage(score, max_score=12):
    return round(min((score / max_score) * 100, 100), 1)


def get_risk_label(percentage):
    if percentage <= 50:
        return "Low"
    elif 50 < percentage <= 75:
        return "Moderate"
    else:
        return "High"

@app.route('/predict-disease', methods=['POST'])
def predict_disease():
    data = request.json
    age = int(data.get('age', 0))
    bp = int(data.get('bp', 0))
    sugar = int(data.get('sugar', 0))
    bmi = float(data.get('bmi', 0))
    
   
    smoking_input = data.get('smoking', '').lower()
    is_smoker = (smoking_input == "smoker")
    
   
    activity_input = data.get('activity', '').lower()
    is_low_activity = (activity_input == "low activity")

    results = []

    
    h_score, h_reasons = 0, []
    if age > 60: h_score += 2; h_reasons.append("Age factor (Senior)")
    elif age >= 40: h_score += 1; h_reasons.append("Age factor (40-60)")
    if bp >= 140: h_score += 2; h_reasons.append("Hypertension (High BP)")
    elif bp >= 120: h_score += 1; h_reasons.append("Pre-hypertension")
    if sugar >= 126: h_score += 2; h_reasons.append("High Blood Sugar")
    elif sugar >= 100: h_score += 1; h_reasons.append("Prediabetic sugar levels")
    if bmi >= 30: h_score += 2; h_reasons.append("Obese BMI")
    elif bmi >= 25: h_score += 1; h_reasons.append("Overweight BMI")
    if is_smoker: h_score += 2; h_reasons.append("Regular Smoker")
    if is_low_activity: h_score += 2; h_reasons.append("Sedentary Lifestyle")
    
    h_pct = calculate_percentage(h_score)
    results.append({"name": "Heart Disease", "percentage": h_pct, "risk": get_risk_label(h_pct), "reasons": h_reasons, "tips": ["Reduce salt intake", "30 mins cardio daily", "Quit smoking"]})

   
    l_score, l_reasons = 0, []
    if is_smoker: l_score += 6; l_reasons.append("Regular Smoking (Major Risk)")
    if age > 60: l_score += 2; l_reasons.append("Age factor (>60)")
    if bp >= 140: l_score += 2; l_reasons.append("High BP impact")
    if is_low_activity: l_score += 2; l_reasons.append("Low lung capacity indicators")
    
    l_pct = calculate_percentage(l_score)
    results.append({"name": "Lung Disease", "percentage": l_pct, "risk": get_risk_label(l_pct), "reasons": l_reasons, "tips": ["Breathing exercises", "Avoid pollution", "Pulmonary checkup"]})

   
    k_score, k_reasons = 0, []
    if sugar >= 126: k_score += 4; k_reasons.append("Diabetes (Primary Kidney Threat)")
    if bp >= 140: k_score += 4; k_reasons.append("Chronic Hypertension")
    if bmi >= 30: k_score += 2; k_reasons.append("Obesity strain")
    if age > 60: k_score += 2; k_reasons.append("Age-related filtration decline")
    
    k_pct = calculate_percentage(k_score)
    results.append({"name": "Kidney Disease", "percentage": k_pct, "risk": get_risk_label(k_pct), "reasons": k_reasons, "tips": ["Stay hydrated", "Limit salt", "Control BP & Sugar"]})

   
    d_score, d_reasons = 0, []
    if sugar >= 126: d_score += 6; d_reasons.append("High Fasting Glucose")
    elif sugar >= 100: d_score += 3; d_reasons.append("Prediabetic levels")
    if bmi >= 30: d_score += 3; d_reasons.append("Obesity (Major contributor)")
    if age > 50: d_score += 2; d_reasons.append("Age above 50")
    
    d_pct = calculate_percentage(d_score)
    results.append({"name": "Diabetes", "percentage": d_pct, "risk": get_risk_label(d_pct), "reasons": d_reasons, "tips": ["Low sugar diet", "Daily exercise", "Monitor glucose"]})
 
    lv_score, lv_reasons = 0, []
    if bmi >= 30: lv_score += 4; lv_reasons.append("Obese BMI (Strongest contributor)")
    elif bmi >= 25: lv_score += 2; lv_reasons.append("Overweight (Key factor)")
    if sugar >= 126: lv_score += 4; lv_reasons.append("Diabetes (Major Cause)")
    if is_low_activity: lv_score += 2; lv_reasons.append("Sedentary lifestyle")
    if age > 55: lv_score += 2; lv_reasons.append("Age above 55")
    
    lv_pct = calculate_percentage(lv_score)
    lv_risk = get_risk_label(lv_pct)
    
    
    
    results.append({"name": "Liver Disease", "percentage": lv_pct, "risk": lv_risk, "reasons": lv_reasons, "tips": ["Avoid sugary beverages", "Weight management", "Liver screening"], "note": "Your liver risk is mainly influenced by weight and metabolic health."})

    return jsonify(results)
import pypdf 
@app.route('/simplify-report', methods=['POST'])
def simplify_report():
    report_text = ""

   
    if 'file' in request.files and request.files['file'].filename != '':
        pdf_file = request.files['file']
        try:
            reader = pypdf.PdfReader(pdf_file)
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    report_text += text + "\n"
        except Exception as pdf_err:
            print("PDF READ ERROR:", str(pdf_err))
            return jsonify({"error": "Could not read the PDF file."}), 400
    
  
    else:
        report_text = request.form.get('text', '').strip()

   
    if not report_text:
        return jsonify({
            "simple_summary": "No report content found.",
            "term_explanations": [],
            "medication_guide": [],
            "general_suggestions": ["Please paste text or upload a PDF first."]
        })

    
    prompt = f"""
    Act as a helpful and friendly health assistant. Translate this medical report into plain, simple English that anyone can understand.
    
    Structure your response as a JSON object with these EXACT four sections:
    1. "simple_summary": A warm, easy-to-read overview of what is happening in the person's body based on the report in five to six lines or may be more based on the report and each sentence should be in new line giving a point wise explanation and should all the aspects all th report.
    2. "term_explanations": A list of complex medical terms found in the report, what they actually mean, and a simple tip for each.
    3. "medication_guide": A list of any medicines mentioned. Include the name, what it's for, and the specific time/dosage mentioned in the report. If no medicines are found, return an empty list [].
    4. "general_suggestions": 3-4 friendly lifestyle suggestions based on the results.

    REPORT TO ANALYZE:
    {report_text}

    RETURN ONLY THE JSON IN THIS FORMAT:
    {{
      "simple_summary": "...",
      "term_explanations": [{{"term": "...", "meaning": "...", "tip": "..."}}],
      "medication_guide": [{{"name": "...", "purpose": "...", "timing": "..."}}],
      "general_suggestions": ["...", "..."]
    }}
    """

    try:
        
        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=prompt
        )

        raw_text = (response.text or "").strip()
        print("RAW GEMINI OUTPUT:\n", raw_text)

       
        cleaned = raw_text.replace("```json", "").replace("```", "").strip()

        parsed = json.loads(cleaned)
        return jsonify(parsed)

    except Exception as e:
        print("FULL BACKEND ERROR:", repr(e))
        return jsonify({
            "simple_summary": "Something went wrong during analysis.",
            "term_explanations": [],
            "medication_guide": [],
            "general_suggestions": [f"Error details: {repr(e)}"]
        })
@app.route('/simplified-report') 
def simplified_report_view(): 
    return render_template('simplified_report.html')

if __name__ == '__main__':
    app.run()
