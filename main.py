import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
import joblib

# Step 1: Load data 
data = pd.read_csv('lead_scoring_dataset.csv')

# Step 2: Convert Revenue to numeric
def revenue_to_number(rev):
    if pd.isnull(rev):
        return 0
    rev = rev.replace('$', '').replace('+', '').upper().strip()
    parts = rev.split('-')

    def convert_part(part):
        part = part.strip()
        if part.endswith('B'):
            return float(part[:-1])*1000
        elif part.endswith('M'):
            return float(part[:-1])
        elif part.endswith('K'):
            return float(part[:-1]) / 1000
        else:
            return float(part)

    if len(parts) == 2:
        low = convert_part(parts[0])
        high = convert_part(parts[1])
        return (low + high) / 2
    else:
        return convert_part(parts[0])

data['Revenue_num'] = data['Revenue'].apply(revenue_to_number)

# Step 3: Select features and target
features = ['Industry', 'Product/Service Category', 'Business Type', 'Employees Count',
            'Revenue_num', 'Year Founded', 'BBB Rating', 'City', 'State']
target = 'Lead Score'
X = data[features]
y = data[target]

# Step 4: Define categorical columns and preprocessing pipeline
categorical_cols = ['Industry', 'Product/Service Category', 'Business Type', 'BBB Rating', 'City', 'State']

preprocessor = ColumnTransformer(
    transformers=[
        ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_cols)
    ],
    remainder='passthrough'
)

# Step 5: Fit transform the data
X_processed = preprocessor.fit_transform(X)

# Step 6: Split and train
X_train, X_test, y_train, y_test = train_test_split(X_processed, y, test_size=0.2, random_state=42)

model = RandomForestRegressor(random_state=42)
model.fit(X_train, y_train)

# Step 7: Save model and preprocessor
joblib.dump(model, 'model.pkl')
joblib.dump(preprocessor, 'preprocessor.pkl')

# Step 8: Evaluate
y_pred = model.predict(X_test)
print("MAE:", mean_absolute_error(y_test, y_pred))
print("R2 Score:", r2_score(y_test, y_pred))
