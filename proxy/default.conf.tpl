server {
    listen ${LISTEN_PORT};

    location /static {
        alias /vol/static;
    }

   location /ws {
        proxy_pass http://${APP_HOST}:${WS_PORT};
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    location / {
        uwsgi_pass              ${APP_HOST}:${APP_PORT};
        include                 /etc/nginx/uwsgi_params;
        client_max_body_size    10M;
    }
}
