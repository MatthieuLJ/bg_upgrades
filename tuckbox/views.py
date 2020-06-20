import base64
import json
import tempfile
import os
from . import box, tasks
from django.shortcuts import render, redirect
from django.http import FileResponse, HttpResponse, JsonResponse
from django import forms


class PatternForm(forms.Form):
    height = forms.CharField()
    width = forms.CharField()
    depth = forms.CharField()
    paper_height = forms.CharField()
    paper_width = forms.CharField()
    front_angle = forms.CharField()
    back_angle = forms.CharField()
    left_angle = forms.CharField()
    right_angle = forms.CharField()
    top_angle = forms.CharField()
    bottom_angle = forms.CharField()
    front_smart_rescale = forms.CheckboxInput()
    back_smart_rescale = forms.CheckboxInput()
    left_smart_rescale = forms.CheckboxInput()
    right_smart_rescale = forms.CheckboxInput()
    bottom_smart_rescale = forms.CheckboxInput()
    top_smart_rescale = forms.CheckboxInput()
    folding_guides = forms.CheckboxInput()
    folds_dashed = forms.CheckboxInput()


def index(request):
    form = PatternForm()
    return render(request, "pattern_form.html.j2", {'form': form})


def preview(request):
    tmp = tempfile.NamedTemporaryFile(delete=True, suffix=".png")
    print(tmp.name)

    data = json.loads(request.body)
    paper = data['paper']
    tuckbox = data['tuckbox']

    # Would need to fill the faces and the options to use this again
    my_box = box.TuckBoxDrawing(tuckbox, paper, {}, {})
    my_box.create_box_file(tmp.name)

    encoded_string = base64.b64encode(tmp.read())

    return HttpResponse(encoded_string, content_type="image/png")


def check_fit(request):
    data = json.loads(request.body)
    paper = data['paper']
    tuckbox = data['tuckbox']

    my_box = box.TuckBoxDrawing(tuckbox, paper, {}, {})

    return HttpResponse(status=200 if my_box.will_it_fit() else 406)

def pattern(request):
    if request.method != 'POST':
        return redirect('index')

    form = PatternForm(request.POST)
    if not form.is_valid():
        return JsonResponse(data= {'error_text': "Form has invalid data"}, status=400)

    paper = {'width': float(form.cleaned_data['paper_width']),
             'height': float(form.cleaned_data['paper_height'])}
    tuckbox = {'width': float(form.cleaned_data['width']),
               'height': float(form.cleaned_data['height']),
               'depth': float(form.cleaned_data['depth'])}
    faces = {}
    options = {}

    for face in ['front', 'back', 'top', 'bottom', 'left', 'right']:
        if face in request.FILES:
            faces[face] = request.FILES[face]
        options[face+"_angle"] = int(form.cleaned_data[face+"_angle"])
        options[face+"_smart_rescale"] = face+"_smart_rescale" in form.data

    options["folding_guides"] = "folding_guides" in form.data
    options["folds_dashed"] = "folds_dashed" in form.data

    parameters = {
        'tuckbox': tuckbox,
        'paper': paper,
        'options': options,
        'faces': faces,
    }

    async_result = tasks.build_box.delay(parameters)

    return JsonResponse(data={'task_id': async_result.id}, status=202)
