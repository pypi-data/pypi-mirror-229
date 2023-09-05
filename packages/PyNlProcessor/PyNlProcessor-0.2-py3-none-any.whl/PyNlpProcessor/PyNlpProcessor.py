def natural_language_processing(data_frame):
    # Download stopwords if not already downloaded
    nltk.download('stopwords')
    nltk.download('punkt')
    nltk.download('wordnet')

    # Define a function to remove unwanted characters
    def remove_unwanted_characters(words):
        cleaned_words = []
        pattern = r"[^\w\s]"  # Regex pattern to match non-alphanumeric characters

        for word in words:
            cleaned_word = re.sub(pattern, "", word)
            if cleaned_word:  # Check if the word is not empty after removing characters
                cleaned_words.append(cleaned_word)

        return cleaned_words

    # Define a function to preprocess and clean the text
    def preprocess_text(text):
        # Tokenize words
        words = word_tokenize(text.lower())

        # Remove stopwords
        stop = set(stopwords.words('english'))
        words = [word for word in words if word not in stop]

        # Remove unwanted characters
        words = remove_unwanted_characters(words)

        # Apply stemming or lemmatization (choose one)
        # stemmer = PorterStemmer()
        # words = [stemmer.stem(word) for word in words]

        lemmatizer = WordNetLemmatizer()
        words = [lemmatizer.lemmatize(word) for word in words]

        return ' '.join(words)

   # Convert the text_column to a list
    text_column = to_change.iloc[:, 1]
    documents = text_column.tolist()

    # Preprocess the documents
    preprocessed_documents = [preprocess_text(doc) for doc in documents]

    # Create a CountVectorizer with a maximum of 1000 features
    count_vec = CountVectorizer(max_features=1000)

    # Fit and transform the data using CountVectorizer
    x_train_features = count_vec.fit_transform(preprocessed_documents)

    # Create a DataFrame to store the word counts
    word_counts_df = pd.DataFrame(
        data=x_train_features.toarray(),
        columns=count_vec.get_feature_names_out(),
    )

    # Print the word counts DataFrame
    return word_counts_df
