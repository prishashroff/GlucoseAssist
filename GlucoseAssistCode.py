
import itertools
import math
import pandas as pd
import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt
from numpy import array
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import Flatten
from keras.layers import Conv1D
from keras.layers import MaxPooling1D
from sklearn.metrics import mean_squared_error
from sklearn.metrics import mean_absolute_error
from sklearn.metrics import mean_absolute_percentage_error
from sklearn.metrics import mean_squared_log_error
from sklearn.metrics import r2_score
from sklearn.metrics import confusion_matrix
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split

"""Code for 30 minute predictions of blood glucose levels"""

#importing of the timeseries data from AUC excel (due to personalized model- only import data for 1 patient at a time)

#importing all parameters for Patient 5
xls1 = pd.read_excel('/content/Traindata.xlsx', 'P05' )

#automatically creating an datasheet of organized data for direct classifier input

#rownum is associated with each meal
def create_array(rownum):
  list1 = []
  #iterating through the 120 cgm points in the dataset
  for i in range(8,128):
    list1 = list1 + [xls1.iat[rownum, i]]
  def split_sequence(sequence, n_steps_in, n_steps_out):
    X, y = list(), list()
    for i in range(0, len(sequence), 15):
      #find the end of this pattern
      end_ix = i + n_steps_in
      #check if we are beyond the sequence
      if end_ix > len(sequence)-5:
        break
      #gather input and output parts of the pattern
      seq_x, seq_y = sequence[i:end_ix], sequence[end_ix:i+n_steps_in +n_steps_out]
      X.append(seq_x)
      y.append(seq_y)
    return array(X), array(y)
    #splitting into my ideal size of 60 min input and 30 min output
  X, y = split_sequence(list1, 30, 15)
  df = pd.DataFrame(columns=['X parameters', 'Y parameters'])
  for i in range(len(X)):
    df.loc[len(df.index)] = (X[i], y[i])
    #creating the columns for dataframe of training CGM data, and testing CGM data
  data = pd.DataFrame(X, columns = ['T1','T2','T3', 'T4', 'T5','T6','T7', 'T8', 'T9','T10', 'T11','T12','T13', 'T14', 'T15','T16','T17', 'T18', 'T19','T20', 'T21','T22','T23', 'T24', 'T25','T26','T27', 'T28', 'T29','T30'])
  data1 = pd.DataFrame(y, columns = ['G1','G2','G3', 'G4','G5', 'G6','G7','G8', 'G9', 'G10','G11','G12', 'G13', 'G14','G15'])
  return (data, data1)

#initializing a basic dataframe with first row
data, data1 = create_array(0)
numofiter = 6
df1 = pd.DataFrame({'ch' : [xls1.iat[0, 0]] * numofiter , 'fat' : [xls1.iat[0, 1]] * numofiter, 'fiber' : [xls1.iat[0, 2]] * numofiter, 'gl' : [xls1.iat[0, 3]] * numofiter, 'p1' : [xls1.iat[0, 4]] * numofiter, 'p2' : [xls1.iat[0, 5]] * numofiter, 'p3' : [xls1.iat[0, 6]] * numofiter, 'p4' : [xls1.iat[0, 7]] * numofiter})
ans = pd.concat([df1, data, data1], axis = 1)
ans.insert(0, "Time", [0, 30, 60, 90, 120, 150] )
#for loop iterating though the rest of the data and importing the fat, fiber, glucose, etc.
for i in range(1,35):
  data, data1 = create_array(i)
  df1 = pd.DataFrame({'Time' : [0, 30, 60, 90, 120, 150], 'ch' : [xls1.iat[i, 0]] * numofiter , 'fat' : [xls1.iat[i, 1]] * numofiter, 'fiber' : [xls1.iat[i, 2]] * numofiter, 'gl' : [xls1.iat[i, 3]] * numofiter, 'p1' : [xls1.iat[i, 4]] * numofiter, 'p2' : [xls1.iat[i, 5]] * numofiter, 'p3' : [xls1.iat[i, 6]] * numofiter, 'p4' : [xls1.iat[i, 7]] * numofiter})
  #adding all three data frames/columns into the one dataframe
  ans1 = pd.concat([df1, data, data1], axis = 1)
  ans = pd.concat([ans, ans1], axis = 0)

#resize the data and create a dataframe
df = ans
X = df[['Time', 'ch', 'fat', 'fiber', 'gl', 'p1', 'p2', 'p3', 'p4','T1','T2','T3', 'T4', 'T5','T6','T7', 'T8', 'T9','T10', 'T11','T12','T13', 'T14', 'T15','T16','T17', 'T18', 'T19','T20', 'T21','T22','T23', 'T24', 'T25','T26','T27', 'T28', 'T29','T30']].to_numpy()
y = df[['G1','G2','G3', 'G4','G5', 'G6','G7','G8', 'G9', 'G10','G11','G12', 'G13', 'G14','G15']].to_numpy()
X = X.reshape((X.shape[0], X.shape[1], 1))

#split into train (80%) and test(20%) data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)

