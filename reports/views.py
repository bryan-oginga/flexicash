from django.shortcuts import render

def FlexicashDashboard(request):
    context = {}
    return render(request, 'dashboard.html',context)