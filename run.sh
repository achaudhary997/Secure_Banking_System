if [ "$#" -ne 1 ]
then
	echo 'Usage: ./run.sh <TRUE/FALSE for sober>'
else
	sudo fuser -k 8000/tcp
	sober=$1 python3 manage.py runserver 0.0.0.0:8000
fi
