from django.contrib import admin
from gansha.event.models import Event

class EventAdmin(admin.ModelAdmin):
    list_display=('id','title','description',
                  'isprivacy','progress','num_se','start_date','end_date')
    
admin.site.register(Event,EventAdmin)
