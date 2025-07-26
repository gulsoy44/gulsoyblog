from django import forms
from .models import Post, Document
from django.conf import settings
from django.contrib.auth import get_user_model # <--- ADD THIS LINE HERE

class PostForm(forms.ModelForm):
    shared_with = forms.ModelMultipleChoiceField(
        queryset=None,
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label="Share with specific users (only if private)"
    )

    class Meta:
        model = Post
        fields = ['title', 'content', 'is_public', 'shared_with']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 5}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            # CORRECTED LINE: Use get_user_model() to get the actual model class
            self.fields['shared_with'].queryset = get_user_model().objects.exclude(pk=user.pk)


class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['file', 'description']

DocumentFormSet = forms.inlineformset_factory(
    Post,
    Document,
    form=DocumentForm,
    extra=1,
    can_delete=True
)