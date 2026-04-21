from django.shortcuts import render

def aboutpage(request):
	return render (request, 'about/about.html')