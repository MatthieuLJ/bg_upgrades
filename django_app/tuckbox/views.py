import base64
import json
import tempfile
import os
import shutil
from . import box, tasks
from django.conf import settings
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
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
    folding_guides = forms.CheckboxInput()
    folds_dashed = forms.CheckboxInput()


def index(request):
    form = PatternForm()
    return render(request, "pattern_form.html.j2", {'form': form})


def preview(request):
    tmp = tempfile.NamedTemporaryFile(delete=True, suffix=".png")

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
    options = data['options']

    my_box = box.TuckBoxDrawing(tuckbox, paper, {}, options)

    return HttpResponse(status=200 if my_box.will_it_fit() else 406)


def pattern(request):
    if request.method != 'POST':
        return redirect('index')
    
    form = PatternForm(request.POST)
    if not form.is_valid():
        return JsonResponse(data={'error_text': "Form has invalid data"}, status=400)

    paper = {'width': float(form.cleaned_data['paper_width']),
             'height': float(form.cleaned_data['paper_height'])}
    tuckbox = {'width': float(form.cleaned_data['width']),
               'height': float(form.cleaned_data['height']),
               'depth': float(form.cleaned_data['depth'])}
    faces = {}
    options = {}

    for face in ['front', 'back', 'top', 'bottom', 'left', 'right']:
        if face + "_plain_color" in form.data:
            #using color rather than image
            faces[face] = form.data[face + "_color"]
        elif face in request.FILES:
            # Need to copy the contents to a temporary file
            
            _, file_extension = os.path.splitext(request.FILES[face].name)
            new_file = tempfile.NamedTemporaryFile(delete=False, prefix="_"+face, suffix=file_extension)
            shutil.copyfileobj(request.FILES[face], new_file)
            faces[face] = new_file.name
            options[face+"_angle"] = int(form.cleaned_data[face+"_angle"])

    options["folding_guides"] = "folding_guides" in form.data
    options["folds_dashed"] = "folds_dashed" in form.data
    options["two_openings"] = "two_openings" in form.data
    options["two_pages"] = "two_pages" in form.data

    result_pdf = tempfile.NamedTemporaryFile(
        delete=False, dir=settings.TMP_ROOT, suffix=".pdf")

    parameters = {
        'tuckbox': tuckbox,
        'paper': paper,
        'options': options,
        'faces': faces,
        'filename': result_pdf.name,
    }

    async_result = tasks.build_box.delay(parameters)
    
    return JsonResponse(data={'task_id': async_result.id, 'url': settings.TMP_URL + os.path.basename(result_pdf.name)}, status=202)


def check_progress(request):
    task_id = request.GET.get('task_id', 0)
    try:
        state, info = tasks.get_status(task_id)
        data = {'task_id': task_id,
                'state': state,
                'info': info}
        return JsonResponse(data, status=200)
    except:
        data = {'task_id': task_id,
                'state': 'FAILURE' }
        return JsonResponse(data, status=200)
