SANS=""
for i in $(cat sans.txt)
do
  SANS="$SANS -d $i.pnw.social";
done

echo certbot certonly --standalone $SANS -d pnw.social
