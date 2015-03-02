# TAMMY & BENJAMIN Apps

## REQUIREMENTS

* tabvm base box for Vagrant

__or__

* Debian >=7
* Python 3.4
* Postgresql >=9.3
* Nginx with conf such as

```
server {
    listen 80;
    server_name ~^(hooks|backyard|data)\.dev\.tammyandbenjamin\.com;

    access_log /path/to/log/error.log;
    error_log /path/to/log/acces.log;
    location / {
        proxy_pass http://127.0.0.1:4000;
        proxy_redirect off;
        proxy_set_header Host $http_host:80;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

## INSTALL

* Clone the repo
* Setup a virtualenv name py34-tabapp
* Install librairies from requirements.txt
* Create a settings_dev.py file close to settings.py which define the needed config

If you're not using the provided vm you'll need to init the database with a script like

```python

#!/usr/bin/env python
# -*- coding: utf-8 -*-


from tabapp.models import db, Contact

db.create_all()

data = {
    Role: [
        {
            'name': 'Normal',
            'key': 'normal',
            'roles': [],
        },
        {
            'name': 'Admin',
            'key': 'admin',
            'roles': ['normal'],
        },
    ],
    Contact: [
        {
            'firstname': 'Foo',
            'lastname': 'Bar',
            'email': 'foo@bar.com',
            'username': 'user1',
            'password': 'password',
            'roles': ['admin'],
        },
    ],
}

for Entity, records in data.items():
    for record in records:
        entity = Entity()
        for key, value in record.items():
            if key == 'roles':
                roles = Role.query.filter(Role.key.in_(value))
                getattr(entity, key).extend(roles)
            else:
                setattr(entity, key, value)
        db.session.add(entity)
db.session.commit()

```
