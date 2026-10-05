# 🤖 InterviewBuddy AI

> Practice smarter. Speak naturally. Get instant AI feedback.

InterviewBuddy AI is a local AI-powered mock interview coach that helps users practice job interviews through **text or voice**.

It uses **Gemma 3 locally through Ollama** to generate realistic interview questions, evaluate answers, provide scores and feedback, and ask follow-up questions.

Voice answers are converted to text locally using **Faster-Whisper**.

---

## ✨ Features

- 🎯 AI-generated mock interview questions
- 💼 Choose your job role
- 🎓 Beginner, Intermediate, or Experienced levels
- 📚 Technical, HR, Situational, Practical, or Mixed interviews
- ⌨️ Type your interview answers
- 🎙️ Answer using your voice
- 📝 Local speech-to-text with Faster-Whisper
- 🤖 Gemma 3 AI feedback
- 📊 Answer scoring out of 10
- 💡 Strengths and areas for improvement
- ✍️ Better-answer suggestions
- 🔄 AI-generated follow-up questions
- 🏆 Final interview performance report

---

## 🧠 How It Works

```text
              InterviewBuddy AI
                     │
                     ▼
             Choose Job & Level
                     │
                     ▼
            AI Generates Question
                     │
             ┌───────┴───────┐
             ▼               ▼
        ⌨️ Type Answer    🎙️ Voice Answer
             │               │
             │        Faster-Whisper
             │               │
             └───────┬───────┘
                     ▼
              Gemma 3 via Ollama
                     │
                     ▼
          Score + Feedback + Tips
                     │
                     ▼
             Follow-up Question
                     │
                     ▼
             Final Performance
                  Report

| Technology     | Purpose                                    |
| -------------- | ------------------------------------------ |
| Python         | Application logic                          |
| Streamlit      | Web interface                              |
| Ollama         | Local AI model runtime                     |
| Gemma 3        | Interview question generation and feedback |
| Faster-Whisper | Local speech-to-text                       |
| PyAV           | Audio processing                           |

🔒 Local & Private AI

InterviewBuddy AI is designed to run locally.
The interview interaction is processed on the user's own machine using:

Ollama
Gemma 3
Faster-Whisper

This gives users more control over their interview practice and avoids requiring a cloud AI API for the core interview interaction.


🚀 Installation
1. Clone the repository
    git clone YOUR_GITHUB_REPOSITORY_URL
    cd INTERVIEW_BUDDY

2. Create a virtual environment
    python -m venv venv

3. Activate the virtual environment
    Windows PowerShell:
        venv\Scripts\Activate.ps1

4. Install dependencies
    pip install -r requirements.txt


🤖 Install and Run Gemma 3

Install Ollama on your computer and make sure it is running.
Then download Gemma 3:
             ollama pull gemma3:latest
You can verify the model with:
            ollama list

▶️ Run the Application

Start InterviewBuddy AI with:
                        streamlit run Interview_Buddy_app.py
    The application will open in your browser.


🎙️ Voice Interview Mode

InterviewBuddy AI also supports voice-based interview practice.
The flow is:
    🎙️ Record Answer
           ↓
    Faster-Whisper
           ↓
    📝 Speech → Text
           ↓
    🤖 Gemma 3
           ↓
    📊 Score + Feedback
Voice transcription runs locally using Faster-Whisper.


🎯 Interview Categories

Users can practice:

Technical
HR
Situational
Practical
Mixed

The number of questions can also be selected before starting an interview.

📊 AI Feedback

For every answer, InterviewBuddy AI provides:
1. Score out of 10
2. Strengths
3. Areas to Improve
4. Better Answer
5. Follow-up Question
6. Communication Tip

🌱 Why Open-Source AI?

Interview preparation can involve personal experiences, career goals, and spoken answers.
Using an open-weight model locally gives users more control over where their interview practice happens.
InterviewBuddy AI demonstrates how an open AI model such as Gemma 3 can be integrated into a practical application instead of using AI only as a simple chatbot.

🔮 Future Improvements :
    📄 Resume-based interview questions
    🎯 Job-description-based interviews
    📈 Detailed performance analytics
    🗣️ More advanced voice analysis
    💾 Interview history
    🎤 Pronunciation and speaking-confidence analysis
    🌐 Optional deployment support

👩‍💻 Built With:-----

Python • Streamlit • Ollama • Gemma 3 • Faster-Whisper
Built as a project for the Hacktoberfest Weekend Challenge 2026.

## 📜 License

This project is open source and available under the MIT License.