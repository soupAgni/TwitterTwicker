from tweet_to_file import *
import json
import math
import string
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import style
style.use("ggplot")
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity
try:
    import json
except ImportError:
    import simplejson as json
from twitter import Twitter, OAuth, TwitterHTTPError, TwitterStream
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.tokenize import RegexpTokenizer
import string, re

idf = {}                    #idf value of each unique word from all tweets
arr_tf = None               #tf value of each word in each tweet
tfidf = None                #tfidf of each word in each tweet
documents_per_word_count={} #No of documents that word appears in.

words_set = None            #dictionary of words
index_word = None           #indexing the words in dictionary
zerosOnEveryRecipe = None   #initial vector matrix

kmeans = None               #This variable does not change for test data

total = None
total_tweets = None         #Total number of tweets in training set
tweets = None

new_tweet = None            #Contains new tweet
data_dict = None            #Json object containing new tweet
new_tfidf = {}              #TFIDF for each word in new tweet


users = []                 #Array of all the screen names
classified_tweets =[]
similar_tweets = {}
tweets_in_clusters = {}

tokenizer = RegexpTokenizer(r'\w+')


def initvar():
    global tfidf, words_set, total, arr_tf, index_word
    tfidf = [{}]
    words_set = {}
    total = 0
    arr_tf = []
    index_word = {}

def load_data_from_file():
    #print "load_data()"
    #getTrainingSet()
    global tweets
    tweets = json.load(open('data.json'))['tweetno']

def load_data_from_json():
    # Variables that contains the user credentials to access Twitter API
    ACCESS_TOKEN = '927683752532365313-tBAFC5zBzRpG7PcF8K9Hq9fPltGLyhe'
    ACCESS_SECRET = '4fHIQYa3CMOAJJqt4HqjQamVoJu4LvZWha3x8KczLCb1x'
    CONSUMER_KEY = 'pIboRFJU8EN17UVyis1qCuOtS'
    CONSUMER_SECRET = '52XINB2kmqBPdlNv1WCHreoJI9vpmBtyfqywBnSFUQnbrMUmFO'

    oauth = OAuth(ACCESS_TOKEN, ACCESS_SECRET, CONSUMER_KEY, CONSUMER_SECRET)

    # Initiate the connection to Twitter Streaming API
    twitter_api = Twitter(auth=oauth)

    # Get a sample of the public data following through Twitter
    iterator = twitter_api.statuses.user_timeline(count =1, screen_name='tanmaygore_03')

    global data_dict
    tweet_count = 1
    data_dict = {}
    data_dict["tweetno"] = []

    for tweet in iterator:
        if tweet.get("text") is None:
            #print "skipped a tweet"
            continue

        tweet_count -= 1
        data_dict["tweetno"].append(tweet)

        if tweet_count <= 0:
            break

    global new_tweets
    new_tweets = data_dict['tweetno']

def get_tweets():
    #print "get_tweets()"

    global tweets, word_set, arr_tf, tfidf, total_tweets, users, tokenizer


    stop_words = set(stopwords.words('english'))
    i = 0
    for item in tweets:
        #print item.get("text")

        user = item.get('user').get('screen_name')
        users.append(user);

        #tweet =  item.get('text').split(' ')
        newtweet = re.sub(r"http\S+", "",item.get('text') )
        tweet = tokenizer.tokenize(newtweet)

        #tweet.split(" ")
        #print tweet
        filteredTweet = ' '
        for word in tweet:
            #print word
            #filteredTweet = []
            #for t in tweet:
                #print t
            if(not word in stop_words):
                #print word
                filteredTweet += word
                filteredTweet += ' '
                #filteredTweet.append(word)
        #print filteredTweet
        #tweets[i] = ''.join(filteredTweet)

        tweets[i] = (filteredTweet)
        i = i+1
    # for u in users:
    #         print u

    for item in tweets:
        #sentence = item.get("text").split()
        sentence = item.split(' ')
        term_frequency = {}
        tweet_length = 0
        for word in sentence:
            if not word.startswith('http'):
                if word in words_set:
                    words_set[word] += 1.0
                else:
                    words_set[word] = 1.0
                tweet_length+=1.0
                if word in term_frequency:
                    term_frequency[word] += 1.0
                else:
                    term_frequency[word] = 1.0
        for k,v in term_frequency.items():
            term_frequency[k] = v/tweet_length
        arr_tf.append(term_frequency)

    total_tweets = len(arr_tf)


    global idf
    for word in words_set:
        doc_word_freq = 0
        for item in arr_tf:
            if word in item:
                doc_word_freq += 1
            #print doc_word_freq
        idf[word] = math.log(total_tweets/doc_word_freq)
        documents_per_word_count[word] = doc_word_freq


	#tfidf = []
    for item in arr_tf:
        temp_tfidf = {}
        for k, v in item.items():
            idf_val = idf[k]
            temp_tfidf[k] = idf[k]*v
            tfidf.append(temp_tfidf)

    #print "tfidf obtained"

	#print tfidf
	#for i in tfidf:
		#for k,v in i.items():
			#print k, v


