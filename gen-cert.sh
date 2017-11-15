SANS=""
for i in $(cat sans.txt)
do
  SANS="$SANS -d $i.pnw.social";
done

certbot certonly --standalone $SANS -d pnw.social
