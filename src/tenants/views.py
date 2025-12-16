from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404,redirect
from django.contrib.auth import get_user_model
from .models import Tenants
from helpers.db.schemas import use_tenant_schema
from allauth.account.forms import SignupForm
User = get_user_model()

@login_required
def tenant_list_view(request):
    owner=request.user
    context = {
        "object_list": Tenants.objects.filter(owner=owner),
        "owner_name":owner.username
    }
    return render(request, "tenants/list.html", context)


@login_required
def tenant_detail_view(request, pk):
    instance = get_object_or_404(Tenants, pk=pk)
    enterprise_users=User.objects.none()
    with use_tenant_schema(instance.schema_name,create_if_missing=True,revert_public=True):
        enterprise_users=list(User.objects.all())
    context = {
        "object": instance,
        "instance": instance,
        "enterprise_users":enterprise_users
    }
    return render(request, "tenants/detail.html", context)

@login_required
def tenant_createuser_view(request, pk):
    instance = get_object_or_404(Tenants, pk=pk)

    form = None # Initialize form outside the with block in case of GET request

    with use_tenant_schema(instance.schema_name,create_if_missing=True,revert_public=True):
        form=SignupForm(request.POST or None)
        if form.is_valid():
            form.save(request)
            # No need to reassign pk, instance.pk is already what we need
            return redirect(f'/tenants/{instance.pk}') # Use instance.pk directly
    
    context = {
        "object": instance,
        "instance": instance,
        "form": form, # Make sure to pass the form to the context
        "owner_name": instance.owner,
    }
    return render(request, "tenants/new-user.html", context)
