# Item Catalog Project

> Omar Piñero Rivera

## About

This is a project for the Full Stack Web Developer Nanodegree from Udacity. This project consist to develop a web application that provides a list of items within a varierty of categories. The web integrate a Google user registration and authentication. The authenticated users have the feature to add categories an their own items. The web catalog had a sqlalchemy database that contains a users, categories and items table that store all data.

## To Run

### You will need:
- Python 2.7
- Python Flask package
- Python SQLAlchemy package
- Python httplib2 package
- Python requests package
- Vagrant
- VirtualBox
- Web Browser

### Setup
1. Install Python 2.7
2. Install Python Flask, SQLAlchemy, httplib2 and requests packages
3. Install Vagrant And VirtualBox
4. Clone this repository inside vagrant folder


### To Run

- Launch Vagrant VM by running `vagrant up`, then run the secure shell command `vagrant ssh` and then type `cd /vagrant` to access the shared files.

- From the command line execute the program `python application.py`.  
_The categories.db database should be created with the following tables:_

> - user table
> - catalog table
> - item table

- Then execute the program `python add_data.py` to add a dummy data on the database.

- Execute the program `python logs_analysis_project.py` from the command line.

- Open on the browser the following link `http://0.0.0.0:5000/` or `http://localhost:5000/` to enter on the Item Catalog Web.
