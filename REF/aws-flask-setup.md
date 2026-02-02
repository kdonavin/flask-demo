# AWS EC2 + Flask Setup

While Flask's built-in development server (`app.run()`) is excellent for local testing, it's not designed for production use. This guide walks through deploying Flask applications to AWS EC2.

## Contents

* [Why Not Use Flask's Development Server in Production?](#why-not-use-flasks-development-server-in-production)
* [Deployment Overview](#deployment-overview)
* [Part 1: Preparing Your Flask App for Deployment](#part-1-preparing-your-flask-app-for-deployment)
* [Part 2: Deploying to AWS EC2](#part-2-deploying-to-aws-ec2)
* [Part 3: Production Best Practices](#part-3-production-best-practices)
* [Part 4: Troubleshooting Common Issues](#part-4-troubleshooting-common-issues)
* [Resources](#resources)

## Why Not Use Flask's Development Server in Production?

* Not designed for security or performance
* Single-threaded by default (can't handle concurrent requests efficiently)
* Lacks robustness and stability features
* No load balancing or process management

## Deployment Overview

Deploying a Flask app involves two main phases:
1. Preparing your Flask app with production-ready configurations
2. Deploying to a cloud server (AWS EC2)

## Part 1: Preparing Your Flask App for Deployment

### Required File Structure for Hosting

Flask requires a specific directory structure for web hosting. The only **required** elements are:

```
your_app/
├── app.py                 # Your Flask application (REQUIRED)
└── templates/             # HTML template files (REQUIRED if using render_template)
    └── index.html
```

### Optional but Common Structure

```
your_app/
├── app.py                 # Your Flask application
├── requirements.txt       # Python dependencies (highly recommended)
├── templates/             # HTML template files
│   └── index.html
└── static/               # Static assets (only needed if you have CSS/JS/images)
    ├── css/              # Stylesheets
    ├── js/               # JavaScript files
    ├── images/           # Image files
    └── fonts/            # Font files (if needed)
```

### What's Actually Required for Hosting

- ✅ **`app.py`** (or your main Flask file) - absolutely required
- ✅ **`templates/`** directory - required only if you use `render_template()`
- ❌ **`static/`** directory - only needed if you have CSS, JavaScript, images, or other static files
- ❌ **Bootstrap or any specific framework** - not required; use any CSS framework or none at all

**Note:** The `static/` and `templates/` folder names are Flask conventions. These can be customized when creating your Flask app:

```python
app = Flask(__name__,
            template_folder='my_templates',
            static_folder='my_static')
```

### Before Deployment - Test Locally

Visit `http://localhost:5000` to verify your app works correctly before deployment.

## Part 2: Deploying to AWS EC2

### Prerequisites

- AWS account (free tier eligible)
- Flask app repository on GitHub
- Basic command line knowledge

### Step-by-Step Deployment Process

#### 1. Push Your App to GitHub

Ensure your `web_app` folder is committed and pushed to GitHub. You'll clone this repository onto your EC2 instance.

#### 2. Launch an EC2 Instance

1. Log into the [AWS Console](https://aws.amazon.com/console/)
2. Navigate to EC2 and click "Launch Instance"
3. Select a Community AMI (Amazon Machine Image) - look for a Python/Data Science configured image
   - **Pricing Note**: Community AMIs themselves are typically free - you only pay for the EC2 instance costs (which are covered by the free tier for t2.micro). The AMI selection page may not show pricing because the AMI has no additional cost beyond the standard EC2 charges.
   - **Subscription Delay**: First-time Community AMI subscriptions may take longer than expected (up to an hour in rare cases, though usually under 30 seconds). This is normal - AWS is setting up the subscription to that AMI.
   - **Alternative**: If you prefer, you can use an official AWS AMI (like Ubuntu Server) which won't require subscription, though you'll need to install Python and dependencies yourself.
4. Choose the **t2.micro** instance type (free tier eligible)
5. Configure instance details (defaults are usually fine)
6. Add storage (8GB is sufficient for most Flask apps)
7. Add tags: Name your instance (e.g., `my-flask-app`)

#### 3. Configure Security Group

Security groups control inbound/outbound traffic to your instance:

1. Create a new security group or modify existing (e.g., "Flask App SG")
2. Add inbound rules:

   **For SSH (port 22):**
   - **Type**: SSH
   - **Port**: 22
   - **Source**: Options based on your needs:
     - **Most Secure**: Your current IP only (e.g., `203.0.113.25/32`)
     - **Practical**: Multiple IPs or ranges you commonly use (home, office, VPN)
     - **Flexible**: `0.0.0.0/0` if you frequently change networks/locations

   **For Flask App:**
   - **Type**: Custom TCP Rule
   - **Port**: `5000` (Flask's default port, or choose another like `8080`, `8105`, etc.)
   - **Source**:
     - `0.0.0.0/0` (allows access from anywhere) - **for public web apps**
     - Specific IP/CIDR (e.g., `203.0.113.0/24`) - **for internal/restricted apps**

**Security Considerations:**

- **SSH Access Tradeoff**: Restricting SSH to your IP is most secure, but impractical if you change networks (coffee shops, home, work, travel). Solutions:
  - Add multiple IPs/ranges to the security group as needed
  - Use AWS Systems Manager Session Manager (no SSH port needed)
  - Use a bastion host or VPN for centralized access control
  - If using `0.0.0.0/0` for SSH, use strong authentication (key-based only, no passwords, consider fail2ban)

- **Public Web Apps**: Must use `0.0.0.0/0` on your app port (5000 or whichever you chose) so anyone can access your website

- **AWS Warning**: "Rules with source of 0.0.0.0/0 allow all IP addresses to access your instance. We recommend setting security group rules to allow access from known IP addresses only."

**Updating Security Groups**: You can modify security group rules at any time through the AWS Console without restarting your instance. If you get locked out due to IP restrictions, use the AWS Console from any browser to update the rules.

#### 4. Create/Select Key Pair

1. Create a new key pair or select an existing one
2. **Download the `.pem` file** - you'll need this to SSH into your instance
3. **Important**: Store this file securely; you can't download it again

#### 5. Launch and Connect

1. Click "Launch Instance" and wait for it to initialize
2. Move your key pair file to your `~/.ssh` directory:

```bash
mv ~/Downloads/my-key-pair.pem ~/.ssh/
chmod 400 ~/.ssh/my-key-pair.pem  # Restrict permissions
```

3. Get your instance's **IPv4 Public Address**:
   - In AWS Console, go to EC2 > Instances
   - Click on your instance
   - Look in the bottom panel under "Instance summary"
   - Find "Public IPv4 address" (e.g., `54.123.45.67`)

4. Create an SSH config file (`~/.ssh/config`) for easy access:

```
Host my-flask-app                           # Nickname (choose any name you want)
    HostName 54.123.45.67                   # Your EC2 Public IPv4 address from step 3
    User ubuntu                              # Default username for your AMI (see below)
    IdentityFile ~/.ssh/my-key-pair.pem     # Path to your downloaded .pem file
```

**Finding the correct User for your AMI:**
- When you selected your AMI, the username is typically shown in the AMI description or usage instructions
- In AWS Console: Go to EC2 > Instances > Select your instance > Click "Connect" button at top
- AWS will show the correct SSH command with the proper username, e.g., `ssh -i "keypair.pem" ubuntu@54.123.45.67`
- The username is the part between the `@` symbol and before the IP address
- Most Python/Data Science Community AMIs use `ubuntu`

5. SSH into your instance:

```bash
ssh my-flask-app
```

#### 6. Set Up Your App on EC2

1. **Update the system**:
```bash
sudo apt-get update
sudo apt-get upgrade
```

2. **Clone your repository**:
```bash
git clone https://github.com/your-username/your-web-app.git
cd your-web-app
```

**Note:** Use HTTPS URL (starts with `https://`), not SSH URL (starts with `git@github.com:`). If you copied the SSH URL and get a "Permission denied (publickey)" error, replace it with the HTTPS version:
- ❌ SSH (won't work without setup): `git@github.com:username/repo.git`
- ✅ HTTPS (works immediately): `https://github.com/username/repo.git`

For private repositories, you may be prompted for your GitHub username and password (or personal access token).

3. **Create and activate a virtual environment**:
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate
```

Your command prompt will change to show `(venv)` at the beginning, indicating the virtual environment is active.

4. **Install dependencies** (if you have a `requirements.txt`):
```bash
pip install -r requirements.txt
```

#### 7. Configure Flask for Production

Modify your `app.py` to use the correct port and enable threading:

```python
if __name__ == '__main__':
    app.run(host='0.0.0.0',  # Listen on all network interfaces
            port=5000,        # Default Flask port; match your security group port
            threaded=True)    # Enable threading for concurrent requests
```

**Important Configuration Notes:**
- `host='0.0.0.0'`: Allows external connections (not just localhost)
- `port=5000`: Flask's default port. Must match the port opened in your security group. You can use any port (e.g., 8080, 8105), just ensure consistency.
- `threaded=True`: Enables handling multiple requests simultaneously
- **Never use `debug=True` in production** (security risk)

#### 8. Run Your App with tmux

`tmux` allows your app to continue running even after you disconnect from SSH:

1. **Start a tmux session**:
```bash
tmux new -s flask-app
```

2. **Run your Flask app**:
```bash
python app.py
```

3. **Detach from tmux** (keeps app running):
   - Press `Ctrl+b`, then press `d`

4. **Your app is now live!** Access it at:
```
http://<EC2-IPv4-Address>:5000
```

(Replace `5000` with whatever port you configured in your security group and `app.py`)

**Useful tmux Commands:**
- Reattach to session: `tmux attach -t flask-app`
- List sessions: `tmux ls`
- Kill session: `tmux kill-session -t flask-app`

#### 9. Verify Deployment

Open a web browser and navigate to `http://<your-ec2-ip-address>:5000`. You should see your Flask app running!

## Part 3: Production Best Practices

While the above deployment works for learning and small projects, production applications should consider:

1. **Use a Production WSGI Server**
   - **Gunicorn**: `gunicorn -w 4 -b 0.0.0.0:5000 app:app`
   - **uWSGI**: More configuration required but very robust

2. **Process Management**
   - **systemd**: Create a service that auto-starts on boot
   - **Supervisor**: Process control system for managing long-running programs

3. **Reverse Proxy**
   - **Nginx**: Handles static files, SSL, load balancing
   - **Apache**: Alternative to Nginx with similar capabilities

4. **Security Considerations**
   - Never run Flask with `debug=True` in production
   - Use environment variables for secrets (API keys, database passwords)
   - Enable HTTPS with SSL/TLS certificates (Let's Encrypt is free)
   - Keep your system and packages updated
   - Implement proper authentication and authorization
   - Use security groups to restrict access

5. **Monitoring and Logging**
   - Set up application logging (Python's `logging` module)
   - Monitor server resources (CPU, memory, disk)
   - Use AWS CloudWatch for instance monitoring
   - Consider application performance monitoring (APM) tools

6. **Database Considerations**
   - Use AWS RDS for managed database hosting
   - Never commit database credentials to Git
   - Use connection pooling for better performance
   - Regular backups

7. **Continuous Deployment**
   - Set up automated deployment with GitHub Actions or similar
   - Use blue-green deployment strategies
   - Implement proper testing before deployment

## Part 4: Troubleshooting Common Issues

**App Not Accessible:**
- Verify security group has correct port open
- Check that `host='0.0.0.0'` in `app.run()`
- Confirm app is running: `ps aux | grep python`
- Check firewall settings on EC2 instance

**Port Already in Use:**
```bash
# Find process using the port
sudo lsof -i :5000
# Kill the process
sudo kill -9 <PID>
```

**Permission Denied Errors:**
```bash
# Ensure correct key permissions
chmod 400 ~/.ssh/my-key-pair.pem
```

**App Crashes:**
- Check tmux session logs: `tmux attach -t flask-app`
- Review application logs
- Verify all dependencies are installed

## Resources

- [Flask Deployment Documentation](https://flask.palletsprojects.com/en/stable/deploying/)
- [AWS EC2 Getting Started](https://aws.amazon.com/ec2/getting-started/)
- [Gunicorn Documentation](https://gunicorn.org/)
- [Nginx Configuration for Flask](https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-gunicorn-and-nginx-on-ubuntu-20-04)
