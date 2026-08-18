# AI Travel Recommendation System

A Flask-based AI Travel Recommendation System that helps users discover suitable travel destinations based on their preferences such as destination type, budget, number of days, location, season, travel style, activities, number of travelers, accommodation, and food preference.

## 1. Project Overview

The AI Travel Recommendation System is a web-based application designed to provide personalized travel recommendations.

The system collects travel preferences from the user and uses a recommendation approach based on text feature extraction and cosine similarity to identify destinations that best match the selected preferences.

### Main Technologies

- **Frontend:** HTML, CSS, JavaScript
- **Backend:** Python, Flask
- **Database:** SQLite
- **Data Processing:** Pandas, NumPy
- **Machine Learning:** Scikit-learn
- **Recommendation Method:** TF-IDF Vectorization + Cosine Similarity
- **Deployment:** Compatible with platforms such as Render using Gunicorn

---

## 2. Objectives

The main objectives of this project are:

1. To provide personalized travel destination recommendations.
2. To make travel planning easier for users.
3. To use machine-learning techniques for matching user preferences with destinations.
4. To provide a simple and responsive web interface.
5. To store application-related data using SQLite.
6. To build a practical end-to-end Python and machine-learning project.

---

## 3. Key Features

### 3.1 Personalized Recommendations

Users can enter or select travel preferences including:

- Destination type
- Budget
- Number of days
- Location
- Season
- Travel style
- Activities
- Number of travelers
- Accommodation preference
- Food preference

The system processes these preferences and returns relevant destinations.

### 3.2 Recommendation Engine

The application uses:

- TF-IDF Vectorization
- Cosine Similarity
- Pandas
- NumPy
- Scikit-learn

The user's preferences are converted into a text representation and compared with destination information.

### 3.3 Destination Information

Recommended destinations can contain information such as:

- Destination name
- Location
- Destination type
- Budget
- Suitable season
- Activities
- Travel style
- Accommodation
- Food options

### 3.4 Wishlist

Users can save preferred destinations to a wishlist, depending on the application's configured functionality.

### 3.5 Database

SQLite is used for lightweight local data storage.

The project contains:

```text
database.db
```

### 3.6 Responsive Interface

The frontend is designed using HTML, CSS, and JavaScript so that the application can be used on different screen sizes.

---

## 4. How the System Works

The general workflow is:

```text
User
  |
  v
Travel Preference Form
  |
  v
Flask Backend
  |
  v
Input Processing
  |
  v
TF-IDF Feature Extraction
  |
  v
Cosine Similarity
  |
  v
Destination Ranking
  |
  v
Recommended Destinations
  |
  v
Web Interface
```

### Step 1: User Input

The user provides travel requirements through the web interface.

Example:

```text
Destination Type: Beach
Budget: Medium
Days: 5
Season: Summer
Travel Style: Relaxation
Activities: Water Sports
Travelers: 2
Accommodation: Hotel
Food: Local Food
```

### Step 2: Data Preparation

The application combines relevant destination attributes into text features.

For example:

```text
Beach Medium 5 Summer Relaxation Water Sports Hotel Local Food
```

### Step 3: TF-IDF Vectorization

The text information is converted into numerical vectors using `TfidfVectorizer`.

TF-IDF helps represent the importance of words/features in the destination data.

### Step 4: Similarity Calculation

The application calculates similarity between the user's preferences and available destinations using cosine similarity.

Conceptually:

```text
Similarity = Cosine(User Preference Vector, Destination Vector)
```

### Step 5: Ranking

Destinations with higher similarity scores are ranked higher.

### Step 6: Recommendation

The best matching destinations are displayed to the user.

---

## 5. Technology Stack

| Technology | Purpose |
|---|---|
| Python | Main programming language |
| Flask | Web application backend |
| HTML | Web page structure |
| CSS | Styling and responsive design |
| JavaScript | Frontend interactions |
| SQLite | Database |
| Pandas | Data processing |
| NumPy | Numerical operations |
| Scikit-learn | Machine-learning and similarity calculations |
| TF-IDF | Text feature extraction |
| Cosine Similarity | Recommendation matching |
| Gunicorn | Production WSGI server |

---

## 6. Project Structure

The project follows a structure similar to:

```text
ai-travel-recommendation-system/
│
├── app.py
├── database.db
├── requirements.txt
├── runtime.txt
├── Dockerfile
├── README.md
├── DOCUMENTATION.md
│
├── dataset/
│   └── destination/travel dataset files
│
├── static/
│   ├── css/
│   ├── js/
│   └── images/
│
├── templates/
│   ├── index.html
│   └── other HTML templates
│
└── venv/
```

> The exact files and subfolders may vary depending on the current version of the project.

---

## 7. Backend

The backend is developed using Flask.

The main application file is:

```text
app.py
```

Flask is responsible for:

- Starting the web server
- Handling HTTP requests
- Processing user input
- Running the recommendation logic
- Communicating with the SQLite database
- Rendering HTML templates
- Returning recommendation results

