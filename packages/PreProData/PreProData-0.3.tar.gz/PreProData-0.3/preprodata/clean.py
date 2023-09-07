def remove_duplicates(data):
    # Remove duplicate rows from the dataset
    cleaned_data = data.drop_duplicates()
    return cleaned_data
