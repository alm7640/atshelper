import gradio as gr
import PyPDF2
import docx2txt
import os
from dotenv import load_dotenv
import openai
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import tempfile
import io
from typing import Tuple, Optional

# Load environment variables
load_dotenv()

# Initialize OpenAI client
openai.api_key = os.getenv("OPENAI_API_KEY")

class ATSResumeChecker:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(stop_words='english', max_features=5000)
        self.last_resume_text = ""
        self.last_job_description = ""
        
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text from PDF file using PyPDF2."""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                return text.strip()
        except Exception as e:
            return f"Error extracting PDF: {str(e)}"
    
    def extract_text_from_docx(self, docx_path: str) -> str:
        """Extract text from DOCX file using docx2txt."""
        try:
            return docx2txt.process(docx_path)
        except Exception as e:
            return f"Error extracting DOCX: {str(e)}"
    
    def extract_resume_text(self, file_path: str) -> str:
        """Extract text from resume file based on its extension."""
        if not file_path:
            return "No file provided"
        
        file_extension = os.path.splitext(file_path)[1].lower()
        
        if file_extension == '.pdf':
            return self.extract_text_from_pdf(file_path)
        elif file_extension == '.docx':
            return self.extract_text_from_docx(file_path)
        else:
            return "Unsupported file format. Please upload PDF or DOCX files only."
    
    def calculate_similarity_score(self, resume_text: str, job_description: str) -> float:
        """Calculate cosine similarity between resume and job description."""
        try:
            documents = [resume_text, job_description]
            tfidf_matrix = self.vectorizer.fit_transform(documents)
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
            return similarity[0][0]
        except Exception as e:
            print(f"Error calculating similarity: {e}")
            return 0.0
    
    def get_gpt4_evaluation(self, resume_text: str, job_description: str, similarity_score: float) -> str:
        """Get detailed evaluation from GPT-4."""
        try:
            prompt = f"""
            As an expert ATS analyzer and resume consultant, please evaluate how well this resume matches the job description.
            
            Job Description:
            {job_description}
            
            Resume:
            {resume_text}
            
            Cosine Similarity Score: {similarity_score:.3f}
            
            Please provide:
            1. Overall ATS Score (0-100)
            2. Key strengths of the resume
            3. Missing keywords and skills
            4. Specific improvement recommendations
            5. ATS optimization suggestions
            
            Format your response clearly with headings and bullet points.
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert ATS analyzer and resume consultant with extensive experience in recruitment and resume optimization."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1500,
                temperature=0.3
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"Error getting GPT-4 evaluation: {str(e)}"
    
    def generate_improved_resume(self, resume_text: str, job_description: str) -> str:
        """Generate an improved resume using GPT-4."""
        try:
            prompt = f"""
            As an expert resume writer and ATS optimization specialist, please rewrite and improve this resume to better match the job description.
            
            Job Description:
            {job_description}
            
            Original Resume:
            {resume_text}
            
            Please:
            1. Incorporate relevant keywords from the job description
            2. Restructure content for better ATS compatibility
            3. Enhance bullet points with quantifiable achievements
            4. Optimize formatting and sections
            5. Maintain factual accuracy while improving presentation
            6. Add relevant skills that align with the job requirements
            
            Provide the complete improved resume in a professional format.
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert resume writer and ATS optimization specialist with proven success in helping candidates get interviews."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.4
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"Error generating improved resume: {str(e)}"
    
    def evaluate_resume(self, resume_file, job_description: str) -> Tuple[str, str, str]:
        """Main function to evaluate resume against job description."""
        if not resume_file:
            return "Please upload a resume file.", "", ""
        
        if not job_description.strip():
            return "Please provide a job description.", "", ""
        
        # Extract resume text
        resume_text = self.extract_resume_text(resume_file.name)
        
        if resume_text.startswith("Error") or resume_text.startswith("Unsupported"):
            return resume_text, "", ""
        
        # Store for later use in resume improvement
        self.last_resume_text = resume_text
        self.last_job_description = job_description
        
        # Calculate similarity score
        similarity_score = self.calculate_similarity_score(resume_text, job_description)
        
        # Determine pass/fail
        pass_fail = "✅ PASS" if similarity_score >= 0.3 else "❌ FAIL"
        threshold_info = f"Similarity Score: {similarity_score:.3f} (Threshold: 0.30)"
        
        # Get GPT-4 evaluation
        gpt_evaluation = self.get_gpt4_evaluation(resume_text, job_description, similarity_score)
        
        # Combine results
        evaluation_result = f"""
## ATS Resume Evaluation Results

### {pass_fail}
**{threshold_info}**

