BusFlow Documentation
=====================

**Seamless Bus Booking & Fleet Management Platform**

BusFlow is a Python Flask web application for online bus ticket booking 
and transportation management. It provides dedicated portals for passengers, 
drivers, and administrators to manage urban bus transportation efficiently.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   modules
   models
   controllers
   views
   services

Features
--------

User Portal
^^^^^^^^^^^
* Search buses by route (source → destination)
* Book seats with visual seat selection
* View booking history
* Cancel tickets

Driver Portal
^^^^^^^^^^^^^
* View assigned buses and routes
* Check bus capacity and status

Admin Portal
^^^^^^^^^^^^
* Full fleet management (add, edit buses)
* Driver assignment to buses
* Create driver accounts
* Manage routes

Architecture
------------

BusFlow follows the **MVC (Model-View-Controller)** architecture:

* **Models**: Data structures representing Users, Buses, and Bookings
* **Views**: Flask blueprints handling HTTP requests and rendering templates
* **Controllers**: Business logic layer connecting views to data services

Tech Stack
----------

============ ==================
Layer        Technology
============ ==================
Framework    Flask 3.0
Database     Supabase (PostgreSQL)
Auth         Flask-Login + Supabase Auth
Templates    Jinja2
Styling      Tailwind CSS
Docs         Sphinx
============ ==================

Quick Start
-----------

1. Install dependencies::

    pip install -r requirements.txt

2. Run the development server::

    python run.py

3. Open http://localhost:5000 in your browser

API Reference
-------------

.. automodule:: app
   :members:
   :undoc-members:

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

