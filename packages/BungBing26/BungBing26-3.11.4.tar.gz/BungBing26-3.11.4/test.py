import pandas as pd
from BungBing26 import eda

df =eda.csv_read("titanic_dataset.csv")


twine upload dist/*twine upload dist/*eda.plot(df)





#def csv_read(path):
 #  return pd.read_csv(path)

#sevc_normalized = sevc_values / sum(sevc_values) # คำนวนเป็นเปอร์เซ็น

    #bars = plt.bar(sevc_index, sevc_normalized, color=['#0099cc', 'pink'])

    #plt.ylim(0, 1)
    #plt.yticks(plt.yticks()[0], ['{:,.0%}'.format(x) for x in plt.yticks()[0]])

    # Annotating each bar
    #for i, bar in enumerate(bars):
        #yval = bar.get_height()
        #plt.text(bar.get_x() + bar.get_width()/2.0-0.05, yval, sevc_values[i], va='bottom')  # va: vertical alignment

    #plt.title("Gender")
    #plt.show()


#def easy_plot(df):
    #plt.hist(df.Age.values)
    #plt.show()

