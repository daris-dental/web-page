from django import forms


class BootstrapRadioSelect(forms.RadioSelect):
    template_name = 'widgets/bootstrap_radio.html'
    option_template_name = 'widgets/bootstrap_radio_option.html'


class BootstrapCheckboxSelectMultiple(forms.CheckboxSelectMultiple):
    template_name = 'widgets/bootstrap_radio.html'
    option_template_name = 'widgets/bootstrap_radio_option.html'