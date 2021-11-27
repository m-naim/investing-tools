import matplotlib.pyplot as plt
import numpy as np
import setting
import os
from time import strftime

def plot_graph(test_df,ticker):
    """
    This function plots true close price along with predicted close price
    with blue and red colors respectively
    """
    fig = plt.figure(figsize=(10,5))
    plt.plot(test_df[f'true_adjclose_{setting.LOOKUP_STEP}'], c='b')
    plt.plot(test_df[f'adjclose_{setting.LOOKUP_STEP}'], c='r')
    plt.xlabel("Days")
    plt.ylabel("Price")
    plt.legend(["Actual Price", "Predicted Price"])
    #Saving the plot as an image
    today= strftime("%Y-%m-%d")
    dir_path=os.path.join("predections",'figures',today)
    if not os.path.isdir(dir_path):
        os.mkdir(dir_path)
    graph_name= os.path.join("predections",'figures',today,f'{ticker}.jpg')
    # fig.savefig(graph_name, bbox_inches='tight', dpi=150)
    plt.show()

def get_final_df(model, data):
    """
    This function takes the `model` and `data` dict to 
    construct a final dataframe that includes the features along 
    with true and predicted prices of the testing dataset
    """
    # if predicted future price is higher than the current, 
    # then calculate the true future price minus the current price, to get the buy profit
    buy_profit  = lambda current, pred_future, true_future: true_future/current-1 if pred_future > current else 0
    # if the predicted future price is lower than the current price,
    # then subtract the true future price from the current price
    sell_profit = lambda current, pred_future, true_future: 1-true_future/current if pred_future < current else 0
    X_test = data["X_test"]
    y_test = data["y_test"]
    # perform prediction and get prices
    y_pred = model.predict(X_test)
    if setting.SCALE:
        y_test = np.squeeze(data["column_scaler"]["adjclose"].inverse_transform(np.expand_dims(y_test, axis=0)))
        y_pred = np.squeeze(data["column_scaler"]["adjclose"].inverse_transform(y_pred))
    test_df = data["test_df"]
    # add predicted future prices to the dataframe
    test_df[f"adjclose_{setting.LOOKUP_STEP}"] = y_pred
    # add true future prices to the dataframe
    test_df[f"true_adjclose_{setting.LOOKUP_STEP}"] = y_test
    # sort the dataframe by date
    test_df.sort_index(inplace=True)
    final_df = test_df
    # add the buy profit column
    final_df["buy_profit"] = list(map(buy_profit, 
                                    final_df["adjclose"], 
                                    final_df[f"adjclose_{setting.LOOKUP_STEP}"], 
                                    final_df[f"true_adjclose_{setting.LOOKUP_STEP}"])
                                    # since we don't have profit for last sequence, add 0's
                                    )
    # add the sell profit column
    final_df["sell_profit"] = list(map(sell_profit, 
                                    final_df["adjclose"], 
                                    final_df[f"adjclose_{setting.LOOKUP_STEP}"], 
                                    final_df[f"true_adjclose_{setting.LOOKUP_STEP}"])
                                    # since we don't have profit for last sequence, add 0's
                                    )
    return final_df

def predict(model, data):
    # retrieve the last sequence from data
    last_sequence = data["last_sequence"][-setting.N_STEPS:]
    # expand dimension
    last_sequence = np.expand_dims(last_sequence, axis=0)
    # get the prediction (scaled from 0 to 1)
    prediction = model.predict(last_sequence)
    # get the price (by inverting the scaling)
    if setting.SCALE:
        predicted_price = data["column_scaler"]["adjclose"].inverse_transform(prediction)[0][0]
    else:
        predicted_price = prediction[0][0]
    return predicted_price

def predictionData(model, data):
    result={}
    # get the final dataframe for the testing set
    final_df = get_final_df(model, data)
    # predict the future price
    result['ticker']= data['df']['ticker'][1]
    ticker=result['ticker']
    print(f'Predicting : {ticker}')
    result['last']= data['df']['adjclose'][-1]
    result['future_price'] = predict(model, data)
    result['expected_performance']= result['future_price']/result['last']-1
    # we calculate the accuracy by counting the number of positive profits
    result['accuracy_score'] = (len(final_df[final_df['sell_profit'] > 0]) + len(final_df[final_df['buy_profit'] > 0])) / len(final_df)
    # calculating total buy & sell profit
    result['total_buy_profit']  = final_df["buy_profit"].sum()
    result['total_sell_profit'] = final_df["sell_profit"].sum()
    # total profit by adding sell & buy together
    result['total_profit'] = result['total_buy_profit'] + result['total_sell_profit']
    # dividing total profit by number of testing samples (number of trades)
    result['profit_per_trade'] = result['total_profit'] / len(final_df)
    
    return result
