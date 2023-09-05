# BetterConfig

BetterConfig is config library used to create  config structures for projects

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install betterconfig.

```bash
pip install better-configuration
```

## Usage

```python

from betterconfiguration import config

test_config = config.BaseConfig("test", "this is a test value")

print(test_config.test)
```
### Result
![](images/result.png)



## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License

[MIT](https://choosealicense.com/licenses/mit/)