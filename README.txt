Database management system needed: postgres
instructions are at https://www.postgresql.org/download/linux/ubuntu/

Use your favorite Postres management tool(pgAdmin 4 is really good. installed by the previous step already.)

Create a user: root
Root user password: root

Use pgAdmin to create the database.
Create a database called: superfarmer

Then, Download this repository
To create database tables, run the following:


cd superfamer-backend
pip install -r requirements.txt

python manage.py migrate
python manage.py  makemigrations farmerapp
python manage.py migrate

Create an admin user to login to the portal
---
python manage.py createsuperuser

Start the server
---
python manage.py runserver

and the development server should be running at http://127.0.0.1:8000/
Click login button at the top right corner - http://127.0.0.1:8000/api-auth/login/?next=/

Use the admin credentials to login.

After successful login, API root http://127.0.0.1:8000/ lists some of the rest end points of superfarmer app.

Bootstrap the database - manual
---
http://127.0.0.1:8000/usercategory/
buyer
seller
--
http://127.0.0.1:8000/userstatus/
active, unverified, suspended, tobedeleted
--
http://127.0.0.1:8000/productcategory/
grains
seeds
--
http://127.0.0.1:8000/product/
Product name: groundnuts
Product category: Choose one from the dropdown -- It is not clear how to get the name of the category
into the dropdown - what's currently shown is the id.

Add one more product if you like.
--
http://127.0.0.1:8000/measuringunit/
kg
quintal
--
http://127.0.0.1:8000/inventoryitemstatus/
draft
active
suspended
unavailable
--
http://127.0.0.1:8000/registrationstatus/
## PLEASE MIND THE ORDER! Update in the same order. (first - registered, then, pending)
## This restriction ought to be fixed..
registered
pending
-------------
This is all about bootstrapping the database.

========================================================================================================================
Configuring authentication - and configuring frontend http://localhost:4200/login talk to django
--
Goto http://127.0.0.1:8000/admin/oauth2_provider/ (django)
Add Applications
Fill in the following fields:
User: (search for the admin user you created. and select it)
Client type: Confidential
Authorization grant type:  Resource owner password-based
Name: Superfarmer

Click Save
==================
Now, you must update the client_id, and client_secret of superfarmer-frontend app
https://github.com/venkrao/superfarmer-frontend/blob/master/src/app/login/login.component.ts#L109 and
https://github.com/venkrao/superfarmer-frontend/blob/master/src/app/login/login.component.ts#L110


After this, you can start your froenend server using
ng serve --open
and go to http://localhost:4200/login
Use google-login, and use one of your google login
If login succeeds, you will be redirected to http://localhost:4200/register

Registration, though inserts the data into the UserProfile table, the feature as such is incomplete.
User registration must be completed. Fill in some dummy address.

Now,
go to http://127.0.0.1:8000/buyer/ and add the existing user(yourself) as buyer.
AND
http://127.0.0.1:8000/seller/ and add yourself as the seller.

Now, you can go to http://localhost:4200/listings
and fill in some data. Choose any image from your PC, and the listing should be created.
You will see a hyperlink at the bottom, with the link to the listing, such as
http://localhost:4200/listing/5

If you go there, you will see a fullsize image.
If you to back to http://localhost:4200/listings/, you will see available listings.

