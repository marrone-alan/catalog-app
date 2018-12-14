
# Catalog App
This is a **Catalog App**. A project to show what was learned from CRUD.
It's a app where you can read, create, edit and delete categories and items from a catalog

## Programming language
This program was developed in _python_.
_PostgreSQL was also used to show data.

## How to install python
You can download _python_ [here](https://www.python.org/downloads/).
If you are having trouble on how to install, this [link](http://docs.python-guide.org/en/latest/starting/installation/#python-3-installation-guides) might be useful.

### VirtualBox
You need to download and install **VirtualBox** to execute a virtual machine. You don't need to run after install, **vagrant** will do it for you.
You can download it [here](https://www.virtualbox.org/wiki/Downloads).

### Vagrant
Vagrant is a tool for building and managing virtual machine environments.
You can download it [here](https://www.vagrantup.com/downloads.html).

### Setting up
To configure your Virtual Machine go to your terminal and change to this directory. Inside, you will discover another directory called **Vagrant**. Change the directory to the Vagrant directory.
Execute the command  ```vagrant up ```. This will download and instal Linux. It can take a while.
When  ```vagrant up ``` ends, you will have your shell prompt back. You can use the command ```vagrant ssh``` to log in your Linux VM.


## Starting the database and running the project
To start things up, change the directory to **catalog** and run *python database_setup.py* to create a database.
If you want, there is a file with a lot of categories and itens to show how the program works. Run the *python lotofcategories.py* to get access to it.
Finally, run *python project.py* to start it.
You can check the result in your browse using this: http://localhost:5000/
