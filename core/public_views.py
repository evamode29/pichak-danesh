from django.shortcuts import render


def about(request):
    return render(request, "public/about.html")


def contact(request):
    return render(request, "public/contact.html")


def privacy(request):
    return render(request, "public/privacy.html")


def terms(request):
    return render(request, "public/terms.html")


def refund(request):
    return render(request, "public/refund.html")
