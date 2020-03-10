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
