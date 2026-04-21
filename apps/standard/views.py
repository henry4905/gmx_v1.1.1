from django.shortcuts import render


def standardpage(request):
	return render (request, 'standard/standardpage.html')