# coding: utf-8
from xml.dom import NotFoundErr

from django.conf import settings
from django.core.files import File
from django.core.validators import ValidationError
from django.contrib.auth.models import User
from django.http import Http404
from django.utils.translation import gettext as t
from rest_framework import exceptions
from rest_framework import mixins
from rest_framework import status
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.generics import get_object_or_404
from rest_framework.renderers import BrowsableAPIRenderer
from rest_framework.response import Response
from rest_framework.decorators import action

from onadata.apps.api.tools import get_media_file_response
from onadata.apps.api.permissions import ViewDjangoObjectPermissions
from onadata.apps.logger.models.attachment import Attachment
from onadata.apps.logger.models.instance import Instance
from onadata.apps.logger.models.xform import XForm
from onadata.apps.main.models.meta_data import MetaData
from onadata.apps.main.models.user_profile import UserProfile
from onadata.libs import filters
from onadata.libs.authentication import DigestAuthentication
from onadata.libs.mixins.openrosa_headers_mixin import OpenRosaHeadersMixin
from onadata.libs.renderers.renderers import TemplateXMLRenderer
from onadata.libs.serializers.xform_serializer import XFormListSerializer
from onadata.libs.serializers.xform_serializer import XFormManifestSerializer
from onadata.libs.utils.logger_tools import publish_form, publish_xml_form, \
    get_instance_or_404


def _extract_uuid(text):
    if isinstance(text, str):
        form_id_parts = text.split('/')

        if form_id_parts.__len__() < 2:
            raise ValidationError(t("Invalid formId %s." % text))

        text = form_id_parts[1]
        text = text[text.find("@key="):-1].replace("@key=", "")

        if text.startswith("uuid:"):
            text = text.replace("uuid:", "")

    return text


def _extract_id_string(formId):
    if isinstance(formId, str):
        return formId[0:formId.find('[')]

    return formId


def _parse_int(num):
    try:
        return num and int(num)
    except ValueError:
        pass


class DoXmlFormUpload:

    def __init__(self, xml_file, user):
        self.xml_file = xml_file
        self.user = user

    def publish(self):
        return publish_xml_form(self.xml_file, self.user)


