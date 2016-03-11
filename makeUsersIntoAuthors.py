from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from api.models import Author

'''
python manage.py shell
execfile("makeUsersIntoAuthors.py")
'''

users = User.objects.all()
for i in range(len(users)):
	try:
		author = Author.objects.get(user=users[i])
	except ObjectDoesNotExist:
		author = Author.objects.create(user=users[i])
		author.save()
print("done")