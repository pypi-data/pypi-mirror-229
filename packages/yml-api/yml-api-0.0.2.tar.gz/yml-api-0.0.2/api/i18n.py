
def translate(term):
    from api.viewsets import specification
    s = specification.i18n.get(term.lower())
    if s is None:
        s = term.replace('_', ' ').title()
        # print('{}: {}'.format(term, s))
    return s