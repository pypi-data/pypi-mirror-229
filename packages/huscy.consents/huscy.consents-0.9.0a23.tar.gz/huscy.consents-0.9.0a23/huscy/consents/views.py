import json
from ast import literal_eval

from django.core.files.uploadedfile import SimpleUploadedFile
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.template.loader import get_template
from django.urls import reverse
from django.views import generic
from weasyprint import HTML

from huscy.consents.forms import ConsentForm, CreateConsentForm
from huscy.consents.models import Consent, ConsentCategory
from huscy.consents.services import create_consent_file


class AddTemplateTextFragmentMixin:
    def get(self, request, *args, **kwargs):
        if self.action == 'add':
            template_text_fragment = literal_eval(request.GET.get('template_text_fragment'))
            self.text_fragments.append(template_text_fragment)
        return super().get(request, *args, **kwargs)


class RemoveTextFragmentMixin:
    def get(self, request, *args, **kwargs):
        if self.action == 'remove':
            index = int(request.GET.get('index'))
            del self.text_fragments[index]
        return super().get(request, *args, **kwargs)


class ExchangeTextFragmentsMixin:
    def get(self, request, *args, **kwargs):
        if self.action in ['move_up', 'move_down']:
            index = int(request.GET.get('index'))

        if self.action == 'move_up':
            self.text_fragments[index], self.text_fragments[index-1] = (
                self.text_fragments[index-1], self.text_fragments[index])

        if self.action == 'move_down':
            self.text_fragments[index], self.text_fragments[index+1] = (
                self.text_fragments[index+1], self.text_fragments[index])

        return super().get(request, *args, **kwargs)


class UpdateTextFragmentMixin:
    def get(self, request, *args, **kwargs):
        if self.action == 'update':
            index = int(request.GET.get('index'))
            self.text_fragments[index]['properties']['text'] = request.GET.get('text')
        return super().get(request, *args, **kwargs)


class CreateConsentView(AddTemplateTextFragmentMixin, RemoveTextFragmentMixin,
                        ExchangeTextFragmentsMixin, UpdateTextFragmentMixin, generic.FormView):
    form_class = CreateConsentForm
    template_name = 'consents/create_consent.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data()
        context.update({
            'categories': ConsentCategory.objects.all(),
            'selected_category': self.category,
            'text_fragments': self.text_fragments,
            'text_fragments_as_json': json.dumps(self.text_fragments),
        })
        return context

    def get(self, request, *args, **kwargs):
        self.action = request.GET.get('action', None)
        self.category = (get_object_or_404(ConsentCategory, pk=request.GET.get('category'))
                         if 'category' in request.GET else None)
        self.text_fragments = json.loads(request.GET.get('text_fragments', '[]'))

        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('consent-created')


class SignConsentView(generic.FormView):
    form_class = ConsentForm
    template_name = 'consents/sign_consent.html'

    def dispatch(self, request, *args, **kwargs):
        self.consent = get_object_or_404(Consent, pk=self.kwargs['consent_id'])
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['consent'] = self.consent
        return context

    def form_valid(self, form):
        html_template = get_template('consents/signed_consent.html')

        custom_data = dict((key, value)
                           for key, value in self.request.POST.items()
                           if key.startswith('textfragment'))
        rendered_html = html_template.render({
            "consent": self.consent,
            'custom_data': custom_data,
            'form': form,
        })
        content = HTML(string=rendered_html, base_url=self.request.build_absolute_uri()).write_pdf()
        filename = self.consent.name
        filehandle = SimpleUploadedFile(
            name=filename,
            content=content,
            content_type='application/pdf'
        )
        create_consent_file(self.consent, filehandle)
        return HttpResponse(content, content_type="application/pdf")
