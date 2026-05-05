from django.views.generic import TemplateView


class DashboardView(TemplateView):
    template_name = 'dashboard.html'


class LoginView(TemplateView):
    template_name = 'login.html'


class ProfileView(TemplateView):
    template_name = 'profile.html'


class RegistryListView(TemplateView):
    template_name = 'registry_list.html'


class RegistryDetailView(TemplateView):
    template_name = 'registry_detail.html'


class RegistryEditView(TemplateView):
    template_name = 'registry_edit.html'
