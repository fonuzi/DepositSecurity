git clone <your-repository-url>
cd <repository-name>
```

2. Install the required packages:
```bash
pip install streamlit streamlit-sortables pandas plotly
```

3. Create the Streamlit configuration:
   - Create a `.streamlit` folder in your project root
   - Create a `config.toml` file inside with the following content:
```toml
[server]
headless = true
address = "0.0.0.0"
port = 8501

[theme]
primaryColor = "#0066cc"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"
font = "sans serif"
```

4. Run the application:
```bash
streamlit run main.py
```
The application will be available at `http://localhost:8501`

## Detailed GitHub Deployment Guide

### 1. Repository Setup (One-time setup)

a. Create a new repository on GitHub:
   - Go to https://github.com/new
   - Choose a repository name
   - Select "Public" visibility
   - Don't initialize with README (we'll push our existing one)
   - Click "Create repository"

b. Copy the repository URL (ends with .git)

### 2. Prepare Your Code (In your project directory)

a. Initialize Git repository:
```bash
git init
```

b. Add all files to Git:
```bash
git add .
```

c. Create initial commit:
```bash
git commit -m "Initial commit: Banking Sector Loss Distribution Model"
```

d. Set up the main branch:
```bash
git branch -M main
```

e. Connect to GitHub:
```bash
git remote add origin <your-github-repository-url>
```

f. Push your code:
```bash
git push -u origin main
```

### 3. Deploy to Streamlit Cloud

a. Visit Streamlit Cloud:
   - Go to https://share.streamlit.io/
   - Sign in with your GitHub account

b. Deploy your app:
   - Click "New app"
   - Select your repository from the list
   - Select the main branch
   - Set main file path to: main.py
   - Click "Deploy"

c. Wait for deployment to complete:
   - Streamlit will install dependencies
   - You'll get a unique URL for your app
   - The app will be publicly accessible

### 4. Updating Your App

When you make changes:
1. Commit your changes locally:
```bash
git add .
git commit -m "Description of your changes"
```

2. Push to GitHub:
```bash
git push origin main
```

3. Streamlit Cloud will automatically redeploy your app

## Project Structure
```
├── main.py              # Main application file
├── styles.py            # Custom CSS styles
├── utils.py             # Utility functions
├── data_models.py       # Data models and default values
└── .streamlit/
    └── config.toml      # Streamlit configuration