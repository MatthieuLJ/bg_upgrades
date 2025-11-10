FROM nginx:1.27.3-alpine

COPY uwsgi_params /etc/nginx/
COPY mysite.test-nginx.conf /etc/nginx/conf.d/default.conf

RUN mkdir -p /etc/letsencrypt/

COPY ssl/mysite.test.crt /etc/letsencrypt/
COPY ssl/mysite.test.key /etc/letsencrypt/
COPY options-ssl-nginx.conf /etc/letsencrypt/

CMD ["nginx","-g","daemon off;"]