# -*- coding: utf-8 -*-
"""Give me some Credit.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1jhe0aIT5u87wSYhvxIHROnwDYqBEFUxl

# **Give me some Credit**
### The goal of this assessment is to build a model that borrowers can use to help make the best financial decisions.

## **Import Libraries**
"""

import pandas as pd
import numpy as np
from collections import Counter
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier, AdaBoostClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score

"""## **Load Dataset**

*   Ultimately, we want to predict if the borrower will experience 90 days past due delinquency or worse (SeriousDlqin2yrs)


"""

data = pd.read_csv('cs-training.csv')
data.head()

"""## **Analyze and validate data (i.e. missing data, outlier)**"""

data.info()

# Omit first column
data = data.iloc[: , 1:]

# Number of NaN for each column
data.isna().sum()

"""###**Perform Outlier detection for every column** 

*   Outliers were detected based on different techniques including Interquartile range (IQR) and thresholding.
*   Therefore, rather than simply dropping the outliers, they were either replaced with values based on IQR or min and max threshold was used to stabilize the data.

"""

def IQR(data,column):
  q1 = data[column].quantile(0.25)
  q3 = data[column].quantile(0.75)
  iqr = q3 - q1
  return q1, q3, iqr


for column in data:
  q1, q3, iqr = IQR(data, column)
  outlier = (data[column] < q1 - iqr * 1.5 )| (data[column] > q3 + iqr * 1.5)
  print('Found', len(data[outlier]), 'outlier in', column)

  # data.drop(data[outlier].index, inplace = True)
  # data.plot(kind = "scatter", x = column, y = "SeriousDlqin2yrs")

# Correlation between the variables
data.corr()

# Rather than removing the outliers, threshold of q3 + 1.5iqr was used as maximum value.
q1, q3, iqr = IQR(data, 'RevolvingUtilizationOfUnsecuredLines')

data['RevolvingUtilizationOfUnsecuredLines'] = np.where(data['RevolvingUtilizationOfUnsecuredLines'] > (q3 + iqr * 1.5), (q3 + iqr * 1.5), data['RevolvingUtilizationOfUnsecuredLines'])


data.RevolvingUtilizationOfUnsecuredLines.describe()

# Upon seeing Age column, min was 0, which doesn't make sense. Hence minimum age was set.
for i in range(19,35):
    print (i, len(data[data.age < i]))

data['age'] = np.where(data['age'] < 22, 22, data['age'])
data.age.describe()

# NumberOfTime30-59DaysPastDueNotWorse of 96 and 98 is extremely high compare to other numbers, so max threshold was set.
Counter(data['NumberOfTime30-59DaysPastDueNotWorse'])
data['NumberOfTime30-59DaysPastDueNotWorse'] = np.where(data['NumberOfTime30-59DaysPastDueNotWorse'] > 13, 13, data['NumberOfTime30-59DaysPastDueNotWorse'])

data.DebtRatio.describe()

# Rather than removing the outliers, threshold of q3 + 1.5iqr was used as maximum value.
q1, q3, iqr = IQR(data, 'DebtRatio')

data['DebtRatio'] = np.where(data['DebtRatio'] > (q3 + iqr * 1.5), (q3 + iqr * 1.5), data['DebtRatio'])

data.DebtRatio.describe()

data.MonthlyIncome.describe()

# Rather than removing the outliers, threshold of q3 + 1.5iqr was used as maximum value.
q1, q3, iqr = IQR(data, 'MonthlyIncome')

data['MonthlyIncome'] = np.where(data['MonthlyIncome'] > (q3 + iqr * 1.5), (q3 + iqr * 1.5), data['MonthlyIncome'])

data.MonthlyIncome.describe()

data.NumberOfOpenCreditLinesAndLoans.describe()

Counter(data['NumberOfOpenCreditLinesAndLoans'])

# There were only few numbers more than 36. Thus, 36 was set as the maximum threshold
data['NumberOfOpenCreditLinesAndLoans'] = np.where(data['NumberOfOpenCreditLinesAndLoans'] > 36, 36, data['NumberOfOpenCreditLinesAndLoans'])

Counter(data['NumberOfTimes90DaysLate'])

