import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import numpy as np
import seaborn as sns


# สร้างฟังก์ชันสำหรับอ่านข้อมูล CSV
def read_titanic_data(filename):
    return pd.read_csv(filename)

# สร้างฟังก์ชันสำหรับทำ EDA และพล็อตกราฟ
def perform_eda(data, plot_pclass=True, plot_sex=True, plot_age_vs_fare=True, plot_sibsp=True, plot_parch=True, plot_survived=True):
    if plot_pclass:
        # พล็อตกราฟแท่งแสดงจำนวนผู้โดยสารตามชั้นโดยสาร
        sns.countplot(data=data, x='Pclass')
        plt.title('Number of pasengers by class of service')
        plt.xlabel('Class of service')
        plt.ylabel('Number of passengers')
        plt.show()

    if plot_sex:
        # พล็อตกราฟแท่งแสดงจำนวนผู้โดยสารตามเพศ
        sns.countplot(data=data, x='Sex')
        plt.title('Number of passenger by gender')
        plt.xlabel('Age')
        plt.ylabel('Number of Pasengers')
        plt.show()

    if plot_age_vs_fare:
        # พล็อตกราฟแผนภูมิแสดงความสัมพันธ์ระหว่างอายุและค่าโดยสาร
        plt.scatter(data['Age'], data['Fare'])
        plt.title('Relationship between Age and Fare')
        plt.xlabel('Age')
        plt.ylabel('Fare')
        plt.show()

    if plot_sibsp:
        # พล็อตกราฟแท่งแสดงจำนวนผู้โดยสารตามจำนวนพี่น้อง/คู่สมรส
        sns.countplot(data=data, x='SibSp')
        plt.title('Number of Passengers by Siblings/Spouses')
        plt.xlabel('Number of Siblings/Spouses')
        plt.ylabel('Number of Passengers')
        plt.show()

    if plot_parch:
        # พล็อตกราฟแท่งแสดงจำนวนผู้โดยสารตามจำนวนบิดา/มารดา
        sns.countplot(data=data, x='Parch')
        plt.title('Number of Passengers by Parents/Children')
        plt.xlabel('Number of Parents/Children')
        plt.ylabel('Number of Passengers')
        plt.show()

    if plot_survived:
    # พล็อตกราฟแท่งแสดงจำนวนผู้รอดชีวิตและผู้ไม่รอดชีวิต
        sns.countplot(data=data, x='Survived')
        plt.title('Number of Passengers Who Survived and Who Did Not')
        plt.xlabel('Survived (1) / Did Not Survive (0)ต')
        plt.ylabel('Number of Passengers')
        plt.show()

# เรียกใช้งานฟังก์ชันสำหรับอ่านข้อมูล
titanic_data = read_titanic_data('titanic_dataset.csv')

# เรียกใช้งานฟังก์ชันสำหรับทำ EDA และพล็อตกราฟ
perform_eda(titanic_data, plot_pclass=True, plot_sex=True, plot_age_vs_fare=True, plot_sibsp=True, plot_parch=True, plot_survived=True)

