import joblib

model_directory = {
    "LR": ["logistic_regression_sentiment.pkl", "logistic_regression_sentiment_tfidf_vectorizer.pkl"],
    "NB": ["naive_bayes_sentiment.pkl", "naive_bayes_sentiment_tfidf_vectorizer.pkl"],
    "RF": ["random_forest_sentiment.pkl", "random_forest_sentiment_tfidf_vectorizer.pkl"],
    "SVM" : ["svm_rbf_sentiment.pkl", "svm_rbf_sentiment_tfidf_vectorizer.pkl"]
}


class pretrained_model:
    def __init__(self):
        self.model = "SVM"

    def show_available_models(self):
        print("All the models currently available are:\n", list[model_directory.keys()])
        return list[model_directory.keys()]
    
    def select_pretrained_model(self, name="SVM"):
        self.model = name
        print(f"Model selected- {self.model}")

    def predict(self, input_string):
        print("Loading model & vectorizer...")
        loaded_model = joblib.load("./models/" + model_directory[self.model][0])
        loaded_vectorizer = joblib.load("./models/" + model_directory[self.model][1])
        new_features = loaded_vectorizer.transform([input_string])
        predicted_label = loaded_model.predict(new_features)
        print(predicted_label[0])
        return predicted_label[0]


# # test code for pretrained models
# c = pretrained_model()
# c.show_available_models()
# c.select_pretrained_model("SVM")
# c.predict("এর মত ফালতু বই আর হয় না")