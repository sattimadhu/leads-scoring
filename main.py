import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score

# Load data (example dictionary, replace with your actual data)
# data = [
#     {
#         'Company': 'Moss, Perez and Morgan',
#         'Website': 'https://www.johnson.info/',
#         'Industry': 'Education',
#         'Product/Service Category': 'CRM',
#         'Business Type': 'B2B',
#         'Employees Count': 882,
#         'Revenue': '$1M-$10M',
#         'Year Founded': 2016,
#         'BBB Rating': 'A',
#         'City': 'Lake Jacquelineburgh',
#         'State': 'TX',
#         'Lead Score': 43
#     },
#     {
#         'Company': 'Smith, Johnson and Johnson',
#         'Website': 'https://dalton-robinson.net/',
#         'Industry': 'Software Development',
#         'Product/Service Category': 'e-Learning',
#         'Business Type': 'B2B',
#         'Employees Count': 160,
#         'Revenue': '$1M-$10M',
#         'Year Founded': 1996,
#         'BBB Rating': 'C',
#         'City': 'West Rachelchester',
#         'State': 'PA',
#         'Lead Score': 45
#     }
# ]

# df = pd.DataFrame(data)
data=pd.read_csv('lead_scoring_dataset.csv')
# Preprocessing revenue to numeric
def revenue_to_number(rev):
    if pd.isnull(rev):
        return 0

    rev = rev.replace('$', '').replace('+', '').upper().strip()  # Remove $ and +, upper case

    parts = rev.split('-')

    def convert_part(part):
        part = part.strip()
        if part.endswith('M'):
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

# Select features and target
features = ['Industry', 'Product/Service Category', 'Business Type', 'Employees Count', 'Revenue_num', 'Year Founded', 'BBB Rating', 'City', 'State']
target = 'Lead Score'

X = data[features]
y = data[target]

# One-hot encode categorical columns
categorical_cols = ['Industry', 'Product/Service Category', 'Business Type', 'BBB Rating', 'City', 'State']

preprocessor = ColumnTransformer(
    transformers=[
        ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_cols)
    ], remainder='passthrough')

X_processed = preprocessor.fit_transform(X)

X_train, X_test, y_train, y_test = train_test_split(X_processed, y, test_size=0.2, random_state=42)

model = RandomForestRegressor(random_state=42)
model.fit(X_train, y_train)

y_pred = model.predict(X_test)
print(y_pred)
# Evaluate
print("MAE:", mean_absolute_error(y_test, y_pred))
print("R2 Score:", r2_score(y_test, y_pred))
