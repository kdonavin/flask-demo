# Heroku + Flask Setup

Heroku is a cloud Platform-as-a-Service (PaaS) that makes deploying Flask applications simple. It abstracts away infrastructure management so you can focus on application code. This guide covers Heroku deployment and related Flask setup.

## Contents

* [PaaS Alternatives](#paas-alternatives)
* [Why Choose Heroku?](#why-choose-heroku)
* [Prerequisites](#prerequisites)
* [Deploying to Heroku](#deploying-to-heroku)
* [Managing Your Heroku App](#managing-your-heroku-app)
* [Working with Databases on Heroku](#working-with-databases-on-heroku)
* [Continuous Deployment](#continuous-deployment)
* [Common Heroku Issues and Solutions](#common-heroku-issues-and-solutions)
* [Alternative Hosting Options](#alternative-hosting-options)
* [Heroku vs AWS EC2 Comparison](#heroku-vs-aws-ec2-raw-vm-comparison)
* [Resources](#resources)

## PaaS Alternatives

Heroku is one option in the PaaS category. Common alternatives include:

- **Render**
- **Railway**
- **Fly.io**
- **DigitalOcean App Platform**
- **Google App Engine**
- **Azure App Service**

## Why Choose Heroku?

**Advantages:**
- **Extremely beginner-friendly**: Deploy with a few Git commands
- **No server management**: Heroku handles OS updates, security patches, and server configuration
- **Git-based deployment**: Push to deploy - no SSH or manual file transfers
- **Add-ons ecosystem**: Easy integration with databases, monitoring, caching, etc.
- **Free tier available**: Great for learning and small projects
- **Auto-scaling**: Easy to scale up/down as needed
- **Built-in process management**: No need for tmux or systemd

**Considerations:**
- **Cost**: Can be more expensive than EC2 for larger applications
- **Less control**: Limited access to underlying infrastructure
- **Cold starts**: Free tier apps "sleep" after 30 minutes of inactivity (slight delay on first request)
- **Ephemeral filesystem**: Files written to disk are lost on restart (use external storage for uploads)

## Prerequisites

1. **Heroku account**: Sign up at [heroku.com](https://www.heroku.com/)
2. **Heroku CLI installed**: Download from [devcenter.heroku.com/articles/heroku-cli](https://devcenter.heroku.com/articles/heroku-cli)
3. **Git installed**: Heroku deploys via Git
4. **Flask app in a Git repository**: Your code should be version-controlled

## Deploying to Heroku

### 1. Prepare Your Flask Application

Create these required files in your project root:

**`Procfile`** (no file extension):
```
web: gunicorn app:app
```

The `Procfile` tells Heroku how to run your application:
- `web`: Process type for web applications
- `gunicorn`: Production WSGI server (required - don't use Flask's built-in server)
- `app:app`: First `app` is your Python file name (without `.py`), second is your Flask app variable

If your main file isn't `app.py`, adjust accordingly:
```
web: gunicorn main:application    # For main.py with application = Flask(__name__)
web: gunicorn myapp:server        # For myapp.py with server = Flask(__name__)
```

**`requirements.txt`**:

Generate this file automatically:
```bash
pip freeze > requirements.txt
```

Or create manually with minimum requirements:
```
Flask==3.0.0
gunicorn==21.2.0
```

**Important**: Always include `gunicorn` in `requirements.txt` - it's essential for production deployment.

**`.python-version`** (optional but recommended):

Specify your Python major version (note the dot at the start of the filename):
```
3.11
```

**Important:**
- Use **only the major version** (e.g., `3.11`) not the full version (e.g., `3.11.7`)
- This allows automatic security patch updates when you deploy
- The file should have no extension and must start with a dot

Check supported versions at [devcenter.heroku.com/articles/python-support](https://devcenter.heroku.com/articles/python-support)

### 2. Modify Your Application Code

Heroku assigns a random port via the `PORT` environment variable. Your app must listen on this port:

```python
import os
from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return 'Hello, Heroku!'

if __name__ == '__main__':
    # Get port from environment variable or default to 5000
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
```

**Key changes:**
- Use `os.environ.get('PORT', 5000)` to get Heroku's assigned port
- Convert to `int()` since environment variables are strings
- Keep `host='0.0.0.0'` to accept external connections
- Don't use `debug=True` in production

### 3. Initialize Git Repository (if not already done)

```bash
git init
git add .
git commit -m "Initial commit for Heroku deployment"
```

**Important**: Create a `.gitignore` file to exclude unnecessary files:

```
venv/
__pycache__/
*.pyc
.env
.DS_Store
```

### 4. Install and Login to Heroku CLI

```bash
heroku login
```

### 5. Create a Heroku App

```bash
heroku create your-app-name
```

**Notes:**
- App names must be unique across all Heroku
- If you omit the name, Heroku generates a random one (e.g., `serene-caverns-82714`)
- Your app will be accessible at `https://your-app-name.herokuapp.com`

To rename later:
```bash
heroku apps:rename new-name --app old-name
```

### 6. Deploy Your Application

```bash
git push heroku main
```

**Note**: If your default branch is `master` instead of `main`:
```bash
git push heroku master
```

Or push a different branch:
```bash
git push heroku feature-branch:main  # Deploys feature-branch as main on Heroku
```

**What happens during deployment:**
1. Heroku receives your code
2. Detects it's a Python app (from `requirements.txt`)
3. Installs Python version from `.python-version` (or uses default)
4. Creates a virtual environment
5. Installs all packages from `requirements.txt`
6. Runs the command from `Procfile`

### 7. Ensure at Least One Instance is Running

```bash
heroku ps:scale web=1
```

### 8. Open Your App

```bash
heroku open
```

### 9. View Logs (for debugging)

```bash
heroku logs --tail
```

**Useful flags:**
- `--tail`: Stream logs in real-time (like `tail -f`)
- `--source app`: Show only application logs
- `-n 200`: Show last 200 lines

## Managing Your Heroku App

**View app info:**
```bash
heroku info
```

**Restart your app:**
```bash
heroku restart
```

**Run one-off commands on Heroku:**
```bash
heroku run python
heroku run bash
```

**Set environment variables:**
```bash
heroku config:set SECRET_KEY=your-secret-key
heroku config:set DEBUG=False
```

**View environment variables:**
```bash
heroku config
```

**Delete an app:**
```bash
heroku apps:destroy --app your-app-name
```

## Working with Databases on Heroku

Heroku offers PostgreSQL as an add-on:

**Add Heroku Postgres:**
```bash
heroku addons:create heroku-postgresql:essential-0
```

**Note**: The free "hobby-dev" tier was discontinued in November 2022. The "essential-0" plan is the cheapest paid option (~$5/month).

Heroku automatically sets the `DATABASE_URL` environment variable. Access it in your Flask app:

```python
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Get database URL from environment
database_url = os.environ.get('DATABASE_URL')

# Fix for SQLAlchemy 1.4+ (Heroku uses postgres://, SQLAlchemy needs postgresql://)
if database_url and database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url or 'sqlite:///local.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
```

**Access your database:**
```bash
heroku pg:psql  # Opens PostgreSQL command line
```

## Continuous Deployment

For automatic deployment when you push to GitHub:

1. Go to your Heroku Dashboard
2. Click on your app
3. Go to "Deploy" tab
4. Under "Deployment method", choose "GitHub"
5. Connect your GitHub repository
6. Enable "Automatic deploys" from your main branch
7. Optionally enable "Wait for CI to pass before deploy"

Now every push to your GitHub repository automatically deploys to Heroku.

## Common Heroku Issues and Solutions

**Issue: Application Error (H10)**
- **Cause**: App crashed or not binding to correct port
- **Solution**:
  - Ensure `Procfile` is correct
  - Check `app.run()` uses `port=int(os.environ.get('PORT', 5000))`
  - Review logs: `heroku logs --tail`

**Issue: Requirements Installation Fails**
- **Cause**: Conflicting or outdated packages
- **Solution**:
  - Test locally: `pip install -r requirements.txt` in a fresh virtual environment
  - Pin specific versions in `requirements.txt`
  - Check for typos in package names

**Issue: Static Files Not Loading**
- **Cause**: Heroku's ephemeral filesystem doesn't persist files
- **Solution**:
  - Ensure static files are in Git repository
  - For user uploads, use AWS S3 or similar storage service

**Issue: App Sleeps on Free Tier**
- **Cause**: Free dynos sleep after 30 minutes of inactivity
- **Solution**:
  - Upgrade to paid tier (Eco, Basic, or higher)
  - Or accept the delay (fine for learning projects)

**Issue: Module Not Found Error**
- **Cause**: Missing package in `requirements.txt`
- **Solution**:
  - Add the package: `pip freeze | grep package-name >> requirements.txt`
  - Commit and push changes

## Alternative Hosting Options

Beyond Heroku, consider these platforms:

**Platform-as-a-Service (PaaS):**
- **PythonAnywhere**: Python-specific hosting, simple deployment
- **Google Cloud Platform (App Engine)**: Auto-scaling, pay-per-use
- **Microsoft Azure (App Service)**: Enterprise-grade hosting

**Containerization:**
- **Docker + AWS ECS**: Package app with all dependencies
- **Kubernetes**: For complex, microservice-based apps

**Serverless:**
- **AWS Lambda + API Gateway**: Pay only for requests
- **Google Cloud Functions**: Event-driven architecture

**Cost Comparison:**
- **Heroku**: Free tier with limitations (app sleeps after inactivity)
- **PythonAnywhere**: Free tier for small apps

## Heroku vs AWS EC2 (Raw VM) Comparison

| Feature | Heroku | AWS EC2 |
|---------|--------|---------|
| **Category** | PaaS | Raw VM (IaaS) |
| **Ease of Use** | Extremely easy | More complex |
| **Setup Time** | Minutes | 30-60 minutes |
| **Server Management** | Fully managed | Manual |
| **Deployment** | Git push | SSH + manual setup |
| **Scaling** | Single command | Manual configuration |
| **Cost (small app)** | Free tier available | Free tier (12 months) |
| **Cost (production)** | $7-25+/month | $5-50+/month |
| **Control** | Limited | Full control |
| **Learning Curve** | Minimal | Moderate to high |
| **Best For** | Prototypes, small apps | Full control, custom needs |

**Choose Heroku when you:**
- Are learning deployment for the first time
- Need quick prototypes and MVPs
- Have small to medium applications
- Want to focus on code, not infrastructure
- Don’t have DevOps expertise

**Choose AWS EC2 when you:**
- Need full control over server configuration
- Run specialized software or services
- Need cost optimization for high-traffic apps
- Want to learn cloud infrastructure and DevOps
- Have complex networking or security requirements

## Resources

- [Heroku Python Getting Started](https://devcenter.heroku.com/articles/getting-started-with-python)
- [Heroku Dev Center](https://devcenter.heroku.com/)
- [Deploying Flask Apps on Heroku](https://devcenter.heroku.com/articles/python-gunicorn)
- [Flask Deployment Documentation](https://flask.palletsprojects.com/en/stable/deploying/)
- [Gunicorn Documentation](https://gunicorn.org/)
