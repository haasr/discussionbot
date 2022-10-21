**************
discussionbot
**************

GUI + modularized 1100 discussion grading bot.

.. image::
    ./readme_images/showcase.png
    :width: 700
    :alt: Showcase discussionbot GUI


Setup
#####

Install dependencies
--------------------

For this project, we want to first set up a virtual environment. This way, we can install
dependencies to this virtual environment rather than our global Python environment. This
will allows us to isolate our dependencies.

Open your terminal to the main folder of this cloned repository and install the
requirements:

``pip install -r requirements.txt``

(You will have to use ``pip3`` in Linux)

Config
------

Open ``config.py``, enter your ETSU email address, replace the existing course names
with your course names, and modify the disucssions list to your liking.

Execute
#######

Run ``python launch.py`` from the main project folder. You can run multiple windows
in parallel, but I would not run more than two at a time, depending on your computer's
specs.

Shortcut
########

If you want to create a desktop shortcut on Windows, right click on your Desktop, then...

Choose ``New`` > ``Shortcut`` > ``Browse`` and browse the file path until you are in the
root project folder and select ``discussionbot.vbs``. This is easier than running the
program from a terminal although you don't get to see output from Selenium.