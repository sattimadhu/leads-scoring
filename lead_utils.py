import pandas as pd
import joblib

# Load the model and preprocessor
def load_model_and_preprocessor():
    model = joblib.load('model.pkl')
    preprocessor = joblib.load('preprocessor.pkl')
    return model, preprocessor

# Convert revenue string to numeric value
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

# Score leads using the trained model and preprocessor
def score_leads(df, model, preprocessor):
    # Convert Revenue to numeric
    df['Revenue_num'] = df['Revenue'].apply(revenue_to_number)

    # Ensure columns match training
    features = ['Industry', 'Product/Service Category', 'Business Type',
                'Employees Count', 'Revenue_num', 'Year Founded',
                'BBB Rating', 'City', 'State']

    # Filter relevant features
    X = df[features].copy()

    # Transform input using the preprocessor
    X_processed = preprocessor.transform(X)

    # Predict lead scores
    df['Lead Score'] = model.predict(X_processed)  # Optional scaling

    return df
