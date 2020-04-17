import csv
import os
import django
from django.core.exceptions import ValidationError
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'student_feedback.settings')
django.setup()

from feedback.models import*
def load_data_into_table():
    fields = []
    with open("Data Collection.csv", 'r') as csvfile:
        csvreader = csv.reader(csvfile)
        fields = csvreader.__next__()

        for data in csvreader:
            rating_list = ''
            feedback_list = ''
            rating_list = data[2] + '###' + data[4] + '###' + data[6] + '###' + data[8] + '###'
            feedback_list += data[3] + '###' + data[5] + '###' + data[7] + '###' + data[9] + '###'
            try:
                c = College(system_no = int(data[0]),gender = data[1],rating = rating_list,feedback = feedback_list)
                c.save()
            except ValidationError:
                print('Validation Error')

if __name__ == '__main__':
    load_data_into_table()