from sklearn.preprocessing import StandardScaler

def scale_features(data):
    # Scale numeric features to have zero mean and unit variance
    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(data)
    return scaled_data
