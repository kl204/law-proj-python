pipeline {
    agent any
    environment {
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
                    rsync -avz --exclude venv --exclude .git --exclude flask.log ${WORKSPACE}/ ec2-user@your-ec2-instance.amazonaws.com:/home/ec2-user/flaskapp/
                    ssh ec2-user@your-ec2-instance.amazonaws.com "
                        sudo yum update -y
                        sudo yum install -y google-chrome-stable
                        wget https://chromedriver.storage.googleapis.com/your-chromedriver-version/chromedriver_linux64.zip
                        unzip chromedriver_linux64.zip -d /usr/local/bin/
                        sudo chmod +x /usr/local/bin/chromedriver

                        mkdir -p /home/ec2-user/flaskapp
                        cd /home/ec2-user/flaskapp
                        sudo lsof -ti:5001 | xargs --no-run-if-empty sudo kill -9
                        python3 -m venv venv
                        . venv/bin/activate
                        pip install -r requirements.txt
                        echo 'GPT_API_KEY=${GPT_API_KEY}' > .env
                        nohup python flaskAPI.py > flask.log 2>&1 & echo \$! > flaskapp.pid
                    "
                    '''
                }
            }
        }
    }
}
