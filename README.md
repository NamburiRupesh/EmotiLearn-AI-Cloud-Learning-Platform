# EmotiLearn – AI-Powered Emotion-Aware Learning Platform

EmotiLearn is a learning management platform that connects **students and teachers** in one system. It supports course management, student enrollment, lectures and learning materials, quizzes, assignments, attendance, academic performance, and an AI-based emotion-aware learning layer.

## Architecture Flow

```mermaid
flowchart TD
    A[EmotiLearn Web Application] --> B[Authentication & Role Management]

    B --> C[Student Portal]
    B --> D[Teacher Portal]

    C --> C1[Browse Courses]
    C1 --> C2[Join Course]
    C2 --> C3[My Courses]
    C3 --> C4[Lectures & Learning Materials]
    C3 --> C5[Quizzes & Assignments]
    C3 --> C6[Attendance & Results]
    C3 --> C7[Emotion-Aware Learning Support]

    D --> D1[Create & Manage Courses]
    D1 --> D2[View Enrolled Students]
    D --> D3[Lectures & Learning Materials]
    D --> D4[Quizzes & Assessments]
    D --> D5[Assignments & Evaluation]
    D --> D6[Attendance Management]
    D --> D7[Student Performance]
    D --> D8[Emotion Analytics]

    C2 --> E[Flask Backend]
    C4 --> E
    C5 --> E
    C6 --> E
    C7 --> E
    D1 --> E
    D2 --> E
    D3 --> E
    D4 --> E
    D5 --> E
    D6 --> E
    D7 --> E
    D8 --> E

    E --> F[(MySQL Database)]

    F --> F1[(users)]
    F --> F2[(courses)]
    F --> F3[(enrollments)]
    F --> F4[(lectures)]
    F --> F5[(quizzes)]
    F --> F6[(questions)]
    F --> F7[(quiz_results)]
    F --> F8[(assignments)]
    F --> F9[(attendance)]
    F --> F10[(emotion_records)]

    C7 --> G[AI Emotion Detection Layer]
    G --> G1[Webcam / Video Input]
    G1 --> G2[YOLO-Based Emotion Detection]
    G2 --> G3[Emotion + Confidence]
    G3 --> F10
    F10 --> D8
    D8 --> D9[Emotion Trends]
    D8 --> D10[Engagement Insights]
    D8 --> D11[Students Needing Support]
```

## High-Level Data Flow

```text
User
  ↓
Role-Based Login
  ↓
Student / Teacher Portal
  ↓
Flask Backend
  ↓
MySQL Database
  ↓
Learning Activity
  ↓
AI Emotion Detection
  ↓
Emotion Records
  ↓
Student Support + Teacher Analytics
```

## Core Modules

### Student Portal

- Student registration and login
- Browse available courses
- Join courses
- View enrolled courses
- Access lectures and learning materials
- Attempt quizzes and assessments
- Submit assignments
- View attendance and academic results
- Emotion-aware learning support

### Teacher Portal

- Teacher registration and login
- Create and manage courses
- View enrolled students
- Add lectures and learning materials
- Add video and notes/PDF links
- Create and conduct quizzes
- Manage assignments and evaluation
- Manage attendance
- Monitor student performance
- Emotion analytics for learning engagement and student support

## Current Learning Flow

```text
Teacher creates course
        ↓
Student browses available courses
        ↓
Student joins course
        ↓
Enrollment is stored in MySQL
        ↓
Course appears in student's dashboard
        ↓
Student appears in teacher's enrolled-students list
        ↓
Teacher manages lectures and learning materials
        ↓
Student accesses course learning materials
```

## Emotion-Aware Learning Flow

```text
Student Learning Session
        ↓
Webcam / Video Input
        ↓
YOLO-Based Emotion Detection
        ↓
Detected Emotion + Confidence
        ↓
Emotion Record
        ↓
Learning Engagement Analysis
        ↓
Teacher Emotion Analytics
        ↓
Personalized Student Support
```

## Technology Stack

