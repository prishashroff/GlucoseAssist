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

# Defining the CNN Model
CNN = Sequential()
n_steps1 = 1
CNN.add(Conv1D(filters=240, kernel_size=2, activation='relu', input_shape=(X.shape[1], n_steps1,)))
CNN.add(MaxPooling1D(pool_size=2))
CNN.add(Flatten())
CNN.add(Dense(50, activation='relu'))
CNN.add(Dense(15))
CNN.compile(optimizer='adam', loss='mse')
print(CNN.summary())

# fit model
CNN.fit(X_train, y_train, epochs=10, verbose=0)

# demonstrate prediction
x_input = X_test
CNNyhat = CNN.predict(X_test, verbose=0)
CNNyhat = np.around(CNNyhat, decimals=1)

# Defining the LSTM Model
LSTM = Sequential()
n_steps1=1
LSTM.add(LSTM(256, return_sequences=True, input_shape=(X.shape[1], n_steps1,)))
LSTM.add(Dropout(0.5))
LSTM.add(LSTM(256, return_sequences=True, input_shape=(X.shape[1], n_steps1,)))
LSTM.add(Dropout(0.5))
LSTM.add(LSTM(256, return_sequences=True, input_shape=(X.shape[1], n_steps1,)))
LSTM.add(Dropout(0.5))
LSTM.add(LSTM(256, input_shape=(X.shape[1], n_steps1,)))
LSTM.add(Dropout(0.5))
LSTM.add(Dense(50, activation='relu'))
LSTM.add(Dense(15))
LSTM.compile(loss='mse', optimizer='adam')
LSTM.fit(X_train, y_train, epochs=10, verbose=0)
LSTMyhat = LSTM.predict(X_test, verbose=0)

#validation metrics
MSE = mean_squared_error(y_test, CNNyhat)
RMSE = math.sqrt(MSE)
MAE = mean_absolute_error(y_test,CNNyhat)
rmspe = (np.sqrt(np.mean(np.square((y_test - CNNyhat) / y_test)))) * 100
MAPE = mean_absolute_percentage_error(y_test, CNNyhat)
MSLE = mean_squared_log_error(y_test, CNNyhat)
h = tf.keras.losses.Huber()
huber = h(y_test, CNNyhat).numpy()
l = tf.keras.losses.LogCosh()
log = l(y_test, CNNyhat).numpy()
r2=  r2_score(y_test, CNNyhat)

print {"CNN: Metrics"}
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
for x in CNNyhat:
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

auc = np.trapz(CNNyhat)
num = 0
count = 0
for x in auc:
  num = x + num
  count = count + 1
total = num/count
print("Predicted:" )
print(total)

#validation metrics
MSE = mean_squared_error(y_test, LSTMyhat)
RMSE = math.sqrt(LSTMyhat)
MAE = mean_absolute_error(y_test,LSTMyhat)
rmspe = (np.sqrt(np.mean(np.square((y_test - LSTMyhat) / y_test)))) * 100
MAPE = mean_absolute_percentage_error(y_test, LSTMyhat)
MSLE = mean_squared_log_error(y_test, LSTMyhat)
h = tf.keras.losses.Huber()
huber = h(y_test, LSTMyhat).numpy()
l = tf.keras.losses.LogCosh()
log = l(y_test, LSTMyhat).numpy()
r2=  r2_score(y_test, LSTMyhat)

print {"LSTM: Metrics"}
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
for x in LSTMyhat:
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

auc = np.trapz(LSTMyhat)
num = 0
count = 0
for x in auc:
  num = x + num
  count = count + 1
total = num/count
print("Predicted:" )
print(total)
