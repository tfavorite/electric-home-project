# electric-home-project

A simple calculator to determine potential energy/cost savings from
replacing an HVAC system from a furnace to an air-source heat pump.

Created by Joesan Gabaldon, Tim Favorite, and Nam Pham as part of Terra.do's 
Software Stacks course, based on code provided by Jason Curtis.

# Setup and launching (for development)

Create the virtual environment. You can replace the path and virtualenv name below.
```
python3 -m venv ~/.virtualenvs/eh-env
```

Install the requirements into your local environment. Be sure to use the same name if you changed it from the above.
```
source ~/.virtualenvs/eh-env/bin/activate
```

[Almost] everything else we need to do is in the project folder anyway...
```
cd path/to/electric-home-project/electrichome
```

Installing requirements in the virtualenv
```
pip install -r ../requirements.txt
```

Setup credentials by copying the template file into the actual file django
will look at.
```
cp credentials.py.template credentials.py
```
Afterwards you'll need to edit the new file following the instructions in
the comments there.

Next repeat the above with the `local_settings.py` file. For development the default values are fine so you won't need to edit this one.

```
cp local_settings.py.template local_settings.py
```

Finally you can run the actual server with:
```
$ python manage.py runserver
```

It should now be accessible in your browser at `localhost:8000`.
