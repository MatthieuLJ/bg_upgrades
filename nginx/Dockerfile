FROM nginx:1.27.3-alpine

COPY uwsgi_params /etc/nginx/
COPY local.nginx.conf /etc/nginx/conf.d/default.conf

CMD ["nginx","-g","daemon off;"]