from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout, Bidirectional
from tensorflow.keras.callbacks import ModelCheckpoint, TensorBoard
from sklearn.model_selection import train_test_split
from keras.models import load_model

import os
import market
import setting

def create_model(sequence_length, n_features, units=setting.UNITS, cell=setting.CELL, n_layers=setting.N_LAYERS, dropout=setting.DROPOUT,loss=setting.LOSS, optimizer=setting.OPTIMIZER, bidirectional=setting.BIDIRECTIONAL):
    model = Sequential()
    for i in range(n_layers):
        if i == 0:
            # first layer
            if bidirectional:
                model.add(Bidirectional(cell(units, return_sequences=True), batch_input_shape=(None, sequence_length, n_features)))
            else:
                model.add(cell(units, return_sequences=True, batch_input_shape=(None, sequence_length, n_features)))
        elif i == n_layers - 1:
            # last layer
            if bidirectional:
                model.add(Bidirectional(cell(units, return_sequences=False)))
            else:
                model.add(cell(units, return_sequences=False))
        else:
            # hidden layers
            if bidirectional:
                model.add(Bidirectional(cell(units, return_sequences=True)))
            else:
                model.add(cell(units, return_sequences=True))
        # add dropout after each layer
        model.add(Dropout(dropout))
    model.add(Dense(1, activation="linear"))
    model.compile(loss=loss, metrics=["mean_absolute_error"], optimizer=optimizer)
    return model

def train_model(model_filename,model_name,data):
    # construct the model
    model = create_model(setting.N_STEPS, len(setting.FEATURE_COLUMNS))
    # some tensorflow callbacks
    checkpointer = ModelCheckpoint(os.path.join("models", model_name + ".h5"), save_weights_only=True, save_best_only=True, verbose=1)
    tensorboard = TensorBoard(log_dir=os.path.join("logs", model_name))
    history = model.fit(data["X_train"], data["y_train"],setting.BATCH_SIZE,setting.EPOCHS
        ,validation_data=(data["X_test"], data["y_test"]),callbacks=[checkpointer, tensorboard],verbose=1)

    model_path = os.path.join("models", model_name) + ".h5"
    model.load_weights(model_path)

    # evaluate the model
    loss, mae = model.evaluate(data["X_test"], data["y_test"], verbose=0)
    # calculate the mean absolute error (inverse scaling)
    if setting.SCALE:
        mean_absolute_error = data["column_scaler"]["adjclose"].inverse_transform([[mae]])[0][0]
    else:
        mean_absolute_error = mae
    # save the model to disk
    model.save(model_filename)
    # model metrics
    print(f"{setting.LOSS} loss:", loss)
    print("Mean Absolute Error:", mean_absolute_error)
    return model

def getModel(ticker,ticker_data_filename,model_name):
    # load the data
    data = market.load_data(ticker)
    # save the dataframe
    data["df"].to_csv(ticker_data_filename)

    model_filename = os.path.join("models", model_name) + ".sav"
    # load the model from disk
    if(os.path.exists(model_filename)):
        loaded_model = load_model(model_filename)
        return loaded_model,data
    else:
        return train_model(model_filename,model_name,data),data