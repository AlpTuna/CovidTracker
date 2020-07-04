import requests
import json
import datetime
import time
import os

API_KEY = "tNjwteT3yGDr"
PROJECT_TOKEN = "tnodRHPNMECn"

keyWords = {'Cases':['case','cases','c'],             # These keywords are the possible inputs the user can type in
            'Death':['death','deaths','dead','deads','d'],   
            'WorldWide':['world','worldwide','total','global','globally','w'],
            'FirstQuestion':['top list','1','list','sort','toplist'],
            'SecondQuestion':['data','datas','2','country datas'],
            'ThirdQuestion':['exactplace','3','exact place'],
            'RefreshData':['refresh','r','refresh data','refresh database','refresh datas','4'],
            'SaveData':['save data','5','save','savedata','save datas','savedatas']
            }

class Data():
    def RefreshData(self):
        self.response = requests.get(f'https://www.parsehub.com/api/v2/projects/{PROJECT_TOKEN}/last_ready_run/data', params={"api_key": API_KEY})
        self.data = json.loads(self.response.text)
        self.AskWhichQuestion()


    def AddCommasBetweenNumber(self,number):   # Makes the number more readable by adding a comma in every three digits
        return "{:,}".format(number)

    def DeleteLastRun(self):
        last_run = requests.get(f'https://www.parsehub.com/api/v2/projects/{PROJECT_TOKEN}/last_ready_run',params={"api_key": API_KEY})
        last_run_datas = last_run.text.replace('run_token','').replace('{','').replace('}','').replace('"','').replace(':','').replace(' ','')  # Removes every unnecesary character
        last_run_key = ''
        for x in last_run_datas:
            if x != ',':           # First value (until the first comma) is always the run token. With this loop, we get the run token from all the datas
                last_run_key += x 
            else:    
                break
        requests.delete(f'https://www.parsehub.com/api/v2/runs/{last_run_key}', params={"api_key": API_KEY})   # Deletes the last run

    def RunAgain(self):
        print(f'\nCTRL + C to continue updating in the background (Might cause some problems)')
        try:
            self.DeleteLastRun()        # If there is a previous run, it will be deleted
        except:
            pass                        # If there isn't, it will be passed
        requests.post(f'https://www.parsehub.com/api/v2/projects/{PROJECT_TOKEN}/run',params={"api_key": API_KEY})
        i = 0                                     
        wait_time = 65                           # How long the running lasts (usually between 60-70 seconds)
        print_frequency = 5                       # In how many seconds the time left will be printed
        try:
            while i < wait_time:
                if i % print_frequency == 0:
                    print(f'Refreshing Database .... ({wait_time-i} Seconds Left)')
                i+=1
                if i == wait_time:                      # If the countdown is over
                    print(f'SUCCESS : DATA UPDATED !\nUpdate Time : {datetime.datetime.now().date()} {datetime.datetime.now().hour}:{datetime.datetime.now().minute}')
                    self.RefreshData()
                time.sleep(1)
                        
        except KeyboardInterrupt:
                print('Update is resuming in the background')   # The new run still continues in the server, but the user doesn't have to wait the timer this way 
                self.AskWhichQuestion()
        

    def CreateTextFileOfSort(self):
        self.GetAllCountries()                          # Refreshes the countriesList 
        date = datetime.datetime.now()
        with open ("SavedDatas.txt","r") as textToRead:
            lines = textToRead.readlines()
        textFile= open("SavedDatas.txt","a+")
        count = 0
        todays_date = str(date.date())
        if os.path.getsize("SavedDatas.txt") > 0:
            for line in lines:
                if todays_date in line:
                    count = count + 1           
    
        if count == 0:                # If todays data has not been saved
            print(f"\nIMPORTANT : Saving the last updated database. Refreshing the data is suggested if you haven't updated recently.")
            if os.path.getsize("SavedDatas.txt") > 0:      # If the text file has text in it
                textFile.write(f'\n-----------------------------------------------------------------------------') # Seperates two different saves
                textFile.write(f'\nDate : {date.date()}\n\n')    # If there is text in it, starts with two new lines so it gets seperated from the previous data
            else:
                textFile.write(f'Date : {date.date()}\n\n')     # If there is no text, starts without adding only one new line so there wont be an unnecessary empty line in the beggining
            self.wantedData = 'case'
            textFile.write(f'Worldwide - {self.GetTotalCases()} Cases')
            for x in range(0,len(self.countriesList)):
                    textFile.write(f'\n{x+1}) {self.countriesList[x].capitalize()} - {self.AddCommasBetweenNumber(self.GetCountryData(self.countriesList[x],self.wantedData))} Cases')
            textFile.close()
            print(f'Saved At {os.getcwd()}')
        elif count > 0:                          # If todays data has already been saved
            print(f'The data for {date.date()} has already been saved')
        
        self.AskWhichQuestion()

    def GetCountryData(self,country,dataType):
        self.wantedCountry = country
        if self.wantedCountry != "world":
            for x in self.data['countries']:
                if (x['name'].lower() == country.lower()):
                    if self.wantedData in keyWords['Cases']:   
                        value = x['cases']
                        value = value.replace(',','')    # Removes commas so it will be possible to convert the value to an int
                        return int(value)                # Commas will still be added later on, when printing the values
                        
                    if self.wantedData in keyWords['Death']:
                        value = x['deaths']
                        value = value.replace(',','')  # Removes commas so it will be possible to convert the value to an int
                        return int(value)              # Commas will still be added later on, when printing the values
        else:
            if self.wantedData in keyWords['Cases']:
                value = self.GetTotalCases()
                value = value.replace(',','')           # Removes commas so it will be possible to convert the value to an int
                return int(value)                       # Commas will still be added later on, when printing the values  
            if self.wantedData in keyWords['Death']:
                value = self.GetTotalDeaths()
        self.AskWhichQuestion()
        
        
    def GetAllCountries(self):
        self.countriesList = []             # Clears the list first, so the countries wont be added multiple times
        for x in self.data['countries']:
            self.countriesList.append(x['name'].lower())
        return self.countriesList

    def AskWhichQuestion(self):
        print('')
        self.wantedQuestion = str(input('Top List (1) / Datas (2) / Exact Place (3) / Refresh Data (4) / Save Current Data (5)?')).lower()
        if self.wantedQuestion in keyWords['FirstQuestion']:
            self.TopList()
        elif self.wantedQuestion in keyWords['SecondQuestion']:
            self.AskCountry()
        elif self.wantedQuestion in keyWords['ThirdQuestion']:
            self.ExactPlaceFinder()
        elif self.wantedQuestion in keyWords['RefreshData']:
            self.RunAgain()
        elif self.wantedQuestion in keyWords['SaveData']:
            self.CreateTextFileOfSort()


    def SortByDeath(self):
        country_Death = {}
        sorted_countries = []
        self.wantedData = 'deaths'
        for x in self.data['countries']:
            if 'deaths' in x.keys():
                country_Death.update({x['name'] : (self.GetCountryData(x['name'],self.wantedData))})
        sorted_countries = sorted(country_Death.items(), key=lambda x: x[1],reverse= True)
        number = int(input('How many countries?    (0 for all countries)'))
        if number != 0:
            if number < len(sorted_countries):
                for x in range(0,number):
                    self.wantedCountry = sorted_countries[x][0]
                    self.wantedData = 'death'
                    print(f'{x+1}) {self.wantedCountry.capitalize()} - {self.AddCommasBetweenNumber(self.GetCountryData(sorted_countries[x][0],self.wantedData))} Deaths')
            else:
                for x in range(0,len(sorted_countries)):
                    self.wantedCountry = sorted_countries[x][0]
                    self.wantedData = 'death'
                    print(f'{x+1}) {self.wantedCountry.capitalize()} - {self.AddCommasBetweenNumber(self.GetCountryData(sorted_countries[x][0],self.wantedData))} Deaths')
        else:
            for x in range(0,len(sorted_countries)):
                self.wantedCountry = sorted_countries[x][0]
                self.wantedData = 'death'
                print(f'{x+1}) {self.wantedCountry.capitalize()} - {self.AddCommasBetweenNumber(self.GetCountryData(sorted_countries[x][0],self.wantedData))} Deaths')
        
    def SortByCases(self):
        self.wantedData = 'cases'
        number = int(input('How many countries?    (0 for all countries)'))
        if number != 0:                                        # If the user doesnt want all the countries
            if number <= len(self.countriesList):           # If the user typed a smaller value than the number of incfected countries
                for x in range(0,number):
                    self.wantedCountry = self.countriesList[x]
                    self.wantedData = 'case'
                    print(f'{x+1}) {self.countriesList[x].capitalize()} - {self.AddCommasBetweenNumber(self.GetCountryData(self.wantedCountry,self.wantedData))} Cases')
            else:                                          # If the user typed a bigger value than the number of infected countries
                for x in range(0,len(self.countriesList)):
                    self.wantedCountry = self.countriesList[x]
                    self.wantedData = 'case'
                    print(f'{x+1}) {self.countriesList[x].capitalize()} - {self.AddCommasBetweenNumber(self.GetCountryData(self.wantedCountry,self.wantedData))} Cases')
        else:                                       
            for x in range(0,len(self.countriesList)):
                self.wantedCountry = self.countriesList[x]
                self.wantedData = 'case'
                print(f'{x+1}) {self.countriesList[x].capitalize()} - {self.AddCommasBetweenNumber(self.GetCountryData(self.wantedCountry,self.wantedData))} Cases')

    def TopList(self):
        self.GetAllCountries()
        wantedsort = input('Sort By Cases (1) / Sort By Deaths (2) ?')
        if wantedsort == '1':
            self.SortByCases()
        elif wantedsort == '2':
            self.SortByDeath()
        self.AskWhichQuestion()

    def ExactPlaceFinder(self):
        self.GetAllCountries()
        place = 1
        self.wantedCountry = (str(input('Please select a country...')).lower()).strip()
        while (not self.wantedCountry.strip() in self.countriesList):
            print(f'{self.wantedCountry} couldnt be found')
            self.wantedCountry = (str(input('Please select a country...')).lower()).strip()
        for x in self.countriesList:
            if x == self.wantedCountry:
                print(f'#{place} out of {len(self.countriesList)} countries')
                self.AskWhichQuestion()
            else:
                place +=1

    def AskCountry(self):
        self.GetAllCountries()
        print('')
        self.wantedCountry = (str(input('Please select a country (or worldwide)...')).lower()).strip()
        while (not self.wantedCountry.strip() in self.countriesList) and not self.wantedCountry in keyWords['WorldWide']:
            print(f'{self.wantedCountry} couldnt be found')
            self.wantedCountry = (str(input('Please select a country (or worldwide)...')).lower()).strip() 
        if self.wantedCountry in keyWords['WorldWide']:
            self.wantedCountry = "world"   
        self.AskDataType(self.wantedCountry)  
    
    def AskDataType(self,country):
        self.dataTypes = keyWords['Cases']+keyWords['Death']
        self.wantedCountry = country
        print("")
        self.wantedData = str(input('Please select the data type...')).lower()
        while not self.wantedData in self.dataTypes:
            print('Unknown Data!')
            self.wantedData = str(input('Please select the data type...')).lower()
        if self.wantedCountry != 'world':
            if self.wantedData in keyWords['Death']:
                print(f'Total Deaths In {self.wantedCountry.capitalize()} : {self.AddCommasBetweenNumber(self.GetCountryData(self.wantedCountry,self.wantedData))}')
            elif self.wantedData in keyWords['Cases']:
                print(f'Total Cases In {self.wantedCountry.capitalize()} : {self.AddCommasBetweenNumber(self.GetCountryData(self.wantedCountry,self.wantedData))}')
        else:
            if self.wantedData in keyWords['Death']:
                print(f'Total Deaths Worldwide : {self.AddCommasBetweenNumber(self.GetTotalDeaths())}')
            elif self.wantedData in keyWords['Cases']:
                print(f'Total Cases Worldwide : {self.AddCommasBetweenNumber(self.GetCountryData(self.wantedCountry,self.wantedData))}')

        self.AskWhichQuestion()
    
    def GetTotalDeaths(self):
        for x in self.data['worldwide']:
            if x['name'] == "Deaths:":
                return (x["value"])

    def GetTotalCases(self):
        for x in self.data['worldwide']:
            if x['name'] == "Coronavirus Cases:":
                return (x["value"])

    def WriteManual(self):
        print(f'Welcome to COVID-19 Tracker by Alp Tuna.\nInformation taken from: https://www.worldometers.info/coronavirus/')

    def __init__(self):
        try:
            self.WriteManual()
            self.RefreshData()
        except:
            print(f'An Error Occured! Please do the following.\n1) Check your internet connection\n2) There might be an update in the databases. Wait for a minute.')
    

d1 = Data()