## Dp Logging

A logger for creating structured log statements that conform to the [dp logging standards](https://github.com/ONSdigital/dp-standards/blob/main/LOGGING_STANDARDS.md).


## Usage

The logger is always instantiated with a namespace

```python
from dpytools.logging.logger import DpLogger

logger = DpLogger("my-app")
```


`DEBUG`, `INFO` and `WARNING` level logs all use the same signature.

- The log message, a positional argument.
- A `raw` keyword for passing in arbitrary strings (to allow capture of information from third parties)
- A `data` keyword that accepts arbitrary key value pairs - this is where you capture variables that a person debugging an issue might need to know.

Examples:

```python
from dpytools.logging.logger import DpLogger

logger = DpLogger("my-app")

# Debug
logger.debug("A debug level message")

# Info
useful_value = "some useful data we want a dev to know"
logger.info("An info level message", data={"variable": useful_value})

logger.warning("A warning level message", raw="arbitrary_string", data={"foo": "bar"})
```

The `ERROR` and `CRITICAL` level logs differ in that they expect a captured python exception to be passed in, so require:

- The log message, a positional argument.
- A _raised and caught_ python exception, a second positional argument.
- A `raw` keyword for passing in arbitrary strings (to allow capture of information from third parties)
- A `data` keyword that accepts arbitrary key value pairs - this is where you capture variables that a person debugging an issue might need to know.

```python
from dpytools.logging.logger import DpLogger

logger = DpLogger("my-app")

# error
try:
    # something went wrong
except Exception as err:
    logger.error("Something went boom", err, data={"some": "variable"})
    raise err

# critical
try:
    # something went wrong
except Exception as err:
    logger.critical("Something went boom", err, data={"some": "variable"})
    raise err
```
