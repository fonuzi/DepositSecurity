git clone <your-repository-url>
cd <repository-name>
```

2. Install the required packages:
```bash
pip install streamlit streamlit-sortables pandas plotly
```

3. Create a `.streamlit` folder and add a `config.toml` file with the following content:
```toml
[server]
headless = true
address = "0.0.0.0"
port = 5000

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

## Sharing Options

### 1. Streamlit Cloud (Recommended)
Deploy the app to Streamlit Cloud for 24/7 access:
1. Follow the GitHub deployment instructions below
2. Access your app at `https://share.streamlit.io/your-username/your-repo-name`
3. Share the URL with anyone who needs access

### 2. Local Network Sharing
To share the app on your local network:
1. Run the app using the instructions above
2. Find your computer's local IP address:
   - On Windows: Open CMD and type `ipconfig`
   - On Mac/Linux: Open Terminal and type `ifconfig` or `ip addr`
3. Share the URL: `http://your-local-ip:5000`
   Note: The recipient must be on the same network

## GitHub Deployment Instructions

1. Create a new repository on GitHub

2. Initialize your local repository and push to GitHub:
```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin <your-github-repository-url>
git push -u origin main
```

3. Deploy to Streamlit Cloud:
   - Visit [Streamlit Cloud](https://share.streamlit.io/)
   - Sign in with your GitHub account
   - Select your repository and branch
   - Choose `main.py` as the main file
   - Click "Deploy"

## Project Structure
```
├── main.py              # Main application file
├── styles.py            # Custom CSS styles
├── utils.py             # Utility functions
├── data_models.py       # Data models and default values
└── .streamlit/
    └── config.toml      # Streamlit configuration