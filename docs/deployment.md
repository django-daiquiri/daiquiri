Installation
============

Install prerequisites
---------------------

Install the prerequisites for your Linux distribution as described [here](prerequisites).

For a deployment Java is *not* needed.


Create user
-----------

Either run Daiquiri as your regular Desktop user or create a dedicated user:

```
useradd -m -d /srv/daiquiri daiquiri -s /bin/bash
su - daiquiri
```

Don't run Daiquiri as root!
