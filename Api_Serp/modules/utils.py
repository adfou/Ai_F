### Project utils ###
"""A set of helper functions to be used through the project"""

## Import modules ##

# General package
import re
import pandas as pd
import contractions
from pickle import dump, load
from .translator import translate_to_arabic, translate_to_english
import os

# NLTK and Transformers packages
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
import transformers
from transformers import BertTokenizer, TFBertForSequenceClassification
data_folder = os.path.join(os.path.dirname(__file__), "data")

# Add the "data" folder to the nltk.data.path variable
nltk.data.path.append(data_folder)
    #nltk.download('punkt')
    #nltk.download('stopwords')
    #nltk.download('wordnet')
    #nltk.download('omw-1.4')


### Data preprocssing ###
"""Functions help on data preprocessing"""

# Lemmatization
def Lemmatizer_stop_word(sentence):
    """Function to lemmatize the data"""
    stop_words = set(stopwords.words('english'))
    lemmatizer = WordNetLemmatizer() #look at other Lemmatizers and stemmers
    sentence = re.sub('[^A-z]', ' ', sentence)
    negative = ['not', 'neither', 'nor', 'but', 'however',
                'although', 'nonetheless', 'despite', 'except',
                        'even though', 'yet']
    stop_words = [z for z in stop_words if z not in negative]
    preprocessed_tokens = [lemmatizer.lemmatize(contractions.fix(temp.lower())) for temp in sentence.split() if temp not in stop_words] #lemmatization
    return ' '.join([x for x in preprocessed_tokens]).strip()

# Stop word removal
def remove_stopwords(phrase):
    """Function to remove stopwords"""
    stop_words = stopwords.words('english')
    words = word_tokenize(phrase)
    # Stopwords removing
    stripped_phrase = []
    for word in words:
        if word.lower() not in stop_words:
            stripped_phrase.append(word)
            
    return ' '.join(stripped_phrase)

# Data preprocess
def data_preprocess(dataset_path):
    """Function to process the dataset"""
    
    # Load the dataset
    train = pd.read_csv(f'{dataset_path}/train.txt', names=['sentences', 'feelings'], sep=';')
    val = pd.read_csv(f'{dataset_path}/val.txt', names=['sentences', 'feelings'], sep=';')
    test = pd.read_csv(f'{dataset_path}/test.txt', names=['sentences', 'feelings'], sep=';')
    
    # Apply lemmatization
    train['sentences'] = train['sentences'].apply(lambda x: Lemmatizer_stop_word(x))
    val['sentences'] = val['sentences'].apply(lambda x: Lemmatizer_stop_word(x))
    test['sentences'] = test['sentences'].apply(lambda x: Lemmatizer_stop_word(x))
    
    # Apply tokenization
    tokenizer = AutoTokenizer.from_pretrained('bert-base-cased')
    max_length = 43
    x_train = tokenizer(
        [x.split() for x in train['sentences']],
        add_special_tokens=True,
        max_length=max_length,
        truncation=True,
        padding=True, 
        return_tensors='tf',
        return_token_type_ids = False,
        return_attention_mask = True,
        is_split_into_words=True,
        verbose = True)

    # Tokenizing validation set
    x_val = tokenizer(
        [x.split() for x in val['sentences']],
        add_special_tokens=True,
        max_length=max_length,
        truncation=True,
        padding=True, 
        return_tensors='tf',
        return_token_type_ids = False,
        return_attention_mask = True,
        is_split_into_words=True,
        verbose = True)

    # Apply enconding
    lb = LabelEncoder()
    labels_train = lb.fit(train.loc[:,'feelings'].to_list())
    labels_train = lb.transform(train.loc[:,'feelings'].to_list())
    labels_val = lb.transform(val.loc[:,'feelings'].to_list())
    labels_test = lb.transform(test.loc[:,'feelings'].to_list())
    
    # Return tha processed data
    return x_train, x_val, labels_train, labels_test, labels_val

##############################################################

### Model Building ###
"""Functions help on model building"""

