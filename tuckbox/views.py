import json
import tempfile
from . import box
from django.shortcuts import render, redirect
from django.http import FileResponse
from django import forms

class PatternForm(forms.Form):
    height = forms.CharField()
    width = forms.CharField()
    depth = forms.CharField()

    def clean(self):
        cleaned_data = super().clean()
        # Here eventually check everything is good and fits...

def index(request):
    form = PatternForm()
    return render(request, "pattern_form.html", { 'form': form })

def preview(request):
    tmp = tempfile.NamedTemporaryFile(suffix=".png")
    print(tmp.name)


    data = json.loads(request.body)
    # hardcode for now
    paper = data['paper']
    tuckbox = data['tuckbox']
    # paper = { 'width': 100, 'height': 100}
    # tuckbox = { 'width': float(form.cleaned_data['width']),
            # 'height': float(form.cleaned_data['height']),
            # 'depth': float(form.cleaned_data['depth'])}
    print("paper: ", paper)
    print("tuckbox: ", tuckbox)

    box.create_box_file(tmp.name, paper, tuckbox)

    return FileResponse(tmp)

def pattern(request):
    if request.method != 'POST':
        return redirect('index')

    form = PatternForm(request.POST)
    if not form.is_valid():
        print("Something went wrong in the form")
        return redirect('index')

    tmp = tempfile.NamedTemporaryFile(suffix=".pdf")
    print(tmp.name)

    # hardcode for now
    paper = { 'width': 100, 'height': 100}
    tuckbox = { 'width': float(form.cleaned_data['width']),
            'height': float(form.cleaned_data['height']),
            'depth': float(form.cleaned_data['depth'])}

    box.create_box_file(tmp.name, paper, tuckbox)

    return FileResponse(tmp)
