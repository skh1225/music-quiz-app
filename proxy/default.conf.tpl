upstream channels {
  server app:8000;
}

server {
    listen ${LISTEN_PORT};

    access_log /var/log/nginx/a.log;
    error_log /var/log/nginx/e.log;

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
        root /var/www/html/;
        index index.html index.htm;
        error_page 404 =200 /index.html;
    }
}