# Build the model
def build_model(x_train, labels_train, x_val, labels_val):
    
    # Model creation
    tf.random.set_seed(79)
    input_ids = Input(shape=(max_length,), dtype=tf.int32, name="input_ids")
    input_mask = Input(shape=(max_length,), dtype=tf.int32, name="attention_mask")
    embeddings = bert(input_ids, attention_mask = input_mask)[0]
    x = tf.keras.layers.GlobalMaxPool1D()(embeddings)
    x = Dense(138, activation='elu',kernel_initializer='GlorotNormal')(x)
    x = tf.keras.layers.Dropout(0.1)(x)
    x = Dense(28,activation = 'elu',kernel_initializer='GlorotNormal')(x)
    output = Dense(6,activation = 'softmax')(x)
    model = tf.keras.Model(inputs=[input_ids, input_mask], outputs=output)
    model.layers[2].trainable = True

    # Model compiling
    opt = Adam(
        learning_rate=5e-05, # works well with BERTs
        epsilon=1e-08,
        decay=0.01,
        clipnorm=1.0)
    model.compile(optimizer=opt, loss='sparse_categorical_crossentropy', metrics=['accuracy']) 

    # Model fitting
    early_stopping_cb=keras.callbacks.EarlyStopping(patience=2,restore_best_weights=True)
    history = model.fit(
        x ={'input_ids':x_train['input_ids'],'attention_mask':x_train['attention_mask']} ,
        y =labels_train,
        validation_data = (
        {'input_ids':x_val['input_ids'],'attention_mask':x_val['attention_mask']}, labels_val
        ),
    epochs=3,
        batch_size=12,callbacks=[early_stopping_cb]
    )

    # Model saving
    #model.save_weights('models/BERT.h5')
    
# Model loading
def load_model(model_path):
    """Function used to load the model"""
    max_length = 43
    bert = TFBertModel.from_pretrained('bert-base-cased')
    input_ids = Input(shape=(max_length,), dtype=tf.int32, name="input_ids")
    input_mask = Input(shape=(max_length,), dtype=tf.int32, name="attention_mask")
    embeddings = bert(input_ids,attention_mask = input_mask)[0] #(0 is the last hidden states,1 is the pooler_output)
    x = tf.keras.layers.GlobalMaxPool1D()(embeddings)
    x = Dense(138, activation='elu',kernel_initializer='GlorotNormal')(x)
    x = tf.keras.layers.Dropout(0.1)(x)
    x = Dense(28,activation = 'elu',kernel_initializer='GlorotNormal')(x)
    output = Dense(6,activation = 'softmax')(x)
    model_saved = tf.keras.Model(inputs=[input_ids, input_mask], outputs=output)
    model_saved.layers[2].trainable = True
    model_saved.load_weights(model_path)
    
    # Return the model
    return model_saved
         
# Prediction making
def make_prediction(arabic_sentence, model_path, label_encoder_path):
    """Function to make predictions"""
    
    # Load model and label encode
    model_saved = load_model(model_path)
    lb = load(open(label_encoder_path, 'rb'))
    
    # Prepare the arabic sentence
    max_length = 43
    tokenizer = AutoTokenizer.from_pretrained('bert-base-cased')
    y_ar = arabic_sentence
    y_en = translate_to_english(y_ar)
    y_s = pd.Series([y_en])
    y_lemm = y_s.apply(lambda x: Lemmatizer_stop_word(x))
    y_tok = tokenizer(
        [x.split() for x in y_lemm],
        add_special_tokens=True,
        max_length=max_length,
        truncation=True,
        padding='max_length',  
        return_tensors='tf',
        return_token_type_ids = False,
        return_attention_mask = True,
        is_split_into_words=True,
        verbose = True)
    
    # Make predictions
    y_pred = model_saved.predict({'input_ids':y_tok['input_ids'],'attention_mask':y_tok['attention_mask']})*100
    class_label = y_pred.argmax(axis=-1)
    class_op_en = lb.inverse_transform(class_label)[0]
    class_op_ar = translate_to_arabic(class_op_en)

    # Return the result
    return y_ar, y_en, class_op_ar, class_op_en

##############################################################



