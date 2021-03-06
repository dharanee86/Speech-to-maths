from django.contrib.auth import authenticate, login, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth import views as auth_views
from django.http import Http404
from django.shortcuts import render, redirect, HttpResponse, reverse

from . import forms, models
from .views_utils import get_document, get_user

import json
import uuid

from s2m.core.formulae import Formula
from s2m.core.s2m_training import s2m_training

LATEX_BASE_TEMPLATE = """\\documentclass{article}
\\usepackage[utf8]{inputenc}

\\title{Title}
\\author{Author}
\\date{Date}

\\usepackage{natbib}
\\usepackage{graphicx}

\\begin{document}

\\maketitle

\\section{Introduction}

\\section{Conclusion}

\\end{document}"""


@login_required
def account(request):
    user = get_user(request)
    email_form = forms.ChangeEmailForm(
        None, initial={'email': request.user.email})
    password_form = forms.ChangePasswordForm(request.user, None)
    suppression_form = forms.DeleteAccountForm(request.user, None)
    return render(request, 'account.html', locals())


@login_required
def log_out(request, **kwargs):
    user = get_user(request)
    s2m_training.schedule(user)
    return auth_views.logout(request, **kwargs)


@login_required
def add_doc(request):
    doc = models.Document()
    doc.content = LATEX_BASE_TEMPLATE
    user = get_user(request)
    doc.author = user
    n = 1
    while True:
        if models.Document.objects.filter(author=user, title="Sans titre %d" % n):
            n += 1
        else:
            break
    doc.title = "Sans titre %d" % n
    uid = uuid.uuid4()
    while models.Document.objects.filter(address=uid):
        uid = uuid.uuid4()
    doc.address = uid
    doc.save()
    return redirect("document", doc.address)


@login_required
def change_email(request):
    user = get_user(request)
    if request.POST:
        email_form = forms.ChangeEmailForm(
            request.POST, initial={'email': request.user.email})
        if email_form.is_valid():
            user.email = email_form.cleaned_data['email']
            user.save()
            return HttpResponse(json.dumps({"action": "informSuccess"}))
    else:
        email_form = forms.ChangeEmailForm(
            None, initial={'email': request.user.email})
    return HttpResponse(json.dumps({"action": "updateForm", "html": str(email_form)}))


@login_required
def change_password(request):
    user = get_user(request)
    if request.POST:
        password_form = forms.ChangePasswordForm(request.user, request.POST)
        if password_form.is_valid():
            user.set_password(password_form.cleaned_data['new_password'])
            user.save()
            update_session_auth_hash(request, user)
            return HttpResponse(json.dumps({"action": "informSuccess"}))
    else:
        password_form = forms.ChangePasswordForm(request.user, None)
    return HttpResponse(json.dumps({"action": "updateForm", "html": str(password_form)}))


@login_required
def delete_account(request):
    user = get_user(request)
    if request.POST:
        suppression_form = forms.DeleteAccountForm(request.user, request.POST)
        if suppression_form.is_valid():
            docs = models.Document.objects.filter(author=user)
            for doc in docs:
                doc.delete()
            user.delete()
            return HttpResponse(json.dumps({"action": "redirect", "newAddress": reverse(sign_up)}))
    else:
        suppression_form = forms.DeleteAccountForm(request.user, None)
    return HttpResponse(json.dumps({"action": "updateForm", "html": str(suppression_form)}))


@login_required
def document(request, address):
    doc = get_document(request, address=address)
    text = doc.content
    try:
        doc.generate_pdf()
    except Exception as exc:
        print("Something did't work with the generation of the PDF file ; check out the 'save_document' function in interface/views.py")
    if doc:
        if doc.is_in_trash:
            return redirect("error_400")
        return render(request, 'document.html', locals())
    raise Http404


@login_required
def documents(request):
    user = get_user(request)
    try:
        for n in request.POST['delete-value'].split(';'):
            doc = get_document(request, id_=int(n))
            doc.is_in_trash = True
            doc.save()
    except Exception:
        pass
    docs = models.Document.objects.filter(author=user, is_in_trash=False)
    return render(request, 'documents.html', locals())


@login_required
def documents_search(request, context_length=50):
    user = get_user(request)
    docs = models.Document.objects.filter(author=user, is_in_trash=False)
    data = json.loads(request.POST['data'])
    search_value = data["searchValue"]
    response = []
    # On parcourt les documents, et on envoie ceux contenant les termes de la recherche
    # Cette structure peut être étendue à une regex
    for doc in docs:
        position = doc.content.lower().find(search_value)
        # Si l'on trouve le texte rechercé
        if position != -1:
            # On récupère ce qu'il y a avant, dans, et après le contenu
            pre = doc.content[max(0, position - context_length):position]
            con = doc.content[position:position + len(search_value)]
            post = doc.content[position + len(search_value):min(
                len(doc.content), position + len(search_value) + context_length)]
            contains_start = position > context_length
            contains_end = position + \
                len(search_value) + context_length < len(doc.content)
            # On rajoute le tout à la liste envoyée
            response.append(
                {"docID": doc.id, "preContent": pre, "content": con, "postContent": post,
                 "containsStart": contains_start, "containsEnd": contains_end})
    response = json.dumps(response)
    return HttpResponse(response)


@login_required
def regenerate_pdf(request, address):
    doc = get_document(request, address=address)
    try:
        doc.generate_pdf()
        doc.save()
        return HttpResponse(json.dumps({"toDo" : "newLink", "pdfUrl": doc.pdf.url}))
    except Exception as exc:
        print("Something did't work with the generation of the PDF file ; check out the 'save_document' function in interface/views.py")
        # This line can be used to test that the pdf is indeed changing if the pdf generator does not work
        # return HttpResponse(json.dumps({"toDo" : "newLink", "pdfUrl": "http://lesmaterialistes.com/files/pdf/classiques/machiavel-le-prince.pdf"})) 
        return HttpResponse(json.dumps({"toDo" : "displayError", "error": "La génération de PDF n'a pas fonctionnée. Le serveur n'est peut-être pas en état de le générer pour l'instant, ou votre code LaTeX pose peut-être problème."}))


@login_required
def save_document(request):
    data=json.loads(request.POST['data'])
    doc=get_document(request, id_=data["docID"])
    doc.content=data["newContent"]
    doc.save()
    s2m_training.schedule(doc)
    return HttpResponse(json.dumps({"result": True}))


def sign_up(request):
    form=forms.InscriptionForm(request.POST or None)
    if form.is_valid():
        username=form.cleaned_data['username']
        psw=form.cleaned_data['password']
        email=form.cleaned_data['email']
        user=models.Utilisateur()
        user.username=username
        user.set_password(psw)
        user.email=email
        user.save()
        user=authenticate(username=username, password=psw)
        login(request, user)
        return redirect("documents")
    return render(request, 'sign-up.html', locals())


@login_required
def training(request):

    def generate_training_data():
        random_formula=Formula.generate_random()
        return random_formula.latex(), random_formula.transcription()

    formule, text=generate_training_data()
    return render(request, 'training.html', locals())
