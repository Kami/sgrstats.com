from django.shortcuts import render_to_response, get_object_or_404, HttpResponse, HttpResponseRedirect, Http404

from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.contrib import messages

from django.db.models import Count
from polls.models import Poll, Choice, Vote

def each_user_can_only_vote_once_per_poll(function = None):
    """ Check that user with this IP address hasn't already voted in this poll. """
    def _dec(view_func):  
        def _view(request, *args, **kwargs): 
            ip_address = request.META['REMOTE_ADDR']

            vote_count = Vote.objects.filter(choice__poll__id = kwargs['poll_id'], ip_address = ip_address).count()

            if vote_count >= 1:
                return HttpResponseRedirect(reverse('poll_results', kwargs = kwargs))

            return view_func(request, *args, **kwargs)
        
        _view.__name__ = view_func.__name__
        _view.__dict__ = view_func.__dict__
        _view.__doc__ = view_func.__doc__
        
        return _view
    
    if function is None:
        return _dec
    else:
        return _dec(function)

def index(request):
    polls = Poll.objects.all().order_by('-date_published')[:15]
    
    return render_to_response('polls/index.html', {'polls': polls}, context_instance = RequestContext(request))

def details(request, poll_id):
    poll = get_object_or_404(Poll, pk = poll_id)
    
    # If user with this IP address has already voted, show him the poll results
    if get_user_vote_count(poll_id, request.META['REMOTE_ADDR']) >= 1 or not poll.enabled:
        return results(request, poll_id)
    
    return render_to_response('polls/details.html', {'poll': poll}, context_instance = RequestContext(request))

def results(request, poll_id, choice_id = None):
    poll = get_object_or_404(Poll, pk = poll_id)
    vote_count = poll.choice_set.aggregate(Count('vote'))['vote__count']

    return render_to_response('polls/results.html', {'poll': poll, 'vote_count': vote_count, 'selected_choice': int(choice_id) if choice_id != None else choice_id}, context_instance = RequestContext(request))

@each_user_can_only_vote_once_per_poll
def vote(request, poll_id):
    poll = get_object_or_404(Poll, pk = poll_id)
    
    try:
        selected_choice = poll.choice_set.get(pk = request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        # Missing or invalid choice
        messages.add_message(request, messages.ERROR, 'Missing or invalid choice.')
        
        return HttpResponseRedirect(reverse('poll_details', args = (poll_id,)))
        
    else:
        vote = Vote(choice = selected_choice, ip_address = request.META['REMOTE_ADDR'])
        vote.save()
        
        return HttpResponseRedirect(reverse('poll_results_choice', args = (poll.id, selected_choice.id)))
    
# Help Function
def get_user_vote_count(poll_id, ip_address):
    return Vote.objects.filter(choice__poll__id = poll_id, ip_address = ip_address).count()