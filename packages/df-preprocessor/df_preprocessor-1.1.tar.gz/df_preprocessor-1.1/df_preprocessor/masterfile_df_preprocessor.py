from pandas import DataFrame
import pandas as pd
from plyer import filechooser
import re
import numpy as np

class df_preprocessor(DataFrame):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

# method import csv werkt ! :)
    @classmethod
    def import_csv(cls, *separators, encoding = 'UTF-8', **kwargs):
        """
        
        Import a CSV file using a pop up window, you can give 1 or more separators and a specific encoding.
        If the separator in your csv file is different than ',' use one argument like: ';'
        If there are two or more different separators use two or more arguments like: ',' , ';'

        No arguments given: default separator ',' and default encoding 'UTF-8' will be used
        
        :param separators: The separator(s) used in the CSV file you want to import
        :type separators: string
    
        :param encoding: The encoding used in the CSV file
        :type encoding: string
            
        :kwargs (dict): Keyword arguments to customize CSV export, see Pandas documentation.
        
        :return: The function will return a Pandas DataFrame with the data in the CSV
        :type return: Pandas DataFrame
        """

        import_path = filechooser.open_file()
    
        if import_path:
            if separators:
                sep_pattern = '|'.join(map(lambda s: re.escape(str(s)), separators))

            else:
                sep_pattern = ','

            df = pd.read_csv(import_path[0], sep=sep_pattern, engine='python', encoding = encoding, **kwargs)
            print('csv file is imported')
            df = df_preprocessor(df)
            return df 
        else:
            print("No file selected.")


#file exporter for csv-file werkt ! :)
    def export_csv(self, **kwargs):
        """
        Export a Pandas DataFrame to a CSV file.

        Parameters:
        - kwargs (dict): Keyword arguments to customize CSV export, see Pandas documentation.

        Returns:
        - None: The function writes the DataFrame to the specified CSV file.

        This function exports a DataFrame to a CSV file with customizable settings specified
        as keyword arguments. If the user selects a save path using a file dialog, the
        function will save the DataFrame to the chosen location. If no file is saved,
        it will print "No file saved."
        """
        export_path = filechooser.save_file()
        if export_path:
            self.to_csv(export_path[0], **kwargs)
            return None
        else:
            print("No file saved")



# method delete nan values  werkt :)      
    def delete_nan_rows(self):
   
        """
   
    deletes all rows in pandas dataframe where value in every column is nan.
   
    :param df: pandas dataframe in which you would like to delete all rows with nan values
    :type df: pandas dataframe
   
    :return: pandas dataframe without rows with nan values
    :type return: pandas dataframe
   
    """
   
    
        nan_rows = self[super().isna().all(axis=1)]
      
        df_cleaned = self.drop(nan_rows.index)
        num_NaN_removed = len(self) - len(df_cleaned)
        print(f"Removed {num_NaN_removed} rows.")
        df_cleaned = df_preprocessor(df_cleaned)
        return df_cleaned
    


# method duplicaten checken
    def check_duplicate_rows(self):
        """
    Check if there are duplicate rows in a DataFrame.
 
    :param df: The Pandas DataFrame you want to check
    :type df: Pandas DataFrame
 
    :return: The function will return an overview of the duplicate rows with a linebreak after every set of duplicates.
    :type return: string
    """
 
        df_sorted = super().sort_values(by=super().columns.tolist()) 
        duplicate_rows = df_sorted[df_sorted.duplicated(keep=False)]
    
        if not duplicate_rows.empty:
            print("Duplicate rows found:")
            prev_row = None
            for index, row in duplicate_rows.iterrows():
                if prev_row is None or not row.equals(prev_row):
                    print("  ")
                print(index, "\t", " ".join(row.astype(str)))
                prev_row = row
        else:
            print("No duplicate rows found")


  
# method duplicate rijen verwijderen
    def delete_duplicate_rows(self):
   
        """
   
    deletes all duplicate rows that are found in the pandas dataframe
   
    :param df: pandas dataframe in which you would like to delete duplicate rows
    :type df: pandas dataframe
   
    :return: pandas dataframe where all duplicate rows are deleted
    :type return: pandas dataframe
   
    """
   
        df_cleaned = self.drop_duplicates(keep='first')
   
        num_duplicates_removed = len(self) - len(df_cleaned)
        print(f"Removed {num_duplicates_removed} duplicate rows.")
        df_cleaned = df_preprocessor(df_cleaned)
        return df_cleaned
    

