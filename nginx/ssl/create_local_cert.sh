#!/bin/bash

set -x

openssl genrsa -des3 -passout pass:x -out myCA.key 2048 

openssl req -x509 -new -nodes -key myCA.key -passin pass:x -sha256 -days 1825 -out myCA.pem  \
  -subj "/C=US/ST=CA/L=San Francisco/O=My Desk/OU=IT Department/CN=mysite.test"

openssl x509 -req -days 365 -in server.csr -signkey server.key -out server.crt

openssl genrsa -passout pass:x -out mysite.test.key 2048

openssl req -new -key mysite.test.key -out mysite.test.csr \
  -subj "/C=US/ST=CA/L=San Francisco/O=My Desk/OU=IT Department/CN=mysite.test"

openssl x509 -req -in mysite.test.csr -passin pass:x -CA myCA.pem -CAkey myCA.key \
-CAcreateserial -out mysite.test.crt -days 825 -sha256 -extfile mysite.test.ext