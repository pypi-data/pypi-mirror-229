`splitn` is a CLI application that generates combinations of chars being a result of splitting strings provided *explicite* or randomly generated from regex patterns. It is made mainly for testing NLU applications, e.g. chatbots or tools for extracting structural data from text like [duckling](https://github.com/facebook/duckling).

# Installation
```
pipx install splitn
```

or

```
pip install splitn
```

# Examples
## Basic usage
```bash
splitn 486

# result
486
48 6
4 86
4 8 6
```
