from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode


def send_activation_mail(request, user, activation_token):
    ''' Build an activation link and send it to the user's email address. '''
    # 1 Benuter ID kodieren 
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk)) # force_bytes bekommt die Benutzer ID und wandelt sie in Bytes um. urlsafe_base64_encode bekommt diese Bytes und erzeugt daraus die URL-taugliche Zeichenkette
    
    # 2 Aktivierungslink generieren
    activation_path = reverse("activation-mail", kwargs={'uidb64': uidb64, 'token': activation_token})
    activation_url = request.build_absolute_uri(activation_path) # hier wird nun einen vollständige Adresse inklusive Domain erzeugt
    
    # 3. E-Mail Inhalte definieren
    subject = 'Bitte aktiviere deinen Account'
    message = (
        f"Bitte klicke auf den folgenden Link, um deinen Account zu aktivieren:\n"
        f"{activation_url}\n\n"
        f"Falls du dich nicht registriert hast, kannst du diese E-Mail ignorieren."
    )
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [user.email]
    
    #4. E-Mail versenden
    send_mail(
        subject = subject,
        message = message,
        from_email=from_email,
        recipient_list=recipient_list,
        fail_silently=False
    )
    
def send_password_reset_mail(request, user, reset_token):
    ''' Build a password reset link and send it to the user's email address. '''
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    
    reset_path = reverse("confirm-password", kwargs={'uidb64': uidb64, 'token': reset_token}) # reverse() baut den Pfad mit Benutzer-ID und Token.
    reset_url = request.build_absolute_uri(reset_path) # build_absolute_uri() ergänzt Protokoll und Domain.
    
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [user.email]
    
    subject = 'Bitte ändere dein Passwort'
    message = (
        f"Bitte klicke auf den folgenden Link, um dein Passwort zu ändern:\n"
        f"{reset_url}\n\n"
        f"Falls du keine Passwortänderung angefordert hast, kannst du diese E-Mail ignorieren."
    )
        
    send_mail(
        subject = subject,
        message = message,
        from_email=from_email,
        recipient_list=recipient_list,
        fail_silently=False
    )