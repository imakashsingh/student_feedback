from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponse
from django.views.generic import FormView
from feedback.forms.feedback import *
import pickle
from feedback.models import College
from matplotlib import pyplot as plt
import numpy as np
from django.urls import resolve
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from student_feedback.settings import IMAGES_FOLDER,MODEL_FOLDER,CONFIG_FOLDER



def survey(results, category_names):
    """
    Parameters
    ----------
    results : dict
        A mapping from question labels to a list of answers per category.
        It is assumed all lists contain the same number of entries and that
        it matches the length of *category_names*.
    category_names : list of str
        The category labels.
    """
    labels = list(results.keys())
    data = np.array(list(results.values()))
    data_cum = data.cumsum(axis=1)
    category_colors = plt.get_cmap('RdYlGn')(
        np.linspace(0.15, 0.85, data.shape[1]))

    fig, ax = plt.subplots(figsize=(9.2, 5))
    ax.invert_yaxis()
    ax.xaxis.set_visible(False)
    ax.set_xlim(0, np.sum(data, axis=1).max())

    for i, (colname, color) in enumerate(zip(category_names, category_colors)):
        widths = data[:, i]
        starts = data_cum[:, i] - widths
        ax.barh(labels, widths, left=starts, height=0.5,
                label=colname, color=color)
        xcenters = starts + widths / 2

        r, g, b, _ = color
        text_color = 'white' if r * g * b < 0.5 else 'darkgrey'
        for y, (x, c) in enumerate(zip(xcenters, widths)):
            ax.text(x, y, str(int(c)), ha='center', va='center',
                    color=text_color)
    ax.legend(ncol=len(category_names), bbox_to_anchor=(0, 1),
              loc='lower left', fontsize='small')
    plt.title('Frequency Of Rating Stars for each Subject',y=1.08)
    plt.savefig(IMAGES_FOLDER+'survey.png')
    #return fig, ax

def pie_chart(labels,sizes,title,fname):
    fig1, ax1 = plt.subplots()
    ax1.pie(sizes, labels=labels, autopct='%1.1f%%',
            shadow=True, startangle=90)
    ax1.axis('equal')
    plt.title(title)
    plt.savefig(IMAGES_FOLDER+fname+'.png')

def bar_graph(xlabel,ylabel,title,fname):
    plt.figure(figsize=(7.0, 5.0))
    plt.bar(x=xlabel,height=ylabel,width=0.7,align='center')
    plt.title(title)
    plt.savefig(IMAGES_FOLDER+fname+'.png')


def get_no_of_subjects():
    file = open(CONFIG_FOLDER + 'config.txt', 'r')
    sub_cn = file.readline()
    sub_cn = sub_cn.strip()
    temp_list = sub_cn.split(':')
    no_of_subs = int(temp_list[1])
    file.close()
    return no_of_subs

def get_subjects_list():
    sub_list = []
    file = open(CONFIG_FOLDER+'config.txt', 'r')
    file.readline()
    subs = file.readlines()
    for each_sub in subs:
        sub_list.append(each_sub.strip())
    file.close()
    return sub_list

def check_for_sub_dup(sub_name):
    sub_list = get_subjects_list()
    if sub_name in sub_list:
        return True
    else:
        return False

def write_to_config(sub_count,sub_list):
    file = open(CONFIG_FOLDER + 'config.txt', 'w')
    file.write('Subjects : '+(str(sub_count))+'\n')
    for sub in sub_list:
        file.write(sub+'\n')
    file.close()

class SubmitFeedbackView(FormView):
    ips = []
    no_of_sub = get_no_of_subjects()
    sub_list = get_subjects_list()
    print(no_of_sub)
    print(sub_list)
    def get(self, request, *args, **kwargs):
        form = SubmitFeedback()
        print(SubmitFeedbackView.no_of_sub)
        context = {
            'form' : form,
            'no_of_sub' : SubmitFeedbackView.no_of_sub,
            'sub_list' : SubmitFeedbackView.sub_list,
        }
        return render(request,
                      template_name="feedback/SubmitFeedback.html",context=context)

    def post(self, request, *args, **kwargs):
        rating_list = ''
        feedback_list = ''
        print('Form Enter')
        form =SubmitFeedback(request.POST)
        print('Form Exit')
        if form.is_valid():
            print("system no "+str(request.POST.get('system_no')))
            print(SubmitFeedbackView.ips)
            if(request.POST['system_no'] in SubmitFeedbackView.ips):
                return render(request, template_name="feedback/Restrict.html", context={'form': form})
            else:
                system_no = request.POST.get('system_no')
                gender = request.POST.get('gender')
                for i in SubmitFeedbackView.sub_list:
                    print(i)
                    rating_list += request.POST.get("rt "+i)
                    rating_list += '###'
                print(rating_list)
                for i in SubmitFeedbackView.sub_list:
                    feedback_list += request.POST.get("fd "+i)
                    feedback_list += '###'
                print(feedback_list)
                SubmitFeedbackView.ips.append(request.POST['system_no'])
                print(SubmitFeedbackView.ips)
                c = College(system_no = system_no,gender = gender,feedback=feedback_list,rating = rating_list)
                c.save()
                return render(request, template_name="feedback/ThankYou.html", context={'form': form})
        return render(request,template_name="feedback/SubmitFeedback.html",context={'form': form})



