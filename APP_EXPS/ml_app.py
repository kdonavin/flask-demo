# Here we train and pickle a logistic regression model on the iris dataset
# Based on:
# https://scikit-learn.org/stable/auto_examples/linear_model/plot_logistic_multinomial.html

from flask import Flask, request
import matplotlib.pyplot as plt
import numpy as np
import os
import pickle
from io import BytesIO
from sklearn import datasets
from sklearn.linear_model import LogisticRegression

# import data
iris_df = datasets.load_iris(as_frame=True)
X = iris_df.data.iloc[:, :2].values  # we only take the first two features.
Y = iris_df.target.values

# declare model
logreg = LogisticRegression(C=1e5)

# fit the data
logreg.fit(X, Y)

# create static directory to hold pickled model and data
static_dir = "static"
if not os.path.exists(static_dir):
    os.makedirs(static_dir)
iris_df.frame.to_csv(os.path.join(static_dir, "iris_data.csv"), index=False)

# pickle the data (wouldn't normally do this but want to plot prediction vs the train data)
trainXY = np.hstack((X,Y.reshape(-1,1)))
with open('static/trainXY.pkl', 'wb') as f:
    pickle.dump(trainXY, f)

# pickle the model
with open('static/model_logreg.pkl', 'wb') as f:
    pickle.dump(logreg, f)

# Flask app to load the pickled model and make predictions -- usually would be in its own separate app.py file
# Initialize app
app = Flask(__name__)

# load the pickled model
with open('static/model_logreg.pkl', 'rb') as f:
    model = pickle.load(f)

# load the pickled training data to display with prediction
with open('static/trainXY.pkl', 'rb') as f:
    trainXY = pickle.load(f)

trainX = trainXY[:,:2]
trainY = trainXY[:,2]

# Home page with form on it to submit new data
@app.route('/')
def get_new_data():
    return '''
        <form action="/predict" method='POST'>
          Sepal length (4.0 - 9.0):<br>
          <input type="text" name="length"> 
          <br>
          Sepal width (1.0 - 5.0):<br>
          <input type="text" name="width"> 
          <br><br>
          <input type="submit" value="Submit for class prediction">
        </form>
        '''

@app.route('/predict', methods = ["GET", "POST"])
def predict():
    # request the text from the form 
    length = float(request.form['length'])
    width = float(request.form['width'])
    X_n = np.array([[length, width]])
    
    # predict on the new data
    Y_pred = model.predict(X_n)

    # for plotting 
    X_0 = trainX[trainY == 0] # class 0
    X_1 = trainX[trainY == 1] # class 1
    X_2 = trainX[trainY == 2] # class 2
    
    # color-coding prediction 
    if Y_pred[0] == 0:
        cp = 'b'
    elif Y_pred[0] == 1:
        cp = 'r'
    else:
        cp = 'g'

    if plt:
        plt.clf() # clears the figure when browser back arrow used to enter new data

    plt.scatter(X_0[:, 0], X_0[:, 1], c='b', edgecolors='k', label = 'class 0')
    plt.scatter(X_1[:, 0], X_1[:, 1], c='r', edgecolors='k', label = 'class 1')
    plt.scatter(X_2[:, 0], X_2[:, 1], c='g', edgecolors='k', label = 'class 2')
    plt.scatter(X_n[:, 0], X_n[:, 1], c=cp, edgecolors='k', marker = 'd', \
        s=100, label = 'prediction')
    plt.xlabel('Sepal length')
    plt.ylabel('Sepal width')
    plt.title('Prediction plotted with training data')
    plt.legend()
        
    image = BytesIO()
    plt.savefig(image)
    out = image.getvalue(), 200, {'Content-Type': 'image/png'}
    return out

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)