# define model
model = Sequential()
n_steps1 = 1
model.add(Conv1D(filters=240, kernel_size=2, activation='relu', input_shape=(X.shape[1], n_steps1,)))
model.add(MaxPooling1D(pool_size=2))
model.add(Flatten())
model.add(Dense(50, activation='relu'))
model.add(Dense(15))
model.compile(optimizer='adam', loss='mse')
print(model.summary())

# fit model
model.fit(X_train, y_train, epochs=10, verbose=0)

# demonstrate prediction
x_input = X_test
yhat = model.predict(X_test, verbose=0)
yhat = np.around(yhat, decimals=1)

#validation metrics
MSE = mean_squared_error(y_test, yhat)
RMSE = math.sqrt(MSE)
MAE = mean_absolute_error(y_test,yhat)
rmspe = (np.sqrt(np.mean(np.square((y_test - yhat) / y_test)))) * 100
MAPE = mean_absolute_percentage_error(y_test, yhat)
MSLE = mean_squared_log_error(y_test, yhat)
h = tf.keras.losses.Huber()
huber = h(y_test, yhat).numpy()
l = tf.keras.losses.LogCosh()
log = l(y_test, yhat).numpy()
r2=  r2_score(y_test, yhat)

print ("Mean Squared Error: " + str(MSE))
print ("Root Mean Squared Error: " + str(RMSE))
print ("Mean Absolute Error: " + str(MAE))
print ("Root Mean Squared Percentage Error: " + str(rmspe))
print ("Mean Absolute Percent Error: " + str(MAPE))
print ("Mean Squared Logarithmic Error: " + str(MSLE))
print ("Huber Loss: " + str(huber))
print ("LogCosh: " + str(log))
print ("R Squared: " + str(r2))
print ("AUC:")

predlist =[]
for x in yhat:
  for y in x:
    predlist.append(y)

testlist =[]
for x in y_test:
  for y in x:
    testlist.append(y)

auc = np.trapz(y_test)
n = 0
c = 0
for x in auc:
  n = x + n
  c = c +1
t = n/c
print("Actual:")
print(t)

auc = np.trapz(yhat)
num = 0
count = 0
for x in auc:
  num = x + num
  count = count + 1
total = num/count
print("Predicted:" )
print(total)

#plotting an actual vs. predicted graph
x1  = []
for i in range(1,len(testlist)+1) :
  x1.append(i)

x2  = []
for i in range(1,len(testlist)+1) :
  x2.append(i)

# line 1 points
y1 = testlist
# plotting the line 1 points
plt.plot(x1, y1, label = "actual")

# line 2 points
y2 = predlist
# plotting the line 2 points
plt.plot(x2, y2, label = "predicted")

# naming the x axis
plt.xlabel('time')
# naming the y axis
plt.ylabel('glucose levels')
# giving a title to my graph
plt.title('Predicting Glucose')
plt.axhline(y = 7.8, color = 'r', linestyle = '-')
plt.axhline(y = 3.3, color = 'r', linestyle = '-')

# show a legend on the plot
plt.legend()

# function to show the plot
plt.show()

