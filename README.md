🛡️ Network Guardian - Network Security Management System

📋 Overview

Network Guardian is a comprehensive network security management system designed for educational institutions to protect campus networks from cyber threats. It provides a centralized dashboard where administrators can monitor network devices in real-time, detect threats instantly, and take immediate action.


---

🎯 Key Features

✅ Core Features

Real-time monitoring of network devices (routers, firewalls, servers)

One-click block and unblock functionality for compromised devices

Interactive dashboard with live data visualization

Traffic monitoring to detect abnormal patterns

Instant email notifications for security alerts


🚀 Advanced Features

AI-powered threat detection using machine learning

Detection of DDoS attacks and brute force attempts

Root cause analysis with recommended actions

Graph ON/OFF toggle for customizable dashboard view



---

🛠️ Tech Stack

Layer	Technology

Frontend	HTML5, CSS3, JavaScript, Chart.js
Backend	FastAPI (Python)
Database	SQLite
AI/ML	Scikit-learn (Random Forest)
Email	SMTP (Gmail)
Deployment	Docker



---

📊 System Requirements

Python 3.9 or higher

SQLite3 (built-in)

Modern web browser (Chrome/Firefox/Edge)

Gmail account (for email notifications)



---

🚀 Installation & Setup

1. Clone the Repository

git clone https://github.com/yourusername/network-guardian.git
cd network-guardian

2. Setup Backend

cd backend
python -m venv venv

3. Activate Virtual Environment

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate

4. Install Dependencies

pip install -r requirements.txt

5. Configure Environment Variables

Create a .env file in the backend folder:

EMAIL=your_email@gmail.com
EMAIL_PASSWORD=your_app_password

6. Run the Application

uvicorn main:app --reload


---

📧 Email Configuration

Use Gmail SMTP for sending alerts

Enable 2-Step Verification

Generate an App Password and use it in the .env file



---

📊 How It Works

1. The system continuously monitors network traffic and devices


2. Machine learning model analyzes traffic patterns


3. Suspicious activities like DDoS or brute force attacks are detected


4. Alerts are generated with root cause analysis


5. Email notifications are sent to administrators instantly


6. Admin can take action (block/unblock devices)




---

🌍 Impact

This project supports:

SDG 9: Industry, Innovation, and Infrastructure

SDG 11: Sustainable Cities and Communities


By providing an affordable and scalable security solution for educational institutions.


---

📌 Future Improvements

Integration with cloud-based databases

Advanced deep learning models for better detection

Mobile app for real-time monitoring

Role-based access control



---

📜 License

This project is licensed under the MIT License.


---

🙌 Acknowledgement

Developed as part of an academic project to demonstrate practical implementation of network security and AI-based threat detection.
