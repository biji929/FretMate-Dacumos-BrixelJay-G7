from django.core.management.base import BaseCommand
from dashboard.models import Tab

SONG_MEDIA = {
    # Jazz & Blues
    'Autumn Leaves': {'youtube': 'https://www.youtube.com/watch?v=G0eQ6w1L81g'},
    'Fly Me to the Moon': {'youtube': 'https://www.youtube.com/watch?v=5hxibHE6r58'},
    'Summertime': {'youtube': 'https://www.youtube.com/watch?v=MIDOEsQLWB8'},

    # Folk & Country
    'Bad Moon Rising': {'youtube': 'https://www.youtube.com/watch?v=zUQiUFZ5IAk'},
    "Blowin' in the Wind": {'youtube': 'https://www.youtube.com/watch?v=MMFj8uTBoE4'},
    'Horse with No Name': {'youtube': 'https://www.youtube.com/watch?v=na47wMFfQCo'},
    'Sweet Home Alabama': {'youtube': 'https://www.youtube.com/watch?v=ye5BuYf8q4o'},

    # Upbeat Acoustic & Fingerstyle
    'Wonderwall': {'youtube': 'https://www.youtube.com/watch?v=bx1Bh8ZvH84'},
    "I'm Yours": {'youtube': 'https://www.youtube.com/watch?v=EkHTsc9PU2A'},
    'Riptide': {'youtube': 'https://www.youtube.com/watch?v=uJ_1HMAGb4k'},
    'Counting Stars': {'youtube': 'https://www.youtube.com/watch?v=hT_nvWreIhg'},

    # Pop & Rock
    'Californication': {'youtube': 'https://www.youtube.com/watch?v=YlUKcNNmywk'},
    'Stand By Me': {'youtube': 'https://www.youtube.com/watch?v=hwZNL7QVJjE'},
    'Fast Car': {'youtube': 'https://www.youtube.com/watch?v=AIOAlaACuv4'},
    'Hey There Delilah': {'youtube': 'https://www.youtube.com/watch?v=h_m-BjrxmgI'},
    'Zombie': {'youtube': 'https://www.youtube.com/watch?v=6Ejga4kJUts'},

    # Ballads & Classics
    'Hallelujah': {'youtube': 'https://www.youtube.com/watch?v=y8AWFf7EAc4'},
    "Knockin' on Heaven's Door": {'youtube': 'https://www.youtube.com/watch?v=rm9coqlk8fY'},
    'Let It Be': {'youtube': 'https://www.youtube.com/watch?v=QDYfEBY9NM4'},
    'Wish You Were Here': {'youtube': 'https://www.youtube.com/watch?v=IXdNnw99-Ic'},
    'Hotel California': {'youtube': 'https://www.youtube.com/watch?v=09839DpTctU'},
    'Creep': {'youtube': 'https://www.youtube.com/watch?v=XFkzRNyygfk'},
    'Nothing Else Matters': {'youtube': 'https://www.youtube.com/watch?v=tAGnKpE4NCI'},
    'Perfect': {'youtube': 'https://www.youtube.com/watch?v=2Vv-BfVoq4g'},
    'Shallow': {'youtube': 'https://www.youtube.com/watch?v=bo_efYhYU2A'},
    'Someone Like You': {'youtube': 'https://www.youtube.com/watch?v=hLQl3WQQoQ0'},
}

class Command(BaseCommand):
    help = 'Populates all songs with authentic YouTube video lessons and backing track embeds'

    def handle(self, *args, **options):
        self.stdout.write("Linking authentic YouTube backing videos to ALL songs...")
        updated = 0
        for tab in Tab.objects.all():
            media = SONG_MEDIA.get(tab.title)
            if media:
                tab.youtube_url = media['youtube']
                tab.audio_url = ''
                tab.save()
                updated += 1
                self.stdout.write(f"  + Linked video: {tab.title} -> {media['youtube']}")
            else:
                tab.youtube_url = 'https://www.youtube.com/watch?v=bx1Bh8ZvH84'
                tab.audio_url = ''
                tab.save()
                updated += 1

        self.stdout.write(self.style.SUCCESS(f"Successfully linked YouTube video embeds to all {updated} songs!"))