The application can be started locally with:

```bash
python app.py
```

---

## 8. Database

The project uses SQLite because it is lightweight and does not require a separate database server.

Database file:

```text
database.db
```

SQLite can be used to store application data such as:

- User-related information
- Wishlist data
- Saved destinations
- Application records

The database structure should be checked against the current version of `app.py` before making schema changes.

---

## 9. Dataset

The recommendation system depends on destination/travel data containing attributes that can be compared with user preferences.

Typical fields include:

```text
Destination
Location
Destination Type
Budget
Days
Season
Travel Style
Activities
Travelers
Accommodation
Food Preference
```

Example:

| Destination | Type | Budget | Season | Activities |
|---|---|---|---|---|
| Goa | Beach | Medium | Winter | Water Sports |
| Manali | Mountain | Medium | Summer | Trekking |
| Jaipur | Heritage | Low | Winter | Sightseeing |

The actual dataset included with the project should be treated as the source of truth for available destinations and fields.

---

## 10. Recommendation Algorithm

### 10.1 TF-IDF

TF-IDF stands for **Term Frequency-Inverse Document Frequency**.

It converts text into numerical values based on the importance of terms.

The project uses:

```python
from sklearn.feature_extraction.text import TfidfVectorizer
```

A vectorizer can be created as:

```python
vectorizer = TfidfVectorizer()
```

The destination text is then transformed into vectors.

### 10.2 Cosine Similarity

Cosine similarity measures how similar two vectors are.

The project uses:

```python
from sklearn.metrics.pairwise import cosine_similarity
```

A typical calculation is:

```python
similarity = cosine_similarity(user_vector, destination_vectors)
```

The resulting scores are used to rank destinations.

### 10.3 Why This Method?

TF-IDF + cosine similarity is useful for this project because:

- It is simple to implement.
- It works well with text-based preferences.
- It does not require a large neural-network model.
- It is fast for small and medium-sized datasets.
- It is easy to explain in an academic project.

---

## 11. Installation

### Step 1: Clone the Repository

Clone the project from GitHub:

```bash
git clone https://github.com/aadityapatil-cloud/ai-travel-recommendation-system.git
```

Move into the project directory:

```bash
cd ai-travel-recommendation-system
```

### Step 2: Create a Virtual Environment

Windows:

```powershell
python -m venv venv
```

### Step 3: Activate the Virtual Environment

PowerShell:

```powershell
.env\Scripts\Activate.ps1
```

If PowerShell blocks script execution, run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Then activate again:

```powershell
.env\Scripts\Activate.ps1
```

### Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 5: Run the Application

```bash
python app.py
```

### Step 6: Open the Website

Open:

```text
http://127.0.0.1:5000
```

or:

```text
http://localhost:5000
```

---

## 12. Requirements

The required Python packages are listed in:

```text
requirements.txt
```

Typical dependencies used by this project include:

```text
Flask
pandas
numpy
scikit-learn
gunicorn
```

Install them using:

```bash
pip install -r requirements.txt
```

Do not manually install different versions unless required by the current project configuration.

---

## 13. Running the Project in VS Code

1. Open the project folder in VS Code.
2. Open the terminal.
3. Make sure the terminal is inside the folder containing `app.py`.
4. Activate the virtual environment.
5. Install dependencies.
6. Run the Flask application.

Example:

```powershell
cd path	oi-travel-recommendation-system
.env\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

The terminal should show the Flask server address.

---

## 14. Common Errors and Solutions

### Error: `can't open file 'app.py'`

This usually means the terminal is in the wrong folder.

Check:

```powershell
dir
```

Make sure `app.py` appears in the output.

Then run:

```powershell
python app.py
```

### Error: `ModuleNotFoundError`

Install the required dependencies:

```powershell
pip install -r requirements.txt
```

### Error: PowerShell Execution Policy

Run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Then:

```powershell
.env\Scripts\Activate.ps1
```

### Port Already in Use

If port 5000 is already being used, stop the existing Flask process or configure the application to use another available port.

---

## 15. Deployment

The application can be deployed to a cloud platform that supports Python and Flask applications.

For production deployment, Gunicorn can be used as the WSGI server.

Example:

```bash
gunicorn app:app
```

A deployment configuration should use the project's actual `requirements.txt`, `runtime.txt`, and `Dockerfile` configuration where applicable.

### Important Deployment Checks

Before deploying:

- Verify `app.py` is in the correct root directory.
- Verify `requirements.txt` is present.
- Verify dataset files are included.
- Verify templates are included.
- Verify static files are included.
- Verify SQLite paths work in the deployment environment.
- Test the application locally.
- Check deployment logs after deployment.

---

## 16. Security Considerations

For a production version:

- Do not store secret keys directly in source code.
- Use environment variables for sensitive configuration.
- Do not upload passwords or API keys to GitHub.
- Validate user inputs.
- Use secure session configuration.
- Keep dependencies updated.
- Use HTTPS in production.
- Restrict database access where required.

