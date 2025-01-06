import pandas as pd
from sklearn.ensemble import RandomForestRegressor 
from sklearn.model_selection import train_test_split 
from sklearn.metrics import mean_absolute_error
import matplotlib.pyplot as plt

#data from 2015-2017

df = pd.read_excel("2015_2017CAData.xlsx", "Sheet1")

df_data = pd.DataFrame(df)

#ML processing --------------------------------------------- (Predictive Modeling)

data = df_data

features_measurable = ["Overall Food Insecurity Rate", "# of Food Insecure Persons Overall", "# of Food Insecure Children", "Cost Per Meal", "Weighted Annual Food Budget Shortfall"]

X_training = data[features_measurable]

y_outputPredictor = data["# of Food Insecure Persons Overall"]

X_train, X_test, y_train, y_test = train_test_split(X_training, y_outputPredictor, test_size = 0.2, random_state = 42)

modeling = RandomForestRegressor(random_state = 42)

modeling.fit(X_train, y_train)

y_outputPredictor_predictions = modeling.predict(X_test)

#test with data from 2019-2022

df2 = pd.read_excel("MMG2024_2019-2022_Data_ToShare_v3.xlsx", sheet_name = "County")

df2_data = pd.DataFrame(df2)

state_code = "CA"

df2_sorted = (df2_data[df2_data["State"] == state_code])

df2_sorted.drop(['Food Insecurity Rate among Black Persons (all ethnicities)',  "Food Insecurity Rate among Hispanic Persons (any race)", "Food Insecurity Rate among White, non-Hispanic Persons"], axis=1, inplace=True)

df2_sorted.to_excel(f"{state_code}_countyDataAbridged.xlsx", index=False)

#-----------

future = df2_sorted

features_future_measurable = ["Overall Food Insecurity Rate", "# of Food Insecure Persons Overall", "# of Food Insecure Children", "Cost Per Meal", "Weighted Annual Food Budget Shortfall"]

future_prediction = modeling.predict(future[features_future_measurable])

print(future_prediction)

future["Estimated Number of People Food Insecure"] = future_prediction
ranked_counties = future.sort_values(by='Estimated Number of People Food Insecure', ascending=False) 
print(ranked_counties[['County, State', 'Estimated Number of People Food Insecure']])