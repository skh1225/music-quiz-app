upstream channels {
  server app:8000;
}

server {
    listen ${LISTEN_PORT};

    location /static {
        alias /vol/static;
    }

    location /ws/ {
        proxy_pass http://channels;
        proxy_http_version 1.1;
        include /etc/nginx/proxy_params;
    }

    location ~ ^/(api|admin) {
        uwsgi_pass              ${APP_HOST}:${APP_PORT};
        include                 /etc/nginx/uwsgi_params;
        client_max_body_size    10M;
    }

    location / {
        alias /var/www/html/;
        index index.html index.htm;
    }
}