# NumberOfTimes90DaysLate of 96 and 98 is extremely high compare to other numbers, so max threshold was set.
Counter(data['NumberOfTimes90DaysLate'])
data['NumberOfTimes90DaysLate'] = np.where(data['NumberOfTimes90DaysLate'] > 17, 17, data['NumberOfTimes90DaysLate'])

Counter(data['NumberRealEstateLoansOrLines'])

# There were only few numbers more than 13. Thus, 13 was set as the maximum threshold
data['NumberRealEstateLoansOrLines'] = np.where(data['NumberRealEstateLoansOrLines'] > 13, 13, data['NumberRealEstateLoansOrLines'])

Counter(data['NumberOfTime60-89DaysPastDueNotWorse'])

# NumberOfTime60-89DaysPastDueNotWorse of 96 and 98 is extremely high compare to other numbers, so max threshold was set.
Counter(data['NumberOfTime60-89DaysPastDueNotWorse'])
data['NumberOfTime60-89DaysPastDueNotWorse'] = np.where(data['NumberOfTime60-89DaysPastDueNotWorse'] > 11, 11, data['NumberOfTime60-89DaysPastDueNotWorse'])

# Upon analyzing NumberOfDependents column, max NumberOfDependents was set to 10.
# Additionally, NaN values were replaced to median value in NumberOfDependents.
for i in range(5,21):
    print (i, len(data[data.NumberOfDependents == i]))

data['NumberOfDependents'] = np.where(data['NumberOfDependents'] > 10, 10, data['NumberOfDependents'])
data['NumberOfDependents'].fillna(data['NumberOfDependents'].median(), inplace=True)

"""### Random Forest Regressor was used to fill in NaN values in MonthlyIncome column (little computationally expensive but predictions are reasonable."""

# Rows with MonthlyIncome becomes the training and rows with NaN will be predicted accordingly.
train = data[data.MonthlyIncome.isnull() == False]
test = data[data.MonthlyIncome.isnull() == True]

X_train = train.drop(['MonthlyIncome', 'SeriousDlqin2yrs'], axis=1)
y_train = train['MonthlyIncome']

regr = RandomForestRegressor(n_estimators=100, criterion='mse', max_depth=None, min_samples_split=2, min_samples_leaf=1,
                              min_weight_fraction_leaf=0.0, max_features='auto', max_leaf_nodes=None, bootstrap=True,
                              oob_score=False, n_jobs=1, random_state=None, verbose=1)

regr.fit(X_train, y_train)

# Replace NaN with predictions from the model
data['MonthlyIncome'] = np.where(data['MonthlyIncome'].isna(), regr.predict(data.drop(['MonthlyIncome', 'SeriousDlqin2yrs'], axis=1)), data['MonthlyIncome'])

"""## **Prediction**

*   Now that the data cleaning is done, the cleaned data can be used to predict "SeriousDlqin2yrs" 



"""

X = data.drop('SeriousDlqin2yrs', axis=1)
y = data['SeriousDlqin2yrs']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

rand_classifier = RandomForestClassifier(n_estimators=100, criterion='gini', max_depth=None, min_samples_split=2,
                               min_samples_leaf=1, min_weight_fraction_leaf=0.0, max_features='auto',
                               max_leaf_nodes=None, bootstrap=True, oob_score=False, n_jobs=1, 
                               random_state=None, verbose=0)
rand_classifier.fit(X_train, y_train)

ada_classifier = AdaBoostClassifier(n_estimators=100, random_state=0)
ada_classifier.fit(X_train, y_train)

grad_classifier = GradientBoostingClassifier(n_estimators=100, learning_rate=1.0, max_depth=1, random_state=0).fit(X_train, y_train)
grad_classifier.fit(X_train, y_train)

y_rand_pred = rand_classifier.predict(X_test)
y_ada_pred = ada_classifier.predict(X_test)
y_grad_pred = grad_classifier.predict(X_test)

from sklearn.metrics import classification_report
print('Random Forest Classifier\n',classification_report(y_test, y_rand_pred))
print('Ada Boost Classifier\n',classification_report(y_test, y_ada_pred))
print('Gradient Boosting Classifier\n',classification_report(y_test, y_grad_pred))

