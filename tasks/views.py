from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login # might be deleted in the future
from django.contrib import messages # might be deleted in the future
from django.http import HttpResponse, HttpResponseNotAllowed
from .models import Team , Task , UserProfile # importing from models.py Item sql table
from django.template import loader
from .forms import CustomUserForm, TeamForm,TaskForm, UserUpdateForm, UserProfileUpdateForm 

# Create your views here.
from django.http import HttpResponse

from django.core.exceptions import PermissionDenied
from django.views.decorators.http import require_POST

from .permissions import visible_tasks_for, can_edit_task
from django.db.models import Q

# ================= ADMIN-INDEX // CONTROL-PANEL =====================

@login_required
def admin_index(request):
    
    if not request.user.is_superuser: # Only admin can access this page
        return HttpResponse("You are not authorized to acces this page.")
    
    task_list = Task.objects.all() # rn they (task_list) are objects
    team_list = Team.objects.all()
    user_list = UserProfile.objects.all()
    
    task_count = task_list.count() # count metod counts all the elements in the list
    team_count = team_list.count()
    user_count = user_list.count()
    
    # template = loader.get_template("tasks/index.html") # with the help of loader we save the html like an variable.
    context = { # we use this to create dynamique pages we use this variable as an attribute | we use the content in it like objects
        "task_list":task_list,
        "team_list":team_list,
        "user_list":user_list,
        
        "user_count": user_count,
        "team_count": team_count,
        'task_count': task_count,
        
        "current_user": request.user, # after login it contains current users information
    }
    return render(request,"admin-index.html",context)


# ================= INDEX =====================


@login_required
def index(request):
    current_user = request.user

    # Tasks created by, assigned to, or shared
    # through teams with the current user.
    users_task_list = Task.objects.filter(
        Q(creator=current_user)
        | Q(users=current_user)
        | Q(teams__users=current_user)
    ).distinct()

    # Public tasks are visible to all authenticated users.
    public_task_list = Task.objects.filter(private=False)

    # Teams the current user belongs to.
    users_team = current_user.teams.all()

    context = {
        "current_user": current_user,
        "public_task_list": public_task_list,
        "users_task_list": users_task_list,
        "users_team": users_team,
    }

    return render(request, "index.html", context)


# ======================= DETAILS =====================
# leads us to details.html pages

@login_required
def detail_task(request, task_id):
    task = get_object_or_404(
        visible_tasks_for(request.user),
        pk=task_id
    )

    context = {
        "task": task,
        "visible_subtasks": task.subtasks.filter(
            pk__in=visible_tasks_for(request.user).values("pk")
        ),
        "can_edit": can_edit_task(request.user, task),
    }

    return render(request, "tasks/detail.html", context)

@login_required
def detail_team(request, team_id):
    team = get_object_or_404(Team, pk=team_id)

    visible_tasks = visible_tasks_for(request.user).filter(
        teams=team
    )

    return render(request, "teams/detail.html", {
        "team": team,
        "visible_tasks": visible_tasks,
    })


@login_required
def detail_user(request, user_id):
    profile = get_object_or_404(UserProfile, pk=user_id)

    visible_tasks = visible_tasks_for(request.user).filter(
        users=profile.user
    )

    return render(request, "users/detail.html", {
        "profile": profile,
        "visible_tasks": visible_tasks,
    })



# =================== CREATE ====================
@login_required
def create_user(request):
    form = CustomUserForm(request.POST or None)

    if not request.user.is_superuser: # Only admin can create a user
        return HttpResponse("Only superusers can create new users.")

    if form.is_valid():
        form.save()
        return redirect("task:index")

    return render(request, "users/user-form.html", {"form": form})

@login_required
def create_team(request):
    form = TeamForm(request.POST or None)

    if form.is_valid():
        form.save()
        return redirect("task:index")

    return render(request, "teams/team-form.html", {"form": form})

@login_required
def create_task(request):
    form = TaskForm(request.POST or None)

    if form.is_valid():
        task = form.save(commit=False) # Create task instance, but not saved yet
        task.creator = request.user # Set the current user as the creator
        task.save() # Save the task with the creator
        form.save_m2m() # Creating forms from models | # Save many-to-many fields (users, teams, subtasks) | if not it causes problems
        return redirect("task:index")

    return render(request, "tasks/task-form.html", {"form": form})

@login_required
def create_sub_task(request,task_id):
    
    task = Task.objects.get(id=task_id)
    # Cheking autorization
    in_any_team = False #checks if any user is in one of the teams assaigned on to the task
    for team in task.teams.all():
        if request.user in team.users.all():
            in_any_team = True

    if (not in_any_team) and (request.user != task.creator) and (request.user  not in task.users.all()) and not request.user.is_superuser: # you shall not pass (unless y are superuser or in the team)
        return HttpResponse("You are not authorized to create an sub-task for this task")

    # Creation of sub-task , (we can not use the create_task function because if we do we can not link task and sub-task)
    form = TaskForm(request.POST or None)

    if form.is_valid():
        sub_task = form.save(commit=False) 
        sub_task.creator = request.user 
        sub_task.save() 
        form.save_m2m() 
        
        # we are saving sub-task to task
        task.subtasks.add(sub_task)
        task.save()
        
        return redirect("task:index")

    return render(request, "tasks/task-form.html", {"form": form})