##get_tweets()



def AllWord():
    global tfidf, word_set, index_word
    #print "AllWord()"
    tf_vecs = tfidf
    #print tf_vecs
    everyWord = []
    alldicts = []

    #print words_set
    #getting a list of words.
    for k,v in words_set.items():
        #alldicts.append(dicts)
        everyWord.append(k)

    #print len(everyWord)

    i = 0
    for word in everyWord:
        index_word[word] = i
        i = i+1

##AllWord()

##zerosOnEveryRecipe = np.zeros([len(tfidf),len(index_word)])
def addingToZerosArr():
    global tfidf, index_word, arr_tf, zerosOnEveryRecipe, total_tweets
    #print "addingToZerosArr()"
    i = 0;
    ind = 0;

    zerosOnEveryRecipe = np.zeros([total_tweets,len(index_word)])
    #print zerosOnEveryTweet

    v = True;

    for tw in arr_tf:
        for word, val in tw.items():
            index = index_word[word]
            zerosOnEveryRecipe[i][index] = arr_tf[i][word]

        i = i + 1

    #print len(zerosOnEveryRecipe[1])


##addingToZerosArr()

def KmeansAnalysis():
    #print "KmeansAnalysis()"

    global zerosOnEveryRecipe, kmeans, classified_tweets, similar_tweets,tweets_in_clusters, words_set
    arrayOfInterest = np.array(zerosOnEveryRecipe)

    count = 0
    kmeans = KMeans(n_clusters = 7, n_init = 10) #make ten clusters
    #while(count < 100):
    kmeans.fit(arrayOfInterest)  #fit the data - learning
    centroids = kmeans.cluster_centers_  #grab the centroids
    labels = kmeans.labels_  # and the labels
    classified_tweets = labels.tolist()
    print labels.tolist()
    # for item in classified_tweets:
    #     print item
    tweet = 0


    for item in classified_tweets:
        if item not in similar_tweets:
            similar_tweets[item] = set()
        for words in arr_tf[tweet]:
            similar_tweets[item].add(words)
        tweet += 1



    for k,v in similar_tweets.items():
        print k
        for i in v:
            print i

    count = count + 1
    print "Prediction Model Generated\n"


##KmeansAnalysis()





#**********************************************************************#

def train():
    #Start of Program
    print "Hi there. Please wait while we generate the prediction model\n"
    #getTrainingSet()
    initvar()
    load_data_from_file()
    get_tweets()

    AllWord()
    addingToZerosArr()
    KmeansAnalysis()
    global kmeans
    return kmeans

