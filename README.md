# HIT-SE-proj: Home-Teaching Service System

This project is a web-based platform where students can post and search for home-teaching opportunities.

## Features

- **Information Registration**: Both tutors and students can register their personal information.
- **Posting Information**:
  - Tutors can post their profiles, including subjects, grades, and available times.
  - Students can post their tutoring needs.
- **Matching System**: The platform recommends and matches tutors and students.
- **Information Query**: Users can search for tutors or students based on specific criteria.
- **Evaluation System**: Users can leave feedback and rate each other.

## Getting Started

### Prerequisites

- Python 3.x
- Flask

### Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/Dai-JY/HIT-SE-proj.git
    ```
2. Navigate to the project directory:
    ```sh
    cd HIT-SE-proj
    ```
3. Install the required packages:
    ```sh
    pip install -r requirements.txt
    ```

### Running the Application

1. Set the FLASK_APP environment variable:
    ```sh
    export FLASK_APP=app.py
    ```
2. Run the Flask application:
    ```sh
    flask run
    ```
3. Open your browser and navigate to `http://127.0.0.1:5000/`.

## Folder Structure

- `app.py`: The main application file.
- `models.py`: Database models.
- `static/`: Static files (CSS, JavaScript, images).
- `templates/`: HTML templates.
- `instance/`: Configuration files.
- `__pycache__/`: Compiled Python files.
