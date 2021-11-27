import matplotlib.pyplot as plt

def plot_graph(df):
    """
    This function plots true close price along with predicted close price
    with blue and red colors respectively
    """
    fig = plt.figure(figsize=(10,5))
    plt.plot(df, c='b')
    plt.xlabel("Days")
    plt.ylabel("Price")
    plt.legend(["Actual Price", "Predicted Price"])
    # Saving the plot as an image
    # today= strftime("%Y-%m-%d")
    # dir_path=os.path.join("predections",'figures',today)
    # if not os.path.isdir(dir_path):
    #     os.mkdir(dir_path)
    # graph_name= os.path.join("predections",'figures',today,f'{ticker}.jpg')
    # fig.savefig(graph_name, bbox_inches='tight', dpi=150)
    plt.show()


def plot_graph_multiple(df,ticker):
    df.plot( y=df.columns.values,use_index=True,kind="line", figsize=(10, 10))
    plt.show()
