import pandas as pd

dataset_directory = {
    "Book-Review": {
        "Train": "data/Book/blp23_sentiment_train.tsv",
        "Dev": "data/Book/blp23_sentiment_dev.tsv",
        "Description": "YET TO UPDATE"
    }

}


class Dataset:
    def __init__(self):
        self.dataset_directory = dataset_directory

    def all_dataset_name(self):
        return list(self.dataset_directory.keys())
    
    def get_train_dataset(self, name = "Book-Review"):
        print("Loading Dataset Book-review please wait...")
        loaded_data = pd.read_csv(self.dataset_directory[name]["Train"], sep= '\t')
        
        label_mapping = {'Neutral': 0, 'Positive': 1, 'Negative': -1}
        loaded_data['label'] = loaded_data['label'].map(label_mapping)
        
        print("Loaded")
        return loaded_data
    


# # Test Code 
# a = Dataset()
# d = a.get_train_dataset()
# print(d.head())