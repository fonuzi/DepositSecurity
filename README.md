git clone <your-repository-url>
cd <repository-name>
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
streamlit run main.py
```

## Deployment Steps

### 1. GitHub Setup

1. Create a new repository on GitHub
2. Open terminal in your project directory
3. Initialize and push your code:
```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin <your-github-repository-url>
git push -u origin main
```

### 2. Streamlit Cloud Deployment

1. Go to [Streamlit Cloud](https://share.streamlit.io/)
2. Sign in with your GitHub account
3. Click "New app"
4. Select your repository and branch (main)
5. Set main file path to: `main.py`
6. Click "Deploy"

Your app will be available at: `https://share.streamlit.io/your-username/your-repo-name`

## Sharing Your App

1. **Public Access (Streamlit Cloud)**
   - Once deployed, share your Streamlit Cloud URL
   - Anyone can access the app through this URL

2. **Local Network Access**
   - Run locally using `streamlit run main.py`
   - Share your local network URL: `http://your-local-ip:5000`
   - Note: Users must be on the same network

## Project Structure
```
├── main.py              # Main application file
├── styles.py            # Custom CSS styles
├── utils.py             # Utility functions
├── data_models.py       # Data models and default values
└── .streamlit/
    └── config.toml      # Streamlit configuration