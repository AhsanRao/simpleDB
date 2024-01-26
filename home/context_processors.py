# context_processors.py


def add_business_name(request):
    if request.user.is_authenticated and request.user.business is not None:
        return {"business_name": request.user.business.name}
    else:
        return {"business_name": "A Simple Database"}
