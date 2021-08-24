######################################################################
# @author      : bidaya0 (bidaya0@$HOSTNAME)
# @file        : api_route_cover_rate
# @created     : Friday Aug 20, 2021 16:20:10 CST
#
# @description :
######################################################################

from iast.base.project_version import get_project_version, get_project_version_by_id
from dongtai.models.agent import IastAgent
from dongtai.endpoint import R, UserEndPoint
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from iast.utils import checkcover, batch_queryset
from iast.utils import extend_schema_with_envcheck
from dongtai.models.api_route import IastApiRoute

class ApiRouteCoverRate(UserEndPoint):
    @extend_schema_with_envcheck([{
        'name': 'project_id',
        'type': int
    }, {
        'name': 'version_id',
        'type': int
    }])
    def get(self, request):
        project_id = request.query_params.get('project_id', None)
        version_id = request.query_params.get('version_id', None)
        auth_users = self.get_auth_users(request.user)
        if not version_id:
            current_project_version = get_project_version(
                project_id, auth_users)
        else:
            current_project_version = get_project_version_by_id(version_id)
        agents = IastAgent.objects.filter(
            user__in=auth_users,
            bind_project_id=project_id,
            project_version_id=current_project_version.get("version_id",
                                                           0)).values("id")
        q = Q(agent_id__in=[_['id'] for _ in agents])
        queryset = IastApiRoute.objects.filter(q)
        total = queryset.count()
        cover_count = 0
        for api_route in batch_queryset(queryset):
            if checkcover(api_route,agents):
                cover_count += 1
        cover_rate = "{:.2f}%".format(cover_count / total)
        return R.success(msg=_('API coverage rate obtained successfully'),
                         data={'cover_rate': cover_rate})
