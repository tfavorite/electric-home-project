# electric-home-project

A simple calculator to determine potential energy/cost savings from
replacing an HVAC system from a furnace to an air-source heat pump.

Created with Tim Favorite and Nam Pham as part of Terra.do's 
Software Stacks course.

# Setup and launching

Create the virtual environment and install the requirements

You can replace the path and virtualenv name below
```
$ python3 -m venv ~/.virtualenvs/eh-env
$ source ~/.virtualenvs/eh-env/bin/activate
```

[Almost] everything else we need to do is in the project folder anyway...
```
$ cd path/to/electric-home-project/electrichome
```

Installing requirements in the virtualenv
```
$ pip install -r ../requirements.txt
```

Setup credentials by copying the template file into the actual file django
will look at.
```
$ cp credentials.py.template credentials.py
```
Afterwards you'll need to edit the new file following the instructions in
the comments there.

Finally you can run the actual server with:
```
$ python manage.py runserver
```

It should now be accessible in your browser at `localhost:8000`.