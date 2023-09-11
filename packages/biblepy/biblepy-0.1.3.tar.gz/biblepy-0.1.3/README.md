# biblepy

The King James version of the Bible, and a convenient library to access it.

## Installation

```pip install biblepy```

## API

```python
from bible import KJV

bible = KJV()

# retrieve text for individual verse citations
text = bible.get_text("John 3:16")

# or text for multiple verse citations
text = bible.get_text("Matthew 6:9-13")

# iterate over the bible
for verse in bible:
    print(verse)
```


## Data

The bible is stored in jsonlines format in the bible/data directory.

