import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import numpy as np



def csv_read(path) :
    return pd.read_csv(path)



def chart1(df):
    # แบ่งข้อมูลตามเพศ
    male_data = df[df['Sex'] == 'male']
    female_data = df[df['Sex'] == 'female']

    # คำนวณจำนวนผู้รอดชีวิตในแต่ละเพศ
    male_survived = male_data['Survived'].sum()
    female_survived = female_data['Survived'].sum()

    # สร้างกราฟแท่ง
    plt.bar(['Male', 'Female'], [male_survived, female_survived], color=['red', 'yellow'])
# เพิ่มชื่อแกน X และแกน Y
    plt.xlabel('Sex')
    plt.ylabel('Survived')

  
    plt.title('Survival by Sex')

 
    plt.show()



def chart2(df):
    survived_data = df[df['Survived'] == 1]

# สร้างกราฟแท่ง
    plt.hist(survived_data['Age'], bins=20, color='blue', edgecolor='black')

# เพิ่มชื่อแกน X และแกน Y
    plt.xlabel('Age')
    plt.ylabel('Number of Survivors')

# เพิ่มหัวข้อกราฟ
    plt.title('Age Distribution of Survivors')

# แสดงกราฟ
    plt.show()




def chart3(df):

    pclass_age_counts = {
    'class 1 age < 30': len(df[(df['Pclass'] == 1) & (df['Age'] < 30)]),
    'class 1 age 30-60': len(df[(df['Pclass'] == 1) & (df['Age'] >= 30) & (df['Age'] <= 60)]),
    'class 1 age > 60': len(df[(df['Pclass'] == 1) & (df['Age'] > 60)]),
    'class 2 age < 30': len(df[(df['Pclass'] == 2) & (df['Age'] < 30)]),
    'class 2 age 30-60': len(df[(df['Pclass'] == 2) & (df['Age'] >= 30) & (df['Age'] <= 60)]),
    'class 2 age > 60': len(df[(df['Pclass'] == 2) & (df['Age'] > 60)]),
    'class 3 age < 30': len(df[(df['Pclass'] == 3) & (df['Age'] < 30)]),
    'class 3 age 30-60': len(df[(df['Pclass'] == 3) & (df['Age'] >= 30) & (df['Age'] <= 60)]),
    'class 3 age > 60': len(df[(df['Pclass'] == 3) & (df['Age'] > 60)])
    }


    plt.bar(pclass_age_counts.keys(), pclass_age_counts.values(), color='skyblue')


    plt.xlabel('Pclass and Age')
    plt.ylabel('Count of Passenger')

    plt.title('Passenger Count by Pclass and Age')


    plt.xticks(rotation=45)


    plt.show()

def chart4(df):

    survived_data = df[df['Survived'] == 1]
    not_survived_data = df[df['Survived'] == 0]

    # สร้างกราฟเส้นสำหรับอายุของผู้รอดชีวิต
    plt.plot(survived_data['Age'], label='Survived', color='blue', marker='o', linestyle='-')

    # สร้างกราฟเส้นสำหรับอายุของผู้ไม่รอดชีวิต
    plt.plot(not_survived_data['Age'], label='Not Survived', color='red', marker='x', linestyle='-')

    # เพิ่มชื่อแกน X และแกน Y
    plt.xlabel('Passenger')
    plt.ylabel('Age')

    # เพิ่มหัวข้อกราฟ
    plt.title('Age vs Survival')

    # เพิ่มคำอธิบายแถบสี
    plt.legend()

    # แสดงกราฟ
    plt.show()

def chart5(df):
   
    #กำหนดช่วงอายุ
    age_bins = [0, 20, 40, 60, df['Age'].max() + 1]
    age_labels = ['0-20', '20-40', '40-60', '>60']

    # ใช้ cut เพื่อแบ่งข้อมูลอายุเป็นช่วง
    df['AgeGroup'] = pd.cut(df['Age'], bins=age_bins, labels=age_labels, right=False)

    # คำนวณอัตราการรอดชีวิตเฉลี่ยของแต่ละช่วงอายุเป็นเปอร์เซนต์
    age_survival_rates = df.groupby('AgeGroup')['Survived'].mean() * 100

    # สร้างกราฟแท่ง
    plt.bar(age_survival_rates.index, age_survival_rates.values, color='skyblue')

    # เพิ่มชื่อแกน X และแกน Y
    plt.xlabel('Age Group')
    plt.ylabel('Survival Rate (%)')

    # เพิ่มหัวข้อกราฟ
    plt.title('Survival Rate by Age Group')

    # แสดงกราฟ
    plt.show()
