Benford's Law Challenge
=======================


Install and run
---------------

Build and run Django migrations:

```docker-compose build --no-cache```

Run migrations:

```docker-compose run web python manage.py migrate```

Install npm packages in static folder:

```
docker-compose run -w /app/theme/static web npm install
docker-compose run web python manage.py collectstatic --no-input
```

Finally start Django development server:

```docker-compose up web```

The website should be accessible from [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

Tests
-----

In order to perform automated tests run command:

```docker-compose run --rm testing python manage.py test```

After pulling necessary images you should see end result:

```
Starting challenge2_db_1 ... done
Creating selenium_hub ... done
Creating selenium_firefox ... done
Creating test database for alias 'default'...
System check identified no issues (0 silenced).
........................................
----------------------------------------------------------------------
Ran 40 tests in 22.658s

OK
Destroying test database for alias 'default'...
``` 


Challenge
---------

In 1938, Frank Benford published a paper showing the distribution of the leading digit in many disparate sources of data. In all these sets of data, the number 1 was the leading digit about 30% of the time. Benford’s law has been found to apply to population numbers, death rates, lengths of rivers, mathematical distributions given by some power law, and physical constants like atomic weights and specific heats.

Create a python-based web application (use of tornado or flask is fine) that

1) Can ingest the attached example file (census_2009b) and any other flat file with a viable target column. Note that other columns in user-submitted files may or may not be the same as the census data file and users are known for submitting files that don't always conform to rigid expectations. How you deal with files that don't conform to the expectations of the application is up to you, but should be reasonable and defensible.

2) Validates Benford’s assertion based on the '7_2009' column in the supplied file.

3) Outputs back to the user a graph of the observed distribution of numbers with an overlay of the expected distribution of numbers. The output should also inform the user of whether the observed data matches the expected data distribution.

The delivered package should contain a docker file that allows us to docker run the application and test the functionality directly.

Bonus points for automated tests.

Stretch challenge: persist the uploaded information to a database so a user can come to the application and browse through datasets uploaded by other users. No user authentication/user management is required here… assume anonymous users and public datasets.

