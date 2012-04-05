from django.template import Library, Node, TemplateSyntaxError

from stats.views import get_next_rank_title_and_exp_points

register = Library()

class SetVariable(Node):
    def __init__(self, varname, nodelist):
        self.varname = varname
        self.nodelist = nodelist

    def render(self,context):
        context[self.varname] = self.nodelist.render(context) 
        return ''

@register.tag(name = 'setvar')
def setvar(parser, token):
    """
    Set value to content of a rendered block. 
    {% setvar var_name %}
     ....
    {% endsetvar
    """
    try:
        # split_contents() knows not to split quoted strings.
        tag_name, varname = token.split_contents()
    except ValueError:
        raise TemplateSyntaxError, "%r tag requires a single argument for variable name" % token.contents.split()[0]

    nodelist = parser.parse(('endsetvar',))
    parser.delete_first_token()
    return SetVariable(varname, nodelist)

@register.simple_tag
def active(request, pattern):
    if request.path.startswith(pattern):
        return 'active'
    return ''

@register.simple_tag
def next_rank(category, exp_current):
    next_rank = get_next_rank_title_and_exp_points(category, exp_current)
    
    if not next_rank:
        return 'Next rank is unknown'
    
    (title, exp_needed, exp_total) = next_rank
    return '<strong>%d EXP</strong> needed to reach the rank <strong>%s</strong> (<strong>%d EXP</strong>)' % (exp_needed, title, exp_total)