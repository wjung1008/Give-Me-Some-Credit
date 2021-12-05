# Give-Me-Some-Credit
- Data Scientist Position Assignment

## Data was acquired from Kaggle
- https://www.kaggle.com/c/GiveMeSomeCredit/data
- The Goal of this task was to build a model that borrowers can use to help make the best financial decisions.

## Overview
### Analyze and clean data
- First of all, given data (cs-training.csv) was analyzed and cleaned.
- Outliers were detected based on different techniques including Interquartile range (IQR) and thresholding.
- Therefore, rather than simply dropping the outliers, they were either replaced with values based on IQR or min and max threshold was used to stabilize the data.

### Fill in NaN
- Upon observing the data, "NumberOfDependents" and "MonthlyIncome" contained NaN.
- NumberOfDependents was filled in with Median.
- MonthlyIncome was predicted using Random Forest Regressor and filled in.

### Model Test
- Cleaned data was used to test prediction models.
- Following models were tested:
  -  Random Forest
  -  Ada Boost
  -  Gradient Boosting
- Models were evaluated by Precision, Recall, F1-Score and ROC_AUC score

### Test Data Prediction
- Ada Boost Classifier showed better performance than models.
- The test data was cleaned in same manner as the training data.
- The predicted "SeriousDlqin2yrs" was appended to the cleaned test data and saved as "cs-predictions.csv".
