import asyncio
import aiohttp
from bs4 import BeautifulSoup
from datetime import datetime
from dataclasses import dataclass
from itertools import groupby,chain
from .extra import crop, headers,get_student_year
from .exceptions import DateNotFoundError




@dataclass
class Journal():
  
  def __repr__(self) -> str:
    return f"{self.subject}[{self.mark}]"
  
  date : datetime
  subject : str 
  mark : str



def average(marks : list[Journal]) -> float | int:
  marks = list(chain(*[i.mark for i in marks]))
  marks = [float(i) for i in marks if i.isdigit()]
  average = round(sum(marks) / len(marks),2)
  return f"{average:g}"

class Marks():
  
  def __init__(self, __cookies : dict) -> None:
    self.__cookies = __cookies
  
  @staticmethod
  def __group_journals(journals : list[Journal]) -> list[Journal]:
    grouped_journals = {}
    for journal in journals:
        key = (journal.date, journal.subject)
        if key in grouped_journals:
            grouped_journals[key].mark += f", {journal.mark}"
        else:
            grouped_journals[key] = Journal(date=journal.date, mark=str(journal.mark), subject=journal.subject)
            
    # Преобразуем словарь обратно в список объектов Journal
    grouped_journals_list = list(grouped_journals.values())
    
    return grouped_journals_list
  
  def __marks(self) -> list[Journal]:

    async def pagination(session : aiohttp.ClientSession) -> int:
      response = await session.get('https://cabinet.ruobr.ru//student/progress/',cookies = self.__cookies,headers=headers)
      soup = BeautifulSoup(await response.text(), 'lxml')
      href_list = soup.find('ul',class_='pagination noprint').find_all('a')[-1]
      number = crop(str(href_list),'?page=', '"')
      return int(number)
    
    async def catch_page(url: str ,session : aiohttp.ClientSession):
      async with session.get(url=url,headers=headers,cookies = self.__cookies) as response:
        return await response.text()
        
    async def pages(timeout: float):
      tasks = []
      async with aiohttp.ClientSession() as session:
        pagination_num = await pagination(session)
        
        for num in range(pagination_num,0,-1):
          url = f"https://cabinet.ruobr.ru//student/progress/?page={num}"
          tasks.append(asyncio.create_task(catch_page(url,session))) 
          await asyncio.sleep(timeout)
          
        return await asyncio.gather(*tasks)
    
    async def sorter() -> list[Journal]:
      all_marks = []
      for page in await pages(0.0065):
        soup = BeautifulSoup(page, 'html.parser')
        data = list(map(str, soup.find_all('tr')))
        for t in data:
          cleantext = BeautifulSoup(t, 'html.parser').text.split('\n')[3:6]
          header = ['Дата', 'Дисциплина', 'Отметка']
          if cleantext != header:
            cleantext[2] = {'отлично': 5,'хорошо': 4,'удовлетворительно': 3,'неудовлетворительно': 2}[cleantext[2]]
            cleantext[0] = datetime.strptime(cleantext[0], '%d.%m.%Y')
            cleantext : Journal = Journal(date = cleantext[0], subject= cleantext[1],  mark = cleantext[2])
            all_marks.append(cleantext)
      
      
      all_marks.sort(key=lambda x: x.date)
      grouped_journals_list = self.__group_journals(all_marks)
      return grouped_journals_list
    
    async def main():
      return await sorter()
    
    return asyncio.run(main())

  def get_last(self) -> list[Journal]:
    import requests
    all_marks = []
    url = 'https://cabinet.ruobr.ru//student/progress/'
    response = requests.get(url,cookies=self.__cookies,headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    data = list(map(str, soup.find_all('tr')))
    for t in data:
      cleantext = BeautifulSoup(t, 'html.parser').text.split('\n')[3:6]
      header = ['Дата', 'Дисциплина', 'Отметка']
      if cleantext != header:
        cleantext[2] = {'отлично': 5,'хорошо': 4,'удовлетворительно': 3,'неудовлетворительно': 2}[cleantext[2]]
        cleantext[0] = datetime.strptime(cleantext[0], '%d.%m.%Y')
        cleantext : Journal = Journal(date = cleantext[0], subject= cleantext[1],  mark = cleantext[2])
        all_marks.append(cleantext)
            
    all_marks.sort(key=lambda x: x.date)
    grouped_journals_list = self.__group_journals(all_marks)
    return grouped_journals_list
    
  def get_all(self) -> list[Journal]:
    return self.__marks()

  def get_average(self, date : str) -> str:
    """
    param date - дата  для которой нужно вывести среднюю оценку по предметам
    """
    # Год
    if len(date.split('.')) == 1:
      croped_marks : list = [i for i in self.get_all() if i.date.strftime('%m.%Y') in get_student_year(date)]
    # Месяц
    elif len(date.split('.')) == 2:
      croped_marks : list = [i for i in self.get_all() if i.date.strftime('%m.%Y') in date]
    else: 
      raise DateNotFoundError(f"Could not find any data for {date}")
    
    if not croped_marks:
      raise DateNotFoundError(f"Could not find any data for {date}")
    
    
    croped_marks.sort(key=lambda x: x.subject)
    lessons = groupby(croped_marks, key=lambda y : y.subject)
    
    result = []
    for subject,marks in lessons:
      result.append(f'{subject}: {average(marks)}')
    return '\n'.join(result)
  
  def get_day_marks(self, date : str) -> str:
    croped_marks : list = [i for i in self.get_all() if i.date.strftime('%d.%m.%Y')==date]
    
    if not croped_marks:
      raise DateNotFoundError(f"Could not find any data for {date}")
    
    result = []
    for journal in croped_marks:
      result.append(f'{journal.subject}: {journal.mark}')
    return '\n'.join(result)
       
  