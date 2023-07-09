# HN Service


Note this project uses a patched version of `django-url-filter`
So running `pip install django-url-filter` on the master branch would cause breaking errors.

Use `drf-patch-bypass` branch to avoid the above issue, it comes with a patched version of the library.

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
    from django.utils.translation import gettext_lazy as ungettext_lazy
```

## Views
This app has two major views

- `<host-url>/` and `<host-url>/stories/` direct to the main page of the application showing a list of recent stories.
- `<host-url>/stories/<pk>/` show infromation on a single story

## API's
All api calls occur on the base url
`<host-url>/api/v1/`

### `/stories/`
This end point supports POST and GET requests for the creation of stories and Viewing of a list of stories

- Post
    ```json
    {
    "text": "string",
    "url": "string",
    "title": "string"
    }
    ```

### `/stories/<pk>/`
Supports GET, PUT, and DELETE requests for the retreival, update and deletion of a single entity by its unique identifier

- PUT
    ```json
    {
    "id": "integer",
    "text": "string",
    "url": "string",
    "title": "string"
    }
    ```

### `/stories/<pk>/comments/`
supports a GET and POST request to List all direct comments for or add a comment to a particualar story
- POST
    ```json
    {
    "text": "string",
    "url": "string",
    }
    ```

### `/comments/`
This end point supports POST and GET requests for the creation of stories and Viewing of a list of stories

- Post
    ```json
    {
    "text": "string",
    "url": "string",
    }
    ```

### `/comments/<pk>/`
Supports GET and PUT requests for the retreival, and update of a single entity by its unique identifier

- PUT
    ```json
    {
    "id": "integer",
    "text": "string",
    "url": "string",
    }
    ```

### `/comments/<pk>/sub_comments/`
supports a GET request to List all direct comments for a particualar comment

