## To Install Main Package

```
pip install censius -U

```

## To Install Dev Package
```
 pip install --trusted-host pypi-dev.eastus.azurecontainer.io:8080 \
 --index-url http://pypi-dev.eastus.azurecontainer.io:8080/simple/ censius -U
```

## API Reference to execute operation

https://documentation.censius.ai/api-reference

## Testing
 - build the package with below command
 ```
    python setup.py sdist
 ```
 your package will be available in dist folder

 - install package in local venv
 ```
    pip install your_package_name
 ```