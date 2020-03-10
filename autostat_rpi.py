import os

os.chdir('~/Documents/GitHub/COVIDanalysis')

import predict
import mldistr2

with open('daily_update.txt','r') as file:
  previous = file.read()
  file.close()
with open('daily_update.txt','w') as file:
  file.write('=' * 80 + '\n')
  file.write(predict.report)
  file.write('-' * 80 + '\n')
  file.write(mldistr2.report)
  file.write(previous)
  file.close()

os.system('git add -A')
os.system("git commit -m 'daily update'")
os.system("git push")
