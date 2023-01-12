DATE=`date +"%Y.%m.%d-%T"`
LOGFILE="log_$DATE"
echo $LOGFILE

gunicorn --workers=5 simpleserver:app --threads 2 -b 137.184.187.8:8081 --certfile=cert.pem --keyfile=key.pem --log-file $LOGFILE
