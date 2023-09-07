from sklearn.preprocessing import StandardScaler

def scale_features(data):
    # Separate numeric and string columns
    numeric_columns = data.select_dtypes(include=['number']).columns
    string_columns = data.select_dtypes(include=['object']).columns

    # Scale only numeric columns
    if not numeric_columns.empty:
        scaler = StandardScaler()
        scaled_numeric_data = scaler.fit_transform(data[numeric_columns])
        data[numeric_columns] = scaled_numeric_data

    return data
