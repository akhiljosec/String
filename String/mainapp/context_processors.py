
subjects = ('common', 'physics', 'chemistry', 'maths', 'artificial intelligence', 'nano technology', 'quantum computing')
product_types = ('book', 'cap')

def all_subjects(request):
    subjects = ['physics', 'chemistry', 'maths']
    return dict(subjects=subjects)
