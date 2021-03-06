def split_space_data(X_normalized,X,Y,file_path,observation_number,test_size):
    from sklearn.model_selection import StratifiedShuffleSplit
    # Create the helper object
    sss = StratifiedShuffleSplit(n_splits=1,test_size=test_size)
    # Generate the indecis
    train_index, test_index = next(sss.split(X_normalized, Y))
    # Shuffle and split the data
    X_normalized_train, X_normalized_test = X_normalized[train_index], X_normalized[test_index]
    X_train, X_test = X[train_index], X[test_index]
    Y_train, Y_test = Y[train_index], Y[test_index]
    file_path_train, file_path_test = file_path[train_index], file_path[test_index]
    observation_number_train, observation_number_test = observation_number[train_index], observation_number[test_index]
    return (X_normalized_train,X_train,Y_train,file_path_train,observation_number_train), (X_normalized_test,X_test,Y_test,file_path_test,observation_number_test)

def metrics(outputs, labels, threshold=0.5): 
    # Set the predicions to either 0 or 1 based on the given threshold
    predictions = outputs >= (1 - threshold)
    # Set the indices to either 0 or 1 based on the metric we are checking
    true_positive_indices = (predictions == 0.) * (labels == 0)
    false_positive_indices = (predictions == 0.) * (labels == 1)
    true_negative_indices = (predictions == 1.) * (labels == 1)
    false_negative_indices = (predictions == 1.) * (labels == 0)
    # Get the total count for each metric we are checking
    true_positive_count = true_positive_indices.sum()
    false_positive_count = false_positive_indices.sum()
    true_negative_count = true_negative_indices.sum()
    false_negative_count = false_negative_indices.sum()
    # Calculate and store the FPR and MDR in a dictionary for convenience
    fpr_and_mdr = {'MDR': false_negative_count / (true_positive_count + false_negative_count),'FPR': false_positive_count / (true_negative_count + false_positive_count)}
    return fpr_and_mdr

def get_metrics(outputs, labels, with_acc=True):
    import numpy as np
    all_metrics = {}
    # FPR and MDR 0.4
    temp = metrics(outputs, labels, threshold=0.4)
    all_metrics["FALSE_POSITIVE_RATE_4"] = temp["FPR"]
    all_metrics["MISSED_DETECTION_RATE_4"] = temp["MDR"]
    # FPR and MDR 0.5
    temp = metrics(outputs, labels, threshold=0.5)
    all_metrics["FALSE_POSITIVE_RATE_5"] = temp["FPR"]
    all_metrics["MISSED_DETECTION_RATE_5"] = temp["MDR"]
    # FPR and MDR 0.6
    temp = metrics(outputs, labels, threshold=0.6)
    all_metrics["FALSE_POSITIVE_RATE_6"] = temp["FPR"]
    all_metrics["MISSED_DETECTION_RATE_6"] = temp["MDR"]
    # Summed FPR and MDR
    all_metrics["FALSE_POSITIVE_RATE"] = all_metrics["FALSE_POSITIVE_RATE_4"] + all_metrics["FALSE_POSITIVE_RATE_5"] + all_metrics["FALSE_POSITIVE_RATE_6"] 
    all_metrics["MISSED_DETECTION_RATE"] = all_metrics["MISSED_DETECTION_RATE_4"] + all_metrics["MISSED_DETECTION_RATE_5"] + all_metrics["MISSED_DETECTION_RATE_6"]
    # The true sum
    all_metrics["PIPPIN_METRIC"] = all_metrics["FALSE_POSITIVE_RATE"] + all_metrics["MISSED_DETECTION_RATE"]
    # Accuracy
    if with_acc:
        predictions = np.around(outputs).astype(int)
        all_metrics["ACCURACY"] = (predictions == labels).sum() / len(labels)
    return all_metrics

def create_result_csv(user_params, model_params, metrics, extra_dict=None, file_name="results.csv"):
    import pandas as pd
    import os
    # Define results file
    results_file = file_name
    # Dictionary to be turned into a CSV
    csv_dict = {}
    # Set the important columns in a set order
    csv_header_order = [
        "INITIALS",
        "MODEL_DESCRIPTION",
        "VERSION",
        "FALSE_POSITIVE_RATE_4", 
        "MISSED_DETECTION_RATE_4",
        "FALSE_POSITIVE_RATE_5", 
        "MISSED_DETECTION_RATE_5", 
        "FALSE_POSITIVE_RATE_6", 
        "MISSED_DETECTION_RATE_6",
        "FALSE_POSITIVE_RATE",
        "MISSED_DETECTION_RATE",
        "PIPPIN_METRIC",
        "ACCURACY", 
        "NUMBER_OF_FILTERS_1",
        "NUMBER_OF_FILTERS_2",
        "NUMBER_OF_FILTERS_3",
        "NUMBER_OF_FILTERS_4",        
        "LEARNING_RATE", 
        "BATCH_SIZE",
        "NUMBER_OF_EPOCHS",
        "NUMBER_OF_FILTERS",
        "POOL_SIZE",
        "KERNAL_SIZE",
        "NUMBER_OF_LAYERS",
        "DROPOUT_PERCENT",
        "FPR_ALPHA",
        "MDR_ALPHA",
        "DENSE_LAYER_SHAPES"
    ]
    # Loop through headers and create the dictionary
    for header in csv_header_order:
        # Check where the header is
        if header in metrics.keys():
            csv_dict[header] = str(metrics[header])
        elif header in user_params.keys():
            csv_dict[header] = str(user_params[header])
        elif header in model_params.keys():
            csv_dict[header] = str(model_params[header])
    # Turn the current data to a Dataframe
    updated_df = pd.DataFrame(csv_dict, index=[0])
    # Check if a CSV already exists so we can add the current experiment to the previously logged ones
    if os.path.isfile(results_file):
        df = pd.read_csv(results_file)
        updated_df = pd.concat([df, updated_df])
    # Write the CSV to disk
    updated_df.to_csv(results_file, index=False)
    return updated_df