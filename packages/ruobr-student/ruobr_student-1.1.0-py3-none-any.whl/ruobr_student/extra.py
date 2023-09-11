from datetime import datetime
from dateutil.relativedelta import relativedelta

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Referer': 'https://cabinet.ruobr.ru/',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36',
}

def crop(__string: str, start:str, end:str) -> str:
  s = __string.find(start) + len(start)
  __string = __string[s:]
  e = __string.find(end)
  return __string[:e]

def get_student_year(__year : str) -> list :
  start = datetime.strptime(f'0109{__year}', "%d%m%Y").date()
  dates = [start.strftime('%m.%Y')]+ [(start + relativedelta(months=date)).strftime('%m.%Y') for date in range(1, 10)]
  return dates

