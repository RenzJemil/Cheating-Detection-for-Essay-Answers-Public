# Cheating-Detection-for-Essay-Answers

The goal is to develop a Web Application using the Flask framework in the Python programming language; also, HTML, CSS and JavaScript since it’s an application supposed to run on the web.

The Web Application should be able to compare the answers of students to the essay parts of exams and find how similar the answers are to each other; thus, being able to detect if one student copied another’s answer. It is done by employing the Bag of Words Model to turn the answers into vectors then finding the Euclidean distance between two vectors. The lower the distance, the more likely they cheated.

### REQUIREMENTS, TOOLS, MODULES/PACKAGES/LIBRARIES

The following were used to develop the Web Application:

* **Windows Computer** – the Web Application was developed in a laptop with Windows 10 as an Operating System

* **Python 3.10.5** – the exact version of Python that was used while under development. Using older versions might cause problems because some features in this version are not in the older ones.
* **pip 22.1.2** – the exact version of the Python package manager. Using older versions might cause problems when installing the packages/modules/libraries needed
* **XAMPP** – allows easy offline MySQL.
    * An overview to xampp and how to set up: https://hevodata.com/learn/flask-mysql/
    * Download link: https://www.apachefriends.org/download.html
* **Flask** – the framework used to develop the Web Application. To install:
    *       pip install flask
* **Flask-MySQLdb** – the module used to communicate to the database. To install:
    *       pip install flask_mysqldb
* **SciPy** – the module used to calculate the Euclidean distance. But it’s a lot more powerful than just that. To install:
    *       pip install scipy
* **NumPy** – used to create the array to put the vectors in. Also a lot more powerful than just that. To install:
    *       pip install numpy
* **NLTK** – the module/library used to implement the Bag of Words Model. To install:
    *       pip install nltk
    * To use this library, open the terminal and enter the following commands:

            python
            import nltk
            nltk.download()
    * A GUI will open. Click the first row “All packages” then click Download
    * After it finish downloading, you can now use the library.

* **Matplotlib** – the library used to display a graphical representation of the vectors. Although it has an issue that it can’t seem to run well with flask. Since flask is a backend framework and Matplotlib needs a GUI. To install:
    *       pip install matplotlib

### NOTE

* The responsiveness of the UI of the Web Application is not suitable for mobile devices. It was developed in a laptop with screen resolution of 1980x1080. It may be able to adjust well on other laptops or PCs but definitely can’t on mobile devices