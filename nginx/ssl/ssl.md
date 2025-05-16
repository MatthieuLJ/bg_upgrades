To generate a self signed certificate [doc](https://deliciousbrains.com/ssl-certificate-authority-for-local-https-development/)

##### Generating the Private Key

``` term
openssl genrsa -des3 -out myCA.key 2048
```

##### Generating a root certificate 
``` term
openssl req -x509 -new -nodes -key myCA.key -sha256 -days 1825 -out myCA.pem
```

##### Install the certificate
###### on linux:
```term
sudo cp myCA.pem /usr/local/share/ca-certificates/myCA.crt
```
 on Windows with the mmc command and messing up with certificates

> 1. Open the “Microsoft Management Console” by using the **Windows + R** keyboard combination, typing `mmc` and clicking **Open**
> 2. Go to **File > Add/Remove Snap-in**
> 3. Click **Certificates** and **Add**
> 4. Select **Computer Account** and click **Next**
> 5. Select **Local Computer** then click **Finish**
> 6. Click **OK** to go back to the MMC window
> 7. Double-click **Certificates (local computer)** to expand the view
> 8. Select **Trusted Root Certification Authorities**, right-click on **Certificates** in the middle column under “Object Type” and select **All Tasks** then **Import**
> 9. Click **Next** then **Browse**. Change the certificate extension dropdown next to the filename field to **All Files (*.*)** and locate the `myCA.pem` file, click **Open**, then **Next**
> 10. Select **Place all certificates in the following store**. “Trusted Root Certification Authorities store” is the default. Click **Next** then click **Finish** to complete the wizard.

##### Creating CA-Signed Certificates for Your Dev Sites

`openssl genrsa -out hellfish.test.key 2048`

(`hellfish.test` can be changed to anything else that looks like a site name)

`openssl req -new -key hellfish.test.key -out hellfish.test.csr`

Create a file `hellfish.test.ext` with the content:
``` term
authorityKeyIdentifier=keyid,issuer
basicConstraints=CA:FALSE
keyUsage = digitalSignature, nonRepudiation, keyEncipherment, dataEncipherment
subjectAltName = @alt_names

[alt_names]
DNS.1 = hellfish.test
```


```
openssl x509 -req -in hellfish.test.csr -CA myCA.pem -CAkey myCA.key \
-CAcreateserial -out hellfish.test.crt -days 825 -sha256 -extfile hellfish.test.ext
```

##### Hardcode DNS entry

https://learn.microsoft.com/en-us/answers/questions/1689135/manually-adding-dns-resolution

File to edit is `C: \ Windows \ System32 \ drivers \ etc \ hosts`
Then run `ipconfig /flushdns` in a terminal

Check also https://www.f5.com/company/blog/nginx/using-free-ssltls-certificates-from-lets-encrypt-with-nginx for how to setup nginx and stuff