---

## 17. Testing

The project should be tested for:

### Functional Testing

- Home page loads correctly.
- Travel preference form submits successfully.
- Recommendations are generated.
- Destination details display correctly.
- Wishlist functionality works if enabled.
- Database operations work correctly.

### Input Testing

Test:

- Different budgets
- Different destination types
- Different seasons
- Different travel styles
- Different activity preferences
- Different numbers of travelers
- Missing or invalid inputs

### UI Testing

Check:

- Desktop layout
- Tablet layout
- Mobile layout
- Navigation
- Forms
- Buttons
- Destination cards
- Images and static files

---

## 18. Advantages

The system provides several advantages:

1. Personalized recommendations.
2. Easy-to-use web interface.
3. Fast recommendation generation.
4. Lightweight architecture.
5. Simple machine-learning approach.
6. Easy local development.
7. Can be expanded with additional destinations and features.
8. Demonstrates practical use of Python, Flask, SQLite, and machine learning.

---

## 19. Limitations

The current recommendation approach may have limitations:

- Recommendation quality depends on the dataset.
- TF-IDF mainly works with text-based matching.
- It may not understand complex user preferences like a large language model.
- It does not automatically learn from every user's historical behavior unless such data is added.
- Destination information must be maintained and updated.
- SQLite is better suited to lightweight applications than high-traffic production systems.

---

## 20. Future Enhancements

Possible future improvements include:

### AI/ML Improvements

- Use advanced recommendation models.
- Add collaborative filtering.
- Add content-based and hybrid recommendation methods.
- Use embeddings for semantic similarity.
- Add an LLM-based travel assistant.

### User Features

- User registration and login.
- Personalized user profiles.
- Travel history.
- Save and compare trips.
- Ratings and reviews.
- Improved wishlist functionality.

### Travel Planning

- Automatic day-by-day itinerary generation.
- Hotel recommendations.
- Restaurant recommendations.
- Transport suggestions.
- Estimated trip cost.
- Weather-based recommendations.

### Maps and APIs

Future versions can integrate:

- Google Maps or another map provider
- Weather APIs
- Hotel APIs
- Flight APIs
- Places APIs

API credentials should always be stored securely using environment variables.

---

## 21. Example User Flow

```text
1. User opens the website
        |
        v
2. User enters travel preferences
        |
        v
3. Flask receives the request
        |
        v
4. System processes the preferences
        |
        v
5. TF-IDF converts text into vectors
        |
        v
6. Cosine similarity calculates matching scores
        |
        v
7. Destinations are ranked
        |
        v
8. Best destinations are displayed
        |
        v
9. User can explore or save preferred destinations
```

---

## 22. Academic Project Description

**AI Travel Recommendation System** is an end-to-end web application developed using Python, Flask, SQLite, Pandas, NumPy, and Scikit-learn.

The project demonstrates how machine-learning techniques can be integrated into a web application to provide personalized travel recommendations. User preferences are processed and compared with destination data using TF-IDF vectorization and cosine similarity. The system then ranks destinations according to their similarity with the user's requirements.

This project demonstrates practical knowledge of:

- Python programming
- Flask web development
- Machine learning
- Natural language/text processing
- Data processing
- SQLite database management
- Frontend development
- Recommendation systems
- Application deployment

---

## 23. Project Highlights

- **Application:** AI Travel Recommendation System
- **Backend:** Flask
- **Programming Language:** Python
- **Database:** SQLite
- **ML Technique:** TF-IDF + Cosine Similarity
- **Data Processing:** Pandas + NumPy
- **Frontend:** HTML + CSS + JavaScript
- **Deployment Ready:** Yes
- **Project Type:** Machine Learning + Web Application

---

## Live Demo

Try the deployed application here:

https://ai-travel-recommendation-system.onrender.com/

## 24. GitHub Repository

Repository:

```text
https://github.com/aadityapatil-cloud/ai-travel-recommendation-system
```

For a renamed repository, update this URL in the documentation and other project files after changing the GitHub repository name.

---

## 25. Author

**Aaditya Patil**

B.Sc. Data Science

GitHub:

```text
https://github.com/aadityapatil-cloud
```

LinkedIn:

```text
https://www.linkedin.com/in/aaditya-patil-2a5810376
```

---

## 26. License

This project can be distributed and modified according to the license selected for the GitHub repository.

If no license has been added yet, consider adding an appropriate open-source license before publicly allowing others to reuse the project.

---

## 27. Conclusion

The AI Travel Recommendation System demonstrates how a machine-learning recommendation technique can be combined with a Flask web application to create a practical travel-planning platform.

By collecting user preferences, processing travel data, calculating similarity scores, and ranking destinations, the system provides a simple personalized recommendation experience.

The project can be further improved by adding real-time travel APIs, advanced machine-learning models, user profiles, reviews, maps, itinerary generation, and AI-powered travel assistance.