- **Frontend:** HTML, CSS, JavaScript
- **Backend:** Python, Flask
- **Database:** MySQL / MySQL Workbench
- **AI:** YOLO-based facial emotion detection
- **Authentication:** Role-based Student and Teacher authentication

## Project Structure

```text
EmotiLearn-AI-Cloud-Learning-Platform/
│
├── backend/
│   ├── app.py
│   ├── auth.py
│   ├── database.py
│   └── requirements.txt
│
├── frontend/
│   ├── static/
│   │   └── css/
│   │       ├── style.css
│   │       └── portal.css
│   │
│   └── templates/
│       ├── index.html
│       ├── login.html
│       ├── signup.html
│       ├── student_dashboard.html
│       ├── teacher_dashboard.html
│       └── teacher_lectures.html
│
└── README.md
```

## Local Setup

### 1. Clone the repository

```bash
git clone https://github.com/NamburiRupesh/EmotiLearn-AI-Cloud-Learning-Platform.git
cd EmotiLearn-AI-Cloud-Learning-Platform
```

### 2. Create and activate the virtual environment

```powershell
python -m venv emotilearn_env
emotilearn_env\Scripts\activate
```

### 3. Install dependencies

```powershell
pip install -r backend\requirements.txt
```

### 3. Install dependencies

```powershell
pip install -r backend\requirements.txt
```

### 4. Configure Database (Cloud MySQL or Local MySQL)

#### Option A: Free Cloud MySQL (Recommended: TiDB Cloud Serverless or Aiven)
1. **Create a Free Database**:
   - Go to [TiDB Cloud](https://tidbcloud.com) or [Aiven](https://aiven.io) and create a free MySQL database cluster.
2. **Execute the Database Schema**:
   - In your cloud provider's web SQL console, copy and run the contents of [`database/emotilearn_db.sql`](database/emotilearn_db.sql) to create all 11 required tables and indexes.
3. **Configure Environment Variables**:
   - Copy `.env.example` to `.env`:
     ```powershell
     copy .env.example .env
     ```
   - Provide your cloud credentials or `DATABASE_URL` in `.env`:
     ```env
     # Option 1: Full URL
     DATABASE_URL=mysql://<user>:<password>@<cloud-host>:<port>/<dbname>?ssl=true

     # OR Option 2: Individual variables
     MYSQL_HOST=<cloud-host>
     MYSQL_PORT=<cloud-port>
     MYSQL_USER=<user>
     MYSQL_PASSWORD=<password>
     MYSQL_DATABASE=<dbname>
     MYSQL_SSL=true
     SECRET_KEY=your-secure-random-secret
     ```
4. **Test the Connection**:
   ```powershell
   python backend\database.py
   ```

#### Option B: Local MySQL
- Create `emotilearn_db` in MySQL / MySQL Workbench.
- Run [`database/emotilearn_db.sql`](database/emotilearn_db.sql).
- Set `MYSQL_PASSWORD` and `MYSQL_SSL=false` in `.env`.

### 5. Run the Application

```powershell
python backend\app.py
```

Open:

```text
http://127.0.0.1:5000
```

### 6. Cloud Deployment

EmotiLearn is cloud-ready and can be deployed anywhere:
- **Render / Railway / Heroku**: Use the included `Procfile` (`web: gunicorn --chdir backend app:app`). Connect your GitHub repo, set your environment variables (`DATABASE_URL`, `SECRET_KEY`), and deploy.
- **Docker / GCP Cloud Run / AWS App Runner**: Build and run the included `Dockerfile`:
  ```bash
  docker build -t emotilearn .
  docker run -p 5000:5000 --env-file .env emotilearn
  ```


## Current Development Status

### Completed

- Student and Teacher role selection
- Role-specific login
- Student dashboard
- Teacher dashboard
- Teacher course creation
- Student course browsing
- Student course enrollment
- Teacher enrolled-student list
- Teacher lecture and learning-material management
- Emotion-aware learning sections in Student and Teacher portals

### Next Modules

- Quiz creation and question management
- Student quiz attempts and results
- Assignment creation and submission
- Attendance management
- Student performance analytics
- Full YOLO emotion detection integration
- Teacher emotion analytics dashboard
- Online class integration
