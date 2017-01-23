# -*- coding: utf-8 -*-

import json
from datetime import datetime

from django.http import HttpResponseRedirect, HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.contrib import auth
from django.contrib.auth.models import User

from core.jsonresponse import create_response
import models as project_models

@login_required
def bug_list(request):
    """
    需求列表
    """
    jsons = {'items':[]}
    project_id = request.GET.get('project_id', -1)

    c = RequestContext(request, {
        'jsons': jsons,
        'project_id': project_id,
        'first_nav': 'bug'
    })
    return render_to_response('bug/bug_list.html', c)


def get_bug(request):
    """
    获取需求
    """
    project_id = request.GET.get('project_id', -1)
    users = User.objects.all()
    user_id2name = {user.id:user.first_name for user in users}
    bugs = project_models.Requirement.objects.filter(project_id=project_id, require_type=1).order_by('-id')
    # require_bugs = []
    # if bugs:
    #     require_bugs = [{
    #         'id': bug.id,
    #         'status': requirement.status,
    #         'name': bug.name,
    #         'creator': bug.creator,
    #         'participant': bug.creator if not bug.participant else ('%s,%s')%(bug.creator,bug.participant),
    #         'created_at': '' if not bug.created_at else bug.created_at.strftime("%Y-%m-%d %H:%M"),
    #         'end_at': '-----' if not bug.end_at else bug.end_at.strftime("%Y-%m-%d %H:%M")
    #     }for bug in bugs]
    # print require_bugs,"========wwww===="

    require_bugs = []
    for bug in bugs:
        participant_name = []
        participant_name.append(bug.creator)
        participants =  [] if not bug.participant else bug.participant.split(',')
        for participant in participants:
            if participant and int(participant) in user_id2name and participant != bug.creator_id:
                participant = int(participant)
                participant_name.append(user_id2name[participant])

        require_bugs.append({
            'id': bug.id,
            'status': bug.status,
            'require_type': bug.require_type,
            'name': bug.name,
            'remark': bug.remark,
            'creator': bug.creator,
            'participant_name': ','.join(participant_name),
            'created_at': '' if not bug.created_at else bug.created_at.strftime("%Y-%m-%d %H:%M"),
            'end_at': '-----' if not bug.end_at else bug.end_at.strftime("%Y-%m-%d %H:%M")
        })
    response = create_response(200)
    response.data = {
        'require_bugs': json.dumps(require_bugs)
    }
    return response.get_response()

def add_bug(request):
    """
    添加需求
    """
    name = request.POST.get('name', '')
    remark = request.POST.get('remark', '')
    project_id = request.POST.get('project_id', -1)

    try:
        acount_name = User.objects.get(id=request.user.id).first_name
        project_models.Requirement.objects.create(
            project_id = project_id,
            name= name,
            remark= remark,
            creator= acount_name,
            creator_id = request.user.id,
            require_type = 1
        )
    except Exception, e:
        print e
    
    response = create_response(200)
    return response.get_response()