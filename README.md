# 🎯 Project BCT - Advanced Task Management System

![Django](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white) 
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)
![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-07405E?style=for-the-badge&logo=sqlite&logoColor=white)

A high-performance, modern productivity application built with Django. **Project BCT** (Brain-Centered Tracking) features a sleek Cyberpunk-inspired UI and a robust task management system integrated with a GitHub-style activity heatmap to visualize your daily progress.

## 🌐 Live Demo

**[👉 Click here to view the live project](https://to-do-01m0.onrender.com)**
- [NOTICE!] wait for few seconds to run the server.!!

---

## ✨ Key Features

### 🔐 Secure Authentication
- Complete user registration and login system.
- Persistent sessions and secure password hashing.
- Profile management with customizable avatars/profile pictures.

### 🎯 Pro Task Management
- Create tasks with three priority levels: **High**, **Medium**, and **Routine**.
- Real-time task completion and undo functionality.
- Smooth AJAX-powered updates for a lag-free experience.
- Soft-deletion of tasks to maintain historical data.

### 📊 Activity Heatmap
- **GitHub-style Contribution Grid**: Visualize your productivity over the last 52 weeks.
- Dynamic color-coded boxes representing task intensity (powered by neon cyan and magenta gradients).
- Interactive tooltips showing completion stats for specific dates.

### 🎨 Premium UI/UX
- **Cyberpunk Aesthetic**: Modern dark mode with plexux node backgrounds and glassmorphic elements.
- **Dynamic Backgrounds**: Custom SVG plexus backgrounds generated programmatically via `generate.py`.
- **Responsive Design**: Fully optimized for desktop and mobile devices.

---

## 🛠️ Technology Stack

- **Backend**: Python 3.12+, Django 6.0.3
- **Database**: SQLite (default)
- **Frontend**: HTML5, Vanilla JavaScript (ES6+), CSS3
- **Icons**: Custom SVG icons and FontAwesome integration
- **Styling**: Modern CSS variables, glassmorphism, and neon glow effects

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10 or higher installed.
- Pip (Python Package Installer).

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/ArpanHait/PROJECT_BCT.git
   cd PROJECT_BCT
   ```

2. **Install Dependencies**
   ```bash
   pip install django
   ```

3. **Database Migration**
   ```bash
   python manage.py migrate
   ```

4. **Background Generation (Optional)**
   If you want to refresh the plexus background patterns:
   ```bash
   python generate.py
   ```

5. **Run the Development Server**
   ```bash
   python manage.py runserver
   ```

6. **Access the App**
   Open your browser and navigate to `http://127.0.0.1:8000`.

---

## 📂 Project Structure

- `DJANGO/`: Core project configuration and settings.
- `accounts/`: User management, profile logic, and task database models.
- `home/`: Landing page and static site logic.
- `templates/`: Global templates (Dashboard, Navbar, Theme components).
- `media/`: Storage for uploaded user profile images.
- `generate.py`: Utility script for generating dynamic SVG backgrounds.

---

## 🌟 Acknowledgements

- Inspired by the productivity workflows of modern developers.
- Designed with a focus on visual excellence and minimal cognitive load.

---

*Made with ❤️ for high-performance individuals.*
