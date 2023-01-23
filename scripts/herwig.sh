docker run -i  --rm  -u `id -u $USER`:`id -g`  -v $PWD:$PWD -w $PWD  patrickkirchgaesser/herwig  Herwig $1 $2 $3 $4
