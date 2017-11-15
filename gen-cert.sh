

SANS=""
for i in $(cat sans.txt)
do
  SANS="$SANS -d $i.$1";
done

certbot certonly --standalone $SANS -d $1
DOMAIN='$1' sudo -E bash -c 'cat /etc/letsencrypt/live/$DOMAIN/fullchain.pem /etc/letsencrypt/live/$DOMAIN/privkey.pem > /etc/haproxy/certs/$DOMAIN.pem'
