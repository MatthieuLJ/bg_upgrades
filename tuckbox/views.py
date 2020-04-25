from django.shortcuts import render, redirect

def index(request):
    return render(request, "pattern_form.html")

def pattern(request):
    return redirect('index')

