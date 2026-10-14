from django import forms


class BootstrapFormMixin:
    """Añade clases Bootstrap 5 a los widgets que lo necesitan."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            widget = field.widget
            classes = set((widget.attrs.get('class') or '').split())

            if isinstance(widget, forms.HiddenInput):
                continue
            if isinstance(widget, (forms.RadioSelect, forms.CheckboxSelectMultiple)):
                continue  # los maneja el widget personalizado
            if isinstance(widget, forms.CheckboxInput):
                classes.add('form-check-input')
            elif isinstance(widget, forms.Select):
                classes.add('form-select')
            else:
                classes.add('form-control')

            widget.attrs['class'] = ' '.join(sorted(classes)).strip()

            if isinstance(widget, (forms.TextInput, forms.EmailInput,
                                   forms.NumberInput, forms.PasswordInput,
                                   forms.Textarea)) and not widget.attrs.get('placeholder'):
                widget.attrs['placeholder'] = field.label or name.replace('_', ' ').title()