import re
import string
import unicodedata

from django.core.files.uploadedfile import SimpleUploadedFile
from django.forms import formset_factory
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.template.loader import get_template
from django.views import generic
from weasyprint import HTML

from . import forms
from huscy.project_consents.models import ProjectConsentFile, ProjectConsentToken


def sanitize_string(_string):
    # replace umlauts
    _string = re.sub('[ä]', 'ae', _string)
    _string = re.sub('[Ä]', 'Ae', _string)
    _string = re.sub('[ö]', 'oe', _string)
    _string = re.sub('[Ö]', 'Oe', _string)
    _string = re.sub('[ü]', 'ue', _string)
    _string = re.sub('[Ü]', 'Ue', _string)
    _string = re.sub('[ß]', 'ss', _string)

    # remove accents
    _string = ''.join(c for c in unicodedata.normalize('NFKD', _string)
                      if not unicodedata.combining(c))

    # remove punctuation
    _string = _string.translate(str.maketrans('', '', string.punctuation))

    return _string


class SignProjectConsentView(generic.FormView):
    form_class = formset_factory(forms.SignatureForm, extra=2)
    template_name = 'project_consents/sign_project_consent.html'

    def dispatch(self, request, *args, **kwargs):
        self.token = get_object_or_404(ProjectConsentToken, pk=self.kwargs['token'])
        self.project = self.token.project
        self.subject = self.token.subject
        self.project_consent = self.project.projectconsent
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['consent'] = self.project_consent
        context['experimenter'] = self.token.created_by
        context['project'] = self.project
        context['subject'] = self.subject
        return context

    def form_valid(self, form):
        html_template = get_template('project_consents/signed_project_consent.html')

        custom_data = dict((key, value)
                           for key, value in self.request.POST.items()
                           if key.startswith('textfragment'))
        rendered_html = html_template.render({
            'consent': self.project_consent,
            'custom_data': custom_data,
            'experimenter': self.token.created_by,
            'form': form,
            'project': self.project,
            'subject': self.subject,
        })
        content = HTML(string=rendered_html, base_url=self.request.build_absolute_uri()).write_pdf()

        filename = '_'.join([
            *sanitize_string(self.subject.contact.display_name).split(),
            self.subject.contact.date_of_birth.strftime("%Y%m%d")
        ]) + '.pdf'
        filehandle = SimpleUploadedFile(
            name=filename,
            content=content,
            content_type='application/pdf'
        )
        ProjectConsentFile.objects.create(
            project_consent=self.project_consent,
            project_consent_version=self.project_consent.version,
            filehandle=filehandle,
            subject=self.subject
        )
        self.token.delete()

        return HttpResponse(content, content_type="application/pdf")
