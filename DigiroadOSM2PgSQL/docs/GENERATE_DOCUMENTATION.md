# Autodocumentation

To generate the project documentation you must to have installed the following libraries:

* [sphinx][sphinx]
* [sphinx_rtd_theme][sphinx_rtd_theme]

Then run the following commands to generate the documentation html files:

```
$ cd ./docs
$ sphinx-apidoc -o ./source ./../digiroad
$ make html
```

Open the file `./docs/build/html/intex.html`. You will be able to see all the code documentation in your browser.

[sphinx]:https://anaconda.org/anaconda/sphinx
[sphinx_rtd_theme]:https://anaconda.org/anaconda/sphinx_rtd_theme