IFS=$'\n'  
for i in `cat $1`
do
echo $i| grep "dn:"
if [ $? -eq 0 ]
then
R1=$RANDOM
R2=$RANDOM
file=${R1}_${R2}
fi
echo "$i">> RH_$file
done
