@echo off
REM Upload MicroStream to Oracle Cloud Free VM

echo ============================================================
echo MicroStream - Upload to Oracle Cloud
echo ============================================================
echo.

REM Configuration
set VM_IP=YOUR_VM_IP_HERE
set VM_USER=ubuntu
set SSH_KEY=path\to\your\ssh_key.pem

echo [1/3] Creating archive...
tar -czf microstream.tar.gz ^
    services/ ^
    docker-compose.free-tier.yml ^
    .env ^
    requirements.txt ^
    deploy_oracle_cloud.sh

echo [2/3] Uploading to VM...
scp -i %SSH_KEY% microstream.tar.gz %VM_USER%@%VM_IP%:~/

echo [3/3] Extracting and deploying...
ssh -i %SSH_KEY% %VM_USER%@%VM_IP% "cd ~ && tar -xzf microstream.tar.gz && mv docker-compose.free-tier.yml docker-compose.yml && chmod +x deploy_oracle_cloud.sh && ./deploy_oracle_cloud.sh"

echo.
echo ============================================================
echo Deployment Complete!
echo ============================================================
echo.
echo Access dashboard at: http://%VM_IP%:8501
echo.
pause
