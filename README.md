# FileFetch

## What is it?

**filefetch** is a Python package that allows users to
fetch data from publicly available websites using a variety of methods.
Data retrieval has been tested using APIs, file links, DataWrapper, and
for different types of files (e.g., csv, xlsx, pdf).

## Main Features

 - Provides ability to retrieve or download data into a pandas DataFrame using
 one of a variety of methods, therefore eliminating the need to write lots of code.
 - Additional functionality is easy to incorporate by adding a new fetch method
 to the FileFetch Class or by providing a new Mixin Class to the FileFetch Base Class.
 - Input on datasets of interest are easily stored and provided to FileFetch via
 yaml files. Storage in a yaml also makes it easy to update or add dataset information
 over time without having to make changes to the underlying code.

## Documentation

Documentation and help are provided [here](./docs/index.html).

Sample input yaml files are also included [here][./input]
