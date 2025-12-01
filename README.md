# SwiftMail

## AI-Powered Email Automation Challenge Submission

This project is a mini-AI powered email assistant built as a solution for the Constructure AI Applicant Challenge. It is designed to simulate real product work under time constraints, providing a robust, full-stack application capable of secure authentication, natural language processing, and performing real actions within a user's Gmail inbox.

The application features a secure Google OAuth flow, a conversational chatbot interface (dashboard), and leverages AI to summarize emails, suggest replies, and intelligently parse user commands for read, respond, and delete operations.

***

## ⚙️ Technologies Used

| Category | Technology | Key Libraries | Purpose |
| :--- | :--- | :--- | :--- |
| **Backend** | **FastAPI (Python 3.11)** | `uvicorn`, `google-api-python-client`, `motor`, `pymongo` | High-performance API server, handling authentication and business logic. |
| **Frontend** | **React.js (Vite)** | `react-router-dom`, `axios`, **Tailwind CSS** | Clean, responsive chatbot dashboard UI. |
| **Database** | **MongoDB** | `motor`, `pymongo` | Persistent, asynchronous storage for user OAuth tokens and session data. |
| **AI/NLP** | **Google Gemini API** | `google-genai` | Used for natural language intent parsing, email summarization, and reply generation. |
| **Authentication** | **Google OAuth2** | `google-auth-oauthlib` | Secure user login and authorization for Gmail access (Read, Send, Delete). |
| **Deployment** | **Vercel** (Frontend), **Custom Server** (Backend) | `Dockerfile` | Testable, live deployment of the application. |

***

## 🚀 Setup Instructions

### 1. Prerequisites

* Node.js (v18+) and npm
* Python (3.11+)
* A Google Cloud Project with the Gmail API and People API enabled.
* A MongoDB instance (local or Atlas cluster).

### 2. Google OAuth Configuration

1.  **Google Cloud Console:** Navigate to **APIs & Services** > **Credentials**.
2.  **Create OAuth 2.0 Client ID** (Web application type).
3.  **Authorized JavaScript origins:**
    * `http://localhost:5173`
    * `https://swift-mail-chi.vercel.app`
4.  **Authorized redirect URIs:**
    * `http://localhost:8000/api/auth/callback`
    * `https://swiftmail-backend-ty9c.onrender.com/api/auth/callback`
5.  **Test User:** Add `test@gmail.com` as a **Test User** in the OAuth Consent Screen settings.

### 3. Clone the repository
```bash
    git clone https://github.com/lakshendra02/SwiftMail.git
    cd SwiftMail 
```
### 4. Backend (FastAPI) Setup

1.  **Navigate:** `cd backend`
2.  **Environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate
    ```
3.  **Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Configuration:** Create a file named `.env` within the backend folder based on the template below.

    ```ini
    SECRET_KEY="A_VERY_LONG_AND_RANDOM_STRING_FOR_SESSION_MIDDLEWARE"
    
    GOOGLE_CLIENT_ID="<YOUR_GOOGLE_CLIENT_ID_HERE>"
    GOOGLE_CLIENT_SECRET="<YOUR_GOOGLE_CLIENT_SECRET_HERE>"
    
    GOOGLE_REDIRECT_URI="http://localhost:8000/api/auth/callback" 
    
    GEMINI_API_KEY="<YOUR_GEMINI_API_KEY_HERE>" 
    
    MONGO_URI="mongodb://localhost:27017" 
    MONGO_DB_NAME="ai_assistant_db"
    MONGO_COLLECTION_NAME="user_tokens"
    
    FRONTEND_URL="http://localhost:5173"
    ```
    
5.  **Run Locally:**
    ```bash
    uvicorn app.main:app --reload --port 8000
    ```
    The backend will run on `http://localhost:8000`.

### 5. Frontend (React/Vite) Setup

1.  **Navigate:** `cd frontend`
2.  **Dependencies:**
    ```bash
    npm install
    ```
3.  **Run Locally:**
    ```bash
    npm run dev
    ```
    The frontend will run on `http://localhost:5173`.

***

