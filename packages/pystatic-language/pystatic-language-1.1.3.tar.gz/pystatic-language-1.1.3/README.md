# pystatic

> This package is a collection of methods and classes for making python more secure, robust, and reliable.
> This could be achieved through the simple usage of decorators, function calls and inheritance of base classes.
> Generally, this package can make python a programming language, closer to other static-typed languages, 
> without losing python's dynamic powerful features and.

first of all
------------

#### specifics:

- writen and owned by: Shahaf Frank-Shapir
- all the rights are saved for: Shahaf Frank-Shapir
- programming languages: python 3.9.12 (100%)

before we start
---------------

#### description:

> This package contains the following systems to be embedded in any python codebase:
> 
> - overloading: Functions and methods (static, class and instance) 
> can have the same name yet different arguments' signature 
> (different arguments - different names or same names and difference 
> in type hints.) through the usage of the overload decorator on top 
> of the base function\method and inherit from the overloading 
> protocol class, when the usage is made in a class.
>
> - privacy: Attributes of classes and instances can now be private 
> in a way that prevents getting access to them in the traditional 
> ways, as well as the more shady ones This can be used whn a class 
> inherits from the private property protocol, or the private attributes 
> being defined as private using the private descriptor.
>
> - cleaning: Cleaning of unnecessary objects, values, imported namespaces 
> from your modules, so an object imported into a module cannot be 
> imported with anything else that is written inside the module. 
> Essentially, enforcing what can and cannot be imported from you modules.
>
> - scope protection: The protection of attributes that are being accessed 
> from outside their class scope, so they couldn't be modified there.
>
> - automatic dynamic type checking and enforcement: decorators 
> and functions to check at run-time is the type, and structure of 
> types of the object equals to any type hint This can be done for 
> functions at every call for all the parameters, sing a decorator, 
> or manually, calling a function on a variable.

#### dependencies:

- opening:
  As for this is a really complex program, which uses a lot of modules, there are required dependencies needed
  in order to run the program. keep in mined the program was writen in python 3.9, so any python version lower
  than 3.8 might not work properly. Moreover, built-in python modules are being used, so keep that in mind.

- install app dependencies by writing the "-r" option to install the requirements
  writen in a file, and write the following line in the project directory:
````
pip install -r requirements.txt
````

run a test
-----------

#### run from windows command line (inside the project directory)
- run with python by writing to the command line in the project directory:
````
python test.py
````