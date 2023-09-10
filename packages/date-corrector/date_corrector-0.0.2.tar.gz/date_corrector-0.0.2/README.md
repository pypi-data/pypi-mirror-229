# Description
date-corrector is a simple postprocessing library to provide correction suggestions for dates extracted by an OCR. The library utilizes the levenshtein distance concept and uses backtracking with dynamic programming to search for possible date corrections. It can correct both english and arabic dates.

# Installation
```console
pip install date-corrector
```

# Usage
```python
from date_corrector import correctDate, listLanguages

languages = listLanguages()
print(languages)    # ['en', 'ar']

suggestions = correctDate('IZIo212O21', 'en')
print(suggestions)    # [('17/02/2021', 40.0), ('12/02/2021', 40.0)]
```