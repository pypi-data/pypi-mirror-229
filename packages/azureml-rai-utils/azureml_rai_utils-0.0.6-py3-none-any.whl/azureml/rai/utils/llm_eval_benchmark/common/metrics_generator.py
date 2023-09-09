# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from sklearn.metrics import accuracy_score, confusion_matrix
import pandas as pd


class MetricsGenerator:
    """MetricsGenerator is responsible for creating metrics based on the full dataframe
    which contains both the true labels and AOAI-scored labels
    """
    def __init__(self):
        return

    def eval(self, df, save_fp):
        """Evaluate dataframe accuracy and save confusion matrix at specified path.

        :param df: dataframe with true label and gpt labels
        :type df: dataframe
        :param save_fp: file path to save confusion matrix as csv
        :type save_fp: str
        :return: accuracy
        :rtype: float
        """
        if df.shape[0] == 0:
            return 0
        df["rating"] = df["rating"].astype(int)
        accuracy = accuracy_score(df['label_true'], df['rating'])
        all_label_list = []
        max_label = df["label_true"].max()
        if max_label == 1:
            all_label_list = [0,1]
        elif max_label == 0:
            all_label_list = [0]
        else:
            all_label_list = list(range(1, max_label+1))
        confusion = confusion_matrix(df['label_true'], df['rating'], labels=[-1]+all_label_list)
        predicted_columns = ["malformatted"] + [f"predicted-{i}" for i in all_label_list]
        actual_rows = ["malformatted"] + [f"actual-{i}" for i in all_label_list]
        confusion_matrix_df = pd.DataFrame(confusion, columns=predicted_columns, index=actual_rows)
        print(confusion_matrix_df)
        confusion_matrix_df.to_csv(save_fp)
        return accuracy
