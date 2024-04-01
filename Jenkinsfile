pipeline {
    agent any
    environment {
        // 환경 변수 설정
        GPT_API_KEY = credentials('GPT_API_KEY')
    }
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        stage('Prepare Environment') {
            steps {
                sh '''
                python3 -m venv venv
                . venv/bin/activate
                pip install -r requirements.txt
                echo 'GPT_API_KEY=${GPT_API_KEY}' > .env

                // Chrome 설치
                sudo sh -c 'wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -'
                sudo sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
                sudo apt-get update
                sudo apt-get install -y google-chrome-stable

                // ChromeDriver 설치
                CHROME_DRIVER_VERSION=`curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE`
                wget -N http://chromedriver.storage.googleapis.com/$CHROME_DRIVER_VERSION/chromedriver_linux64.zip
                unzip chromedriver_linux64.zip -d /usr/local/bin/
                chmod +x /usr/local/bin/chromedriver
                '''
            }
        }
        stage('Deploy') {
            steps {
                sshagent(credentials: ['ssh-key-pairs']) {
                    sh '''
                    echo 'Syncing files...'
                    rsync -avz --exclude venv --exclude .git --exclude flask.log ${WORKSPACE}/ ec2-user@ec2-44-216-19-144.compute-1.amazonaws.com:/home/ec2-user/flaskapp/
                    ssh ec2-user@ec2-44-216-19-144.compute-1.amazonaws.com "
                        echo 'Creating application directory if not exists...'
                        mkdir -p /home/ec2-user/flaskapp
                        cd /home/ec2-user/flaskapp
                        echo 'Terminating existing Flask application processes on port 5001...'
                        sudo lsof -ti:5001 | xargs --no-run-if-empty sudo kill -9
                        echo 'Setting up Python virtual environment...'
                        python3 -m venv venv
                        . venv/bin/activate
                        echo 'Installing dependencies...'
                        pip install -r requirements.txt
                        echo 'GPT_API_KEY=${GPT_API_KEY}' > .env
                        echo 'Starting Flask application...'
                        nohup python flaskAPI.py > flask.log 2>&1 & echo \$! > flaskapp.pid
                        echo 'Deployment complete.'
                    "
                    '''
                }
            }
        }
    }
}
