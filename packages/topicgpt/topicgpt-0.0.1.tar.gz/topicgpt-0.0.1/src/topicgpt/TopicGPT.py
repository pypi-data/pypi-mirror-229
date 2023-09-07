import numpy as np
import os
import pickle
# make sure the import works even if the package has not been installed and just the files are used
try:
    from topicgpt.Clustering import Clustering_and_DimRed
    from topicgpt.ExtractTopWords import ExtractTopWords
    from topicgpt.TopwordEnhancement import TopwordEnhancement
    from topicgpt.GetEmbeddingsOpenAI import GetEmbeddingsOpenAI
    from topicgpt.TopicPrompting import TopicPrompting
    from topicgpt.TopicRepresentation import Topic
    import topicgpt.TopicRepresentation as TopicRepresentation
except:
    from Clustering import Clustering_and_DimRed
    from ExtractTopWords import ExtractTopWords
    from TopwordEnhancement import TopwordEnhancement
    from GetEmbeddingsOpenAI import GetEmbeddingsOpenAI
    from TopicPrompting import TopicPrompting
    from TopicRepresentation import Topic
    import TopicRepresentation as TopicRepresentation

embeddings_path= "SavedEmbeddings/embeddings.pkl" #global variable for the path to the embeddings

class TopicGPT:
    """
    This is the main class for doing topic modelling with TopicGPT. 
    """

    def __init__(self, 
                 openai_api_key: str,
                 n_topics: int = None,
                 openai_prompting_model: str = "gpt-3.5-turbo-16k",
                 max_number_of_tokens: int = 16384,
                 corpus_instruction: str = "",  
                 document_embeddings: np.ndarray = None,
                 vocab_embeddings: dict[str, np.ndarray] = None,
                 embedding_model: str = "text-embedding-ada-002",
                 max_numer_of_tokens_embedding: int = 8191,
                 use_saved_embeddings: bool = True,
                 clusterer: Clustering_and_DimRed = None, 
                 n_topwords: int = 2000,
                 n_topwords_description: int = 500,
                 topword_extraction_methods: list[str] = ["tfidf", "cosine_similarity"], 
                 compute_vocab_hyperparams: dict = {},
                 enhancer: TopwordEnhancement = None,
                 topic_prompting: TopicPrompting = None
                 ) -> None:
        
        """
        Initialize the main class for doing topic modelling with TopicGPT.

        params:
            openai_api_key: your OpenAI API key. You can get this from https://beta.openai.com/account/api-keys.
            n_topics: number of topics to find. If None, then it will be automatically determined using the Hdbscan algorithm (https://pypi.org/project/hdbscan/). Otherwise agglomerative clustering will be used. Note that in case of too little data less than the specified number of topics may be found.
            openai_prompting_model: Model provided by Openai to describe the topics and answer the prompts. For available models see https://platform.openai.com/docs/models. 
            max_number_of_tokens: maximum number of tokens to use for the OpenAI API.
            corpus_instruction: If further information on the given corpus are available, it can be beneficial to let the model know about it. 
            document_embeddings: document embeddings for the corpus. If None, then it will be computed using the openAI API.
            vocab_embeddings: vocab embeddings for the corpus. Is given in a dictionary where the keys are the words and the values are the embeddings. If None, then it will be computed using the openAI API.
            embedding_model: Name of the embedding model to use. See https://beta.openai.com/docs/api-reference/text-embedding for available models.
            max_numer_of_tokens_embedding: Maximum number of tokens to use for the OpenAI API when computing the embeddings.
            use_saved_embeddings: Whether to use saved embeddings. If True, then the embeddings will be loaded from the file SavedEmbeddings/embeddings.pkl. If False, then the embeddings will be computed using the openAI API and saved to the file SavedEmbeddings/embeddings.pkl.
            clusterer: the clustering and dimensionality reduction object. The class can be found in the "Clustering/Clustering" folder. If None, a clustering object with default parameters will be used. Note that it doe note make sense to provide document and vocab embeddings and an embedding object at the same time. The number of topics specified in the clusterer will overwrite the n_topics argument.
            n_topwords: number of top words to extract and save for each topic. Note that fewer top words might be used later. 
            n_topwords_description: number of top words to give to the LLM in order to describe the topic. 
            topword_extraction_methods: list of methods to use for extracting top words. The available methods are "tfidf", "cosine_similarity", and "topword_enhancement". See the file ExtractTopWords/ExtractTopWords.py for more details.
            compute_vocab_hyperparams: hyperparameters for computing the vocab embeddings. See the file ExtractTopWords/ExtractTopWords.py for more details.
            enhancer: the topword enhancement object. Is used to describe the The class can be found in the "TopwordEnhancement/TopwordEnhancement.py" folder. If None, a topword enhancement object with default parameters will be used. Note that if an openai model is specified here it will overwrite the openai_prompting_model argument for topic description.
            topic_prompting: the topic prompting object. This object is used to formulate the prompts. The class can be found in the "TopicPrompting/TopicPrompting.py" folder. If None, a topic prompting object with default parameters will be used. Note that if an openai model is specified here it will overwrite the openai_prompting_model argument for topic description.
        """

        # Do some checks on the input arguments
        assert openai_api_key is not None, "You need to provide an OpenAI API key."
        assert n_topics is None or n_topics > 0, "The number of topics needs to be a positive integer."
        assert max_number_of_tokens > 0, "The maximum number of tokens needs to be a positive integer."
        assert max_numer_of_tokens_embedding > 0, "The maximum number of tokens for the embedding model needs to be a positive integer."
        assert n_topwords > 0, "The number of top words needs to be a positive integer."
        assert n_topwords_description > 0, "The number of top words for the topic description needs to be a positive integer."
        assert len(topword_extraction_methods) > 0, "You need to provide at least one topword extraction method."
        assert n_topwords_description <= n_topwords, "The number of top words for the topic description needs to be smaller or equal to the number of top words."

        self.openai_api_key = openai_api_key
        self.n_topics = n_topics
        self.openai_prompting_model = openai_prompting_model
        self.max_number_of_tokens = max_number_of_tokens
        self.corpus_instruction = corpus_instruction
        self.document_embeddings = document_embeddings
        self.vocab_embeddings = vocab_embeddings
        self.embedding_model = embedding_model
        self.max_numer_of_tokens_embedding = max_numer_of_tokens_embedding
        self.embedder = GetEmbeddingsOpenAI(api_key = self.openai_api_key, embedding_model = self.embedding_model, max_tokens = self.max_numer_of_tokens_embedding)
        self.clusterer = clusterer
        self.n_topwords = n_topwords
        self.n_topwords_description = n_topwords_description
        self.topword_extraction_methods = topword_extraction_methods
        self.compute_vocab_hyperparams = compute_vocab_hyperparams
        self.enhancer = enhancer
        self.topic_prompting = topic_prompting	
        self.use_saved_embeddings = use_saved_embeddings

        # if embeddings have already been downloaded to the folder SavedEmbeddings, then load them
        if self.use_saved_embeddings and os.path.exists(embeddings_path):
            with open(embeddings_path, "rb") as f:
                self.document_embeddings, self.vocab_embeddings = pickle.load(f)


        for elem in topword_extraction_methods:
            assert elem in ["tfidf", "cosine_similarity", "topword_enhancement"], "Invalid topword extraction method. Valid methods are 'tfidf', 'cosine_similarity', and 'topword_enhancement'."
        
        if clusterer is None:
            self.clusterer = Clustering_and_DimRed(number_clusters_hdbscan = self.n_topics)
        else:
            self.n_topics = clusterer.number_clusters_hdbscan
        
        if enhancer is None:
            self.enhancer = TopwordEnhancement(openai_key = self.openai_api_key, openai_model = self.openai_prompting_model, max_context_length = self.max_number_of_tokens, corpus_instruction = self.corpus_instruction)

        if topic_prompting is None:
            self.topic_prompting = TopicPrompting(topic_lis = [], openai_key = self.openai_api_key, openai_prompting_model = "gpt-3.5-turbo-16k",  max_context_length_promting = 16000, enhancer = self.enhancer, openai_embedding_model = self.embedding_model, max_context_length_embedding = self.max_numer_of_tokens_embedding, corpus_instruction = corpus_instruction)
        
        self.extractor = ExtractTopWords()
    
    def __repr__(self) -> str:
        repr = "TopicGPT object with the following parameters:\n"
        repr += "-"*150 + "\n"
        repr += "n_topics: " + str(self.n_topics) + "\n"
        repr += "openai_prompting_model: " + self.openai_prompting_model + "\n"
        repr += "max_number_of_tokens: " + str(self.max_number_of_tokens) + "\n"
        repr += "corpus_instruction: " + self.corpus_instruction + "\n"
        repr += "embedding_model: " + self.embedding_model + "\n"
        repr += "clusterer: " + str(self.clusterer) + "\n"
        repr += "n_topwords: " + str(self.n_topwords) + "\n"
        repr += "n_topwords_description: " + str(self.n_topwords_description) + "\n"
        repr += "topword_extraction_methods: " + str(self.topword_extraction_methods) + "\n"
        repr += "compute_vocab_hyperparams: " + str(self.compute_vocab_hyperparams) + "\n"
        repr += "enhancer: " + str(self.enhancer) + "\n"
        repr += "topic_prompting: " + str(self.topic_prompting) + "\n"

        return repr

    def compute_embeddings(self, corpus: list[str]) -> (np.ndarray, dict[str, np.ndarray]):
        """
        This function computes the document and vocab embeddings for the corpus. 
        params:
            corpus: List of strings to embed. Where each element in the list is a document.
        return:
            document_embeddings: document embeddings for the corpus. Has shape (len(corpus), n_embedding_dimensions).
            vocab_embeddings: vocab embeddings for the corpus. Is given in a dictionary where the keys are the words and the values are the embeddings.
        """
        
        self.document_embeddings = self.embedder.get_embeddings(corpus)["embeddings"]

        self.vocab_embeddings = self.extractor.embed_vocab_openAI(self.openai_api_key, self.vocab, embedder = self.embedder)

        return self.document_embeddings, self.vocab_embeddings
    
    def extract_topics(self, corpus) -> list[Topic]:
        """
        This function extracts the topics from the corpus. 
        params:
            corpus: List of strings to embed. Where each element in the list is a document.
        return:
            topics: list of Topic objects. 
        """

        assert self.document_embeddings is not None and self.vocab_embeddings is not None, "You need to compute the embeddings first."

        if self.vocab is None: 
            self.vocab = self.extractor.compute_corpus_vocab(self.corpus, **self.compute_vocab_hyperparams)
        
        self.topic_lis = TopicRepresentation.extract_topics_no_new_vocab_computation(
            corpus = corpus,
            vocab = self.vocab,
            document_embeddings = self.document_embeddings,
            clusterer = self.clusterer,
            vocab_embeddings = self.vocab_embeddings,
            n_topwords = self.n_topwords,
            topword_extraction_methods = self.topword_extraction_methods,
            consider_outliers = True
        )

        return self.topic_lis
    
    def describe_topics(self, topics) -> list[Topic]:
        """
        This function gives topics a name and describes them by using the openai api.
        params:
            topics: list of Topic objects. 
        return:
            topics: list of Topic objects. 
        """

        assert self.topic_lis is not None, "You need to extract the topics first."

        if "cosine_similarity" in self.topword_extraction_methods:
            topword_method = "cosine_similarity"
        elif "tfidf" in self.topword_extraction_methods:
            topword_method = "tfidf"
        else:
            raise ValueError("You need to use either 'cosine_similarity' or 'tfidf' as topword extraction method.")

        self.topic_lis = TopicRepresentation.describe_and_name_topics(
            topics = topics,
            enhancer = self.enhancer,
            topword_method= topword_method,
            n_words = self.n_topwords_description
        )

        return self.topic_lis
    
    def fit(self, corpus, verbose = True): 
        """
        This function computes the embeddings if necessary, extracts the topics, and describes them.
        params:
            corpus: List of strings to embed. Where each element in the list is a document.
            verbose: Whether to print what is happening.
        """
        self.corpus = corpus 
        
        # remove empty documents
        n_empty = 0
        for doc in self.corpus:
            if doc == "":
                self.corpus.remove(doc)
                n_empty += 1
        if verbose: 
            print("Removed " + str(n_empty) + " empty documents.")

        if verbose:
                print("Computing vocabulary...")
        if self.vocab_embeddings is None:
            self.vocab = self.extractor.compute_corpus_vocab(self.corpus, **self.compute_vocab_hyperparams)
        else:
            self.vocab = list(self.vocab_embeddings.keys())

        if self.vocab_embeddings is None or self.document_embeddings is None:  
            if verbose:
                print("Computing embeddings...")
            self.compute_embeddings(corpus = self.corpus)
        
        if verbose: 
            print("Extracting topics...")
        self.topic_lis = self.extract_topics(corpus = self.corpus)

        if verbose:
            print("Describing topics...")
        self.topic_lis = self.describe_topics(topics = self.topic_lis)

        self.topic_prompting.topic_lis = self.topic_lis
        self.topic_prompting.vocab_embeddings = self.vocab_embeddings
        self.topic_prompting.vocab = self.vocab

    def visualize_clusters(self):
        """
        This function visualizes the identified clusters that constitute the topics in a Scatterplot.
        """

        assert self.topic_lis is not None, "You need to extract the topics first."

        all_document_embeddings = np.concatenate([topic.document_embeddings_hd for topic in self.topic_lis], axis = 0)
        all_texts = np.concatenate([topic.documents for topic in self.topic_lis], axis = 0)
        all_document_indices = np.concatenate([np.repeat(i, topic.document_embeddings_hd.shape[0]) for i, topic in enumerate(self.topic_lis)], axis = 0)
        class_names = [str(topic) for topic in self.topic_lis]

        self.clusterer.visualize_clusters_dynamic(all_document_embeddings, all_document_indices, all_texts, class_names)
    
    def repr_topics(self) -> str:
        """
        This function returns a string explaining the topics.
        """
        assert self.topic_lis is not None, "You need to extract the topics first."

        if "cosine_similarity" in self.topword_extraction_methods:
            topword_method = "cosine_similarity"
        elif "tfidf" in self.topword_extraction_methods:
            topword_method = "tfidf"
        else:
            raise ValueError("You need to use either 'cosine_similarity' or 'tfidf' as topword extraction method.")

        repr = ""
        for topic in self.topic_lis:
            repr += str(topic) + "\n"
            repr += "Topic_description: " + topic.topic_description + "\n"
            repr += "Top words: " + str(topic.top_words[topword_method][:10]) + "\n"
            repr += "\n"
            repr += "-"*150 + "\n"

        return repr

    def print_topics(self):
        """
        This function prints the string explaining the topics.
        """   
        print(self.repr_topics())

    def prompt(self, query: str) -> (str, object):
        """
        This function prompts the model with the query. Please Have a look at the TopicPrompting class for more details on available functions for prompting the model.
        params:
            query: The query to prompt the model with.
        return:
            answer: The answer from the model.
            function_result: The result of the function call.
        """

        result = self.topic_prompting.general_prompt(query)

        answer = result[0][-1]["choices"][0]["message"]["content"]
        function_result = result[1]
        self.topic_prompting._fix_dictionary_topwords()
        self.topic_lis = self.topic_prompting.topic_lis

        return answer, function_result
    
    def pprompt(self, query:str, return_function_result: bool = True) -> object:
        """
        This function prompts the model with the query and prints the answer.
        params:
            query: The query to prompt the model with.
            return_function_result: Whether to return the result of the function call by the LLM.
        return:
            function_result: The result of the function call.    
        """

        answer, function_result = self.prompt(query)

        print(answer)

        if return_function_result:
            return function_result
        
    def save_embeddings(self, path = embeddings_path) -> None:
        """
        This function saves the document and vocabulary embeddings to a pickle file. For later re-use
        params:
            path: path to save the embeddings to.
        """

        assert self.document_embeddings is not None and self.vocab_embeddings is not None, "You need to compute the embeddings first."

        # create dictionary if it doesn't exist yet 
        if not os.path.exists("SavedEmbeddings"):
            os.makedirs("SavedEmbeddings")


        with open(path, "wb") as f:
            pickle.dump([self.document_embeddings, self.vocab_embeddings], f)


    # TODO: Change functions to not reduce vocab again