### Detailed Analysis
{gpt_evaluation}
        """
        
        return evaluation_result, "Evaluation completed! You can now generate an improved resume.", ""
    
    def improve_resume(self) -> Tuple[str, str]:
        """Generate improved resume based on last evaluation."""
        if not self.last_resume_text or not self.last_job_description:
            return "Please run an evaluation first before generating improvements.", ""
        
        improved_resume = self.generate_improved_resume(self.last_resume_text, self.last_job_description)
        
        # Create downloadable file
        temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt', prefix='improved_resume_')
        temp_file.write(improved_resume)
        temp_file.close()
        
        return improved_resume, temp_file.name

# Initialize the ATS Resume Checker
ats_checker = ATSResumeChecker()

# Custom CSS for better styling
custom_css = """
.gradio-container {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

.main-header {
    text-align: center;
    color: #2c3e50;
    margin-bottom: 2rem;
}

.section-header {
    color: #34495e;
    border-bottom: 2px solid #3498db;
    padding-bottom: 0.5rem;
    margin-top: 2rem;
}

.info-box {
    background-color: #f8f9fa;
    border-left: 4px solid #3498db;
    padding: 1rem;
    margin: 1rem 0;
    border-radius: 4px;
}

.footer {
    text-align: center;
    margin-top: 3rem;
    padding: 2rem;
    border-top: 1px solid #ecf0f1;
}

.coffee-link {
    display: inline-block;
    background-color: #ff813f;
    color: white;
    padding: 10px 20px;
    border-radius: 25px;
    text-decoration: none;
    font-weight: bold;
    transition: background-color 0.3s;
}

.coffee-link:hover {
    background-color: #e06b35;
}
"""

# Create Gradio Interface
with gr.Blocks(title="ATS Resume Checker") as app:
    gr.HTML("""
    <div class="main-header">
        <h1>🔍 ATS Resume Checker</h1>
        <p>Optimize your resume for Applicant Tracking Systems with AI-powered analysis and improvements</p>
    </div>
    """)
    
    with gr.Tab("📋 Resume Evaluation"):
        gr.HTML('<div class="info-box">Upload your resume and job description to get a comprehensive ATS evaluation with improvement suggestions.</div>')
        
        with gr.Row():
            with gr.Column(scale=1):
                resume_file = gr.File(
                    label="Upload Resume (PDF or DOCX)",
                    file_types=[".pdf", ".docx"],
                    type="filepath"
                )
                
                job_description = gr.Textbox(
                    label="Job Description",
                    placeholder="Paste the job description here...",
                    lines=10,
                    max_lines=15
                )
                
                evaluate_btn = gr.Button("🔍 Evaluate Resume", variant="primary", size="lg")
                
            with gr.Column(scale=2):
                evaluation_output = gr.Markdown(
                    label="Evaluation Results",
                    value="Upload a resume and job description, then click 'Evaluate Resume' to see results."
                )
    
    with gr.Tab("✨ Resume Improvement"):
        gr.HTML('<div class="info-box">Generate an improved version of your resume optimized for the job description using AI.</div>')
        
        with gr.Row():
            with gr.Column(scale=1):
                improvement_status = gr.Textbox(
                    label="Status",
                    value="Run an evaluation first to unlock resume improvement.",
                    interactive=False
                )
                
                improve_btn = gr.Button("✨ Generate Improved Resume", variant="secondary", size="lg")
                
            with gr.Column(scale=2):
                improved_resume_output = gr.Markdown(
                    label="Improved Resume",
                    value="Your improved resume will appear here after generation."
                )
                
                download_file = gr.File(
                    label="Download Improved Resume",
                    visible=False
                )
    
    with gr.Tab("ℹ️ How to Use"):
        gr.Markdown("""
        ## How to Use the ATS Resume Checker
        
        ### Step 1: Resume Evaluation
        1. **Upload your resume** in PDF or DOCX format
        2. **Paste the job description** you're applying for
        3. **Click "Evaluate Resume"** to get:
           - ATS compatibility score
           - Pass/fail verdict based on keyword matching
           - Detailed analysis from AI
           - Specific improvement recommendations
        
        ### Step 2: Resume Improvement
        1. After evaluation, go to the "Resume Improvement" tab
        2. **Click "Generate Improved Resume"** to get:
           - AI-optimized resume with better keyword matching
           - Enhanced formatting for ATS systems
           - Quantified achievements and improved bullet points
           - Download link for the improved resume
        
        ### Tips for Best Results
        - Use complete, detailed job descriptions
        - Ensure your resume file is text-readable (avoid image-based PDFs)
        - Review AI suggestions and customize them to match your experience
        - Test multiple job descriptions to optimize for different roles
        
        ### Scoring System
        - **Similarity Score ≥ 0.30**: ✅ PASS - Good keyword alignment
        - **Similarity Score < 0.30**: ❌ FAIL - Needs improvement
        
        *Note: This tool requires an OpenAI API key to function. Make sure to set your OPENAI_API_KEY environment variable.*
        """)
    
    # Event handlers
    def handle_evaluation(resume_file, job_desc):
        result, status, _ = ats_checker.evaluate_resume(resume_file, job_desc)
        return result, status
    
    def handle_improvement():
        improved_text, file_path = ats_checker.improve_resume()
        if file_path:
            return improved_text, gr.File(value=file_path, visible=True)
        else:
            return improved_text, gr.File(visible=False)
    
    evaluate_btn.click(
        fn=handle_evaluation,
        inputs=[resume_file, job_description],
        outputs=[evaluation_output, improvement_status]
    )
    
    improve_btn.click(
        fn=handle_improvement,
        inputs=[],
        outputs=[improved_resume_output, download_file]
    )
    
    # Footer with coffee link
    gr.HTML("""
    <div class="footer">
        <p>Made with ❤️ for job seekers worldwide</p>
        <a href="https://buymeacoffee.com/devopsdepo" class="coffee-link" target="_blank">
            ☕ Buy me a coffee
        </a>
    </div>
    """)

# Launch the application
if __name__ == "__main__":
    app.launch(
        css=custom_css,
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        debug=True
    )