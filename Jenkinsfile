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
                        
                        wget https://storage.googleapis.com/chrome-for-testing-public/123.0.6312.86/linux64/chrome-linux64.zip
                        sudo unzip chrome-linux64.zip -d /home/ec2-user/

                        wget https://storage.googleapis.com/chrome-for-testing-public/123.0.6312.86/linux64/chromedriver-linux64.zip
                        sudo unzip chromedriver-linux64.zip -d /home/ec2-user/  
                        sudo chmod +x /home/ec2-user/chromedriver
                        
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