@login_required
def create_sub_team(request,task_id):
    
    task = Task.objects.get(id=task_id)
    # Cheking autorization
    in_any_team = False #checks if any user is in one of the teams assaigned on to the task
    for team in task.teams.all():
        if request.user in team.users.all():
            in_any_team = True

    if (not in_any_team) and (request.user != task.creator) and (request.user  not in task.users.all()) and not request.user.is_superuser: # you shall not pass (unless y are superuser or in the team)
        return HttpResponse("You are not authorized to create an sub-task for this task")

    # Creation of sub-task , (we can not use the create_task function because if we do we can not link task and sub-task)
    form = TeamForm(request.POST or None)

    if form.is_valid():
        sub_team = form.save(commit=False)
         
        sub_team.save()
        task.teams.add(sub_team) # first save team to server then add in to the task
        
        form.save_m2m()
        return redirect("task:index")

    return render(request, "teams/team-form.html", {"form": form})
    
    

# ================== UPDATE =====================

@login_required
def update_user(request, id):  # TODO: Should make it right it is creating new users
    user_profile = get_object_or_404(UserProfile, id=id)
    user = user_profile.user

    if request.user != user and not request.user.is_superuser: # you shall not pass (unless y are superuser or profileOwner)
        return HttpResponse("You are not authorized to update this profile.")


    user_form = UserUpdateForm(request.POST or None, instance=user)  # instance=user will put all the info of the user into our form
    profile_form = UserProfileUpdateForm(request.POST or None, request.FILES or None, instance=user_profile)  # extra user info && dont fotget to add 2 formats into the html page

    if user_form.is_valid() and profile_form.is_valid():
        user_form.save()
        profile_form.save() # saving the modified data

        messages.success(request, "User has been updated!!!") 
        return redirect("task:index")  # go back to index after update

    return render(request, 'users/user-form.html', {
        'form': user_form,
        'profile_form': profile_form,
        'user': user
    })

@login_required
def update_team(request, id):
    team = Team.objects.get(id=id)
    form = TeamForm(request.POST or None, instance=team)

    
    if (request.user  not in team.users.all()) and not request.user.is_superuser: # you shall not pass (unless y are superuser or in the team)
        return HttpResponse("You are not authorized to update this profile.")

    if form.is_valid():
        form.save()
        return redirect("task:index")

    return render(request, 'teams/team-form.html', {'form': form, 'team': team})

@login_required
def update_task(request, id):
    task = Task.objects.get(id=id)
    form = TaskForm(request.POST or None, instance=task)

    in_any_team = False #checks if any user is in one of the teams assaigned on to the task
    for team in task.teams.all():
        if request.user in team.users.all():
            in_any_team = True

    if (not in_any_team) and (request.user != task.creator) and (request.user  not in task.users.all()) and not request.user.is_superuser: # you shall not pass (unless y are superuser or in the team)
        return HttpResponse("You are not authorized to update this profile.")


    if form.is_valid():
        form.save()
        return redirect("task:index")

    return render(request, 'tasks/task-form.html', {'form': form, 'task': task})


# ================= DELETE =======================
@login_required
def delete_user(request, id):
    userProfile = UserProfile.objects.get(id=id)
    user = userProfile.user # userProfile and user is connected but we should delete
    # user because it is the main one and we make relations with teams and tasks with 
    # user class not with the other

    if request.user != user and not request.user.is_superuser: # you shall not pass (unless y are superuser or profileOwner)
        return HttpResponse("You are not authorized to delete this profile.")

    if request.method == 'POST':
        user.delete()
        return redirect('task:index')

    return render(request, 'users/user-delete.html', {'user': user})

@login_required
def delete_team(request, id):
    team = Team.objects.get(id=id)
    
    if (request.user  not in team.users.all()) and not request.user.is_superuser: # you shall not pass (unless y are superuser or in the team)
        return HttpResponse("You are not authorized to delete this team.")

    if request.method == 'POST':
        team.delete()
        return redirect('task:index')

    return render(request, 'teams/team-delete.html', {'team': team})

@login_required
def delete_task(request, id):
    task = Task.objects.get(id=id)
    
    if (request.user != task.creator) and not request.user.is_superuser: # you shall not pass (unless y are superuser or in the team)
        return HttpResponse("You are not authorized to delete this. Only the creator of this task can delete it")


    if request.method == 'POST':
        task.delete()
        return redirect('task:index')

    return render(request, 'tasks/task-delete.html', {'task': task})

# ================= Enter ==========================
@login_required
@require_POST
def enter_team(request, team_id, user_id):
    team = get_object_or_404(Team, pk=team_id)
    profile = get_object_or_404(UserProfile, pk=user_id)

    # Only team members or superusers can add users.
    if not (
        request.user.is_superuser
        or team.users.filter(pk=request.user.pk).exists()
    ):
        raise PermissionDenied

    team.users.add(profile.user)

    return redirect("task:detail_team", team_id=team.pk)

    
# ================= Leave ==========================

@login_required
@require_POST
def leave_team(request, team_id, user_id):
    team = get_object_or_404(Team, pk=team_id)
    profile = get_object_or_404(UserProfile, pk=user_id)

    target_user = profile.user

    # Users can leave themselves.
    # Team members and superusers can remove other users.
    if not (
        request.user == target_user
        or request.user.is_superuser
        or team.users.filter(pk=request.user.pk).exists()
    ):
        raise PermissionDenied

    team.users.remove(target_user)

    return redirect("task:detail_team", team_id=team.pk)


# ================= HELLO WORLD ==========================

# @login_required # we do not need and login_required this method does nothing.
def item(request):
    return HttpResponse("<h1>This is an item view</h1>")
    # we don't realy need to do this we can add html files with templates
    # this is not the proper way 