#clark error grid [*code taken from an example and modified by me to work for the units of mmol/L*]
def clarke_error_grid(ref_values, pred_values, title_string):

    #Checking to see if the lengths of the reference and prediction arrays are the same
    assert (len(ref_values) == len(pred_values)), "Unequal number of values (reference : {}) (prediction : {}).".format(len(ref_values), len(pred_values))

    #Checks to see if the values are within the normal physiological range, otherwise it gives a warning
    if max(ref_values) > 22.2 or max(pred_values) > 22.2:
        print ("Input Warning: the maximum reference value {} or the maximum prediction value {} exceeds the normal physiological range of glucose (<22.2 mmol/l).".format(max(ref_values), max(pred_values)))
    if min(ref_values) < 0 or min(pred_values) < 0:
        print ("Input Warning: the minimum reference value {} or the minimum prediction value {} is less than 0 mmol/l.".format(min(ref_values),  min(pred_values)))

    #Clear plot
    plt.clf()

    #Set up plot
    plt.scatter(ref_values, pred_values, marker='o', color='c')
    plt.title(title_string + " Clarke Error Grid: Patient 5")
    plt.xlabel("Reference Concentration (mmol/l)")
    plt.ylabel("Prediction Concentration (mmol/l)")
    plt.xticks([0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22])
    plt.yticks([0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22])
    plt.gca().set_facecolor('white')

    #Set axes lengths
    plt.gca().set_xlim([0, 22.2])
    plt.gca().set_ylim([0, 22.2])
    plt.gca().set_aspect((44.4)/(44.4))

    #Plot zone lines
    plt.plot([0,22], [0,22], ':', c='black')
    plt.plot([0, 3.2375], [3.885, 3.885], '-', c='black')
    #plt.plot([3.2375, 320], [3.885, 22.2], '-', c='black')
    plt.plot([3.2375, 22.2/1.2], [3.885, 22.2], '-', c='black')
    plt.plot([3.885, 3.885], [4.662, 22.2],'-', c='black')
    plt.plot([0, 3.885], [9.99, 9.99], '-', c='black')
    plt.plot([3.885, 16.095],[9.99, 22.2],'-', c='black')
    # plt.plot([3.885, 3.885], [0, 3.2375], '-', c='black')
    plt.plot([3.885, 3.885], [0, 3.108], '-', c='black')
    # plt.plot([3.885, 22.2],[3.2375, 17.76],'-', c='black')
    plt.plot([3.885, 22.2], [3.108, 17.76],'-', c='black')
    plt.plot([9.99, 9.99], [0, 3.885], '-', c='black')
    plt.plot([9.99, 22.2], [3.885, 3.885], '-', c='black')
    plt.plot([13.32, 13.32], [3.885, 9.99],'-', c='black')
    plt.plot([13.32, 22.2], [9.99, 9.99], '-', c='black')
    plt.plot([7.215, 9.99], [0, 3.885], '-', c='black')

    #Add zone titles
    plt.text(1.66, 0.833, "A", fontsize=15)
    plt.text(20.55, 20.55, "A", fontsize=15)
    plt.text(20.55, 14.44, "B", fontsize=15)
    plt.text(15.55, 20.55, "B", fontsize=15)
    plt.text(8.88, 20.55, "C", fontsize=15)
    plt.text(8.88, 0.833, "C", fontsize=15)
    plt.text(1.66, 7.77, "D", fontsize=15)
    plt.text(20.55, 6.66, "D", fontsize=15)
    plt.text(1.66, 20.55, "E", fontsize=15)
    plt.text(20.55, 0.833, "E", fontsize=15)

    #Statistics from the data
    zone = [0] * 5
    for i in range(len(ref_values)):
        if (ref_values[i] <= 3.885 and pred_values[i] <= 3.885) or (pred_values[i] <= 1.2*ref_values[i] and pred_values[i] >= 0.8*ref_values[i]):
            zone[0] += 1    #Zone A

        elif (ref_values[i] >= 9.99 and pred_values[i] <= 3.885) or (ref_values[i] <= 70 and pred_values[i] >= 9.99):
            zone[4] += 1    #Zone E

        elif ((ref_values[i] >= 3.885 and ref_values[i] <= 16.095) and pred_values[i] >= ref_values[i] + 6.105) or ((ref_values[i] >= 7.215 and ref_values[i] <= 9.99) and (pred_values[i] <= (7/5)*ref_values[i] - 10.101)):
            zone[2] += 1    #Zone C
        elif (ref_values[i] >= 13.32 and (pred_values[i] >= 3.885 and pred_values[i] <= 5.55)) or (ref_values[i] <= 3.2373 and pred_values[i] <= 9.99 and pred_values[i] >= 3.885) or ((ref_values[i] >= 3.2373 and ref_values[i] <= 3.885) and pred_values[i] >= (6/5)*ref_values[i]):
            zone[3] += 1    #Zone D
        else:
            zone[1] += 1    #Zone B

    return zone

clarke_error_grid(testlist, predlist,' ')

"""Code for hyperglycemic event classification"""
#takes the predictions from the above predicitions and classifies it as normal, hyperglycemic or hypoglycemic
import __main__  as const

#take above 30 minute predictions and process data
df = pd.DataFrame(yhat)
df.insert(15, 'pred', 0)
for x in range(len(df.axes[0])):
  event = 1
  for y in range(len(df.axes[1])-1):
    #identifying a hyperglycemic event
    if df.iat[x,y] > 7.8:
      const.event = 2
    #identifying a hypoglycemic event
    if df.iat[x,y] <3.3:
      const.event = 0
  df.iat[x,y+1] = event

values = df.values[:, :]
X = values[:, :-1]
y = values[:, -1]

# Spliting the dataset into testing and training data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)

# Setting up the classifier and the data
clf = RandomForestClassifier(n_estimators=10, random_state=0).fit(X_train, y_train)

# Testing the model and evaluating the model
y_test_pred = clf.predict(X_test)
print(accuracy_score(y_test, y_test_pred))

y_train_pred = clf.predict(X_train)
print(accuracy_score(y_train, y_train_pred))

#print a confusion matrix
cm = confusion_matrix(y_true=y_test, y_pred=y_test_pred)
def plot_confusion_matrix(cm, classes,
                        normalize=False,
                        title='Confusion matrix',
                        cmap=plt.cm.Blues):

    plt.imshow(cm, interpolation='nearest', cmap=cmap)
    plt.title(title)
    plt.colorbar()
    tick_marks = np.arange(len(classes))
    plt.xticks(tick_marks, classes, rotation=45)
    plt.yticks(tick_marks, classes)

    if normalize:
        cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
        print("Normalized confusion matrix")
    else:
        print('Confusion matrix, without normalization')

    print(cm)

    thresh = cm.max() / 2.
    for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
        plt.text(j, i, cm[i, j],
            horizontalalignment="center",
            color="white" if cm[i, j] > thresh else "black")

    plt.tight_layout()
    plt.ylabel('Actual')
    plt.xlabel('Predicted')


cm_plot_labels = ['Hyperglycemia', 'Normal', 'Hypoglycemia']
plot_confusion_matrix(cm=cm, classes=cm_plot_labels, title='Glycemia Confusion Matrix')
