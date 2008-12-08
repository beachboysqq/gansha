from django.forms import ModelForm
from gansha.event.models import Event,Sub_event

class EventForm( ModelForm ):
##    def clean_end_date( self ):
##        start_date = self.cleaned_data["start_date"]
##        end_date = self.cleaned_data["end_date"]
##        if end_date < start_date:
##            raise forms.ValidationError("finish date shouldn't earlier than start date!")
    class Meta:
        model=Event
        exclude=('progress','num_se','start_date','end_date','publish_date','user_id')

class Sub_eventForm( ModelForm ):
    class Meta:
        model=Sub_event
        #exclude=('event_id',)


