verify your version of Python 

```python3 -V```

pip3 install virtualenv
python3 -m virtualenv venv
virtualenv venv
source venv/bin/activate
pip3 install -r requirements.txt 
python3 orders.py 


529  pip3 install --target ./package -r requirements.txt 
  530  ls package/
  531  cd package/
  532  zip -r9 ${OLDPWD}/function.zip .
  533  cd $OLDPWD
  534  ls
  535  mv orders.py lambda_function.py
  536  zip -g function.zip lambda_function.py
  537  aws lambda update-function-code --function-name plantafleur --zip-file fileb://function.zip --region eu-west-3
  538  zip -g function.zip lambda_function.py
  539  aws lambda update-function-code --function-name plantafleur --zip-file fileb://function.zip --region eu-west-3
  540  python3 lambda_function.py 
  541  rm test.pdf 
  542  python3 lambda_function.py 
  543  ls
  544  ls
  545  python3 lambda_function.py 
  546  python3 lambda_function.py 
  547  python3 lambda_function.py 
  548  ls
  549  open test.pdf 
  550  zip -g function.zip lambda_function.py
  551  aws lambda update-function-code --function-name plantafleur --zip-file fileb://function.zip --region eu-west-3
