#!/bin/bash

ADDRESS="0.0.0.0"
PORT="8000"

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

source $DIR/environment 2>/dev/null
if [ $? != "0" ] ; then
	echo -e "Cannot import environment path" >&2
	exit 1
fi

source $VIRT_ENV/bin/activate
if [ $? != "0" ] ; then
	echo -e "Cannot access virtual environment" >&2
	exit 1
fi

echo "Starting Django..."
python $DJANGO_PROJ/manage.py runserver $ADDRESS:$PORT



echo -e "\n\nExiting..."

if [ $PID ] ; then
	echo "Killing java gateway..."
	kill $PID
fi
