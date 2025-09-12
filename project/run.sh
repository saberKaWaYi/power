#!/bin/bash


web(){
    touch /var/log/web.log
    nohup gunicorn -w 16 settings.wsgi:application -b 0.0.0.0:8000 -t 600  --timeout 600 >> /var/log/web.log 2>&1 &
    tail -f /var/log/web.log
}

case "$1" in
    web)
        web
        ;;
    *)
        cat <<EOF
选项:
    web) web
    *) --help
EOF
        ;;
esac