def test():
    print "\n\n*****************************************************************\n"
    while True:
        print
        inputstr=raw_input("Please press 'Enter' for next iterations or type 'exit' to end. \n")
        if inputstr.startswith("exit"):
            break
        global new_tweet, idf, words_set, new_tfidf, total_tweets, index_word, documents_per_word_count, zerosOnEveryRecipe
        global tokenizer
        
        user_name = None

        #Get a single tweet
        load_data_from_json()

        #obtain the tf values for this tweet
        for item in new_tweets:
            newtweet = re.sub(r"http\S+", "",item.get('text'))
            sentence = tokenizer.tokenize(newtweet)
            #sentence = item.get("text").split()
            print "Hi", item.get("user").get("screen_name")+ ". Lets find some new users for you to follow."
            print "Post something on Twitter"
            print "Your New Tweet: ", item.get("text")
            term_frequency = {}
            new_tfidf={}
            tweet_length = 0
            for word in sentence:
                if word.startswith('http'):
                    continue
                tweet_length+=1.0
                if word not in words_set:
                    continue
                elif word in term_frequency:
                    term_frequency[word] += 1.0
                else:
                    term_frequency[word] = 1.0

                #for each word in sentence, get the the previous idf value for that word.
                new_tfidf[word] = documents_per_word_count[word] +1

            for k,v in term_frequency.items():
                term_frequency[k] = v/tweet_length                      #get the tf
                new_tfidf[k] = math.log(total_tweets+1 / new_tfidf[k])    #get the idf
                new_tfidf[k] = term_frequency[k] * new_tfidf[k]         #get the tfidf

            #print new_tfidf


        #Compute the vector matrix
        #print len(index_word)
        vector_matrix = np.zeros([1, len(index_word)]) #initialize elements in vector matrix to 0
        nC =np.ndarray(shape=(1, len(index_word)), dtype = float)
        for word in new_tfidf:
            if word in index_word:
                index = index_word[word]
                vector_matrix[0][index] = new_tfidf[word]
                nC[0][index] = new_tfidf[word]
        #print vector_matrix.tolist()

        #print "tfidf obtained"


        #predict the label of new tweet
        global kmeans, users, similar_tweets, tweets_in_clusters
        label = kmeans.predict(vector_matrix)

        print "The new tweet is classified to cluster:", label
        to_follow = []              # the users we are suggesting to follow
        set_union = {}
        #recommending users to follow other users
        i = 0
        for item in classified_tweets:
            if label == item:
                to_follow.append(users[i])
            i += 1
        

        ############ number of tweets in every cluster ##############
        for item in classified_tweets:
            if item not in tweets_in_clusters:
                tweets_in_clusters[item] = 1
            else:
                tweets_in_clusters[item] += 1



        print "Users that you can follow:"
        i=0
        for user in to_follow:
            if i <=10:
                print to_follow[i]
            i += 1

        jac_sim = []
        i = 0
        sim = 0.0
        intersection=0
        for k,v in similar_tweets.items():
            for k1,v1 in new_tfidf.items():
                if k1 in v:
                    intersection+=1
            print "intersection: ",intersection, "union: ", len(v)
            sim =  float(intersection)/len(v)
            jac_sim.append(sim)
            
        ################### COSINE SIMILARITY ###################
        i0 , i1, i2, i3, i4, i5, i6 = 0,0,0,0,0,0,0

        print len(index_word)
        c0 =np.ndarray(shape=(tweets_in_clusters[0], len(index_word)), dtype = float)
        c1 =np.ndarray(shape=(tweets_in_clusters[1], len(index_word)), dtype = float)
        c2 =np.ndarray(shape=(tweets_in_clusters[2], len(index_word)), dtype = float)
        c3 =np.ndarray(shape=(tweets_in_clusters[3], len(index_word)), dtype = float)
        c4 =np.ndarray(shape=(tweets_in_clusters[4], len(index_word)), dtype = float)
        c5 =np.ndarray(shape=(tweets_in_clusters[5], len(index_word)), dtype = float)
        c6 =np.ndarray(shape=(tweets_in_clusters[6], len(index_word)), dtype = float)
        

        index =0
        print len(zerosOnEveryRecipe[index])
        for item in classified_tweets:
            if item == 0:
                c0[i0] = zerosOnEveryRecipe[index]
                i0 +=1
            elif item == 1:
                c1[i1] = zerosOnEveryRecipe[index]
                i1 +=1 
            elif item == 2:
                c1[i2] = zerosOnEveryRecipe[index]
                i2 +=1
            elif item == 3:
                c1[i3] = zerosOnEveryRecipe[index]
                i3 +=1
            elif item == 4:
                c1[i4] = zerosOnEveryRecipe[index]
                i4 +=1
            elif item == 5:
                c1[i5] = zerosOnEveryRecipe[index]
                i5 +=1
            elif item == 6:
                c1[i6] = zerosOnEveryRecipe[index]
                i6 +=1
            index += 1

        
        cos_sim = cosine_similarity(c0, nC)
        print "cos sim", cos_sim


        # for k,v in similar_tweets.items():
        #     sim = float(len(new_tfidf))/len(v)
        #     print "len of tfif", len(new_tfidf), " and len of v", len(v)
        #     jac_sim.append(sim)
        #     i += 1

        for i in jac_sim:
            print i
       
        #Use this to recommend new users
        # Add the user recommendation code here.



train()
test()
