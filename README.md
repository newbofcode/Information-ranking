READ ME
This assignment was done on Jupyter Notebook in VSCode with the python coding language.
How to Run:
1. Either "Run All" or run each code cell in Jupyter or just run the .py program
2. When def main()  is run it will run invert() function which will ask user to enter if they want to activate stopword removal or stemming
3. Wait a moment until user is prompted to enter a query
4. End query by entering zzend
5. While the program is running you can check the top 10 documents and its score in the file called topK.txt ranked 
6. you will be asked if you want to run the eval() function to evaluate performance of this IR system
7. Wait about 2 min depending on the computer and an output of MAP and RPrecision will be shown

General Details
1. The posting lists is ordered by documentID
2. weight is calculated by the standard method of TF = 1 + log(f) where f is frequency of word in document, IDF = log(N/df) where N is total number of documents and df is document frequency of a term. This is applied for both query and documents.
3. Normalization of weight and then cosin Similarity is calculated.
4. The top-K retreival method used is the the "Index Elimination" method where the threshold for the IDF of each term in user query must be higher than 0.6.
5. Only the top 10 documents will be shown and ranked
