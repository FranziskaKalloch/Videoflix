# Was sind Signals?


# Parameter
# sender = welche Instanz hat es gesendet
# instance = die Instanz selber, die Videoklasse hier, das Objektvideo
# created = Boolean Variable, wenn das ganze neu erstellt wurde, dann mache dies
# kwargs = 

from django.db.models.signals import post_save



# Wird immer ausgeführt, wenn 
def video_post_save(sender, instance, created, **kwargs): # wenn die Funktion später automatische aufgerufen werden soll, dann müssen die 4 Parameter enthalten sein!
    if created:
        print('Video wurde gespeichert')




def create_lecture(sender, instance, created, **kwargs):
    if created:
        print('New object created')
        

# Signal definieren
# post_save.connect(create_lecture, sender=Lecture)