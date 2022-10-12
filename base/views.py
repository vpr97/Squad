from django.shortcuts import redirect, render
from django.http import HttpResponse
from .models import Room, Topic, Message
from .form import RoomForm, UserForm
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required

def loginPage(request):
    page = 'login'
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == "POST":
        username = request.POST.get('username').lower()
        password = request.POST.get('password')
        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request,'User does not exist.')

        user = authenticate(request, username=username, password = password)

        if user is not None:
            login(request,user)
            return redirect('home')
        else:
            messages.error(request,'Username or password does not exist.')


    return render(request, 'base/login_register.html',{'page':page})

def logoutUser(request):
    logout(request)
    return redirect('home')

def registerPage(request):
    form = UserCreationForm()

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit = False) #commit=False allows us to use the user object.
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request,'Registration is not allowed.')

    return render(request,'base/login_register.html',{'form':form})


def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q)
        ) # gets the value of all the topic created
    topic = Topic.objects.all()[0:5] # gets the value of all the topics created
    room_count = rooms.count()
    room_message = Message.objects.filter(Q(room__topic__name__icontains=q))

    print("roommessages",room_message)
    print(rooms)

    return render(request, 'base/home.html',{'rooms':rooms, 'topic':topic, 'room_count':room_count, 'room_message':room_message})

def room(request,pk):
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all().order_by('-created') #set.all() is used to query the children
    # Here room is the parent model and message is the child model, by this command we get all the messages in that room
    participants = room.participants.all()
    if request.method == 'POST':
        message = Message.objects.create(
            user = request.user,
            room = room,
            body = request.POST.get('body')
        )
        room.participants.add(request.user)
        return redirect('room', pk=room.id)
    return render(request, 'base/room.html',{'room': room, 'room_messages':room_messages, 'participants':participants})

def userProfile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    room_message = user.message_set.all()
    topics = Topic.objects.all()
    return render(request, 'base/profile.html',{'user':user, 'rooms':rooms, 'room_message':room_message, 'topics':topics})

@login_required(login_url='login')
def createRoom(request):
    form = RoomForm()
    topics = Topic.objects.all()
    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic,created = Topic.objects.get_or_create(name=topic_name)

        Room.objects.create(
            host=request.user,
            topic=topic,
            name=request.POST.get('name'),
            description=request.POST.get('description'),
        )
        # form = RoomForm(request.POST)
        # if form.is_valid():
        #     room = form.save(commit=False)
        #     room.host = request.user
        #     room.save()
        return redirect('home')
    context = {'form':form, 'topics':topics}
    return render(request,'base/room_form.html',context)

@login_required(login_url='login')
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room) # to have the form prefilled when opening
    topics = Topic.objects.all()

    if request.user != room.host: # restricting only logged in user to make update
        return HttpResponse('You can only update your room.')

    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic,created = Topic.objects.get_or_create(name=topic_name)
        # form = RoomForm(request.POST,instance=room) # instance=room provides the information on which room the update should happen
        # if form.is_valid():
        #     form.save()
        room.name = request.host.get('name')
        room.topic = topic
        room.description = request.host.get('description')
        room.save()
        return redirect('home')
    context = {'form': form,'topics':topics,'room':room}

    return render(request,'base/room_form.html', context)

@login_required(login_url='login')
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)
    if request.user != room.host: # restricting only logged in user to make update
        return HttpResponse('You can only delete your room.')

    if request.method == 'POST':
        room.delete() #deletes the selected room
        return redirect('home')
    return render(request,'base/delete.html',{'obj':room})

# Create your views here.
@login_required(login_url='login')
def deleteMessage(request, pk):
    message = Message.objects.get(id=pk)
    if request.user != message.user: # restricting only logged in user to make update
        return HttpResponse('You can only delete your room.')

    if request.method == 'POST':
        message.delete() #deletes the selected room
        return redirect('home')
    return render(request,'base/delete.html',{'obj':message})


@login_required(login_url='login')
def updateUser(request):
    user = request.user
    form = UserForm(instance=user)

    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user-profile', pk=user.id)
    return render(request, 'base/update-user.html',{'form':form})

def topicsPage(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    topics = Topic.objects.filter(name__icontains=q)
    return render(request, 'base/topics.html',{'topics':topics})

def activityPage(request):
    room_message = Message.objects.all()
    return render(request,'base/activity.html',{'room_message':room_message})
