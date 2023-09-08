# Pytick
pytick is a lightweight Python library that provides a simple and intuitive timer class for accurate time interval measurements. It allows you to track elapsed time account for waiting periods, and calculate net time. Ideal for benchmarking, performance analysis, and duration tracking in Python applications.

# Installation
```
pip3 install pytick
```


# Use cases

Normal Case:
```python
import time
from pytick import Tick


def func():
    time.sleep(1)


if __name__ == "__main__":
    Tick.start()
    func()
    Tick.stop()
    print(Tick.get_seconds())


# Output:
1.01297269994393
```

Get the actual time excluding part of the code
```python
import time
from pytick import Tick


def func():
    Tick.wait()
    time.sleep(1)
    Tick.stop_waiting()


if __name__ == "__main__":
    Tick.start()
    func()
    Tick.stop()
    print(Tick.get_active_seconds())

# Output:
1.5600002370774746e-05
```

# Contribution
Feel free to contribute and open a pull request 😄
