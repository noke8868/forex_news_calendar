from bs4 import BeautifulSoup 
from datetime import date, datetime, timedelta
import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

#https://gist.github.com/pohzipohzi/ad7942fc5545675022c1f31123e64c0c
class PyEcoCal:

    def GetEconomicCalendar(self, query_date: datetime):
        base_url = "https://www.forexfactory.com/"

        # get the page and make the soup
        urleco = f"{base_url}calendar?day={query_date.strftime('%b').lower()}{query_date.day}.{query_date.year}"
        date_string = query_date.strftime('%Y-%m-%d')        

        path=r'C:\Users\ychen14\Downloads\chromedriver-win32\chromedriver-win32\chromedriver.exe'
        # Set up Firefox options
        options = Options()
        driver = webdriver.Chrome(executable_path=path, options=options)

        # Load the webpage
        driver.get(urleco)
        driver.implicitly_wait(10)
        # You may need to wait for the page to fully load if there is dynamic content
        # For simplicity, I'm using a static wait here, but you might want to use WebDriverWait
        #element_present = EC.presence_of_element_located((By.CLASS_NAME, 'calendar__row calendar__row--day-breaker'))

        # Wait for a maximum of 10 seconds until the element is present
        #wait = WebDriverWait(driver, 30)
        #wait.until(element_present)

        # Get the page source after waiting for a while (allowing JavaScript to execute)
        html = driver.page_source
        # Save the HTML content to a local file
        #with open("output.html", "w", encoding="utf-8") as file:
        #    file.write(html)
        # Close the browser
        driver.quit()


        soup = BeautifulSoup(html, "html.parser")
        table = soup.find_all('tr', {'data-event-id': True})
        cal_date = soup.find_all("a", {"class": "highlight light options"})[0].span.text.strip()

        eco_day = []
        for item in table:
            dict = {}

            dict["Currency"] = item.find_all("td",{"class": "calendar__currency"})[0].text.strip()  # Currency
            dict["Event"] = item.find_all("span", {"class": "calendar__event-title"})[0].text.strip()  # Event Name
            try:
                time_gmt = item.find_all("td", {"class": "calendar__cell calendar__time"})[
                    0].div.text.strip()  # Time GMT
                datetime_gmt = datetime.strptime(f"{date_string} {time_gmt}", '%Y-%m-%d %I:%M%p')
            except:
                datetime_gmt = datetime.strptime(f"{date_string} 12:00am", '%Y-%m-%d %I:%M%p')
            dict["Time_GMT"] = datetime_gmt.strftime("%Y-%m-%d %H:%M:%S")

            impact = item.find_all("td", {"class": "calendar__cell calendar__impact"})

            for icon in range(0, len(impact)):
                dict["Impact"] = impact[icon].find_all("span")[0]['title'].split(' ', 1)[0]

            try:
                actual=item.find_all("td", {"class": "calendar__cell calendar__actual"})
                span_element= actual[0].find("span")
                if span_element:
                    if len(span_element.get('class'))>0:
                        class_value = span_element.get('class')[0]
                        dict['Signal']=class_value
                    else:
                        dict['Signal']=''
                else:
                    dict['Signal']=''
                actual_value =actual[0].text
                if actual_value is not None:
                    dict["Actual"] = actual_value.strip()
                else:
                    dict["Actual"] = item.find_all("td",{"class": "calendar__cell calendar__actual"})[0].span.text.strip()  # Actual Value
            except:
                dict["Actual"] = ""
                dict['Signal'] = ""
            try:
                dict["Forecast"] = item.find_all("td", {"class": "calendar__cell calendar__forecast"})[0].text.strip()
            except:
                dict["Forecast"] = ""
            try:
                dict["Previous"] = item.find_all("td", {"class": "calendar__cell calendar__previous"})[0].text.strip() # Previous
            except:
                dict["Previous"] = ""

            eco_day.append(dict)
        return eco_day
        
def get_days_ago_events(days_ago=0,N=120):#date ranges from -1 to -120 days ago
    input_date = datetime.today()
    eco = PyEcoCal() 
    result_list=[]
    input_date = datetime.today() - timedelta(days=days_ago)
    # Iterate over the last 60 days
    for _ in range(days_ago):
        # Move to the previous day
        input_date = input_date - timedelta(days=1)
        # Print or use the current date
        print(input_date.strftime("%Y-%m-%d"))        
        ev_list = eco.GetEconomicCalendar(input_date) 
        result_list.extend(ev_list)
    return result_list
        
if __name__ == "__main__":
    rets=get_days_ago_events()
    # Specify the CSV file path
    csv_file_path = 'output.csv'

    # Open the CSV file in write mode
    with open(csv_file_path, 'w', newline='') as csv_file:
        # Extract column headers from the first dictionary in the list
        fieldnames = rets[0].keys()

        # Create a CSV writer object
        csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

        # Write the header row
        csv_writer.writeheader()

        # Write the data rows
        csv_writer.writerows(rets)

    print('done')