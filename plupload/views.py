import os
import datetime
import json

from django.http import HttpResponse, Http404
from django.conf import settings
from django.template import RequestContext
from django.shortcuts import render_to_response


def upload(request):
    if request.method == "POST":
        # Handle the upload here
        pass
    template_vars_template = RequestContext(request)
    return render_to_response('upload_form.html',
                              template_vars_template)


def upload_custom(request):
    if request.method == "POST":
        # Handle the upload here
        pass
    # I'm using a dir with today date as name,
    # so i send the constructed url for the latest file load
    # and for the delete file url
    todays_date = datetime.datetime.now().strftime("%Y/%m/%d/")

    delete_file_url = "/del_file/"+todays_date
    media_folder = "/static/media/csv_files/"+todays_date
    all_files_url = "/get_all_files/"+todays_date
    template_vars = dict(delete_file_url=delete_file_url,
                         media_folder=media_folder,
                         all_files_url=all_files_url)
    template_vars_template = RequestContext(request, template_vars)
    return render_to_response('custom_queue.html',
                              template_vars_template)


def upload_file(request):
    if request.method == 'POST' and request.FILES:
        dir_fd = os.open(
            settings.UPLOAD_ROOT,
            os.O_RDONLY
        )
        os.fchdir(dir_fd)

        for _file in request.FILES:
            handle_uploaded_file(request.FILES[_file],
                                 request.POST.get('chunk', 0),
                                 request.POST['name'])
        os.close(dir_fd)
        # response only to notify plUpload that the upload was successful
        return HttpResponse()
    else:
        raise Http404


def handle_uploaded_file(f, chunk, filename):
    """
    Here you can do whatever you like with your files, like resize them if they
    are images
    :param f: the file
    :param chunk: number of chunk to save
    """

    if int(chunk) > 0:
        # opens for append
        _file = open(filename, 'ab')
    else:
        # erases content
        _file = open(filename, 'wb')

    if f.multiple_chunks:
        for chunk in f.chunks():
            _file.write(chunk)
    else:
        _file.write(f.read())


def del_file(request, year, month, day):
    if 'file' in request.GET:
        dir_name = str.join("-", [year, month, day])
        dir_path = settings.UPLOAD_ROOT
        files = os.listdir(dir_path+dir_name)
        dir_fd = os.open(dir_path+dir_name, os.O_RDONLY)
        os.fchdir(dir_fd)

        for _file in files:
            if str(_file) == request.GET['file']:
                os.remove(_file)
        os.close(dir_fd)
        result = 1
    else:
        result = 0
    return HttpResponse(result)


def get_all_files(request, year, month, day):
    dir_name = str.join("-", [year, month, day])
    dir_path = settings.UPLOAD_ROOT,
    dir_fd = os.open(dir_path+dir_name, os.O_RDONLY)
    os.fchdir(dir_fd)
    filelist = os.listdir(os.getcwd())
    filelist = filter(lambda x: not os.path.isdir(x), filelist)
    files = []
    for file_ in filelist:
        if not file_.startswith("."):
            files.append(dict(name=file_.split(".")[0], filename=file_))
    return HttpResponse(content=json.dumps(files), status=200,
                        content_type="application/json")
