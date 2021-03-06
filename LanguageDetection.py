# -*- coding: utf-8 -*-
"""Copy of Machine_Learning_Proj.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1mBGZRhDZuEBvF4aT4ut5QKxflaB7wk9p

#Setup

Import pandas and set up gdrive path
"""

import pandas as pd
from google.colab import drive
drive.mount('/content/gdrive')

"""Read the labels csv, which translates three letter codes to actual languages"""

labels = pd.read_csv('/content/gdrive/My Drive/Datasets/wili-2018/labels.csv')

"""Break each txt file into lists by newline"""

file1 = open('/content/gdrive/My Drive/Datasets/wili-2018/x_train.txt')
text = file1.readlines()
file2 = open('/content/gdrive/My Drive/Datasets/wili-2018/y_train.txt')
langs = file2.readlines()

"""Consolidate lists into a dataframe"""

df = pd.DataFrame(list(zip(langs, text)), columns =['Languages', 'Text'])

"""Trim the \n off the end of each entry"""

df['Languages'] = df['Languages'].str[:-1]
df['Text'] = df['Text'].str[:-1]

"""#EDA + Data Cleaning + Feature Engineering"""

df.head()

"""This dataset contains 117500 unique texts and 235 unique languages."""

print("Shape: ", df.shape)
print("Languages: ", len(df.Languages.unique()))

"""Define a function to remove numbers and punctuation from all text

*original code*:
```
def clean_numbers(s):
    removedNums=0 #removedNums tracks how many numbers have been removed; otherwise the function would attempt to call indices which have been removed due to shortening
    #iterate through every item in the passed string
    for c in range(len(s)):
      #If its a digit, remove it     
      if s[c-removedNums].isdigit() or s[c-removedNums] in string.punctuation:
        s=s[:c-removedNums]+s[c+1-removedNums:]
        removedNums+=1

    return s
```
"""

import string

def clean_text_simple(s):
  s = ''.join([i.lower() for i in s if not i.isdigit() and not i in string.punctuation])
  return s

"""Maps the clean function to the Text column and removes numbers and punctuation from all text"""

df.Text = df.Text.map(clean_text_simple)

"""Adds the Length feature to the dataset which contains the number of characters in the corresponding string of Text"""

df["Length"]=df["Text"].str.len()

"""Plots a boxplot that shows that there are many outliers in the Length column"""

import seaborn as sns
sns.boxplot(x=df['Length'])

"""Uses the describe() function to find the maximum length of a text: 40532 characters"""

df['Length'].describe()

"""Calculates the IQR of the data to help us find the distribution of the data and identify outliers"""

Q1 = df.quantile(0.25)
Q3 = df.quantile(0.75)
IQR = Q3 - Q1
print(IQR)

"""Uses the IQR to eliminate outliers with the following code, resets the dataframe index, and checks the shape of our new dataframe to see that we eliminated 117500 - 110084 = 7416 outliers"""

df_out = df[~((df < (Q1 - 1.5 * IQR)) |(df > (Q3 + 1.5 * IQR))).any(axis=1)]
df_out.index=range(len(df_out))
df_out

"""Checks the boxplot of df_out so it is safe to say the outliers have been removed"""

sns.boxplot(x=df_out['Length'])

"""Assigns df_out to df and plots a histogram of the Length column"""

df = df_out.copy()
df['Length'].hist()

"""Adds the Accents feature to the dataset which classifies texts into containing characters with accents or not"""

def has_accents(s):
    return not all(ord(c) < 128 for c in s)

df["Accents"] = df['Text'].map(has_accents)
df.head()

"""Locates the texts in English and shows that there are no accents"""

df.loc[df['Languages'] == 'eng']

"""Makes sure that by eliminating outliers, we did not eliminate too many texts from one language and that the training data contains enough texts from each language"""

df.Languages.hist()

"""# Feature Engineering Cont. - Character Frequencies

Cuts  down the dataset by ~1/2 to reduce resource use and computing time
"""

langList = df.Languages.unique()
df_small = pd.DataFrame(columns=df.columns)

for l in langList:  
  df_small = pd.concat([df_small, df.loc[df["Languages"] == l].sample(250)], ignore_index=True)

df = df_small
df = df.sample(frac=1).reset_index(drop=True)
df