print('Random Forest Classifier:',roc_auc_score(y_test,rand_classifier.predict_proba(X_test)[:, 1] , average='macro', sample_weight=None))
print('Ada Boost Classifier:',roc_auc_score(y_test,ada_classifier.predict_proba(X_test)[:, 1] , average='macro', sample_weight=None))
print('Gradient Boosting Classifier:',roc_auc_score(y_test,grad_classifier.predict_proba(X_test)[:, 1] , average='macro', sample_weight=None))

"""## **Test Data Prediction**


*   Since Ada Boost Classifier showed the best performance, it'll be used to predict the test data.
"""

test_data = pd.read_csv('cs-test.csv')
test_data.head()

# Omit first column
test_data = test_data.iloc[: , 1:]

# NaN needs to be filled in.
test_data.isna().sum()

# Test data is cleaned in the same manner
q1, q3, iqr = IQR(test_data, 'RevolvingUtilizationOfUnsecuredLines')

test_data['RevolvingUtilizationOfUnsecuredLines'] = np.where(test_data['RevolvingUtilizationOfUnsecuredLines'] > (q3 + iqr * 1.5), (q3 + iqr * 1.5), test_data['RevolvingUtilizationOfUnsecuredLines'])

test_data['age'] = np.where(test_data['age'] < 22, 22, test_data['age'])

test_data['NumberOfTime30-59DaysPastDueNotWorse'] = np.where(test_data['NumberOfTime30-59DaysPastDueNotWorse'] > 13, 13, test_data['NumberOfTime30-59DaysPastDueNotWorse'])

q1, q3, iqr = IQR(test_data, 'DebtRatio')
test_data['DebtRatio'] = np.where(test_data['DebtRatio'] > (q3 + iqr * 1.5), (q3 + iqr * 1.5), test_data['DebtRatio'])

q1, q3, iqr = IQR(test_data, 'MonthlyIncome')
test_data['MonthlyIncome'] = np.where(test_data['MonthlyIncome'] > (q3 + iqr * 1.5), (q3 + iqr * 1.5), test_data['MonthlyIncome'])

test_data['NumberOfOpenCreditLinesAndLoans'] = np.where(test_data['NumberOfOpenCreditLinesAndLoans'] > 36, 36, test_data['NumberOfOpenCreditLinesAndLoans'])

test_data['NumberOfTimes90DaysLate'] = np.where(test_data['NumberOfTimes90DaysLate'] > 17, 17, test_data['NumberOfTimes90DaysLate'])

test_data['NumberRealEstateLoansOrLines'] = np.where(test_data['NumberRealEstateLoansOrLines'] > 13, 13, test_data['NumberRealEstateLoansOrLines'])

test_data['NumberOfTime60-89DaysPastDueNotWorse'] = np.where(test_data['NumberOfTime60-89DaysPastDueNotWorse'] > 11, 11, test_data['NumberOfTime60-89DaysPastDueNotWorse'])

# Fill in NaN in NumberOfDependents
test_data['NumberOfDependents'] = np.where(test_data['NumberOfDependents'] > 10, 10, test_data['NumberOfDependents'])
test_data['NumberOfDependents'].fillna(test_data['NumberOfDependents'].median(), inplace=True)

# Rows with MonthlyIncome becomes the training and rows with NaN will be predicted accordingly.
train = test_data[test_data.MonthlyIncome.isnull() == False]
test = test_data[test_data.MonthlyIncome.isnull() == True]

X_train = train.drop(['MonthlyIncome', 'SeriousDlqin2yrs'], axis=1)
y_train = train['MonthlyIncome']

# Replace NaN with predictions from the model
test_data['MonthlyIncome'] = np.where(test_data['MonthlyIncome'].isna(), regr.predict(test_data.drop(['MonthlyIncome', 'SeriousDlqin2yrs'], axis=1)), test_data['MonthlyIncome'])

# Predict using the trained model
X = test_data.drop('SeriousDlqin2yrs', axis=1)
SeriousDlqin2yrs = ada_classifier.predict(X)

test_pred = pd.DataFrame({'SeriousDlqin2yrs': SeriousDlqin2yrs})
test_pred = test_pred.join(X)

# Test dataset is successfully predicted
test_pred.SeriousDlqin2yrs.describe()

test_pred.to_csv("./cs-predictions.csv", index=False)