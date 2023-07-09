# HN Service


Note this project uses a patched version of `django-url-filter`
So running `pip install django-url-filter` would cause breaking errors

To fix after running the install command open `validators.py` of the url-filter module
usually located at 
```<path_to_virtual_env>/lib/<python_version>/site-packages/url_filter/validators.py```
Then replace the line
```py
from django.utils.translation import ungettext_lazy
```

with 
```py
try:
    from django.utils.translation import ungettext_lazy
except ImportError:
    from django.utils.translation import gettext_lazy as ungettext_lazy  # for Django>=3.0
```


# API's