"""Goal: define a function to add the character frequencies columns

*original code*:

```
#countChars counts the occurences of each character in a text sample, then stores the count in columns organized by character
#optionally, ints may be passed as the start and finish of rows to be tested on

def countChars(start=0,end=len(df)):
  skipped=0
  for i in range(start,end):
    currentIndex=i-skipped
    if i%100==0:
      print ("passing row "+ str(i)+", which has index "+str(df.index[i]))
    try:
      df.at[currentIndex,"Languages"]
    except:
      skipped+=1
      continue
    for c in df.at[i,"Text"]:
      c = str.lower(c)
      if not ("char: "+c) in df.columns:
        df["char: " + c]=0
        #print ("made column "+c)
      df.at[i,("char: "+c)]+=1
```

*original code for batch execution*:
```
for i in range(1, len(df) // 1000):
  df_temp = df.head(10000)
  df_temp = df_temp.join(pd.json_normalize(df_temp['Frequencies']))
  df_
countChars((len(df) // 1000) * 1000, len(df))
df
```

1. Make a single feature column, Frequencies, containing dictionaries of the texts' characters and character counts
"""

def charFrequencies(s):
  d = {}
  for i in s:
    if (i not in d.keys()):
      d[i] = 1
    else:
      d[i] += 1
 
  return d

df["Frequencies"] = df['Text'].map(charFrequencies)

"""2. Use the pandas json_normalize function on the 'Frequencies' column (this process takes around 1 minute, 48 seconds)

*another way of doing it (slower):
df_test = pd.concat([df_test.drop(['Frequencies'], axis=1), df_test['Frequencies'].apply(pd.Series)], axis=1)*
"""

df = df.join(pd.json_normalize(df['Frequencies']))
df = df.fillna(0)
df

"""Creates a function that returns dictionary mapping the characters to their variances"""

def frequency_dict():
  d = {}
  count = 0
  # starts at index 6 to correspond with the column in df
  for i in range(6,len(df.columns)):
    character = df.columns[i]
    d[character] = df[character].var()
  return d

variances = frequency_dict().values()

"""Shows a boxplot of the range and clustering of the variances"""

import matplotlib.pyplot as plt

plt.boxplot(variances)
plt.show()

"""Uses the numpy library to count how many character variances are less than the median of the character variances"""

l = []
for i in variances:
  l.append(i)

import numpy as np

count = 0
m = np.median(l)
for i in l:
  if (i < m):
    count += 1

count

"""Removes the columns that have variances lower than the median"""

remove = []
d = frequency_dict()
for i in d.keys():
  if d[i] < m:
    remove.append(i)

df = df.drop(remove, axis = 1)

"""Plots a histogram of non-zero cells per row to show that the majority have an average of ~0-50 non-zero cells."""

df_test_chars = df.iloc[:, 5:]
(df_test_chars != 0).astype(int).sum(axis=1).hist()

"""# How do you expect these new features to relate to your outcome variable?

### Feature 1: The length of the text
We can use the length of the text to find out the character frequencies in terms of a percentage. We can use the percentage value because a piece of text with a high percentage of a certain character can be classified based on what language that character is most used in/belongs to. 

### Feature 2: Whether or not the text includes accented characters
Identifying which text has an accent will relate to the outcome variable by helping to identify a language quicker because certain languages have unique accents that will make them automatically identifiable. This will also give the code more specific data to work with because accents are used as more particular characters.

### Feature 3: Character frequencies of each text
Different languages have varied character frequencies.

# Prediction Models + Evaluation of Model + Visualization of Results

Removes the last 1/5 of the dataset and saves that set as a test set
"""

df_testset = df.truncate(after=len(df) - len(df) // 5)

"""Removes character columns which aren't being used much to reduce size for computational purposes"""

def get_charlist():
  char_dict = {}
  names = []

  new_names = []

  count = 0
  avg = 0

  for i in range(5,len(df.columns)-2):
    name = df.columns[i]
    count = df[name].sum()
    avg += count
    char_dict[name] = count
    names.append(name)

  avg /= (len(df.columns)-2) - 4

  for i in range(0,len(char_dict)):
    if(char_dict[names[i]]>=avg):
      new_names.append(names[i])

  outernames = new_names
  return outernames

"""Calculates the number of language groups for K-Means classification purposes"""

import csv

def get_language_family_list():
  language_family = []

  with open('/content/gdrive/My Drive/Datasets/wili-2018/labels.csv') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=';')
    for row in csv_reader:
      idx = 0
      if(row[5] != 'Language family'):

        try:
          idx = language_family.index(row[5])
        except ValueError:
          idx = -1

        if(idx==-1):
          language_family.append(row[5]);

  return language_family

import csv

def get_language_in_category(lang_fam):
  langs = []
  with open('/content/gdrive/My Drive/Datasets/wili-2018/labels.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=';')
        for row in csv_reader:
          if(row[5] == lang_fam):
              langs.append(row[0])
  return langs


def get_language_family_list_dict():
  language_family = {}

  with open('/content/gdrive/My Drive/Datasets/wili-2018/labels.csv') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=';')
    for row in csv_reader:
      idx = 0
      if(row[5] != 'Language family'):
        if(row[5] not in language_family):
          language_family[row[5]] = get_language_in_category(row[5]);

  return language_family

