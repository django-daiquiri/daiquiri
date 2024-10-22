from django.forms.renderers import TemplatesSetting


class DaiquiriFormRenderer(TemplatesSetting):
    form_template_name = 'core/form/form.html'
