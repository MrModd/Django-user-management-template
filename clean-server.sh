#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

source $DIR/environment 2>/dev/null
if [ $? != "0" ] ; then
	echo -e "Cannot import environment path" >&2
	exit 1
fi

read -p "Are you sure you want to clean the server installation? This will erase all data! [y|N] " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
	rm -rf $VIRT_ENV/
	rm -rf $DJANGO_PROJ/db.sqlite3
	rm -rf $DJANGO_PROJ/secret_key.txt
	find $DJANGO_PROJ -name "*.pyc" -exec rm -rf {} \;
	
	echo "Remember to clean ROOT_MEDIA directory"
else
	echo "Aborted."
fi
