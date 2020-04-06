verify your version of Python

```
python3 -V
```

```
verify your have virtualenv installed
pip3 install virtualenv
```
create a virtual env and activate it
```
virtualenv venv
source venv/bin/activate
```
install requirements
```
pip3 install -r requirements.txt
```
launch local script
```
python3 orders.py
```

if using AWS lambda
create a copy of requirements
```
pip3 install --target ./package -r requirements.txt
```
Create a zip out of it
```
cd package/
zip -r9 ${OLDPWD}/function.zip .
cd $OLDPWD
```
Add the lambda function code to the zip
```
zip -g function.zip lambda_function.py
```
send the package to AWS
```
aws lambda update-function-code --function-name plantafleur --zip-file fileb://function.zip --region eu-west-3
```
