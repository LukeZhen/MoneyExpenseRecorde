import kivy
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty

import pandas as pd
import os
from datetime import datetime
import matplotlib.pyplot as plt


def get_monthly_file_name():
    now = datetime.now()
    return f"expenses_{now.year}_{now.month:02d}.csv"

def draw_monthly_chart(year, month):
    file_name = f"expenses_{year}_{month:02d}.csv"

    if not os.path.exists(file_name):
        print(f"No data found for {year}-{month:02d}. File {file_name} does not exist.")
        return

    df = pd.read_csv(file_name)
    df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce")
    df["Day"] = pd.to_numeric(df["Day"], errors="coerce")

    daily_sums = df.groupby("Day", as_index=False)["Amount"].sum().sort_values("Day")

    plt.figure(figsize=(8, 5))
    plt.bar(daily_sums["Day"], daily_sums["Amount"], color="skyblue")
    plt.xlabel("Day of Month")
    plt.ylabel("Total Amount Used")
    plt.title(f"Daily Expenses for {year}-{month:02d}")

    for x, y in zip(daily_sums["Day"], daily_sums["Amount"]):
        plt.text(x, y + 0.05, str(y), ha="center")

    plt.tight_layout()
    plt.show()

def draw_yearly_chart(year):
    monthly_totals = []
    for month in range(1, 13):
        file_name = f"expenses_{year}_{month:02d}.csv"
        if os.path.exists(file_name):
            df_month = pd.read_csv(file_name)
            
            # Ensure numeric conversion
            df_month["Amount"] = pd.to_numeric(df_month["Amount"], errors="coerce")
            # Drop rows with invalid data
            df_month.dropna(subset=["Amount"], inplace=True)
            
            # Calculate the total for the month
            monthly_total = df_month["Amount"].sum()
        else:
            # If no data for the month, total is 0
            monthly_total = 0
        
        monthly_totals.append(monthly_total)

    # Plot the bar chart
    plt.figure(figsize=(10, 6))
    months = [
        "January", "February", "March", "April", "May", "June", 
        "July", "August", "September", "October", "November", "December"
    ]
    plt.bar(months, monthly_totals, color="skyblue")
    plt.xlabel("Month")
    plt.ylabel("Total Expenses")
    plt.title(f"Monthly Expense Summary for {year}")
    plt.xticks(rotation=45)

    # Add text annotations above each bar
    for i, total in enumerate(monthly_totals):
        plt.text(i, total + 0.05, f"{total:.2f}", ha="center", va="bottom")

    plt.tight_layout()
    plt.show()


class MyGrid(Widget):
    amount = ObjectProperty(None)
    day = ObjectProperty(None)
    spinner = ObjectProperty(None)
    def btn(self):
        print("Amount: ", self.amount.text)
        print("Day: ", self.day.text)
        print("Selected Option:", self.spinner.text)
        data = {
            "Amount": [self.amount.text],
            "Day": [self.day.text],
            "Reason": [self.spinner.text],
        }

        df = pd.DataFrame(data)
        new_file = get_monthly_file_name()
        if os.path.exists(new_file):
            df.to_csv(new_file, mode="a", index=False, header=False)  
        else:
            df.to_csv(new_file, mode="w", index=False, header=True)  
        print(f"Data saved to {new_file}.")

        self.amount.text = ""
        self.day.text = ""
        self.spinner.text = "Select Option"
    def show_total(self):
        new_file = get_monthly_file_name()
        if os.path.exists(new_file):
            df = pd.read_csv(new_file)
            df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce")
            total = df["Amount"].sum()
            self.total_label.text = f"Total: {total}"
            print(f"The total amount is {total}")
        else:
            self.total_label.text = "No CSV file found."
            print("No CSV file found. Please add some data first.")
    
    def show_monthly_chart(sefl):
        year = datetime.now().year
        month = datetime.now().month
        draw_monthly_chart(year, month)
    
    def show_yearly_chart(self):
        year = datetime.now().year
        draw_yearly_chart(year)

    def show_food_total(self):
        self._show_category_total("Food")

    def show_entertainment_total(self):
        self._show_category_total("Entertainment")

    def show_internet_total(self):
        self._show_category_total("Internet Service")

    def _show_category_total(self, category_name):
        file_name = get_monthly_file_name()
        if os.path.exists(file_name):
            df = pd.read_csv(file_name)
            df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce")

            # Filter rows where "Reason" matches the category name
            category_df = df[df["Reason"] == category_name]
            total_for_category = category_df["Amount"].sum()

            self.total_label.text = f"{category_name}: {total_for_category}"
            print(f"Total for {category_name} in {file_name}: {total_for_category}")
        else:
            self.total_label.text = "No data for this month."
            print(f"No CSV file found for the current month. Cannot calculate {category_name} total.")

class MyApp(App):
    def build(self):
        return MyGrid()
    
if __name__ == '__main__':
    MyApp().run()

