.. -*- mode: rst -*-

|CircleCI|_

.. |CircleCI| image:: https://circleci.com/gh/hrolfrc/glmnet-classifier.svg?style=shield
.. _CircleCI: https://circleci.com/gh/hrolfrc/glmnet-classifier

GlmnetClassifier
#####################################

A binomial classifier based on glmnet.

Contact
------------------

Rolf Carlson hrolfrc@gmail.com

Install
------------------
Use pip to install glmnet-classifier.

``pip install glmnet-classifier``

Introduction
------------------
The glmnet-classifier project provides GlmnetClassifier for the classification and prediction for two classes, the binomial case.  GlmnetClassifier is based on glmnet. A fortran compiler is required.

GlmnetClassifier is designed for use with scikit-learn_ pipelines and composite estimators.

.. _scikit-learn: https://scikit-learn.org

Example
===========

.. code:: ipython2

    from glmnet_classifier import GlmnetClassifier
    from sklearn.datasets import make_classification
    from sklearn.model_selection import train_test_split

Make a classification problem
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code:: ipython2

    seed = 42
    X, y = make_classification(
        n_samples=30,
        n_features=5,
        n_informative=2,
        n_redundant=2,
        n_classes=2,
        random_state=seed
    )
    X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=seed)

Train the classifier
^^^^^^^^^^^^^^^^^^^^

.. code:: ipython2

    cls = GlmnetClassifier().fit(X_train, y_train)

Get the score on unseen data
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code:: ipython2

    cls.score(X_test, y_test)




.. parsed-literal::

    1.0

Authors
-----------------
The authors of glmnet are Jerome Friedman, Trevor Hastie, Rob Tibshirani and Noah Simon. The Python package, glmnet_py_, is maintained by B. J. Balakumar.

The glmnet-classifier package was written by Rolf Carlson, as an adaptation of glmnet_py_.

.. _glmnet_py: https://pypi.org/project/glmnet-py/


References
------------------
References
Jerome Friedman, Trevor Hastie and Rob Tibshirani. (2008). Regularization Paths for Generalized Linear Models via Coordinate Descent Journal of Statistical Software, Vol. 33(1), 1-22 Feb 2010.

Noah Simon, Jerome Friedman, Trevor Hastie and Rob Tibshirani. (2011). Regularization Paths for Cox’s Proportional Hazards Model via Coordinate Descent Journal of Statistical Software, Vol. 39(5) 1-13.

Robert Tibshirani, Jacob Bien, Jerome Friedman, Trevor Hastie, Noah Simon, Jonathan Taylor, Ryan J. Tibshirani. (2010). Strong Rules for Discarding Predictors in Lasso-type Problems Journal of the Royal Statistical Society: Series B (Statistical Methodology), 74(2), 245-266.

Noah Simon, Jerome Friedman and Trevor Hastie (2013). A Blockwise Descent Algorithm for Group-penalized Multiresponse and Multinomial Regression