# method delete duplicate kolommen 
    def delete_duplicate_column(self, reference_column, column_to_delete):
        """
    When all the values are equal in both columns, the colomn_to_delete will be deleted
 
    :param df: The Pandas DataFrame
    :type df: Pandas DataFrame
 
    :param reference_column: The column you want to check and keep
    :type reference_column: string
 
    :param df: The column you want to check and delete if both columns are the same
    :type column_to_: string
    
    :return: The function will return the DataFrame without the column_to_delete or a message when the columns are not identical
    :type return: string
    """
    
    
        if (self[reference_column] == self[column_to_delete]).all():
            self = super().drop(column_to_delete, axis=1)
            self = df_preprocessor(self)
            return self
        else:
            print(f"The {reference_column} and {column_to_delete} columns do not have the same values.")
        


    def check_nan_value(self):
        """
    Check if there are NaN values in a DataFrame.

 

    :param df: The Pandas DataFrame you want to check.
    :type df: Pandas DataFrame

 

    :return: This function does not return a value; it prints an overview of the NaN values
             with their corresponding row number and column.
    :rtype: None
    """
        missing_rows = self[super().isnull().any(axis=1)]
        if not missing_rows.empty:
            print("Rows with missing values:")
            for index, row in missing_rows.iterrows():
                missing_columns = row.index[row.isnull()]
                print(f"Row {index}:")
                for col in missing_columns:
                    print(f"   {col}: {row[col]}")
        else:
            print("No rows with missing values found.")

        

    def detect_outliers(self, column_name, threshold_zscore=None, threshold_tukey=None, threshold_iqr=None):
        """
        Detect outliers in a column using various methods.

        Parameters:
        - df: dataframe
        - column_name: str, the name of the column for which outliers are to be detected.
        - threshold_zscore: float, optional (default=None)
            - Threshold value for outlier detection methods (usually 2 to 3 for Z-score and 1.5 for IQR and Tukey).

        Returns:
        - outliers_dict: Dictionary containing outlier values and row numbers for each method.
        Keys: 'z-score', 'iqr', 'tukey'
        Values: Tuple containing two lists - outlier values and their corresponding row numbers.
        """
        
        column = self[column_name].values  # Extract the column as a NumPy array
        
        # Initialize the dictionary to store results for each method
        outliers_dict = {
            'z-score': ([], []),  # Tuple with two empty lists
            'iqr': ([], []),
            'tukey': ([], []),
        }

        # Z-score method
        mean = np.mean(column)
        std = np.std(column)
        if threshold_zscore is None:
            threshold_zscore = 2.5  # Default threshold for Z-score
        z_score_outliers = [(x, i) for i, x in enumerate(column) if abs((x - mean) / std) > threshold_zscore]
        outliers_dict['z-score'] = ([x[0] for x in z_score_outliers], [x[1] for x in z_score_outliers])

        # IQR method
        q1 = np.percentile(column, 25)
        q3 = np.percentile(column, 75)
        iqr = q3 - q1
        if threshold_iqr is None:
            threshold_iqr = 1.5  # Default threshold for IQR
        iqr_outliers = [(x, i) for i, x in enumerate(column) if (x < q1 - threshold_iqr * iqr) or (x > q3 + threshold_iqr * iqr)]
        outliers_dict['iqr'] = ([x[0] for x in iqr_outliers], [x[1] for x in iqr_outliers])

        # Tukey's method
        if threshold_tukey is None:
            threshold_tukey = 1.5  # Default threshold for Tukey's Fences
        lower_fence = q1 - threshold_tukey * iqr
        upper_fence = q3 + threshold_tukey * iqr
        tukey_outliers = [(x, i) for i, x in enumerate(column) if (x < lower_fence) or (x > upper_fence)]
        outliers_dict['tukey'] = ([x[0] for x in tukey_outliers], [x[1] for x in tukey_outliers])

        return outliers_dict




    def check_duplicate_columns(self):
        """
        Check a DataFrame for duplicate columns and print a message for each pair of duplicate columns.

    

        :param df: The DataFrame to be checked for duplicate columns
        :type df: Pandas DataFrame

    

        :return: None
        """
        
        column_names = super().columns.tolist()
        found_duplicate = False

    

        for i in range(len(column_names)):
            for j in range(i + 1, len(column_names)):
                column1 = column_names[i]
                column2 = column_names[j]

    

                if (self[column1] == self[column2]).all():
                    found_duplicate = True
                    print(f"'{column1}' and '{column2}' are the same")

    

        if not found_duplicate:
            print("No duplicate columns found")



    def export_excel(self, **kwargs):
        
        """
        export your pandas dataframe as excel file with a pop-up window
        in pop-up window write the name of your file + .xlsx
        
        :param df: the pandas dataframe you want to export to csv-file
        :type df: pandas dataframe
        
        :return: pandas dataframe and an exported csv-file
        :type return: pandas dataframe
    
        """
    

    

        export_path = filechooser.save_file()
        if export_path:
            self = super().to_excel(export_path[0], **kwargs)
            return None
        else:
            print("No file saved")



