import base64
import json
import tempfile
import os
from . import box
from django.shortcuts import render, redirect
from django.http import FileResponse, HttpResponse
from django import forms


class PatternForm(forms.Form):
    height = forms.CharField()
    width = forms.CharField()
    depth = forms.CharField()
    front_angle = forms.CharField()
    back_angle = forms.CharField()
    left_angle = forms.CharField()
    right_angle = forms.CharField()
    top_angle = forms.CharField()
    bottom_angle = forms.CharField()


def index(request):
    form = PatternForm()
    return render(request, "pattern_form.html", {'form': form})


def preview(request):
    tmp = tempfile.NamedTemporaryFile(suffix=".png")
    print(tmp.name)

    data = json.loads(request.body)
    paper = data['paper']
    tuckbox = data['tuckbox']
    print("paper: ", paper)
    print("tuckbox: ", tuckbox)

    # Would need to fill the faces and the options to use this again
    box.create_box_file(tmp.name, paper, tuckbox, {}, {})

    encoded_string = base64.b64encode(tmp.read())

    return HttpResponse(encoded_string, content_type="image/png")


def pattern(request):
    if request.method != 'POST':
        return redirect('index')

    form = PatternForm(request.POST)
    if not form.is_valid():
        print("Something went wrong in the form")
        return redirect('index')

    result_pdf = tempfile.NamedTemporaryFile(delete=True, suffix=".pdf")
    print(result_pdf.name)

    # hardcode for now
    paper = {'width': 100, 'height': 100}
    tuckbox = {'width': float(form.cleaned_data['width']),
               'height': float(form.cleaned_data['height']),
               'depth': float(form.cleaned_data['depth'])}
    faces = {}
    for face in ['front', 'back', 'top', 'bottom', 'left', 'right']:
        if face in request.FILES:
            faces[face] = request.FILES[face]

    options = {'front_angle': int(form.cleaned_data['front_angle']),
               'back_angle': int(form.cleaned_data['back_angle']),
               'left_angle': int(form.cleaned_data['left_angle']),
               'right_angle': int(form.cleaned_data['right_angle']),
               'top_angle': int(form.cleaned_data['top_angle']),
               'bottom_angle': int(form.cleaned_data['bottom_angle']),
               }

    box.create_box_file(result_pdf.name, paper, tuckbox, faces, options)

    return FileResponse(result_pdf)