class PerformAnalysis(LoginRequiredMixin,FormView):
    login_url = '/feedback/loginppage/'
    no_of_sub = get_no_of_subjects()
    sub_list = get_subjects_list()
    def get(self, request, *args, **kwargs):
        with open(MODEL_FOLDER+'model_vec', 'rb') as fv:
            vec = pickle.load(fv)
        with open(MODEL_FOLDER+'model_pickle', 'rb') as fm:
            mp = pickle.load(fm)
        rating_frequency = [[0 for i in range(5) ] for j in range(PerformAnalysis.no_of_sub)]
        sub_pos_rat = PerformAnalysis.no_of_sub * [0]
        sub_pos_rev = PerformAnalysis.no_of_sub * [0]
        gender_analysis = [[0 for i in range(2)] for j in range(PerformAnalysis.no_of_sub)]
        data = College.objects.all().values()
        total_rev_count = len(data)
        print(total_rev_count)
        print(rating_frequency)
        print(gender_analysis)
        #print(data)
        for row in data:
            rating_list = row['rating'].split('###')
            feedback_list = row['feedback'].split('###')
            for i in range(PerformAnalysis.no_of_sub):
                sub_pos_rat[i] += int(rating_list[i])
                sub_pos_rev[i] += int(mp.predict(vec.transform([feedback_list[i]]))[0])
                rating_frequency[i][int(rating_list[i]) - 1] += 1
        print(sub_pos_rat)
        print(sub_pos_rev)
        print(rating_frequency)

        result = {}
        for i in range(PerformAnalysis.no_of_sub):
            result[PerformAnalysis.sub_list[i]] = rating_frequency[i]
        print(result)
        print(PerformAnalysis.sub_list)

        bar_graph(PerformAnalysis.sub_list,sub_pos_rev,'Bargraph','def')

        category_names = ['1','2','3','4','5']
        survey(result,category_names)
        pie_labels = tuple(PerformAnalysis.sub_list)
        pie_chart(pie_labels,sub_pos_rev,'Positive Feedback Distribution','pie')

        for i in range(PerformAnalysis.no_of_sub):
            pie_chart(('Positive', 'Negative'), [sub_pos_rev[i], total_rev_count - sub_pos_rev[i]], PerformAnalysis.sub_list[i], PerformAnalysis.sub_list[i])

        context = {
            'subjects_list':PerformAnalysis.sub_list
        }

        return render(request,template_name="feedback/analysisChart.html",context=context)

class LoginView(FormView):
    def get(self, request, *args, **kwargs):
        form = Login_form()
        return render(request, template_name="feedback/LoginForm.html", context={'form':form})

    def post(self, request, *args, **kwargs):
        if request.method == 'POST':
            form = AuthenticationForm(request.POST)
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(username = username,password = password)
            if user is not None:
                login(request,user)
                return redirect('adminop')
            else:
                return render(request,'feedback/LoginForm.html',{'form':form,'loginerror':'true','msg':'Username Or Password Incorrect'})
        else:
            form = AuthenticationForm()
            return render(request, 'feedback/LoginForm.html', {'form': form})

@login_required
def logout_func(request):
    logout(request)
    return redirect('index')

class LandingPage(FormView):
    def get(self, request, *args, **kwargs):
        if resolve(request.path_info).url_name == 'session_started':
            return render(request,template_name="feedback/feedbackStarted.html",context={})
        return render(request, template_name="feedback/index.html", context={})

    def post(self, request, *args, **kwargs):
        pass

class AdminOptions(LoginRequiredMixin,FormView):
    login_url = '/feedback/loginppage/'
    def get(self, request, *args, **kwargs):
        return render(request, template_name="feedback/adminOptions.html", context={})

    def post(self, request, *args, **kwargs):
        pass


class Subjects(LoginRequiredMixin,FormView):
    login_url = '/feedback/loginppage/'
    def get(self, request, *args, **kwargs):
        context = {
            'no_of_sub': get_no_of_subjects(),
            'sub_list': get_subjects_list(),
        }
        return render(request, template_name="feedback/SubjectsPage.html", context=context)

    def post(self, request, *args, **kwargs):
        pass

class SubjectOperations(LoginRequiredMixin,FormView):
    login_url = '/feedback/loginppage/'
    def get(self, request, *args, **kwargs):
        if resolve(request.path_info).url_name == 'delete_subject':
            sub_name = kwargs.get('sub')
            sub_list = get_subjects_list()
            sub_list.remove(sub_name)
            write_to_config(len(sub_list),sub_list)
            return redirect('subjects')
        elif resolve(request.path_info).url_name == 'edit_subject':
            context = {
                'edit_subject' : kwargs.get('sub')
            }
            return render(request, template_name="feedback/editSubject.html", context=context)
        elif resolve(request.path_info).url_name == "delete_all":
            sub_list = []
            write_to_config(len(sub_list),sub_list)
            return redirect('subjects')
        return render(request, template_name="feedback/addSubject.html", context={})

    def post(self, request, *args, **kwargs):
        if resolve(request.path_info).url_name == 'add_subject':
            form = AddSubject(request.POST)
            if form.is_valid():
                sub_name = str(request.POST.get('subject_name')).upper()
                if(check_for_sub_dup(sub_name)):
                    return render(request,template_name="feedback/SubjectExists.html",context={})
                else:
                    sub_list = get_subjects_list()
                    sub_list.append(sub_name)
                    write_to_config(len(sub_list),sub_list)
            return redirect('subjects')
        elif resolve(request.path_info).url_name == "edit_subject":
            form = AddSubject(request.POST)
            if form.is_valid():
                sub_name = str(request.POST.get('subject_name')).upper()
                sub_list = get_subjects_list()
                sub_list.append(sub_name)
                if(sub_list.count(sub_name) >= 2):
                    return render(request, template_name="feedback/SubjectExists.html", context={})
                else:
                    write_to_config(len(sub_list), sub_list)
            return redirect('subjects')