languages_in_family=get_language_family_list_dict()
print(get_language_family_list_dict())

from sklearn.utils import shuffle
df = shuffle(df)

"""### Linear Regression"""

from sklearn.linear_model import LinearRegression

LR=LinearRegression()

column_chars = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z',' ']

X = df[column_chars]
y = df[['d']]
 
LR.fit(X, y)
 
df['predictionLR'] = LR.predict(X)
df.head()

from sklearn.metrics import mean_squared_error
import numpy as np

np.sqrt(mean_squared_error(df['d'], df['predictionLR']))

from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
 
print(accuracy_score(df['d'],df['predictionLR'].round()))
print(recall_score(df['d'],df['predictionLR'].round(),average='macro'))
print(f1_score(df['d'],df['predictionLR'].round(),average='macro'))

"""### KNN"""

from sklearn.neighbors import KNeighborsClassifier

n_neighbors = len(get_language_family_list())
KNN = KNeighborsClassifier(n_neighbors)
 
X = df[get_charlist()]
y = df['Languages']

KNN.fit(X, y)

df["predictionKNN"] = KNN.predict(X)
df.head()

from sklearn.model_selection import KFold
from sklearn.model_selection import cross_val_score

cv = KFold(n_splits=n_neighbors, shuffle=False)

scores = cross_val_score(KNN, X, y, cv=n_neighbors, scoring = 'f1_macro')
print(np.mean(scores))

from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
 
print(accuracy_score(df['Languages'],df['predictionKNN']))
print(recall_score(df['Languages'],df['predictionKNN'],average='macro'))
print(f1_score(df['Languages'],df['predictionKNN'],average='macro'))

"""Compute accuracies per language"""

# def get_accuracy(condition):
#   df_l = df_test0[df_test0['Languages'] == condition]
#   a = accuracy_score(df_l['Languages'], df_l['predictionKNN'])
#   return a

# df_test0['Accuracy'] = df_test0['Languages'].apply(get_accuracy)

# df_test0.head()

# language_accuracy_dict = pd.Series(df_test0.Accuracy.values,index=df_test0.Languages).to_dict()

from sklearn.metrics import accuracy_score
language_accuracy_dict = {lang : accuracy_score(df_test0[df_test0['Languages'] == lang]['Languages'], df_test0[df_test0['Languages'] == lang]['predictionKNN']) for lang in langList}

"""Compute accuracies per language category"""

from statistics import mean 
familyAccuracies={}
for l in languages_in_family:
  familyAccuracies[l]=mean(list(
      language_accuracy_dict[lang] for lang in languages_in_family[l])) #mean of list of accuracies of languages in family
familyAccuracies

l = []
for k in language_accuracy_dict.keys():
  if (language_accuracy_dict[k] <= 0.5):
    l.append(k)

print(l)

from statistics import mean 
print(mean(language_accuracy_dict.values()))

"""### KMeans"""

from sklearn.cluster import KMeans
 
X = df[get_charlist()]
print(X)

languages =  get_language_family_list()
clusters = len(languages)

kmeans = KMeans(n_clusters = clusters)

df['predictionKMeans'] = kmeans.fit_predict(X,languages)
df.head()

df.loc[df['Languages'] == 'bar']

df_test0 = df[['Languages', 'predictionKMeans']]
df_test0

df['predictionKMeans'].value_counts()

pd.crosstab(df.predictionKMeans, df.Languages).apply(lambda r: r/r.sum(), axis=1).plot.bar(stacked=True)

"""### Decision Tree"""

from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split

decisionTree = DecisionTreeClassifier(criterion="gini", splitter='best')

X = df[get_charlist()]
y = df['Languages']

decisionTree.fit(X, y)

df['predictionDecisionTree'] = decisionTree.predict(X)
df.head()

from sklearn.model_selection import KFold
from sklearn.model_selection import cross_val_score

cv = KFold(n_splits=23, shuffle=False)

scores = cross_val_score(decisionTree, X, y, cv=23, scoring = 'f1_macro')
print(np.mean(scores))

from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
 
print(accuracy_score(df['Languages'],df['predictionDecisionTree']))
print(recall_score(df['Languages'],df['predictionDecisionTree'],average='macro'))
print(f1_score(df['Languages'],df['predictionDecisionTree'],average='macro'))

"""### Random Forest"""

from sklearn.ensemble import RandomForestClassifier

randomForest = RandomForestClassifier(n_estimators=23)

X = df[get_charlist()]
y = df['Languages']

randomForest.fit(X, y)

df['predictionRandomForest'] = randomForest.predict(X)
df.head()

from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
 
print(accuracy_score(df['Languages'],df['predictionRandomForest']))
print(recall_score(df['Languages'],df['predictionRandomForest'],average='macro'))
print(f1_score(df['Languages'],df['predictionRandomForest'],average='macro'))