class BriefcaseApi(OpenRosaHeadersMixin, mixins.CreateModelMixin,
                   mixins.RetrieveModelMixin, mixins.ListModelMixin,
                   viewsets.GenericViewSet):
    """
    Implements the [Briefcase Aggregate API](\
    https://code.google.com/p/opendatakit/wiki/BriefcaseAggregateAPI).
    """
    filter_backends = (filters.AnonDjangoObjectPermissionFilter,)
    queryset = XForm.objects.all()
    permission_classes = (permissions.IsAuthenticated,
                          ViewDjangoObjectPermissions)
    renderer_classes = (TemplateXMLRenderer, BrowsableAPIRenderer)
    serializer_class = XFormListSerializer
    template_name = 'openrosa_response.xml'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Respect DEFAULT_AUTHENTICATION_CLASSES, but also ensure that the
        # previously hard-coded authentication classes are included first
        authentication_classes = [
            DigestAuthentication,
        ]
        self.authentication_classes = authentication_classes + [
            auth_class
            for auth_class in self.authentication_classes
            if auth_class not in authentication_classes
        ]

    def get_object(self):
        formId = self.request.GET.get('formId', '')
        id_string = _extract_id_string(formId)
        uuid = _extract_uuid(formId)
        username = self.kwargs.get('username')

        obj = get_instance_or_404(xform__user__username__iexact=username,
                                  xform__id_string__exact=id_string,
                                  uuid=uuid)
        self.check_object_permissions(self.request, obj.xform)

        return obj

    def filter_queryset(self, queryset):
        username = self.kwargs.get('username')
        if username is None and self.request.user.is_anonymous:
            # raises a permission denied exception, forces authentication
            self.permission_denied(self.request)

        if username is not None and self.request.user.is_anonymous:
            profile = get_object_or_404(
                UserProfile, user__username=username.lower())

            if profile.require_auth:
                # raises a permission denied exception, forces authentication
                self.permission_denied(self.request)
            else:
                queryset = queryset.filter(user=profile.user)
        else:
            queryset = super().filter_queryset(queryset)

        formId = self.request.GET.get('formId', '')

        if formId.find('[') != -1:
            formId = _extract_id_string(formId)

        xform = get_object_or_404(queryset, id_string__exact=formId)
        self.check_object_permissions(self.request, xform)
        instances = Instance.objects.filter(xform=xform).order_by('pk')
        num_entries = self.request.GET.get('numEntries')
        cursor = self.request.GET.get('cursor')

        cursor = _parse_int(cursor)
        if cursor:
            instances = instances.filter(pk__gt=cursor)

        num_entries = _parse_int(num_entries)
        if num_entries:
            instances = instances[:num_entries]

        if instances.count():
            last_instance = instances[instances.count() - 1]
            self.resumptionCursor = last_instance.pk
        elif instances.count() == 0 and cursor:
            self.resumptionCursor = cursor
        else:
            self.resumptionCursor = 0

        return instances

    def create(self, request, *args, **kwargs):
        if request.method.upper() == 'HEAD':
            return Response(status=status.HTTP_204_NO_CONTENT,
                            headers=self.get_openrosa_headers(request),
                            template_name=self.template_name)

        xform_def = request.FILES.get('form_def_file', None)
        response_status = status.HTTP_201_CREATED
        username = kwargs.get('username')
        form_user = (username and get_object_or_404(User, username=username)) \
            or request.user

        if not request.user.has_perm(
            'can_add_xform',
            UserProfile.objects.get_or_create(user=form_user)[0]
        ):
            raise exceptions.PermissionDenied(
                detail=t("User %(user)s has no permission to add xforms to "
                         "account %(account)s" %
                         {'user': request.user.username,
                          'account': form_user.username}))
        data = {}

        if isinstance(xform_def, File):
            do_form_upload = DoXmlFormUpload(xform_def, form_user)
            dd = publish_form(do_form_upload.publish)

            if isinstance(dd, XForm):
                data['message'] = t(
                    "%s successfully published." % dd.id_string)
            else:
                data['message'] = dd['text']
                response_status = status.HTTP_400_BAD_REQUEST
        else:
            data['message'] = t("Missing xml file.")
            response_status = status.HTTP_400_BAD_REQUEST

        return Response(data, status=response_status,
                        headers=self.get_openrosa_headers(request,
                                                          location=False),
                        template_name=self.template_name)

    def list(self, request, *args, **kwargs):
        self.object_list = self.filter_queryset(self.get_queryset())

        data = {'instances': self.object_list,
                'resumptionCursor': self.resumptionCursor}

        return Response(data,
                        headers=self.get_openrosa_headers(request,
                                                          location=False),
                        template_name='submissionList.xml')

    def retrieve(self, request, *args, **kwargs):
        self.object = self.get_object()

        submission_xml_root_node = self.object.get_root_node()
        submission_xml_root_node.setAttribute(
            'instanceID', 'uuid:%s' % self.object.uuid)
        submission_xml_root_node.setAttribute(
            'submissionDate', self.object.date_created.isoformat()
        )

        # Added this because of https://github.com/onaio/onadata/pull/2139
        # Should bring support to ODK v1.17+
        if settings.SUPPORT_BRIEFCASE_SUBMISSION_DATE:
            # Remove namespace attribute if any
            try:
                submission_xml_root_node.removeAttribute('xmlns')
            except NotFoundErr:
                pass

        data = {
            'submission_data': submission_xml_root_node.toxml(),
            'media_files': Attachment.objects.filter(instance=self.object),
            'host': request.build_absolute_uri().replace(
                request.get_full_path(), '')
        }
        return Response(
            data,
            headers=self.get_openrosa_headers(request, location=False),
            template_name='downloadSubmission.xml',
        )

    @action(detail=True, methods=['GET'])
    def manifest(self, request, *args, **kwargs):
        self.object = self.get_object()
        object_list = MetaData.objects.filter(
            data_type__in=MetaData.MEDIA_FILES_TYPE, xform=self.object
        )
        context = self.get_serializer_context()
        serializer = XFormManifestSerializer(object_list, many=True,
                                             context=context)

        return Response(serializer.data,
                        headers=self.get_openrosa_headers(request,
                                                          location=False))

    @action(detail=True, methods=['GET'])
    def media(self, request, *args, **kwargs):
        self.object = self.get_object()
        pk = kwargs.get('metadata')

        if not pk:
            raise Http404()

        meta_obj = get_object_or_404(
            MetaData,
            data_type__in=MetaData.MEDIA_FILES_TYPE,
            xform=self.object,
            pk=pk,
        )

        return get_media_file_response(meta_obj, request)
