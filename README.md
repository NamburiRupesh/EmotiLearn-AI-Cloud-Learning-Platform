# EmotiLearn – AI-Powered Emotion-Aware Cloud Learning Platform

EmotiLearn is a cloud-ready learning management platform that connects **students, teachers, and parents** in one system. The platform manages courses, enrollments, lectures, quizzes, assignments, attendance, academic performance, and an AI-based emotion-aware learning layer.

## Architecture Flow

```mermaid
flowchart TD
    A[EmotiLearn Web Application] --> B[Authentication & Role Management]

    B --> C[Student Portal]
    B --> D[Teacher Portal]
    B --> E[Parent Portal]

    C --> C1[Browse Courses]
    C1 --> C2[Join Course]
    C2 --> C3[My Courses]
    C3 --> C4[Lectures & Materials]
    C3 --> C5[Quizzes & Assignments]
    C3 --> C6[Attendance & Results]

    D --> D1[Create & Manage Courses]
    D1 --> D2[Enrolled Students]
    D --> D3[Lectures & Learning Materials]
    D --> D4[Create & Conduct Quizzes]
    D --> D5[Assignments & Evaluation]
    D --> D6[Attendance Management]
    D --> D7[Student Performance]
    D --> D8[Emotion Analytics]

    E --> E1[Child Profile]
    E --> E2[Attendance]
    E --> E3[Academic Performance]
    E --> E4[Course Progress]
    E --> E5[Learning Engagement]

    C3 --> F[Flask Backend / REST APIs]
    D1 --> F
    D2 --> F
    D3 --> F
    D4 --> F
    D5 --> F
    D6 --> F
    D7 --> F
    E1 --> F
    E2 --> F
    E3 --> F
    E4 --> F
    E5 --> F

    F --> G[(MySQL Database)]

    G --> G1[(users)]
    G --> G2[(courses)]
    G --> G3[(enrollments)]
    G --> G4[(lectures)]
    G --> G5[(quizzes & questions)]
    G --> G6[(quiz_results)]
    G --> G7[(assignments)]
    G --> G8[(attendance)]
    G --> G9[(emotion_records)]

    C4 --> H[AI Emotion Layer]
    H --> H1[Webcam Input]
    H1 --> H2[YOLO-Based Emotion Detection]
    H2 --> H3[Emotion + Confidence]
    H3 --> G9
    G9 --> D8
    D8 --> D9[Emotion Timeline & Engagement Insights]
    D8 --> D10[Students Needing Support]
    D8 --> D11[Smart Learning Recommendations]

    F --> I[Cloud Deployment Layer]
    I --> I1[Cloud Web Application]
    I --> I2[Cloud Database]
    I --> I3[Scalable AI Service]
```

## High-Level Data Flow

```text
User
  ↓
Role-Based Login
  ↓
Student / Teacher / Parent Portal
  ↓
Flask Backend
  ↓
MySQL Database
  ↓
Academic Data & Learning Activity
  ↓
AI Emotion Layer
  ↓
Emotion Records + Learning Insights
  ↓
Personalized Student Support / Teacher Analytics
```

## Core Modules

- Role-based authentication for Student, Teacher, and Parent
- Teacher course creation and management
- Student course browsing and enrollment
- Teacher enrolled-student management
- Lectures and learning materials
- Quizzes and assessments
- Assignments and evaluation
- Attendance management
- Academic performance tracking
- Emotion-aware learning support
- Cloud-ready architecture

## Technology Stack

- **Frontend:** HTML, CSS, JavaScript
- **Backend:** Python, Flask
- **Database:** MySQL
- **AI:** YOLO-based facial emotion detection
- **Deployment:** Cloud-ready web application architecture

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
```
